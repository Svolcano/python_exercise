#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import pathlib

import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint

from binquire.address import AddressInquire
from binquire.name import QualityNameInquire, FuzzyNameInquire
from binquire.utils.cache import LRUCache
from binquire.utils.search import ESearch, TianYanChaApiSearch, \
    YSCreditApiSearch, ESNoPhoneSearch, YSCreditApiFuzzySearch
from blueprints.address import bp as address
from blueprints.name import bp as bp_name
from blueprints.fuzzyname import bp as fz_name
from settings import *

app = Sanic(__name__)
app.blueprint(address)
app.blueprint(bp_name)
app.blueprint(fz_name)


def check_resource():
    # check dotenv file
    env_file = pathlib.Path(__file__).parent / '.env'

    if not env_file.is_file():
        raise Exception("dot env file Not Exist")

    resource = pathlib.Path(__file__).parent / 'resources'

    if len(list(resource.iterdir())) <= 3:
        raise Exception("Resources are not Exist")

    # checking settings
    import settings
    print("Loading Setting....")
    for key in dir(settings):
        if not key.startswith('__'):
            print(key+':', getattr(settings,key))


@app.listener('before_server_start')
async def before_server_start(app, loop):
    app.es = ESearch(ES_HOSTS, INDICES, DOC_TYPES)
    app.es_no_phone = ESNoPhoneSearch(ES_HOSTS, 'qichacha', DOC_TYPES)
    app.tianyancha_api = TianYanChaApiSearch(TIANYANCHA_KEY)
    app.yscredit_api = YSCreditApiSearch(YSCREDIT_UID, YSCREDIT_API, YS_CREDIT_KEY)
    app.ys_fz_api = YSCreditApiFuzzySearch(YSCREDIT_UID, '100003', YS_CREDIT_KEY)

    app.name_inquire = QualityNameInquire(app.es, app.es_no_phone)
    app.addr_inquire = AddressInquire(AMAP_KEY, app.es)

    app.fuzzyname = FuzzyNameInquire()

    # register api
    for api in [app.tianyancha_api, app.yscredit_api]:
        app.name_inquire.register_third_party_api(api)
        app.addr_inquire.register_third_party_api(api)

    app.fuzzyname.api_pool.register_api(app.ys_fz_api)

    # connect redis
    try:
        app.lru_cache = \
            await aioredis.create_redis_pool((REDIS_URL, REDIS_PORT),
                                             db=REDIS_DB)
        app.lru_cache.client_getname()
        await app.lru_cache.config_set('maxmemory', '1G')
        await app.lru_cache.config_set('maxmemory-policy', 'allkeys-lru')
    except Exception as e:
        print(e)
        app.lru_cache = LRUCache(size=10000)

    # connect mongodb
    client = AsyncIOMotorClient(MONGO_URL)
    app.mongo_db = client[MONGO_DB]




@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    await app.es.quit()
    await app.es_no_phone.quit()
    await asyncio.sleep(0)

    # close async redis connect
    if not isinstance(app.lru_cache, LRUCache):
        app.lru_cache.close()
        await app.lru_cache.wait_closed()



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--works', required=False, default=1, type=int)
    parser.add_argument('-b', '--bind', required=False, default='0.0.0.0')
    parser.add_argument('-p', '--port', required=False, default=8000, type=int)
    parser.add_argument('--log', dest='log', action="store_true")
    parser.add_argument('--no-log', dest='log', action="store_false")
    parser.set_defaults(log=True)
    parser.add_argument('--swagger', dest='swagger', action="store_true")
    parser.add_argument('--no-swagger', dest='swagger', action="store_false")
    parser.set_defaults(swagger=True)

    args = parser.parse_args()

    app.config.API_VERSION = "2.0.0"
    app.config.API_TITLE = 'BQC API'
    app.config.API_DESCRIPTION = 'core api, qualityName and address '
    app.config.API_CONTACT_EMAIL = 'minglun.cai@yulore.com'
    app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']

    if args.swagger:
        app.blueprint(openapi_blueprint)
        app.blueprint(swagger_blueprint)

    check_resource()

    app.run(host=args.bind,
            port=args.port,
            workers=args.works,
            access_log=args.log)