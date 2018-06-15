# -*- coding: utf-8 -*-

import base64
import requests
import random
import json
import urllib
import lxml.html
from lxml import etree
import traceback
import re
try:
    from worker.crawler.china_mobile.CQ.base_request_param import *
except:
    from base_request_param import *

# const url
ICS_SERVICE_URL = "http://service.cq.10086.cn/ics"
GET_IMAGE_URL = "https://service.cq.10086.cn/servlet/ImageServlet?random=" + str(random.random())
REFRESH_IMAGE_URL = "https://cq.ac.10086.cn/SSO/img?random={}?width=51&height=22".format(str(random.random()))

# const personal info

PERSONAL_INFO_GOOD_NAME_DICT = {"GRXX": "个人信息", "WDZF": "我的资费", "XJFW": "星级服务"}

# const detail bill info
DETAIL_BILL_GOOD_NAME_DICT = {"XFMX": "消费明细"}


# Functions for Login
def get_validate_image(request_session):
    """
    Get validate image
    :param request_session: Requests session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        image_str: str, Raw byte of Captcha in base64 format, return "" if fail
    """
    headers = {
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://service.cq.10086.cn/httpsFiles/pageLogin.html"
    }
    code, key, resp = request_session.get(GET_IMAGE_URL, headers=headers)
    if code != 0:
        return code, key, ""
    # print '\n\n', 'response.content:', response.content, '\n\n' 
    return 0, 'success', resp


def refresh_validate_image(request_session):
    """
    该函数已废弃
    Get another validate image
    :param request_session: Requests session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        image_str: str, Raw byte of Captcha in base64 format, return "" if fail
    """
    code, key, resp = request_session.get(REFRESH_IMAGE_URL)
    if code != 0:
        return code, key, ""
    return 0, 'success', base64.b64encode(resp.content)
    

def is_cq_local_number(tel, requests):
    """
    Verify if the target tel number is a cq local number
    :param tel: Tel number
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Referer": "http://service.cq.10086.cn/httpsFiles/pageLogin.html"
    }
    code, key, resp = requests.get(url=ICS_SERVICE_URL, params=get_check_cq_local_param(str(tel)), headers=headers)
    if code != 0:
        return code, key, ""
    try:
        root = etree.fromstring(resp.text.encode('utf-8'))
        return_dataset = root.xpath('//*[@id="dataset"]')
        if len(return_dataset) == 0:
            return 9, 'request_error', "No dataset error"
        else:
            return 0, 'success', json.loads(return_dataset[0].text)[0]['FLAG']
    except:
        error = traceback.format_exc()
        return 9, "xml_error", error


def is_validate(user_id, user_password, picture_validate_code, requests):
    """
    Check if the target tel, password, code are valid
    :param user_id: Tel number
    :param user_password: Password
    :param picture_validate_code: code in Capcha image
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    if len(picture_validate_code) < 4:
        return 2, 'verify_error', "您输入的校验码不足4位，请重新填写。".decode('UTF-8')
    elif len(user_password) < 6:
        return 1, 'pin_pwd_error', "您输入的密码不足6位，请重新填写。".decode('UTF-8')
    elif len(user_id) < 11:
        return 1, 'invalid_tel', "您输入的的手机号码不足11位，请重新填写。".decode('UTF-8')

    level, key, message = is_cq_local_number(user_id, requests)
    if level != 0:
        return level, key, message
    elif message == "false":
        return 1, 'invalid_tel', "Not a valid cq tel number".decode('UTF-8')
    elif message == 'true':
        return 0, 'success', 'True'
    else:
        return 9, 'unknown_error', u"unknown return format"

def get_redirect_url_from_text(response_text):
    """
    Get redirect url from target response text
    :param response_text: Response text returned from Request Login
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        url: str, The redirect url
    """
    try:
        if '"RESULT":"0"' in response_text:
            return 'success', 0, 'Get redirect url', re.search('"url":"(.+?)"',response_text).group(0)
        else:
            return 'login_error', 9, "No redirect url error", ""
    except Exception as e:
        return 'unknown_error', 9, u"get redirect_url failed: %s" % e, ""

def get_sam_lart_from_xhtml(xhtml_string):
    """
    Get SAMLart from target xhtml string
    :param xhtml_string: Response returned from Request Login Box
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        samlart: str, The SAMLart id
    """
    try:
        root = lxml.html.document_fromstring(xhtml_string)
        error_info_value = root.xpath('//*[@name="errInfo"]/@value')
        if len(error_info_value) > 0:
            return 'verify_error', 1, urllib.unquote(error_info_value[0]).decode('gbk'), ''

        sam_lart_value = root.xpath('//*[@name="SAMLart"]/@value')
        if len(sam_lart_value) > 0:
            return 'success', 0, 'Get SAMLart', sam_lart_value[0]
        else:
            return 'html_error', 9, "No SAM LArt error", ""
    except Exception as e:
        return 'unknown_error', 9, u"get_sam_lart_from_xhtml failed: %s" % e, ""


