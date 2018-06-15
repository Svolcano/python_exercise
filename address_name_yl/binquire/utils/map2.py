#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABCMeta
from typing import Optional

from area import area
from shapely.geometry import Polygon, mapping

from .exceptions import MapApiException
from .log import getLogger
from .transport import Transport, Response

try:
    import ujson as json
except ImportError:
    import json


class MapApiWrapper(object, metaclass=ABCMeta):
    """ map api wrapper support async and sync
    convention::
        when you call transport you need to return it, because transport can
        return coroutine or response object
    """
    logger = getLogger("MapApi")

    def __init__(self, api_key, connector=None, concurrency_limit=200):
        """
        :param connector: AIOHttpConnector or RequestsHttpConnector
        """
        self.api_key = api_key
        self.transport = Transport(connector, concurrency_limit)

    def address_to_point(self, address: str):
        raise NotImplementedError

    def address_to_polygon_points(self, address: str):
        raise NotImplementedError

    def geom_area(self, points):
        try:
            geom = mapping( Polygon(points))
            geom['coordinates'] = list(map(list, geom['coordinates']))
            return area(geom)
        except Exception as e:
            return 0


class AMapApi(MapApiWrapper):
    geo_url = 'http://restapi.amap.com/v3/geocode/geo?'
    tips_url = 'http://restapi.amap.com/v3/assistant/inputtips?'
    batch = 'http://restapi.amap.com/v3/batch?key={}'
    search_url = 'http://restapi.amap.com/v3/place/text?'

    def __init__(self, api_key, concurrency_limit=200, **kwargs):
        super().__init__(api_key, concurrency_limit=concurrency_limit, **kwargs)
        self.batch = self.batch.format(api_key)

    def __gen_geo_payload(self, address: str, *args, **kwargs) -> dict:
        for addr in args:
            address += '|' + addr
        return {'address': address, 'key': self.api_key,
                'batch': 'true', 'city': kwargs.get('city', '')}

    def process_address_to_point(self, result: dict) -> list:
        """

        :param result: amap response json object
        :return list: [ [ long, lat, level], [ long, lat, level], ... ]
        """
        if result.get('infocode',"20003") != '10000':
            raise MapApiException("AMapApi", errors=result.get('infocode', "20003"))
        return [list(map(float, item['location'].split(','))) + [item['level']]
                if item['location'] else [] for item in result.get('geocodes', {})]

    def address_to_point(self, address: str, *args, **kwargs) -> Response:
        payload = self.__gen_geo_payload(address, *args, **kwargs)
        return self.transport.get(self.geo_url, params=payload)

    def __gen_tips_payload(self, address: str, **kwargs) -> dict:
        return {'keywords': address, 'key': self.api_key,
                'datatype': 'all', 'city': kwargs.get('city','')}

    def process_address_to_polygon_points(self, result: dict) -> list:
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

    def address_to_polygon_points(self, address: str, **kwargs) -> Response:
        payload = self.__gen_tips_payload(address, **kwargs)
        return self.transport.get( url=self.tips_url, params=payload)

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


    def __gen_get_address_by_name_payload(self, name: str, city:str="") -> dict:
        params = {'key': self.api_key,
                  'keywords': name,
                  'city': city,
                  'children': '1',
                  'offset': '2',
                  'page': '1',
                  'extensions': 'all'}
        return params

    def process_get_address(self, result: dict) -> Optional[str]:
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

    def get_address_by_name(self, name: str, city: str = '', ) -> Response:
        payload = self.__gen_get_address_by_name_payload(name, city)
        return self.transport.get(url=self.search_url, params=payload,)

