#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import hashlib
import ujson as json
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import Optional
from urllib.parse import unquote, urlencode

from aioelasticsearch import Elasticsearch

from .exceptions import ThirdPartyApiException
from .log import getLogger
from .transport import Transport


class BaseSearchEngine(metaclass=ABCMeta):

    logger = getLogger("search")

    @abstractmethod
    async def is_phone_exist_info(self, phone: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def search(self,name: str, phone: str) -> dict:
        pass

    @abstractmethod
    def parse(self, obj: dict) -> dict:
        pass

class ESearch(BaseSearchEngine):
    def __init__(self, hosts, indices, doc_types,timeout=10):
        self._es = Elasticsearch(hosts=hosts, timeout=timeout)
        self._indices = ",".join(indices) if isinstance(indices,list) else indices
        self._doc_types = ",".join(doc_types) if isinstance(doc_types,list) else doc_types

    async def quit(self):
        await self._es.close()

    @asyncio.coroutine
    def __aenter__(self):
        return self

    @asyncio.coroutine
    def __aexit__(self, exc_type, exc_val, exc_tb):
        yield from self.quit()

    @staticmethod
    def phone_exist_name_body(phone):
        return {
            "query":{
                "term":{
                    "tels": phone
                }
            }
        }
        # return {
        #   "query": { "nested": { "path": "inputs",
        #       "query": {
        #         "terms": {
        #           "inputs.tel.number": [phone]}}}}}

    async def is_phone_exist_info(self, phone: str) -> Optional[dict]:
        body = ESearch.phone_exist_name_body(phone)
        r = await self._es.search(index=self._indices,
                                  doc_type=self._doc_types,
                                  body=body,
                                  size=2)

        if r['hits']['max_score']:
            return r['hits']['hits'][0]

        return None

    @staticmethod
    def search_body(name, phone):
        """
        create a query body
        """
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"name": name}}],
                    "filter": {
                        "nested": {
                            "path": "inputs",
                            "query": {
                                "term": {
                                    "inputs.tel.number": phone
                                }}}}}}}
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "name": name
                            }
                        }
                    ],
                    "filter": {
                        "term": {
                            "tels": phone
                        }
                    }
                }
            }
        }
        return body

    async def search(self, name: str, phone: str, size=1) -> dict:
        body = self.search_body(name, phone)

        r = await self._es.search(index=self._indices,
                                  doc_type=self._doc_types,
                                  size=size, body=body,
                                  preference='_primary_first')
        obj = r['hits']['hits']

        if obj:
            if size == 1:
                return obj[0]
            else:
                return obj
        return {}

    def parse(self, obj: dict) -> dict:
        """
        :return a dict key is ( sid, name, score )
        """
        doc = obj.get('_source', {})
        result = {
            'sid': obj.get('_id', ''),
            'name': doc.get('name', ''),
            'score': obj.get('_score', 0)
        }
        return result


class ESNoPhoneSearch(ESearch):

    @staticmethod
    def search_body(name, *args):
        body = {"query": {"term": {"name": name}}}
        return body

    @staticmethod
    def _parse(field, obj):
        if not isinstance(obj, list):
            obj = [obj]
        results = set()
        for ele in obj:
            source = ele.get('_source', {})
            if source.get(field):
                results.add(source.get(field))
        return list(results)

    def parse_name(self, obj):
        return self._parse('name', obj)

    def parse_address(self, obj):
        return self._parse('address', obj)


class BaseThirdPartyApiSearch(metaclass=ABCMeta):

    logger = getLogger("search")
    name = "BaseThirdpartyApi"

    def __init__(self, connector=None, limit=0):
        self.transport = Transport(connector, limit)

    @abstractmethod
    def search(self, name: str, **kwargs):
        pass

    @abstractmethod
    def decode_name(self, obj: dict):
        pass

    @abstractmethod
    def decode_address(self, obj:dict):
        pass

    def _fetch_json(self, method: str, url: str, **kwargs):
        try:
            return self.transport.send_request(method, url, **kwargs)
        except Exception as e:
            self.logger.exception(e)
            raise e

    # async def _fetch_json(self, method: str, url: str, **kwargs):
    #     session = kwargs.pop("session", None)
    #     if isinstance(session, aiohttp.ClientSession ):
    #         async with self.semaphore:
    #             retry = 2
    #             while retry > 0:
    #                 try:
    #                     async with async_timeout.timeout(60):
    #                         async with session.request(method=method,
    #                                                    url=url,
    #                                                    **kwargs) as r:
    #                             return await r.json(loads=json.loads)
    #                 except Exception as e:
    #                     self.logger.debug("ERROR TXT:\n" + await r.text())
    #                     retry -= 1
    #                     if retry <= 0:
    #                         self.logger.exception(url)
    #                         self.logger.exception(e)
    #                         raise e
    #     else:
    #         async with aiohttp.ClientSession() as session:
    #             return await self._fetch_json(method, url,
    #                                           session=session, **kwargs)


