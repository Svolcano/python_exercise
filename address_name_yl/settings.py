#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


DB_SHEET_ID = '1IFniVM6cJ5Cax-MT3RgnUB2ahCO5kmc4PmVdNixNaMQ'
AMAP_KEY = os.getenv('amap_key', 'b80b220833baffde5e102c50b932541b')

ES_HOSTS = os.getenv('es_hosts')
if ES_HOSTS is None:
    ES_HOSTS = ['172.18.52.17' + str(idx) for idx in range(1, 5)]
else:
    ES_HOSTS = ES_HOSTS.split(';')

INDICES = os.getenv('indices', ['lifestyle', 'yellowpage', 'bkwd'])
if isinstance(INDICES, str):
    INDICES = INDICES.split(';')
DOC_TYPES = os.getenv('doc_types', 'shop')

TIANYANCHA_KEY = os.getenv('tianyancha_key', 'STcAdHGTUMJx')

YSCREDIT_UID = os.getenv('yscredit_uid', 'yulore')
YSCREDIT_API = os.getenv('yscredit_api', '100101')
YS_CREDIT_KEY = os.getenv('yscredit_key', '602fee764765fab77db4220b6c5566dd')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

REDIS_URL = os.getenv('redis_url')
REDIS_PORT = os.getenv('redis_port')
REDIS_DB = int(os.getenv('redis_db',0))
REDIS_EXPIRE = int(os.getenv('redis_expire', 86400))

MONGO_URL = os.getenv('mongo_url')
MONGO_DB = os.getenv('mongo_db')

del os, load_dotenv
