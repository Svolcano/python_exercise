# -*- coding: utf-8 -*-

import random

before_login = {
    'token': '',
    'redirectUrl': '',
    'appKey': ''
}

# 登录前_图片验证码
def before_login_captcha_params():
    return {
        'token': before_login['token'],
        '_': random.random(),
    }

# 登录
def login_params(**kwargs):
    return {
        'token': before_login['token'],
        'redirectUrl': before_login['redirectUrl'],
        'appKey': before_login['appKey'],
        'action': 'passwd',
        'mp': kwargs['tel'],
        'loginPwd': kwargs['pin_pwd'],
        'captcha': kwargs['captcha_code'],
        'useActest':'N',

    }

# 查询通话详单前_获取短信验证码
def before_call_log_get_sms_params():
    return {
        'service': 'ajaxDirect/1/componant/componant/javascript/',
        'pagename': 'componant',
        'eventname': 'sendMessage',
        'GOODSNAME': u'详单',
        'DOWHAT': 'QUE',
        'ajaxSubmitType': 'get',
        'ajax_randomcode': random.random(),
    }

# 查询通话详单前_验证短信验证码
def before_call_log_verify_sms_params(smsCode):
    return {
        'service': 'ajaxDirect/1/componant/componant/javascript/',
        'pagename': 'componant',
        'eventname': 'validateSms',
        'smsCode': smsCode,
        'ajaxSubmitType': 'get',
        'ajax_randomcode': random.random(),
    }

# 查询通话详单
def call_log_params(echTokenInfo, searchMonth=''):
    return {
        'service': 'ajaxDirect/1/myMobile/myMobile/javascript/',
        'pagename': 'myMobile',
        'eventname': 'queryDetailRecords',
        'billType': '1001',
        'searchMonth':searchMonth,
        'billTypeCode': 'BAS4038',
        'callType': '',
        'commuType': '%',
        'longType': '',
        'echTokenInfo': echTokenInfo,
        'ajaxSubmitType': 'get',
        'ajax_randomcode': random.random(),
    }

# 查询账单
def phone_bill_params(searchMonth=''):
    return {
        'service': 'ajaxDirect/1/myMobile/myMobile/javascript/',
        'pagename': 'myMobile',
        'eventname': 'billInitPage',
        'MONTH':searchMonth,
        'ajaxSubmitType': 'get',
        'ajax_randomcode': random.random(),
    }

def personal_info_params():
    return {
        'service': 'ajaxDirect/1/myMobile/myMobile/javascript/',
        'pagename': 'myMobile',
        'eventname': 'basisDataInitPage',
        'undefined': '',
        'needLogin': '0',
        'ajaxSubmitType': 'get',
        'ajax_randomcode': random.random(),
    }