class TianYanChaApiSearch(BaseThirdPartyApiSearch):

    name = 'TianYanCha'

    def __init__(self, token, connector=None, limit=19):
        self.__token = token
        self.url = 'http://open.api.tianyancha.com/services/v4/open/baseinfo'
        self.headers = {'Authorization': token}
        super().__init__(connector, limit=limit)

    def search(self, name: str, **kwargs):
        try:
            r = self._fetch_json('GET', self.url,
                                 headers=self.headers,
                                 params={'name': name})
            return r
        except Exception:
            raise ThirdPartyApiException(f'{self.name} query error', 300001)

    @staticmethod
    def _check_result(obj:dict):
        if obj.get('error_code') not in [0, 300000]:
            name = TianYanChaApiSearch.name
            raise ThirdPartyApiException(f"{name} Api Exception",
                                         obj.get('error_code'))

    def decode_name(self, obj: dict):
        self._check_result(obj)

        return obj.get('result', {}).get('name', '')

    def decode_address(self, obj: dict):
        self._check_result(obj)

        return obj.get('result', {}).get('regLocation', '')


class YSCreditApiSearch(BaseThirdPartyApiSearch):
    name = "YSCredit"

    url = 'http://open.yscredit.com/api/request'

    def __init__(self, uid, api, key, connector=None, limit=19):
        self._uid = uid
        self._api = api
        self._key = key
        super().__init__(connector=connector, limit=limit)

    def gen_params(self, name: str) -> dict:
        params = OrderedDict([("uid", self._uid),
                              ('api', self._api),
                              ('args', json.dumps({'name': name},
                                                  ensure_ascii=False))])
        sign_params = params.copy()
        sign_params.update([('key', self._key)])
        sign = hashlib.md5(unquote(urlencode(sign_params)).encode()).hexdigest()
        params.update([('sign', sign)])
        return params

    def search(self, name: str, **kwargs) -> dict:
        try:
            r = self._fetch_json('GET', self.url,
                                 params=self.gen_params(name))
        except Exception as e:
            raise ThirdPartyApiException(f'{self.name} query error', 300001)
        return r

    @staticmethod
    def _check_result(obj: dict):
        if obj.get('code') not in ["0000", '0001']:
            name = YSCreditApiSearch.name
            msg = obj.get('msg','')
            raise ThirdPartyApiException(f"{name} Api Exception \nmsg:{msg}",
                                         obj.get('code'))

    @staticmethod
    def __get_basicList(obj: dict) -> list:
        data = obj.get('data') or {}
        return data.get('basicList') or [{}]

    def decode_address(self, obj:dict) -> str:
        self._check_result(obj)
        basic = self.__get_basicList(obj)
        return basic[0].get('address','')
        pass

    def decode_name(self, obj: dict) -> str:
        self._check_result(obj)
        basic = self.__get_basicList(obj)
        return basic[0].get('enterpriseName', '')


class YSCreditApiFuzzySearch(YSCreditApiSearch):
    def gen_params(self, name: str) -> dict:
        params = OrderedDict([("uid", self._uid),
                              ('api', self._api),
                              ('args', json.dumps({'key': name},
                                                  ensure_ascii=False))])
        sign_params = params.copy()
        sign_params.update([('key', self._key)])
        sign = hashlib.md5(unquote(urlencode(sign_params)).encode()).hexdigest()
        params.update([('sign', sign)])
        return params

    def decode_name(self, obj: dict):
        YSCreditApiSearch._check_result(obj)
        names = []
        for ent_name in obj.get('data') or []:
            name = ent_name.get('entName','')
            if name:
                names.append(name)
        return names


if __name__ == '__main__':
    async  def main():
        # api = TianYanChaApiSearch("STcAdHGTUMJx")
        # r = await api.search("北京百度网讯科技有限公司")
        # print(api.decode_name(r))
        es = ESearch(['172.18.19.71'],['yellowpage','lifestyle'],['shop']*2)
        r = await es.search('平顶山信阳甲鱼村', '0375-2889666')
        print(r)
        print(await es.parse(r))
        await es.quit()
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
