#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import pathlib
import random
import re
from collections import defaultdict
from enum import IntEnum
from typing import Tuple, Set, Optional, List

import jieba.analyse
import networkx as nx
from geopy.distance import great_circle
from shapely.geometry import Polygon, Point

from .utils import ChinaAddress
from .utils import DistrictGraphGen
from .utils import JacardCaompare
from .utils import (normalize_region, preprocess_string,
                    cut_parentheses, postprocess)
from .utils import parser
from .utils.distance import levenshtein
from .utils.exceptions import MapApiException
from .utils.log import getLogger
from .utils.map import AMapApi
from .utils.search import BaseSearchEngine


# logging.basicConfig(format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
# logger = logging.getLogger("binquire")
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(level=logging.DEBUG)
# logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger('urllib3').setLevel(logging.WARNING)


class AddressResultCode(IntEnum):
    MapApi_ERROR = -6
    AREA_TOO_BIG = -5   # area is too big
    LNG_LAT_LEVEL_TOO_BIG = -4  # longitude and latitude level is big than street
    MISS_CITY = -3  # address without city field
    MISS_DETAIL = -2    # address without detail field
    EMPTY_ADDRESS = -1  # address string is emtpy or None
    MISMATCH = 0    # two addresses are not same
    EXACT_MATCH = 1     # two addresses are the same
    AMBIGUOUS_MATCH = 2     # two addresses may be the same


class NameResultCode(IntEnum):
    CANT_COMPARE = -1   # dianhua no result so can not compare
    MISMATCH = 0    # compare result is not match
    MATCH = 1   # compare result is exact match
    AMBIGUOUS_MATCH = 2     # compare result is ambiguous match
    TEST = 9999     # for testing code
    IGNORE = 99999  # no suggest match result


def measure_time(func):
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        start = loop.time()
        r = await func(*args,**kwargs)
        print("T",func.__name__, "%.3f sec" % (loop.time() - start))
        return r
    return wrapper


def show_start_time(func):
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        # print("S",func.__name__, "%.3f sec" % (loop.time()) )
        r = await func(*args,**kwargs)
        return r
    return wrapper


class ThirdPartyPool(object):

    def __init__(self):
        self.pool = set()

    def random_choice(self):
        return random.sample(self.pool, 1)[0]

    def register_api(self, api):
        self.pool.add(api)

    def remove_api(self, api):
        try:
            self.pool.remove(api)
        except KeyError:
            return False
        return True

    def __iter__(self):
        for api in self.pool:
            yield api

    def __bool__(self):
        return bool(self.pool)

    def __nonzero__(self):
        return self.__bool__()

