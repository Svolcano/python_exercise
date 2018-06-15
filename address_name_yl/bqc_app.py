#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import re

import aiohttp
from sanic import Sanic
from sanic.response import json
from sanic_openapi import doc
from sanic_openapi import swagger_blueprint, openapi_blueprint

import constants
from binquire.binquire import NameInquire, AddressInquire, QualityNameInquire, \
    NameResultCode
from binquire.settings import amap_key, es_hosts, doc_types, indices, \
    yscredit_api, yscredit_key, yscredit_uid, tianyancha_key
from binquire.utils.exceptions import ThirdPartyApiException
from binquire.utils.search import ESearch, YSCreditApiSearch, \
    TianYanChaApiSearch

app = Sanic()

inquire = NameInquire()
inquire2 = NameInquire(name_rate=-1, industry_rate=-1, type_rate=-1)

logger = logging.getLogger('sanic.error')


def check_args(f):
    def wrapper(request):
        if 'input' not in request.args:
            return json({'msg': constants.status_codes[1002],
                         'status_code': 1001}, 404)
        elif request.args.get('debug'):
            try:
                int(request.args.get('debug'))
            except Exception as e:
                return json({'msg': constants.status_codes[1002],
                             'status_code': 1002}, 404)

        return f(request)

    return wrapper


def complete_endswith(full_str, lack_str):
    f_endswith = full_str[-1]
    l_endswith = lack_str[-1]
    if f_endswith in ['楼', '号', '室'] and re.match('[0-9]', l_endswith):
        lack_str = "".join([lack_str, f_endswith])
    return lack_str


@app.get('/name')
@doc.summary("version 1 Name Query")
@doc.consumes(doc.String("商户名称", name='input'), location="query", required=True)
@doc.consumes(doc.String("反查名称", name='bkwd'), location="query", required=True)
@doc.consumes(doc.String("debug", name='debug', choices=['0', '1']),
              location="query", required=False)
@check_args
async def bqc_name_compare(request):
    input_ = request.args.get('input', '')
    bkwd_ = request.args.get('bkwd', '')
    debug = int(request.args.get('debug', '0'))

    result = {}
    if debug:
        i_info, _ = inquire.get_info(input_)
        b_info, _ = inquire.get_info(bkwd_)
        raw_scores = inquire2.get_result(input_, bkwd_)
        result['input_parser'] = i_info
        result['bkwd_parser'] = b_info
        result['score_region'] = raw_scores[0]
        result['score_name'] = raw_scores[1]
        result['score_industry'] = raw_scores[2]
        result['score_type'] = raw_scores[3]

    scores = inquire.get_result(input_, bkwd_)
    total = inquire.sum_score(*scores)
    result['similarity_score'] = total
    return json(result)


@app.route('/address')
@doc.summary("Address Query")
@doc.consumes(doc.String("商户地址", name='address'), location="query",
              required=True)
@doc.consumes(doc.String("商户名称", name='name'), location="query", required=True)
@doc.consumes(doc.String("商户电话", name='tel'), location="query", required=True)
@doc.consumes(doc.String("debug", name='debug', choices=['0', '1']),
              location="query", required=False)
async def bqc_address_compare(request):
    try:
        name = request.args.get('name', '').strip()
        address = request.args.get('address', '').strip()
        tel = re.sub('\D+', '', request.args.get('tel', '').strip())
        debug = int(request.args.get('debug', '0'))
        if not name or not tel or not address:
            raise Exception()
    except Exception as e:
        return return_error(constants.status_codes[1003], 1003)
    try:
        r = await app.addr_inquire.async_get_all_result(name=name,
                                                        phone=tel,
                                                        address=address)
    except Exception as e:
        msg = constants.status_codes[1999] + f'\nname:{name},tel:{tel}'
        return return_error(msg, 1999, True)
    if debug:
        for obj in r:
            obj['match_result'] = obj['match_result'].name
    return json(dict(msg=constants.status_codes[0],
                     status_code=0,
                     count=len(r),
                     results=r))


