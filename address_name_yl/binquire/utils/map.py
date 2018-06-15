#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from typing import Optional
from urllib.parse import urlparse, urlencode

import aiohttp
import uvloop

from shapely.geometry import Polygon, mapping
from area import area

from .exceptions import MapApiException
from .log import getLogger

"""
Deprecated Pleas using map2
"""

try:
    import ujson as json
except ImportError:
    import json

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class MapApiWrapper(object):

    logger = getLogger("MapApi")

    def __init__(self, api_key, concurrency_limit = 200):
        self.api_key = api_key
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    def address_to_point(self, address: str):
        raise NotImplementedError

    async def async_address_to_point(self, address: str):
        raise NotImplementedError

    def address_to_polygon_points(self, address: str):
        raise NotImplementedError

    async def async_address_to_polygon_points(self, address: str):
        raise NotImplementedError

    def _requests(self, method: str, url: str, **kwargs):
        import requests
        with requests.Session() as session:
            return session.request(method=method, url=url, **kwargs)

    async def _async_requests(self, method: str, url: str, **kwargs):
        session = kwargs.pop("session", None)
        if isinstance(session, aiohttp.ClientSession ):
            async with self.semaphore:
                # print(self.semaphore._value)
                retry = 2
                while retry > 0:
                    try:
                        async with session.request(method=method, url=url, **kwargs) as r:
                            return await r.json(loads=json.loads)
                    except Exception as e:
                        self.logger.exception(url)
                        self.logger.exception(e)
                        retry -= 1
                        if retry <= 0:
                            raise e
        else:
            async with aiohttp.ClientSession() as session:
                return await self._async_requests(method, url, session=session, **kwargs)

    def geom_area(self, points):
        try:
            geom = mapping( Polygon(points))
            geom['coordinates'] = list(map(list, geom['coordinates']))
            return area(geom)
        except Exception as e:
            return 0

    def _wrapper_run_async(self, coroutine, loop=None):
        loop = loop or asyncio.get_event_loop()
        task = asyncio.ensure_future(coroutine)
        rslt = loop.run_until_complete(task)
        return rslt

