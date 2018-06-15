# -*- coding: utf-8 -*-

import random
import time

def login_params(spid,**kwargs):
    login_form = {'type': 'A',
                  'backurl': 'https://gx.ac.10086.cn/4logingx/backPage.jsp',
                  'errorurl': 'https://gx.ac.10086.cn/4logingx/errorPage.jsp',
                  'RelayState': 'type=A;backurl=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp;nl=3;loginFrom=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp',
                  'isValidateCode': 0,
                  'smsValidCode': kwargs['sms_code'],
                  'validCode': '',
                  'servicePassword': '',
                  'mobileNum': kwargs['tel'],
                  'spid': spid,
                  }
    return login_form


def after_login_params(after_login):
    form_data = {'myaction': 'http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp',
                 'netaction': 'http://www.gx.10086.cn/padhallclient/netclient/customer/businessDealing',
                 'SAMLart':after_login,
                 'RelayState':'type=A;backurl=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp;nl=3;loginFrom=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp',
                 }


    return form_data


def before_send_sms_init_params(dateTimeToken):
    _tmpDate = int(time.time() * 1000)
    params = {'is_first_render': 'true', 'lastCombineChild': 'false',
                     '_zoneId': 'busimain', '_menuId': '410900003558',
                     '_tmpDate': str(_tmpDate),
                     '_dateTimeToken': dateTimeToken, '_buttonId': ''}
    return params


def before_call_log_get_sms_params(dateTimeToken):
    _tmpDate = int(time.time() * 1000)
    secondSMSform = {'ajaxType': 'json', '_menuId': '410900003558',
                     '_tmpDate': str(_tmpDate),
                     '_dateTimeToken': dateTimeToken, '_buttonId': ''}
    return secondSMSform


def before_call_log_verify_sms_params(smsCode,dateTimeToken,service_password):
    _tmpDate = int(time.time() * 1000)
    check_sms_form = {
        'input_random_code': smsCode,
        'input_svr_pass': service_password,
        'queryRegOkVal': '',
        'is_first_render': 'true',
        '_zoneId': '_sign_errzone',
        '_menuId': '410900003558',
        '_tmpDate': str(_tmpDate),
        '_dateTimeToken': dateTimeToken,
        '_buttonId': 'other_sign_btn'
    }
    return check_sms_form

def call_log_params(dateTimeToken):
    _tmpDate = int(time.time() * 1000)
    detail_query_params = {
        'is_first_render': 'true',
        'queryDetailTypeList': '1',
        'queryType': '1',
        'detailType': '1',
        'oldPhoneId': '',
        'oldRegId': '',
        'svnsn': '',
        'bankflag': '',
        'iPara': '',
        'queryTypeList': '1',
        '_zoneId': 'queryResult',
        '_menuId': '410900003558',
        '_tmpDate': str(_tmpDate),
        '_dateTimeToken': dateTimeToken,
        'start_time': '',
        'end_time': '',
        'iPage': '',
        'queryMonth': '',
        'queryMonthList': '',
        '_buttonId': 'step-1-btn'}
    return detail_query_params

def phone_bill_querybusi_params(dateTimeToken):
    _tmpDate = int(time.time() * 1000)
    detail_query_params = {
        'begin':'2017-08',
        'queryDetail': 'no',
        'is_first_render': 'true',
        'isMyMob': 'true',
        'query_type_value': '0',
        'month_type_value': '',
        'month_selected_type': '',
        'query_type_selected': '0',
        '_zoneId': 'month-bill-list-container',
        '_menuId': '410900003557',
        '_tmpDate': str(_tmpDate),
        '_dateTimeToken': dateTimeToken,
        '_buttonId': 'queryBtn'}
    return  detail_query_params

def destory_destroyBusi_params(dateTimeToken):
    _tmpDate = int(time.time() * 1000)
    params = {'ajaxType': 'json',
              '_menuId': '410900003558',
              '_tmpDate': str(_tmpDate),
            '_dateTimeToken': dateTimeToken, '_buttonId': ''}
    return params

def init_phone_bill2_params(dateTimeToken):
    _tmpDate = int(time.time() * 1000)
    params = {'is_first_render': 'true',
              'lastCombineChild': 'false',
              '_zoneId': 'busimain',
              '_menuId': '410900003557',
              '_tmpDate': str(_tmpDate),
              '_dateTimeToken': dateTimeToken,
              '_buttonId': ''}
    return params

def phone_bill_curtnessnew_params(dateTimeToken):
    _tmpDate = int(time.time() * 1000)
    params = {'is_first_render': 'true',
              '_zoneId': 'feeinfonew',
              '_menuId': '410900003557',
              '_tmpDate': str(_tmpDate),
              '_dateTimeToken': dateTimeToken,
              '_buttonId': ''}
    return params
