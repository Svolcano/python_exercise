#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from enum import IntEnum
from itertools import chain
from typing import Tuple

from .utils.parser import parser_wrapper
from .utils.exceptions import ThirdPartyApiException
from . import ThirdPartyPool
from .utils import JacardCaompare
from .utils import preprocess_string, cut_parentheses, postprocess, parser
from .utils.search import BaseSearchEngine


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


class NameResultCode(IntEnum):
    CANT_COMPARE = -1   # dianhua no result so can not compare
    MISMATCH = 0    # compare result is not match
    MATCH = 1   # compare result is exact match
    AMBIGUOUS_MATCH = 2     # compare result is ambiguous match
    TEST = 9999     # for testing code
    IGNORE = 99999  # no suggest match result


class QualityNameInquire(object):

    def __init__(self, search_engine, no_phone_engine,
                 distance=JacardCaompare(), **kwargs):
        self.search_engine: BaseSearchEngine = search_engine

        # resources = pathlib.Path(__file__).parents[1] / 'resources'
        # jieba.analyse.set_stop_words(str(resources / 'stop_words'))

        self.distance = distance
        self.third_party_api_pool = ThirdPartyPool()
        self.no_phone_engine = no_phone_engine

    async def a_no_phone_search(self, name, result={}):
        r = await self.no_phone_engine.search(name, None)
        name = self.no_phone_engine.parse_name(r)
        if name:
            result['keyword_similarity'] = 1
            result['name'] = name[0]
            result['source'] = 'dianhua_no_phone'
            result['match_result'] = NameResultCode.MATCH
        return result

    async def get_engine_result(self, name: str, phone: str) -> dict:
        """
        Find similarity name and phone in search engine.
        Extract name key and compare similarity using distance algorithm.

        :param name: quality company name
        :param phone: The china telephone number which is formatted.
            example: ( 0165288803 -> 010-65288803)
        :returns: result_dict include name, score, distance, sid, match_result
            If phone not in search_engine match_result is CANT_COMPARE
        """

        result = {'match_result': NameResultCode.MATCH,
                  'keyword_similarity': 0,
                  'score': 0,
                  'name':'',
                  'source': 'dianhua'}

        exist_info = await self.search_engine.is_phone_exist_info(phone)
        if not exist_info:
            result['match_result'] = NameResultCode.CANT_COMPARE
            result = await self.a_no_phone_search(name, result)
        else:
            search_result = await self.search_engine.search(name, phone)
            search_result = self.search_engine.parse(search_result)

            f1 = feature_extract(name) or name
            f2 = feature_extract(search_result.get('name')) or \
                search_result.get('name')

            distance = self.distance.compare(f1, f2)

            result.update({'keyword_similarity': distance})

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

    async def random_third_party_result(self, name):
        """
        random to get a third party api then, executor api to search match name

        :param name: company name
        :returns: (result, api_name) result is api_response_match_name
        """
        result = ''
        if self.third_party_api_pool is False:
            return result, "No Register Api"

        api = self.third_party_api_pool.random_choice()
        try:
            r = await api.search(name)
            result = api.decode_name(r.json())
        except Exception as e:
            raise ThirdPartyApiException(
                f'{api.name} Api Exception response:{r.text}', 300001)

        return result, api.name

    async def arun(self, name: str, phone: str, third_party=True):
        """
        Get engine result, if no result search third party
        """
        result = await self.get_engine_result(name, phone)
        match_result = result.get('match_result')
        result['source'] = 'dianhua'
        if third_party and match_result == NameResultCode.CANT_COMPARE:
            try:
                t_name, source = await self.random_third_party_result(name)
                result['source'] = source
                result['score'] = 0
                if t_name:
                    result['match_result'] = NameResultCode.IGNORE
                    result['keyword_similarity'] = self.distance.compare(t_name,
                                                                         name)
                    result['name'] = t_name

            except ThirdPartyApiException as e:
                raise e

        return result


class FuzzyNameInquire(object):

    def __init__(self):
        self.api_pool = ThirdPartyPool()
        self.distance = JacardCaompare()

    async def async_search_all(self,name, *args, **kwargs):
        results = []
        for api in self.api_pool:
            resp = await api.search(name=name)
            rslt = api.decode_name(resp.json())
            if rslt:
                results.append(rslt[0])
        return results

    @staticmethod
    def check_region(name, region):
        pairs, parentheses = parser_wrapper(name)

        for pair in pairs:
            if pair.flag == 'region':
                return region in pair.word

        # compare parenthteses
        return region in map(lambda _pair: _pair.word,
                             filter(lambda _pair: _pair.flag == 'region',
                                chain.from_iterable(map(parser, parentheses))))

    def get_key_word_similarity(self, n1, n2):
        f1 = feature_extract(n1) or n1
        f2 = feature_extract(n2) or n2
        return self.distance.compare(f1, f2)
