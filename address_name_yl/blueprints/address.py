#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import re

from sanic.response import json, redirect
from sanic import Blueprint
from sanic_openapi import doc

from binquire.address import AddressResultCode
from binquire.utils.address import ChinaAddress
from binquire.utils.distance import levenshtein
from binquire.utils.cache import a_third_party_cache
from binquire.utils.exceptions import ThirdPartyApiException
from . import return_error, status_codes

bp = Blueprint('Address', '/address')


def get_params(request):
    try:
        name = request.args.get('name', '').strip()
        address = request.args.get('address', '').strip()
        tel = re.sub('\D+', '', request.args.get('tel', '').strip())
        debug = int(request.args.get('debug', '0'))
        if not name or not tel or not address:
            raise Exception("Params Error")
    except Exception as e:
        raise e
    return name, address, tel, debug


@bp.get('/')
@doc.summary("Address Query")
@doc.consumes(doc.String("商户地址", name='address'), location="query",
              required=True)
@doc.consumes(doc.String("商户名称", name='name'), location="query", required=True)
@doc.consumes(doc.String("商户电话", name='tel'), location="query", required=True)
@doc.consumes(doc.String("debug", name='debug', choices=['0', '1']),
              location="query", required=False)
async def default_address(request):
    # url = request.app.url_for('Address.address_v1',**request.args)
    # return redirect(url)
    return await address_v2(request)


@bp.get('/',version='v1')
@doc.summary("Address Query Version 1")
@doc.consumes(doc.String("商户地址", name='address'), location="query",
              required=True)
@doc.consumes(doc.String("商户名称", name='name'), location="query", required=True)
@doc.consumes(doc.String("商户电话", name='tel'), location="query", required=True)
@doc.consumes(doc.String("debug", name='debug', choices=['0', '1']),
              location="query", required=False)
async def address_v1(request):
    try:
        name, address, tel, debug = get_params(request)
    except:
        return return_error(status_codes[1003], 1003)
    addr_inq = request.app.addr_inquire

    try:
        # result = await addr_inq.arun(name, tel, address)
        search_tasks = []
        sources = []
        if addr_inq.search_engine:
            search_tasks.append(addr_inq._get_es_address(name, tel))
            sources.append('dianhua')
        if addr_inq.map_api:
            city = ChinaAddress(address, False).city or ""
            search_tasks.append(addr_inq._get_amap_address(name, city))
            sources.append('amap')
        if addr_inq.third_party_api_pool:
            api = addr_inq.third_party_api_pool.random_choice()
            search_tasks.append(addr_inq._get_third_party_address(api, name))
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
                await addr_inq.async_get_result(address, max_addr)
            result['match_result'] = match_result
            result['detail_similarity'] = detail_similarity
            result['min_distance'] = min_d
            result['max_distance'] = max_d

        if debug:
            result['match_result'] = result['match_result'].name

        status_code = 0
        result = json(dict(msg=status_codes[status_code],
                           status_code=status_code,
                           count=1,
                           results=[result]))
    except ThirdPartyApiException as e:
        result = return_error(str(e), e.error_code)
    except Exception as e:
        msg = status_codes[1999] + f'\nname:{name},tel:{tel}'
        result = return_error(msg, 1999, True)

    return result


@bp.get('/', version='v2')
@doc.summary("Address Query Version 2 support cache and save data to mongo")
@doc.consumes(doc.String("商户地址", name='address'), location="query",
              required=True)
@doc.consumes(doc.String("商户名称", name='name'), location="query", required=True)
@doc.consumes(doc.String("商户电话", name='tel'), location="query", required=True)
@doc.consumes(doc.String("debug", name='debug', choices=['0', '1']),
              location="query", required=False)
async def address_v2(request):
    try:
        name, address, tel, debug = get_params(request)
    except:
        return return_error(status_codes[1003], 1003)

    addr_inq = request.app.addr_inquire
    cache = request.app.lru_cache
    db = request.app.mongo_db
    try:
        # result = await addr_inq.arun(name, tel, address)
        search_tasks = []
        sources = []
        if addr_inq.search_engine:
            search_tasks.append(addr_inq._get_es_address(name, tel))
            sources.append('dianhua')
        if addr_inq.map_api:
            city = ChinaAddress(address, False).city or ""
            search_tasks.append(addr_inq._get_amap_address(name, city))
            sources.append('amap')

        addresses = await asyncio.gather(*search_tasks)

        if addr_inq.third_party_api_pool:
            api = addr_inq.third_party_api_pool.random_choice()
            cache = await a_third_party_cache(cache, db, api, name)
            addresses.append([cache['resp_address']])
            sources.append(cache['api_name'])

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
                await addr_inq.async_get_result(address, max_addr)
            result['match_result'] = match_result
            result['detail_similarity'] = detail_similarity
            result['min_distance'] = min_d
            result['max_distance'] = max_d

        if debug:
            result['match_result'] = result['match_result'].name

        status_code = 0
        result = json(dict(msg=status_codes[status_code],
                           status_code=status_code,
                           count=1,
                           results=[result]))
    except ThirdPartyApiException as e:
        result = return_error(str(e), e.error_code)
    except Exception as e:
        msg = status_codes[1999] + f'\nname:{name},tel:{tel}'
        result = return_error(msg, 1999, True)

    return result