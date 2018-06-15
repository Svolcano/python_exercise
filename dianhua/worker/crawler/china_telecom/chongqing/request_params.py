#!/user/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2017/5/25 16:37
# @Author  : zhangjun
# Title    :

import hashlib
import base64
import calendar

from Crypto.Cipher import AES
from datetime import date
from dateutil.relativedelta import relativedelta


def call_log_data(each_month, **kwargs):
    today = date.today()
    query_date = today + relativedelta(months=each_month)
    query_month = "%d-%02d" % (query_date.year, query_date.month)
    BEGIN_DATE = "%d-%02d-" % (query_date.year, query_date.month) + '01'
    END_DATE = "%d-%02d-" % (query_date.year, query_date.month) + \
               str(calendar.monthrange(query_date.year, query_date.month)[1])
    return{
        "accNbr": kwargs['tel'],
        "productId": "208511296",
        "month": query_month,
        "callType": "00",  # 主叫和被叫
        "listType": "300001",
        "beginTime": BEGIN_DATE,
        "endTime": END_DATE,
        "rc": "",
        "tname": kwargs['full_name'].decode('utf-8')[1:],
        "idcard": kwargs['id_card'][-6:],
        "zq": "2",
    }


def aes_encrypt(n):
    # this is the porting from telecom javascript
    pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
    n = pad(n)
    e = hashlib.md5('login.189.cn')
    t = e.hexdigest()
    i = t.encode('utf-8')
    r = u'1234567812345678'.encode('utf-8')
    encryption_suite = AES.new(i, AES.MODE_CBC, r)
    cipher_text = encryption_suite.encrypt(n)
    base64.b64encode(cipher_text)
    return base64.b64encode(cipher_text)


def login_data(**kwargs):
    return {
        "Account": kwargs['tel'],
        "UType": '201',
        "ProvinceID": '04',
        "AreaCode": "",
        "CityNo": "",
        "RandomFlag": '0',
        "Password": aes_encrypt(kwargs['pin_pwd']),
        "Captcha": kwargs['captcha_code']
    }


def err_times_data(**kwargs):
    return {
        "m": "loadlogincaptcha",
        "Account": kwargs['tel'],
        "UType": '201',
        "ProvinceID": '04',
        "AreaCode": "",
        "CityNo": "",
    }


def month_bill_data(month, **kwargs):
    return {
            'accNbr': kwargs['tel'],
            'productId': '208511296',
            'month': month,
            'queryType': '2',
        }