class AddressInquire(object):

    logger = getLogger('AddressInquire')

    def __init__(self, key='',
                 search_engine=None,
                 map_wrapper=AMapApi,
                 concurrency_limit=300, **kwargs):

        self.key = key
        self.base_payload = {'key':key}
        self.map_api = map_wrapper(key, concurrency_limit)
        self.area_tolerate = kwargs.get('area', 40000)
        self.__long_distance = kwargs.get('long_distance', 1000)
        self.__short_distance = kwargs.get('short_distance', 50)
        self.search_engine = search_engine
        self.third_party_api_pool = ThirdPartyPool()
        self.ss = asyncio.Semaphore(100)

    def register_third_party_api(self, third_party) -> None:
        self.third_party_api_pool.register_api(third_party)

    def remove_third_party_api(self, third_party) -> bool:
        return self.third_party_api_pool.remove_api(third_party)

    def address_to_point(self,address: str) -> list:
        return self.map_api.address_to_point(address)

    async def async_address_to_point(self, address: str) -> list:
        return await self.map_api.async_address_to_point(address)

    def isIntersects(self, points1, points2):
        pg1 = Polygon(points1)
        pg2 = Polygon(points2)
        return pg1.intersects(pg2)

    async def _show_url(self,addr1, addr2,size=500):
        url = f'http://restapi.amap.com/v3/staticmap?zoom=15&size={size}*{size}' \
              f'&key={self.key}&scale=1'

        paths = []
        mks = []
        A = 'A'
        a2 = ChinaAddress(addr2)
        for addr in [addr1, addr2]:
            x = await self.map_api.async_address_to_point(addr, city=a2.city)
            A = chr(ord(A) + 1)
            if x and self.map_api.isPrecisionPoint(long_lat_level=x[0]):
                mk = f'mid,,{A}:' + ",".join(map(str, x[0][:-1]))
                mks.append(mk)
            else:
                x = await self.map_api.async_address_to_polygon_points(addr)
                if x:
                    pg = '5,0x0000FF,1,0xFFFF00,0.2:' + \
                         f'{x[0][0]},{x[0][1]};{x[0][0]},' \
                         f'{x[2][1]};{x[2][0]},{x[2][1]};{x[2][0]},{x[0][1]}'
                    paths.append(pg)
                else:
                    x = await self.map_api.async_address_to_point(addr, city=a2.city)
                    if x:
                        mk = f'mid,,{A}:' + ",".join(map(str, x[0][:-1]))
                        mks.append(mk)
        if paths:
            url = url + '&paths=' + "|".join(paths)
        if mks:
            url = url + '&markers=' + "|".join(mks)
        return url


    def get_result(self, addr1, addr2):
        r = self.map_api._wrapper_run_async(self.async_get_result(addr1,
                                                                  addr2))
        return r

    def ___point_close_point(self,p1, p2):
        d = great_circle(p1[::-1], p2[::-1]).meters
        if d > self.__long_distance:
            return AddressResultCode.MISMATCH
        elif d < self.__short_distance:
            return AddressResultCode.EXACT_MATCH
        return AddressResultCode.AMBIGUOUS_MATCH

    def __point_close_block(self,p1, p2):
        if self.map_api.geom_area(p1) > self.area_tolerate:
            return AddressResultCode.AREA_TOO_BIG

        polygon = Polygon(p1)
        point = Point(*p2[0])
        if polygon.intersects(point):
            return AddressResultCode.AMBIGUOUS_MATCH

        return AddressResultCode.MISMATCH

    def __block_close_block(self, p1, p2):
        if self.map_api.geom_area(p1) > self.area_tolerate or \
                self.map_api.geom_area(p2) > self.area_tolerate:
            return AddressResultCode.AREA_TOO_BIG
        else:
            pg1 = Polygon(p1)
            pg2 = Polygon(p2)
            if pg1.intersects(pg2) or pg1 == pg2:
                return AddressResultCode.AMBIGUOUS_MATCH

        return AddressResultCode.MISMATCH

    @staticmethod
    def __complete_endswith(full_str, lack_str):
        f_endswith = full_str[-1]
        l_endswith = lack_str[-1]
        if f_endswith in ['楼', '号', '室'] and re.match('[0-9]', l_endswith):
            lack_str = "".join([lack_str, f_endswith])
        return lack_str

    async def _get_es_address(self, name: str, phone: str):
        es_addresses = []
        # get es addresses
        r = await self.search_engine.search(name=name, phone=phone, size=5)
        for source in r:
            ele = source.get('_source', {})
            if ele.get('address'):
                es_addresses.append(ele.get('address').strip())
        return es_addresses

    async def _get_amap_address(self, name: str, city: str):
        return await self.map_api.async_get_address_by_name(name, city)

    async def _get_third_party_address(self, api, name: str) -> Optional[str]:
        try:
            result = await api.search(name)
            return api.decode_address(result)
        except Exception:
            return None

    async def async_get_all_result(self, name: str, phone: str, address: str):
        async def gen_result(source, address, s_address):
            match_result, detail_similarity, min_d, max_d = \
                await self.async_get_result(address, s_address)
            if s_address:
                rew_similarity = 1 - levenshtein(address, s_address)
            else:
                rew_similarity = None
            result = {'source': source,
                      'match_result': match_result,
                      'detail_similarity': detail_similarity,
                      'min_distance': min_d,
                      'max_distance': max_d,
                      'raw_address_similarity': rew_similarity,
                      'address':s_address or ""}

            return result

        search_tasks = []
        sources = []
        if self.search_engine and False:
            search_tasks.append(self._get_es_address(name, phone))
            sources.append('dianhua')
        if self.map_api:
            city = ChinaAddress(address,False).city or ""
            search_tasks.append(self._get_amap_address(name, city))
            sources.append('amap')
        if self.third_party_api_pool and False:
            api = self.third_party_api_pool.random_choice()
            search_tasks.append(self._get_third_party_address(api, name))
            sources.append(api.name)

        loop = asyncio.get_event_loop()
        start = loop.time()
        search_addresses = await asyncio.gather(*search_tasks)
        # print("get_all_address", f"{loop.time() - start:.3f} sec")

        results = []
        for source, s_address in zip(sources, search_addresses):
            if isinstance(s_address, list):
                for ele in s_address:
                    results.append( gen_result(source,address,ele))
                if not s_address:
                    results.append( gen_result(source, address, None))
            else:
                results.append( gen_result(source, address, s_address))
        # start = loop.time()
        # print("gen_result len: ",len(results))
        result = await asyncio.gather(*results)
        # print("Pin time", f'{loop.time() - start:.3f} sec')
        return result

    @show_start_time
    async def async_get_result(self,addr1: str, addr2: str, **kwargs):
        if not (addr1 and addr2): return AddressResultCode.EMPTY_ADDRESS, None, None, None
        addr2 = self.__complete_endswith(addr1, addr2)
        addr1 = self.__complete_endswith(addr2, addr1)
        a1 = ChinaAddress(addr1,False)
        a2 = ChinaAddress(addr2,False)

        # address without detail
        string_similarity = 1-levenshtein(a1.detail, a2.detail)

        if not a1.detail or not a2.detail:
            self.logger.debug(f"input:{a1.detail}, bkwd:{a2.detail}, miss detail")
            return AddressResultCode.MISS_DETAIL, None, None, None

        if not (a1.city or a2.city or a2.province or a1.province):
            self.logger.debug(f'input:{a1}, bkwd:{a2} miss city')
            return AddressResultCode.MISS_CITY, string_similarity, None, None

        if a1 == a2:
            return AddressResultCode.EXACT_MATCH, string_similarity, 0, 0
        if a1.province and a2.province and a1.province != a2.province:
            return AddressResultCode.MISMATCH, string_similarity, None, None
        if a1.city and a2.city and a1.city != a2.city:
            return AddressResultCode.MISMATCH, string_similarity, None, None
        try:
            p1, p2 = await self.async_get_address_geo(a1, a2)
        except MapApiException as e:
            return AddressResultCode.MapApi_ERROR, string_similarity, None, None

        if not (p1 and p2):
            return AddressResultCode.LNG_LAT_LEVEL_TOO_BIG, \
                   string_similarity, None, None

        distances = self.get_geo_distance(p1, p2)
        match_result = AddressResultCode.MISMATCH

        if len(p1) < len(p2):
            p1, p2 = p2, p1

        if len(p2) == 1 and len(p1) == 1:
            match_result = self.___point_close_point(p1[0],p2[0])
        elif len(p2) == 1 and len(p1) != 1:
            match_result = self.__point_close_block(p1,p2)
        elif len(p2) != 1 and len(p1) != 1:
            match_result = self.__block_close_block(p1, p2)

        # if distances <= (0, 50):
        #     if 1 - levenshtein(a1.detail, a2.detail) > 0.7:
        #         match_result = AddressResultCode.EXACT_MATCH
        #     else:
        #         match_result = AddressResultCode.AMBIGUOUS_MATCH
        # elif distances[1] <= 50:
        #     if 1 - levenshtein(a1.detail, a2.detail) == 1:
        #         match_result = AddressResultCode.EXACT_MATCH
        #     elif 1 - levenshtein(a1.detail, a2.detail) > 0.5:
        #         match_result = AddressResultCode.AMBIGUOUS_MATCH

        return (match_result, string_similarity, *distances)

    # @measure_time
    async def async_get_address_geo(self, addr1: ChinaAddress, addr2: ChinaAddress, **kwargs):

        session = kwargs.get('session')
        city = addr2.city or addr1.city
        loop = asyncio.get_event_loop()
        p1, p2 = \
            await self.map_api.async_address_to_point(addr1.raw_address,
                                                      addr2.raw_address,
                                                      city=city,
                                                      session=session)
        # geo level too big, can't compare case
        if self.map_api.isAmbigiousPoint(long_lat_level=p1) or \
            self.map_api.isAmbigiousPoint(long_lat_level=p2):
            return [[], []]

        # Precision Point case
        self.logger.debug(f'({addr1},{p1}); ({addr2},{p2})')
        if self.map_api.isPrecisionPoint(long_lat_level=p1) and \
                self.map_api.isPrecisionPoint(long_lat_level=p2):
            return [[p1[:-1]], [p2[:-1]]]

        # block case
        if not self.map_api.isPrecisionPoint(long_lat_level=p1):
            # p1 = tips1 or [p1[:-1]]
            p1 = await self.map_api.async_address_to_polygon_points(
                addr1.raw_address, city=city, session=session) or [p1[:-1]]
        else:
            p1 = [p1[:-1]]

        if not self.map_api.isPrecisionPoint(long_lat_level=p2):
            # p2 = tips2 or [p2[:-1]]
            p2 = await self.map_api.async_address_to_polygon_points(
                addr2.raw_address, city=city, session=session) or [p2[:-1]]
        else:
            p2 = [p2[:-1]]

        self.logger.debug(f'({addr1},{p1}); ({addr2},{p2})')
        return [p1, p2]

    @staticmethod
    def get_geo_distance(p1, p2) -> Tuple[float, float]:
        min_dist = float('Inf')
        max_dist = float('-Inf')
        for coord1 in p1:
            for coord2 in p2:
                # great_circle([ latitude, longitude], [ latitude, longitude] )
                dist = great_circle(coord1[::-1], coord2[::-1]).meters
                min_dist = min(min_dist, dist)
                max_dist = max(max_dist, dist)
        return min_dist, max_dist


