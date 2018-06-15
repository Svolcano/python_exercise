# -*- coding: utf-8 -*-
import random
import datetime
try:
    from worker.crawler.china_mobile.CQ.des_js import *
except:
    from des_js import *


# General Functions
def mix_current_time():
    """
    Current datetime for various of requests
    :return: Mixed datetime
    """
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    mix_time = "{}{}{}".format(current_time, str(random.random())[1:],random.randint(999,9999))
    return mix_time


# Functions for Login
def get_check_cq_local_param(tel):
    """
    Assemble params for is_cq_local_number
    :param tel: Tel number
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/login/login/javascript/"
    param_dict['pagename'] = "login"
    param_dict['eventname'] = "checkIsLocalNumberNow"
    param_dict['cond_TELNUM'] = tel
    param_dict['ajaxSubmitType'] = "get"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


def get_sso_login_param(user_id, user_password, picture_validate_code, sms_code):
    """
    Assemble params for Request SSO Login
    :param user_id: Tel number
    :param user_password: Password
    :param picture_validate_code: code in Capcha image
    :return: Params in dict
    """
    param_dict = {
        'service': "ajaxDirect/1/login/login/javascript/",
        'pagename': "login",
        'eventname': "interfaceLogin",
        'cond_REMEMBER_TAG': "false",
        'cond_LOGIN_TYPE': "0",
        'cond_SERIAL_NUMBER': user_id,
        'cond_USER_PASSWD': "",
        'cond_USER_PASSSMS': sms_code,
        'cond_VALIDATE_CODE': picture_validate_code,
        'ajaxSubmitType': "post",
        'ajax_randomcode': mix_current_time()
    }
    return param_dict


def get_start_event_param():
    """
    Assemble params for Request Start Event
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/smartmaket/smartmaket/javascript/"
    param_dict['pagename'] = "smartmaket"
    param_dict['eventname'] = "IntellectualMarket_pop_window"
    param_dict['state'] = "start"
    param_dict['ID'] = "operation.success.wttccs1"
    param_dict['ajaxSubmitType'] = "get"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


def get_login_info_form(user_id, user_password, picture_validate_code):
    """
    Assemble form for Request Login Box
    :return: form in dict
    """
    param_dict = dict()
    param_dict['service'] = "CHOQ"
    param_dict['failUrl'] = "http://service.cq.10086.cn/CHOQ/authentication/authentication_error.jsp"
    param_dict['username'] = user_id
    param_dict['password'] = user_password
    param_dict['passwordType'] = "2"
    param_dict['validateCode'] = picture_validate_code
    param_dict['smsRandomCode'] = user_password
    return param_dict


def get_success_return_info_form(sam_lart_code):
    """
    Assemble form for Request Auth Return
    :return: form in dict
    """
    post_data_dict = dict()
    post_data_dict['RelayState'] = ""
    post_data_dict['SAMLart'] = sam_lart_code
    post_data_dict['PasswordType'] = "2"
    post_data_dict['errorMsg'] = ""
    return post_data_dict


def get_success_return_param():
    """
    Assemble params for Request Auth Return
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['timeStamp'] = int((datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds())
    return param_dict


def get_success_login_info_form(user_id, flag, error_code, uuid):
    """
    Assemble form for Request Return Success
    :param user_id: Tel number
    :param flag: Success/Fail from response of Request Auth Return
    :param error_code: error info from response of Request Auth Return
    :param uuid: uid from response of Request Auth Return
    :return: form in dict
    """
    post_data_dict = dict()
    post_data_dict['SERIAL_NUMBER'] = user_id
    post_data_dict['flag'] = flag
    post_data_dict['errorInfo'] = error_code
    post_data_dict['UID'] = uuid
    return post_data_dict


# Functions for Personal Info
def get_good_id_param(good_ename):
    """
    Assemble params for Get Good IDs
    :param good_ename: The target good's ename
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/home/home/javascript/"
    param_dict['pagename'] = "home"
    param_dict['eventname'] = "initGoodsId"
    param_dict['cond_GOODS_ENAME'] = good_ename
    param_dict['ajaxSubmitType'] = "post"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


def get_ip_to_cookie_param():
    """
    Assemble params for Push Local IP to Cookie
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/home/home/javascript/"
    param_dict['pagename'] = "home"
    param_dict['eventname'] = "getIpToCookie"
    param_dict['ajaxSubmitType'] = "get"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


def get_personal_info_param(event_name, good_ename, good_id, good_name):
    """
    Assemble params for Get Personal Info
    :param event_name: The target event
    :param good_ename: The target good's ename
    :param good_id: The target good's id
    :param good_name: The target good's name
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/myMobile/myMobile/javascript/"
    param_dict['pagename'] = "myMobile"
    param_dict['eventname'] = event_name
    param_dict['cond_GOODS_ENAME'] = good_ename
    param_dict['cond_GOODS_NAME'] = good_name
    param_dict['cond_TRANS_TYPE'] = "Q"
    param_dict['cond_GOODS_ID'] = good_id
    param_dict['ajaxSubmitType'] = "get"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


# Functions for Detail Info
def get_second_validation_param():
    """
    Assemble params for Trigger Second Validation
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/secondValidate/secondValidate/javascript/"
    param_dict['pagename'] = "secondValidate"
    param_dict['eventname'] = "getTwoVerification"
    param_dict['GOODSNAME'] = "用户详单"
    param_dict['DOWHAT'] = "QUE"
    param_dict['ajaxSubmitType'] = "post"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


def get_check_sms_info_param(sms_validate_code):
    """
    Assemble params for Check SMS Validate Code
    :param sms_validate_code: SMS validate code received from cell phone
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/secondValidate/secondValidate/javascript/"
    param_dict['pagename'] = "secondValidate"
    param_dict['eventname'] = "checkSMSINFO"
    param_dict['cond_USER_PASSSMS'] = sms_validate_code
    param_dict['cond_CHECK_TYPE'] = "DETAIL_BILL"
    param_dict['cond_loginType'] = "2"
    param_dict['ajaxSubmitType'] = "post"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


def get_check_cqip_param():
    """
    Assemble params for Check CQIP
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/myMobile/myMobile/javascript/"
    param_dict['pagename'] = "myMobile"
    param_dict['eventname'] = "checkCQIP"
    param_dict['ajaxSubmitType'] = "get"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


def get_detail_bill_param(year_month, good_id):
    """
    Assemble params for Get Detail Info
    :param year_month: The year-month of detail bill info
    :param good_id: The good's id of detail bill
    :return: Params in dict
    """
    param_dict = dict()
    param_dict['service'] = "ajaxDirect/1/myMobile/myMobile/javascript/"
    param_dict['pagename'] = "myMobile"
    param_dict['eventname'] = "getDetailBill"
    param_dict['cond_DETAIL_TYPE'] = "3"
    param_dict['cond_QUERY_TYPE'] = "0"
    param_dict['cond_QUERY_MONTH'] = year_month
    param_dict['cond_GOODS_ENAME'] = "XFMX"
    param_dict['cond_GOODS_NAME'] = "消费明细"
    param_dict['cond_TRANS_TYPE'] = "Q"
    param_dict['cond_GOODS_ID'] = good_id
    param_dict['ajaxSubmitType'] = "post"
    param_dict['ajax_randomcode'] = mix_current_time()
    return param_dict


if __name__ == "__main__":
    pass
