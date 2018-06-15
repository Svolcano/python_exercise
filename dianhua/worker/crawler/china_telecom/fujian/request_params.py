#!/user/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2017/8/14 11:37
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
    month = "%d%02d" % (query_date.year, query_date.month)
    e_day = str(calendar.monthrange(query_date.year, query_date.month)[1])
    return {
        'SDAY': '1',
        'v_choosetype': '0',
        'EDAY': e_day,
        'MONTH': month,
        'PRODTYPE': 50,
        'PRODNO': base64.b64encode(str(kwargs['tel'])),
        'PAGENO': '1',
        'INTERPAGE': '9999',

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
        "ProvinceID": '14',
        "AreaCode": "",
        "CityNo": "",
        "RandomFlag": '0',
        "Password": aes_encrypt(kwargs['pin_pwd']),
        "Captcha": kwargs['captcha_code'],
    }


def month_bill_data(month, **kwargs):
    return {
            'PRODNO': kwargs['tel'],
            'citycode': '591',
            'ck_month': month,
            'PRODTYPE': '50',
        }