class NameInquire(object):

    logger = getLogger('NameInquire')

    def __init__(self,distance=JacardCaompare(),
                 name_rate=0.6, industry_rate=0.5, type_rate=0.5):
        self.distance = distance

        # init
        self.name_ambiguous = name_rate
        self.industry_ambiguous = industry_rate
        self.type_ambiguous = type_rate
        self.graph = DistrictGraphGen().get_graph()

    @staticmethod
    def get_info(_string):
        pre_input = preprocess_string(_string)
        pre_string, cuts = cut_parentheses(pre_input)
        if not pre_string:
            return None, None
        info = defaultdict(list)

        for item in cuts:
            r = parser(item)
            r = filter(lambda _pair: _pair.flag == 'region', r)
            r = map(lambda _pair: _pair.word, r)
            info['region'].extend(list(r))

        pairs = parser(pre_string)
        pairs = postprocess(pairs)
        for pair in pairs:
            info[pair.flag].append(pair.word)
        info['name'] = info.pop('x',[])
        return info, pre_string

    def __keep_parentheses(self,input_name, bkwd_name):
        i_name = re.sub('\W+', '', preprocess_string(input_name))
        b_name = re.sub('\W+', '', preprocess_string(bkwd_name))
        if self.distance.compare(i_name, b_name) > 0.8:
            return i_name, b_name
        else:
            return input_name, bkwd_name


    def get_result(self, input_name, bkwd_name):
        input_name,bkwd_name = self.__keep_parentheses(input_name,bkwd_name)
        input_info, pre_input = self.get_info(input_name)
        bkwd_info, pre_bkwd = self.get_info(bkwd_name)

        # Empty String
        if not input_info or not bkwd_info:
            return -1, -1, -1, -1

        # Exact match
        if pre_input == pre_bkwd:
            return 1, 1, 1, 1

        region_score = self.compare_region(input_info.get('region',[]),
                                           bkwd_info.get('region',[]))

        name_score = self.compare_string(input_info.get('name',[]),
                                         bkwd_info.get('name',[]),
                                         self.name_ambiguous)
        industry_score = self.compare_string(input_info.get('industry',[]),
                                             bkwd_info.get('industry',[]),
                                             self.industry_ambiguous)

        type_score = self.compare_string(input_info.get('type',[]),
                                         bkwd_info.get('type',[]),
                                         self.type_ambiguous)

        total = self.sum_score(region_score,name_score,industry_score,type_score)
        raw_string_score = self.distance.compare(input_name, bkwd_name)
        i_name = "".join(input_info.get('name',[]))
        b_name = "".join(bkwd_info.get('name',[]))

        # special case raw input and bkwd string is high similarity
        if 0.8 <= raw_string_score > total < 0.6:
            self.logger.info(f"jaccard distance > 0.8 :{input_name},{bkwd_name}")
            return 0.6, 0.6, 0.6, 0.6

        # special case name of input is full subset in name of bkwd

        elif i_name and len(i_name) > 2 and len(b_name) > 2 and \
                ( i_name in b_name or b_name in input_name) \
                and total < 0.6:
            self.logger.info(f"Complete substring :{input_name}, {bkwd_name}")
            return 0.6,0.6,0.6,0.6
        else:

            # clear error bkwd name
            item_count = 0
            for item in bkwd_info.values():
                if item:
                    flag = True
                    for ele in item:
                        if len(ele) == 1:
                            flag = False
                        elif len(ele) > 1:
                            flag = True
                            break
                    if flag:
                        item_count += 1
            if item_count <= 1 and name_score < 0.6:
                return -2, -2, -2, -2

            return region_score,name_score,industry_score,type_score

    def compare_region(self, input_regions, bkwd_regions):
        if not input_regions or not bkwd_regions:
            return 0
        input_regions = [normalize_region(region) for region in input_regions]
        bkwd_regions = [normalize_region(region) for region in bkwd_regions]
        if set(input_regions) & set(bkwd_regions):
            return 1

        for region1 in set(input_regions):
            for region2 in set(bkwd_regions):
                try:
                    has_path = nx.has_path(self.graph, region1,
                                           region2) or \
                               nx.has_path(self.graph, region2, region1)
                except nx.exception.NodeNotFound as e:
                    has_path = False
                    self.logger.error(f'{region1} or {region2} are not region')
                if has_path:
                    return 0.5
        return 0


    def compare_string(self, input_names, bkwd_names, ambiguous=0.):
        scores = []
        if len(bkwd_names) > len(input_names):
            input_names, bkwd_names = bkwd_names, input_names

        # two items compare one item case
        if len(input_names) == 2 and len(bkwd_names) == 1:
            scores.append(max(self.distance.compare(bkwd_names[0],
                                                    input_names[0]),
                              self.distance.compare(bkwd_names[0],
                                                    input_names[1])))
        else:
            for input_, bkwd_ in zip(input_names, bkwd_names):
                raw_score = self.distance.compare(input_, bkwd_)
                scores.append( raw_score )

        if not scores:
            return 0
        if len(scores) == 1:
            return self.conv_score(scores[0],ambiguous )
        if len(scores) == 2:
            return self.conv_score(scores[0] * 0.8 + scores[1] * 0.2, ambiguous)
        else:
            _ = sum(scores[2:]) / len( scores[2:] )
            return self.conv_score(scores[0] * 0.7 + _ * 0.3, ambiguous )

    def sum_score(self, region, name, industry, _type):
        region_score = 0.25
        name_score = 0.6
        industry_score = 0.1
        type_score = 0.05

        return region_score * region + name_score * name + \
               industry_score * industry + type_score * _type

    def conv_score(self, score, base=0.):
        if base < 0:
            return score
        if score >= base:
            return score if score != 1 else 1
        else:
            return 0


