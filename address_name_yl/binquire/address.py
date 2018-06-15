#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import re
from enum import IntEnum
from typing import Optional, Tuple

from geopy.distance import great_circle
from shapely.geometry import Polygon, Point

from .utils.distance import levenshtein
from .utils.exceptions import MapApiException, ThirdPartyApiException
from .utils.address import ChinaAddress
from . import ThirdPartyPool
from .utils.log import getLogger
from .utils.map2 import AMapApi


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


def complete_endswith(full_str, lack_str):
    f_endswith = full_str[-1]
    l_endswith = lack_str[-1]
    if f_endswith in ['楼', '号', '室'] and re.match('[0-9]', l_endswith):
        lack_str = "".join([lack_str, f_endswith])
    return lack_str


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

    async def async_address_to_point(self, address: str) -> list:
        return await self.map_api.async_address_to_point(address)

    def isIntersects(self, points1, points2):
        pg1 = Polygon(points1)
        pg2 = Polygon(points2)
        return pg1.intersects(pg2)

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

    async def arun(self, name: str, phone: str, address: str):
        search_tasks = []
        sources = []
        if self.search_engine:
            search_tasks.append(self._get_es_address(name, phone))
            sources.append('dianhua')
        if self.map_api:
            city = ChinaAddress(address, False).city or ""
            search_tasks.append(self._get_amap_address(name, city))
            sources.append('amap')
        if self.third_party_api_pool:
            api = self.third_party_api_pool.random_choice()
            search_tasks.append(self._get_third_party_address(api, name))
            sources.append(api.name)

        addresses = await asyncio.gather(*search_tasks)
        max_source = max_addr = None
        max_similarity = 0
        for source, addr_result in zip(sources, addresses):
            for addr in addr_result:
                if addr:
                    similarity = 1 - levenshtein(address, addr)
                    if max_similarity < similarity:
                        max_similarity = similarity
                        max_source = source
                        max_addr = addr

        result = {'source': max_source,
                  'match_result': AddressResultCode.EMPTY_ADDRESS,
                  'detail_similarity': None,
                  'min_distance': None,
                  'max_distance': None,
                  'raw_address_similarity': max_similarity or None,
                  'address': max_addr}
        if max_addr:
            match_result, detail_similarity, min_d, max_d = \
                await self.async_get_result(address, max_addr)
            result['match_result'] = match_result
            result['detail_similarity'] = detail_similarity
            result['min_distance'] = min_d
            result['max_distance'] = max_d

        return result


    async def _get_es_address(self, name: str, phone: str):
        es_addresses = []
        r = await self.search_engine.search(name=name, phone=phone, size=5)
        for source in r:
            ele = source.get('_source', {})
            if ele.get('address'):
                es_addresses.append(ele.get('address').strip())
        return es_addresses

    async def _get_amap_address(self, name: str, city: str):
        try:
            resp = await self.map_api.get_address_by_name(name, city)
            return [self.map_api.process_get_address(resp.json())]
        except Exception as e:
            raise MapApiException()

    async def _get_third_party_address(self, api, name: str):
        try:
            result = await api.search(name)
            return [api.decode_address(result.json())]
        except Exception as e:
            raise ThirdPartyApiException(
                f'{api.name} Api Exception response:{r.text}', 300001)

    async def async_get_result(self,addr1: str, addr2: str, **kwargs):
        if not (addr1 and addr2): return AddressResultCode.EMPTY_ADDRESS, None, None, None
        addr2 = complete_endswith(addr1, addr2)
        addr1 = complete_endswith(addr2, addr1)
        a1 = ChinaAddress(addr1, False)
        a2 = ChinaAddress(addr2, False)

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

        return (match_result, string_similarity, *distances)

    async def async_get_address_geo(self, addr1: ChinaAddress, addr2: ChinaAddress, **kwargs):

        session = kwargs.get('session')
        city = addr2.city or addr1.city

        resp = await self.map_api.address_to_point(addr1.raw_address,
                                                      addr2.raw_address,
                                                      city=city,
                                                      session=session)

        p1, p2 = self.map_api.process_address_to_point(resp.json())

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
            resp = await self.map_api.address_to_polygon_points(
                addr1.raw_address, city=city, session=session) or [p1[:-1]]
            p1 = self.map_api.process_address_to_polygon_points(resp.json())
        else:
            p1 = [p1[:-1]]

        if not self.map_api.isPrecisionPoint(long_lat_level=p2):
            # p2 = tips2 or [p2[:-1]]
            resp = await self.map_api.address_to_polygon_points(
                addr2.raw_address, city=city, session=session) or [p2[:-1]]
            p2 = self.map_api.process_address_to_polygon_points(resp.json())
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

        AddressInquire.logger.debug(
            "geo: p1=" + str(p1) + ' && p2=' + str(p2) + "\t" +
            'distance: min=%.2f meter, max=%.2f meter' % (min_dist, max_dist))

        return min_dist, max_dist