def return_error(msg, status_code, exec_info=False):
    result = {'msg': msg, 'status_code': status_code}
    if exec_info:
        import traceback
        traceback.print_exc()
        result['debug'] = {'traceback': traceback.format_exc()}
    return json(result, 404)


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
@app.get('/qualityname')
async def quality_name(request):
    try:
        name = request.args.get('name', '').strip()
        tel = re.sub('\D+', '', request.args.get('tel', '').strip())
        debug = int(request.args.get('debug', '0'))
        thrid_party = int(request.args.get('third_party_api', '1'))
        if not name or not tel:
            raise Exception()
    except Exception as e:
        return return_error(constants.status_codes[1003], 1003)
    try:
        inq: QualityNameInquire = app.qname_inquire
        result = await inq.get_engine_result(name, tel)

        result['source'] = 'dianhua'
        result['status_code'] = 0
        result['msg'] = constants.status_codes[0]

        # debug mode
        if debug:
            debug_info = {'match_result': result['match_result'],
                          'name1': inq.feature_extract(name),
                          'name2': inq.feature_extract(result.get('name'))}
            result['debug'] = debug_info

        # ignore default compare result
        if result['match_result'] != NameResultCode.CANT_COMPARE:
            result['match_result'] = NameResultCode.IGNORE

        # if ES no doc, call third party api to find match company name
        if thrid_party and (
                result.get('match_result') == NameResultCode.CANT_COMPARE):
            try:
                t_name, source = await inq.random_third_party_api_result(name)
                result['source'] = source
                result['score'] = 0

                if t_name:
                    result['match_result'] = NameResultCode.IGNORE
                    result['keyword_similarity'] = inq.distance.compare(t_name,
                                                                        name)
                    result['name'] = t_name

            except ThirdPartyApiException as e:
                return return_error(str(e), e.error_code)

    except Exception as e:
        msg = constants.status_codes[1999] + f'\nname:{name},tel:{tel}'
        return return_error(msg, 1999, True)
    else:
        return json(result)


@app.listener('before_server_start')
async def before_server_start(app, loop):
    # https://stackoverflow.com/questions/46991562/how-to-reuse-aiohttp-clientsession-pool
    app.client_session = await aiohttp.ClientSession().__aenter__()
    app.es = ESearch(es_hosts, indices, doc_types)
    app.tianyancha_api = TianYanChaApiSearch(tianyancha_key)
    app.yscredit_api = YSCreditApiSearch(yscredit_uid, yscredit_api, yscredit_key)

    app.qname_inquire = QualityNameInquire(app.es)
    app.addr_inquire = AddressInquire(amap_key, app.es)

    # register api
    for api in [app.tianyancha_api, app.yscredit_api]:
        app.qname_inquire.register_third_party_api(api)
        app.addr_inquire.register_third_party_api(api)


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    await app.client_session.__aexit__(None, None, None)
    await app.es.quit()
    # http://aiohttp.readthedocs.io/en/stable/client.html#graceful-shutdown
    await asyncio.sleep(0)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--works', required=False, default=1, type=int)
    parser.add_argument('-b', '--bind', required=False, default='0.0.0.0')
    parser.add_argument('-p', '--port', required=False, default=8000, type=int)
    parser.add_argument('--log', dest='log', action="store_true")
    parser.add_argument('--no-log', dest='log', action="store_false")
    parser.set_defaults(log=True)
    parser.add_argument('-s', '--swagger', required=False, default=True,
                        type=bool)
    args = parser.parse_args()

    # app.run(host='0.0.0.0',port=8000, access_log=True)
    app.config.API_VERSION = "2.0.0"
    app.config.API_TITLE = 'BQC API'
    app.config.API_DESCRIPTION = 'core api, name, qualityName and address '
    app.config.API_CONTACT_EMAIL = 'minglun.cai@yulore.com'
    app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']

    if args.swagger:
        app.blueprint(openapi_blueprint)
        app.blueprint(swagger_blueprint)

    # # only testing
    # from xxx import blueprint as xxx
    # app.blueprint(xxx)
    print(args.log)
    app.run(host=args.bind,
            port=args.port,
            workers=args.works,
            access_log=args.log)
