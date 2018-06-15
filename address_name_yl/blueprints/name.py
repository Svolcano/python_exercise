#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from sanic.response import json, redirect
from sanic import Blueprint
from sanic_openapi import doc

from binquire.name import NameResultCode, feature_extract
from binquire.utils.exceptions import ThirdPartyApiException
from binquire.utils.cache import a_third_party_cache
from . import return_error, status_codes

bp = Blueprint('Name', '/qualityname')


def get_params(request):
    try:
        name = request.args.get('name', '').strip()
        tel = re.sub('\D+', '', request.args.get('tel', '').strip())
        debug = int(request.args.get('debug', '0'))
        third_party_api = int(request.args.get('third_party', '1'))
        if not name or not tel:
            raise Exception("Params Error")
    except Exception as e:
        raise e
    return name, tel, third_party_api, debug


@bp.get('/')
@doc.summary("Quality Name Query")
@doc.consumes(doc.String("商户名称", name='name'), location="query", required=True)
@doc.consumes(doc.String("使用第三方API(0不使用,1使用,预设1)",
                         name='third_party_api', choices=['0', '1']),
              location="query", required=False)
@doc.consumes(doc.String("格式化之电话号码", name='tel'), location="query",
              required=True)
@doc.route(produces={"match_result": int, "keyword_similarity": float,
                     'sid': str, 'name': str, 'score': float, 'source': str,
                     'status_code': int, 'msg': str})
async def default_name(request):
    # url = request.app.url_for('Name.name_v1', **request.args)
    # return redirect(url)
    return await name_v2(request)


@bp.get('/', version='v1')
@doc.summary("Quality Name Query Version 1")
@doc.consumes(doc.String("商户名称", name='name'), location="query", required=True)
@doc.consumes(doc.String("使用第三方API(0不使用,1使用,预设1)",
                         name='third_party_api', choices=['0', '1']),
              location="query", required=False)
@doc.consumes(doc.String("格式化之电话号码", name='tel'), location="query",
              required=True)
@doc.route(produces={"match_result": int, "keyword_similarity": float,
                     'sid': str, 'name': str, 'score': float, 'source': str,
                     'status_code': int, 'msg': str})
async def name_v1(request):
    try:
        name, tel, third_party, debug = get_params(request)
    except:
        return return_error(status_codes[1003], 1003)
    name_inq = request.app.name_inquire

    try:
        # Get engine result, if no result search third party
        # result = await name_inq.arun(name, tel, bool(third_party_api))
        result = await name_inq.get_engine_result(name, tel)
        match_result = result.get('match_result')
        result['source'] = 'dianhua'
        if third_party and match_result == NameResultCode.CANT_COMPARE:
            t_name, source = await name_inq.random_third_party_result(name)
            result['source'] = source
            result['score'] = 0
            if t_name:
                result['match_result'] = NameResultCode.IGNORE

                result['keyword_similarity'] = \
                    name_inq.distance.compare(t_name, name)
                result['name'] = t_name
        if debug:
            debug_info = {'match_result': result['match_result'],
                          'name1': feature_extract(name),
                          'name2': feature_extract(result.get('name'))}
            result['debug'] = debug_info

        if result['match_result'] != NameResultCode.CANT_COMPARE:
            result['match_result'] = NameResultCode.IGNORE

        result['status_code'] = 0
        result['msg'] = status_codes[result['status_code']]
        result = json(result)

    except ThirdPartyApiException as e:
        result = return_error(str(e), e.error_code)
    except Exception as e:
        status_code = 1999
        msg = status_codes[status_code] + f'\nname:{name},tel:{tel}'
        result = return_error(msg, status_code, True)

    return result


@bp.get('/', version='v2')
@doc.summary("Quality Name Query Version 2 support cache and save data to mongo")
@doc.consumes(doc.String("商户名称", name='name'), location="query", required=True)
@doc.consumes(doc.String("使用第三方API(0不使用,1使用,预设1)",
                         name='third_party_api', choices=['0', '1']),
              location="query", required=False)
@doc.consumes(doc.String("格式化之电话号码", name='tel'), location="query",
              required=True)
@doc.route(produces={"match_result": int, "keyword_similarity": float,
                     'sid': str, 'name': str, 'score': float, 'source': str,
                     'status_code': int, 'msg': str})
async def name_v2(request):
    try:
        name, tel, third_party, debug = get_params(request)
    except:
        return return_error(status_codes[1003], 1003)

    name_inq = request.app.name_inquire
    cache = request.app.lru_cache
    db = request.app.mongo_db
    try:
        # Get engine result, if no result search third party
        # result = await name_inq.arun(name, tel, bool(third_party_api))
        result = await name_inq.get_engine_result(name, tel)
        match_result = result.get('match_result')
        # result['source'] = 'dianhua'
        if third_party and match_result == NameResultCode.CANT_COMPARE:
            t_name = ""
            source = "No_Register_Api"
            if name_inq.third_party_api_pool:
                api = name_inq.third_party_api_pool.random_choice()
                cache = await a_third_party_cache(cache, db, api, name)
                t_name = cache['resp_name']
                source = cache['api_name']

            result['source'] = source
            result['score'] = 0
            if t_name:
                result['match_result'] = NameResultCode.IGNORE

                result['keyword_similarity'] = \
                    name_inq.distance.compare(t_name, name)
                result['name'] = t_name

        if debug:
            debug_info = {'match_result': result['match_result'].name,
                          'name1': feature_extract(name),
                          'name2': feature_extract(result.get('name'))}
            result['debug'] = debug_info

        if result['match_result'] != NameResultCode.CANT_COMPARE:
            result['match_result'] = NameResultCode.IGNORE

        result['status_code'] = 0
        result['msg'] = status_codes[result['status_code']]
        result = json(result)

    except ThirdPartyApiException as e:
        result = return_error(str(e), e.error_code)
    except Exception as e:
        status_code = 1999
        msg = status_codes[status_code] + f'\nname:{name},tel:{tel}'
        result = return_error(msg, status_code, True)

    return result