# def get_uid_from_xhtml(xhtml_string):
#     """
#     Get UUID from target xhtml string
#     :param xhtml_string: Response returned from Request Auth Return
#     :return:
#         status_key: str, The key of status code
#         level: int, Error level
#         message: unicode, Error Message
#         uid_data: dict, The flag, uid, and error_info
#     """
#     try:
#         root = lxml.html.document_fromstring(xhtml_string)
#         flag_value = root.xpath('//*[@name="flag"]/@value')[0]
#         uid_value = root.xpath('//*[@name="UID"]/@value')[0]
#         error_info_value = root.xpath('//*[@name="errorInfo"]/@value')[0]
#         return 'success', 0, "Get uid", {"flag": flag_value, "uid": uid_value, "error_info": error_info_value}
#     except Exception as e:
#         return 'unknown_error', 9, u"get_uid_from_xhtml failed: %s" % e, ""


def get_good_id_from_xml(xml_string):
    """
    Get good id from target xml string
    :param xml_string: Response returned from Get Good IDs
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        good_id: str, The good id
    """
    try:
        root = etree.fromstring(xml_string.encode('utf-8'))
        return_dataset = root.xpath('//*[@id="dataset"]')
        if len(return_dataset) == 0:
            return 9, "xml_error", "No good id dataset error", ""
        else:
            good_id_value = json.loads(return_dataset[0].text)[0].get('X_RETURNRESULT', "")
            if good_id_value:
                if len(good_id_value) == 0:
                    return 9, "xml_error", "No good id", ""
                good_id_str = good_id_value[0]['GOODS_ID']
            else:
                good_id_str = re.findall('"GOODS_ID":"(.*?)"', return_dataset[0].text)[0]
        return 0, "success", "Get good id", good_id_str
    except:
        error = traceback.format_exc()
        return 9, 'unknown_error', error, ""


def get_personal_info_from_xml(xml_string):
    """
    Get personal info from target xml string
    :param xml_string: Response returned from Get Personal Info
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        personal_info_value: dict, The person's info
    """
    try:
        root = etree.fromstring(xml_string.encode('utf-8'))
        return_dataset = root.xpath('//*[@id="dataset"]')
        if len(return_dataset) == 0:
            return 9, "xml_error", "No personal info dataset error", {}
        else:
            personal_info_value = json.loads(return_dataset[0].text)[0]
            if len(personal_info_value) == 0:
                return 9, "xml_error", "No personal info", {}
        return 0, "success", "Get personal info", personal_info_value
    except:
        error = traceback.format_exc()
        return 9, 'unknown_error', error, {}


def get_second_validate_result_from_xml(xml_string):
    """
    Get second validate result from xml string
    :param xml_string: Response returned from Check SMS Validate Code
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    try:
        if u'Stack Trace' in xml_string:
            return 9, 'website_busy_error', ""
        root = etree.fromstring(xml_string.encode('utf-8'))
        return_dataset = root.xpath('//*[@id="dataset"]')
        if len(return_dataset) == 0:
            return 9, "xml_error", ""
        else:
            second_validate_value = json.loads(return_dataset[0].text)[0]
            if len(second_validate_value) == 0:
                return 9, "xml_error", ""
            elif second_validate_value['FLAG'] == "false":
                if second_validate_value['RESULT'] == '7':
                    return 2, 'verify_error', ""
                #  “短信验证码已失效” 错误处理
                if second_validate_value['RESULT'] == '8':
                    return 9, 'param_timeout', ""
                return 9, "xml_error", ""
        return 0, "success", ""
    except:
        error = traceback.format_exc()
        return 9, 'unknown_error', error


def get_detail_bill_from_xml(xml_string):
    """
    Get detail bill from target xml string
    :param xml_string: Response returned from Get Detail Info
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        detail_bill_value: list, The list of detail bill info
    """
    try:
        root = etree.fromstring(xml_string.encode('utf-8'))
        return_dataset = root.xpath('//*[@id="dataset"]')
        if len(return_dataset) == 0:
            return 9, "xml_error", "No personal info dataset error", []

        detail_bill_value = json.loads(return_dataset[0].text)[0]
        if len(detail_bill_value) == 0:
            return 9, "xml_error", "No detail bill info", []
        elif detail_bill_value['X_RESULTCODE'] != "0":
            if detail_bill_value['X_RESULTCODE'] == "102":
                return 0, "success", detail_bill_value['X_RESULTINFO'], []
            if u'打开的文件过多' in xml_string:
                return 9, "website_busy_error", "{}".format(xml_string), []
            return 9, "expected_key_error", detail_bill_value['X_RESULTINFO'], []

        return 0, "success", "Got detail bill info", detail_bill_value['resultData']
    except Exception as e:
        return 9, 'unknown_error', u"get_detail_bill_from_xml failed: %s" % e, []


if __name__ == "__main__":
    pass