class QualityNameInquire(object):

    def __init__(self, search_engine, distance=JacardCaompare(), **kwargs):
        self.search_engine: BaseSearchEngine = search_engine
        resources = pathlib.Path(__file__).parents[1] / 'resources'
        jieba.analyse.set_stop_words(str(resources / 'stop_words'))
        self.distance = distance
        self.third_party_api_pool = ThirdPartyPool()

    @staticmethod
    def feature_extract(name) -> str:
        pre_input = preprocess_string(name)
        pre_string, cuts = cut_parentheses(pre_input)
        if not pre_string:
            return ''
        info = defaultdict(list)

        pairs = parser(pre_string)
        pairs = postprocess(pairs)
        for pair in pairs:
            info[pair.flag].append(pair.word)
        return "".join(info.pop('x', []))

    async def get_engine_result(self, name: str, phone: str) -> dict:
        """
        Find similarity name and phone in search engine.
        Extract name key and compare similarity using distance algorithm.

        :param name: quality company name
        :param phone: The china telephone number which is formatted.
            example: ( 0165288803 -> 010-65288803)
        :returns: result_dict include name, score, distance, sid, match_result
        """

        result = {'match_result': NameResultCode.MATCH,
                  'keyword_similarity': 0,
                  'score': 0,
                  'name':''}

        exist_info = await self.search_engine.is_phone_exist_info(phone)
        if not exist_info:
            result['match_result'] = NameResultCode.CANT_COMPARE
        else:
            search_result = await self.search_engine.search(name, phone)
            search_result = self.search_engine.parse(search_result)

            f1 = self.feature_extract(name) or name
            f2 = self.feature_extract(search_result.get('name')) or \
                search_result.get('name')

            distance = self.distance.compare(f1, f2)

            result = {'match_result': NameResultCode.MATCH,
                      'keyword_similarity': distance}

            if not search_result.get('name'):
                exist_info = self.search_engine.parse(exist_info)
                search_result['name'] = exist_info.get('name')
                search_result['sid'] = exist_info.get('sid')

            result.update(search_result)

            if distance < 0.4 or search_result['score'] < 5:
                result['match_result'] = NameResultCode.MISMATCH

        return result

    def register_third_party_api(self, third_party) -> None:
        self.third_party_api_pool.register_api(third_party)

    def remove_third_party_api(self, third_party) -> bool:
        return self.third_party_api_pool.remove_api(third_party)

    async def get_third_party_result(self, name) -> Tuple[str, str]:
        """
        executor all third party api to search match name,
        if find name immediate return response.

        :param name: company name
        :return: a match name from third party api
        """

        result = ''
        source = "No Register Api"
        for api in self.third_party_api_pool:
            try:
                r = await api.search(name)
                result = api.decode_name(r.json())
                source = api.name
                if result:
                    break
            except Exception as e:
                raise e

        return result, source

    async def random_third_party_api_result(self, name):
        """
        random to get a third party api then, executor api to search match name

        :param name: company name
        :return: a match name from third party api
        """
        result = ''
        if self.third_party_api_pool is False:
            return result, "No Register Api"

        api = self.third_party_api_pool.random_choice()
        try:
            r = await api.search(name)
            result = api.decode_name(r.json())
        except Exception as e:
            raise e

        return result, api.name