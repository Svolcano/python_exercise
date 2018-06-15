# -*- coding: utf-8 -*-

import datetime
try:
    from worker.crawler.china_mobile.SH.des_js import *
except:
    from des_js import *


def get_current_millisecond_timestamp():
    """
    Get current datetime in timestamp format(millisecond)
    :return:
    """
    current_timestamp = int((datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds() * 1000)
    return str(current_timestamp)


# Functions for Login
def get_rnd_param():
    """
    Assemble params for get_validate_image
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['act'] = "13"
    return param_dict


def get_rnd_form():
    """
    Assemble form for get_validate_image
    :return: form in dict
    """
    post_data_dict = dict()
    post_data_dict['source'] = 'wsyyt'
    return post_data_dict


def get_image_param(rnd):
    """
    Assemble params for get_validate_image
    :param rnd: rnd from LOGIN_EX_URL
    :return: Param in dict
    """
    param_dict = dict()
    param_dict['rnd_code'] = "1"
    param_dict['rnd'] = rnd
    return param_dict


def get_validate_result_param():
    """
    Assemble param for get_validate_result
    :return: Param in dict
    """
    param_dict = dict()
    param_dict['act'] = "12"

    return param_dict


def get_validate_result_form(tel_num, validate_code):
    """
    Assemble form for get_validate_result
    :param tel_num: Tel number
    :param validate_code: Validate code from capcha image
    :return: Param in dict
    """
    post_data_dict = dict()
    post_data_dict['source'] = 'wsyyt'
    post_data_dict['telno'] = tel_num
    post_data_dict['validcode'] = validate_code
    return post_data_dict


def get_login_result_param():
    """
    Assemble form for get_login_result
    :return: Param in dict
    """
    param_dict = dict()
    param_dict['act'] = "2"

    return param_dict


def get_login_result_form(tel_num, user_password, validate_code):
    """
    Assemble form for get_login_result
    :param tel_num: Tel number
    :param user_password: User's password
    :param validate_code: Validate code from capcha image
    :return: Form in dict
    """
    post_data_dict = dict()
    post_data_dict['source'] = 'wsyyt'
    post_data_dict['decode'] = '1'
    post_data_dict['ctype'] = '1'
    post_data_dict['authLevel'] = '2'
    post_data_dict['telno'] = des_encode(tel_num)
    post_data_dict['password'] = des_encode(user_password)
    post_data_dict['validcode'] = validate_code
    return post_data_dict


def get_forward_result_param(uid_value):
    """
    Assemble param for get_forward_result
    :param uid_value: UUID from get_login_result
    :return: Param in dict
    """
    param_dict = dict()
    param_dict['uid'] = uid_value
    param_dict['tourl'] = 'http%3A%2F%2Fwww.sh.10086.cn%2Fsh%2Fservice%2F'
    return param_dict


def get_second_validate_param(tel_num):
    """
    Assemble param for get_second_validate
    :param tel_num: Tel number
    :return: Param in dict
    """
    param_dict = dict()
    param_dict['act'] = '1'
    param_dict['source'] = 'wsyytpop'
    param_dict['telno'] = tel_num
    param_dict['password'] = ''
    param_dict['validcode'] = ''
    param_dict['authLevel'] = ''
    param_dict['decode'] = '1'
    param_dict['iscb'] = '1'
    return param_dict


def get_check_second_validate_form(tel_num, sms_validate_code):
    """
    Assemble form for get_check_second_validate
    :param tel_num: Tel number
    :param sms_validate_code: Validate code from SMS
    :return: Form in dict
    """
    post_data_dict = dict()
    post_data_dict['act'] = '2'
    post_data_dict['source'] = 'wsyytpop'
    post_data_dict['telno'] = des_encode(tel_num)
    post_data_dict['password'] = des_encode(sms_validate_code)
    post_data_dict['validcode'] = ''
    post_data_dict['authLevel'] = '1'
    post_data_dict['decode'] = '1'
    post_data_dict['iscb'] = '1'
    return post_data_dict


def get_login_post_result_form(uuid):
    """
    Assemble form for get_login_post_result
    :param uuid: UUID from get_login_result
    :return: Form in dict
    """
    post_data_dict = dict()
    post_data_dict['act'] = '2'
    post_data_dict['ret'] = '0'
    post_data_dict['message'] = ""
    post_data_dict['uid'] = uuid
    return post_data_dict


def get_current_month_detail_bill_form(start_date, end_date):
    """
    Assemble form for get_current_month_detail_bill
    :param start_date: Start date of detail bill
    :param end_date: End date of detail bill
    :return: Form in dict
    """
    post_data_dict = dict()
    post_data_dict['billType'] = 'NEW_GSM'
    post_data_dict['startDate'] = start_date
    post_data_dict['endDate'] = end_date
    post_data_dict['jingque'] = ''
    post_data_dict['searchStr'] = '-1'
    post_data_dict['index'] = '0'
    post_data_dict['isCardNo'] = '0'
    post_data_dict['gprsType'] = ''
    post_data_dict['r'] = get_current_millisecond_timestamp()
    return post_data_dict


def get_past_month_detail_bill_form(start_date, end_date):
    """
    Assemble form for get_past_month_detail_bill
    :param start_date: Start date of detail bill
    :param end_date: End date of detail bill
    :return: Form in dict
    """
    post_data_dict = dict()
    post_data_dict['billType'] = 'NEW_GSM'
    post_data_dict['startDate'] = start_date
    post_data_dict['endDate'] = end_date
    post_data_dict['filterfield'] = u'输入对方号码：'
    post_data_dict['filterValue'] = ''
    post_data_dict['searchStr'] = '-1'
    post_data_dict['index'] = '0'
    post_data_dict['isCardNo'] = '0'
    post_data_dict['gprsType'] = ''
    post_data_dict['r'] = get_current_millisecond_timestamp()
    return post_data_dict


if __name__ == "__main__":
    USER_ID = "15901735976"
    USER_PASSWORD = "191396"

    from pprintpp import pprint

    pprint(get_past_month_detail_bill_form("2016-11-01", "2016-11-30"))