class AMapApi(MapApiWrapper):
    geo_url = 'http://restapi.amap.com/v3/geocode/geo?'
    tips_url = 'http://restapi.amap.com/v3/assistant/inputtips?'
    batch = 'http://restapi.amap.com/v3/batch?key={}'
    search_url = 'http://restapi.amap.com/v3/place/text?'

    def __init__(self, api_key, concurrency_limit=200):
        super().__init__(api_key, concurrency_limit)
        self.batch = self.batch.format(api_key)

    def __gen_geo_payload(self, address: str, *args, **kwargs) -> dict:
        for addr in args:
            address += '|' + addr
        return {'address': address, 'key': self.api_key,
                'batch': 'true', 'city': kwargs.get('city', '')}

    def __handle_address_to_point(self, result: dict) -> list:
        """

        :param result: amap response json object
        :return list: [ [ long, lat, level], [ long, lat, level], ... ]
        """
        if result.get('infocode',"20003") != '10000':
            raise MapApiException("AMapApi", errors=result.get('infocode', "20003"))
        return [list(map(float, item['location'].split(','))) + [item['level']]
                if item['location'] else [] for item in result.get('geocodes', {})]

    def address_to_point(self, address: str, *args, **kwargs) -> list:
        # payload = self.__gen_geo_payload(address, *args, **kwargs)
        # result = self._requests('GET',url=self.geo_url,params=payload)
        # return self.__handle_address_to_point(result.json())
        rslt = self._wrapper_run_async(self.async_address_to_point(address,
                                                                   *args,
                                                                   **kwargs))
        return rslt

    async def async_address_to_point(self, address: str, *args, **kwargs) -> list:
        payload = self.__gen_geo_payload(address, *args, **kwargs)
        session = kwargs.get('session',None)
        result = self._async_requests('GET', url=self.geo_url, params=payload,
                                      session=session)
        return self.__handle_address_to_point(await result)

    def __gen_tips_payload(self, address: str, **kwargs) -> dict:
        return {'keywords': address, 'key': self.api_key,
                'datatype': 'all', 'city': kwargs.get('city','')}

    def __handle_address_to_polygon_points(self, result: dict) -> list:
        if result.get('infocode',"20003") != '10000':
            raise MapApiException("AMapApi",errors=result.get('infocode', "20003"))
        poi_long_lati = [tuple(map(float, item.get('location', '').split(',')))
                         for item in result.get('tips', {}) if isinstance(item.get('location'), str)]
        if len(poi_long_lati) < 2:
            return []

        min_x = max_x = poi_long_lati[0][0]
        min_y = max_y = poi_long_lati[0][1]

        for cur_x, cur_y in poi_long_lati:
            min_x = min(min_x, cur_x)
            min_y = min(min_y, cur_y)
            max_x = max(max_x, cur_x)
            max_y = max(max_y, cur_y)

        return [[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]]
        pass

    def address_to_polygon_points(self, address: str, **kwargs) -> list:
        return \
            self._wrapper_run_async(
                self.async_address_to_polygon_points(address, **kwargs))
        # payload = self.__gen_tips_payload(address,city)
        # result = self._requests("GET",url=self.tips_url,params=payload)
        # if result.status_code != 200:
        #     return []
        # return self.__handle_address_to_polygon_points(result.json())

    async def async_address_to_polygon_points(self, address: str, **kwargs) -> list:
        payload = self.__gen_tips_payload(address, **kwargs)
        session = kwargs.get('session', None)
        result = self._async_requests('GET', url=self.tips_url, params=payload, session=session)
        return self.__handle_address_to_polygon_points(await result)

    def isPrecisionPoint(self, address: str = '', long_lat_level: list = []):
        p_level = ['门牌号', '公交站台', '地铁站',
                   '道路交叉路口', '兴趣点','道路', '单元号']
        if address:
            payload = self.__gen_geo_payload(address)
            r = self._requests('GET', self.geo_url, params=payload)
            return r.json()['geocodes'][0]['level'] in p_level
        elif long_lat_level:
            level = long_lat_level[-1]
            return level in p_level

    def isAmbigiousPoint(self, address: str = '', long_lat_level: list = []):
        big_level = ['国家', '省', '市', '区县']
        if address:
            payload = self.__gen_geo_payload(address)
            r = self._requests('GET', self.geo_url, params=payload)
            return r.json()['geocodes'][0]['level'] in big_level
        elif long_lat_level:
            level = long_lat_level[-1]
            return level in big_level
        return True

    async def async_batch_query(self, addr1:str, addr2:str, **kwargs):
        payload = {'ops': []}
        session = kwargs.get('session',None)

        geo_payload = self.__gen_geo_payload(addr1, addr2, **kwargs)
        geo_part_url = \
            "".join([urlparse(self.geo_url).path, "?", urlencode(geo_payload)])
        payload['ops'].append({'url': geo_part_url })
        for addr in [addr1, addr2]:
            tips_payload = self.__gen_tips_payload(addr, **kwargs)
            tips_part_url = \
                "".join([urlparse(self.tips_url).path, "?", urlencode(tips_payload)])
            payload['ops'].append({'url': tips_part_url})

        result = await self._async_requests("POST",
                                            url=self.batch,
                                            json=payload,
                                            session=session)

        geos = self.__handle_address_to_point(result[0].get('body',{}))

        tips1 = self.__handle_address_to_polygon_points(result[1].get('body',{}))
        tips2 = self.__handle_address_to_polygon_points(result[2].get('body', {}))

        return geos, tips1, tips2

    def __gen_get_address_by_name_payload(self, name: str, city:str="") -> dict:
        params = {'key': self.api_key,
                  'keywords': name,
                  'city': city,
                  'children': '1',
                  'offset': '2',
                  'page': '1',
                  'extensions': 'all'}
        return params

    def __handle_get_address(self, result: dict) -> Optional[str]:
        count = int(result.get('count','0'))
        if count == 1:
            detail = result.get('pois',[])[0]
            province = detail.get('pname','')
            city = detail.get('cityname','')
            city = city if province != city != '' else ''
            district = detail.get('adname','')
            address = detail.get('address','')
            if address:
                return "".join([province,city,district,address.strip()])
        else:
            return None

    async def async_get_address_by_name(self, name: str, city: str = '', **kwargs) -> Optional[str]:
        session = kwargs.get('session', None)
        payload = self.__gen_get_address_by_name_payload(name,city)
        result = await self._async_requests("GET",
                                            url=self.search_url,
                                            params=payload,
                                            session=session)
        return self.__handle_get_address(result)

    def get_address_by_name(self, name: str, **kwargs) -> Optional[str]:
        return self._wrapper_run_async(
            self.async_get_address_by_name(name,**kwargs))
