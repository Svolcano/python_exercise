# -*- coding: utf-8 -*-

import random

try:
    from worker.crawler.china_mobile.SD.base_security_js import *
except:
    from base_security_js import *


# Functions for Login
def get_login_cookie_param(field_id):
    """
    Assemble params for get_login_cookie
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['FieldID'] = str(field_id)
    param_dict['random'] = str(random.randrange(1000, 9999)) + '.' + str(random.randrange(100000000000, 999999999999))
    return param_dict


def get_main_logon_do_form():
    """
    Assemble form for get_main_logon_do
    :return: form in dict
    """
    post_data_dict = dict()
    post_data_dict['continueUrl'] = 'http://www.sd.10086.cn/eMobile/jsp/common/prior.jsp?menuid=index'
    return post_data_dict


def get_login_image_param():
    """
    Assemble params for get_login_image
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['random'] = str(random.random() * 100000) + str(random.randrange(1000, 9999))
    return param_dict


def get_login_result_form(tel_num, user_password, validate_code):
    """
    Assemble form for get_login_result
    :return: form in dict
    """
    post_data_dict = dict()
    post_data_dict['mobileNum'] = des_encode(tel_num)
    post_data_dict['servicePWD'] = des_encode(user_password)
    post_data_dict['randCode'] = validate_code
    post_data_dict['smsRandomCode'] = ''
    post_data_dict['submitMode'] = '2'
    post_data_dict['logonMode'] = '1'
    post_data_dict['FieldID'] = '1'
    post_data_dict['ReturnURL'] = 'www.sd.10086.cn/eMobile/jsp/common/prior.jsp'
    post_data_dict['ErrorUrl'] = '../mainLogon.do'
    post_data_dict['entrance'] = 'IndexBrief'
    post_data_dict['codeFlag'] = '0'
    post_data_dict['openFlag'] = '1'
    return post_data_dict


def get_sso_login_param(attribute_id):
    """
    Assemble params for get_sso_login
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['Attritd'] = attribute_id
    return param_dict


def get_second_validate_image_param():
    """
    Assemble params for get_second_validate_image
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['pageId'] = str(random.random() * 0.1) + str(random.randrange(1000, 9999))
    return param_dict


def send_second_validate_sms_param():
    """
    Assemble params for get_second_validate_sms
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['menuid'] = 'billdetails'
    param_dict['pageid'] = str(random.random()) + str(random.randrange(1000, 9999))
    return param_dict


def get_second_validate_result_param(validate_code, sms_code):
    """
    Assemble params for get_second_validate_result
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['menuid'] = 'customerinfo'
    param_dict['fieldErrFlag'] = ""
    param_dict['contextPath'] = "/eMobile"
    param_dict['randomSms'] = sms_code
    param_dict['confirmCode'] = validate_code
    return param_dict


def get_personal_info_param():
    """
    Assemble params for get_personal_info
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['menuid'] = 'customerinfo'
    param_dict['pageid'] = str(random.random())
    return param_dict


def get_balance_left_form(tel_num):
    """
    Assemble form for basic info
    :return: form in dict
    """
    post_data_dict = dict()
    post_data_dict['servNumber'] = tel_num
    return post_data_dict


def get_detail_bill_param(start_date, end_date):
    """
    Assemble params for get_detail_bill
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['dateType'] = 'byTime'
    param_dict['menuid'] = 'billdetails'
    param_dict['startDate'] = start_date
    param_dict['EndDate'] = end_date
    param_dict['month'] = ""
    param_dict['cycle'] = "undefined"
    param_dict['queryType'] = '2'
    param_dict['pageid'] = str(random.random())
    return param_dict


if __name__ == '__main__':
    print(send_second_validate_sms_param())
    print(get_second_validate_result_param("1111", "222222"))
