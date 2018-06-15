# -*- coding: utf-8 -*-

import re
import json
import base64
import traceback
import time,datetime
import ast
import requests
import lxml.html

try:
    from worker.crawler.china_mobile.SH.base_request_param import *
except:
    from base_request_param import *
# from pprintpp import pprint

# const login url
LOGIN_EX_URL = "https://sh.ac.10086.cn/loginex"
VALIDATE_CODE_URL = "https://sh.ac.10086.cn/validationCode"
FORWARD_URL = "http://www.sh.10086.cn/sh/wsyyt/ac/forward.jsp"
LOGIN_POST_URL = "http://www.sh.10086.cn/sh/wsyyt/ac/loginpost.jsp"

# const personal info url
DETAIL_PERSONAL_INFO_URL = "http://www.sh.10086.cn/sh/wsyyt/action?act=myarea.getinfoManageMore"

# const detail bil url
CURRENT_MONTH_DETAIL_BILL_URL = "http://www.sh.10086.cn/sh/wsyyt/busi/historySearch.do?method=getOneBillDetailAjax"
PAST_MONTH_DETAIL_BILL_URL = "http://www.sh.10086.cn/sh/wsyyt/busi/historySearch.do?method=getFiveBillDetailAjax"


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
    try:
        response = request_session.get(url=LOGIN_EX_URL, params=get_rnd_param(), data=get_rnd_form())
        if '5' in str(response.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(response.status_code), ""
        if response.status_code != 200:
            return 'request_error', 9, response.status_code, ""

        rnd = json.loads(response.content)['message']
        response = request_session.get(url=VALIDATE_CODE_URL, params=get_image_param(rnd))
        if '5' in str(response.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(response.status_code), ""
        if response.status_code != 200:
            return 'request_error', 9, response.status_code, ""

        return 'success', 0, 'Get image', base64.b64encode(response.content)
    except Exception as e:
        return 'unknown_error', 9, "get_validate_image failed: %s" % e, ""


def get_validate_result(request_session, tel_num, picture_validate_code):
    """
    Check if the validate code is correct
    :param request_session: Requests session
    :param tel_num: Tel number
    :param picture_validate_code: Validate code from image
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    try:
        response = request_session.post(url=LOGIN_EX_URL, params=get_validate_result_param(), data=get_validate_result_form(tel_num, picture_validate_code))
        if '5' in str(response.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(response.status_code)
        if response.status_code != 200:
            return 'request_error', 9, response.status_code
    except Exception as e:
        return 'unknown_error', 9, "get_validate_result failed: {}".format(str(e))

    try:
        if response.text.strip() == "":
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(response.status_code)
        validate_result = json.loads(response.text)
        if validate_result['result'] != '0':
            # TODO: add logging
            return 'verify_error', 1, validate_result['message']
        return 'success', 0, validate_result['message']
    except Exception as e:
        return 'unknown_error', 9, "get_validate_json failed: {},\n{}".format(str(e), response.text)


def is_validate(tel_num, user_password):
    """
    Check if the tel and the password are valid
    :param tel_num: Tel number
    :param user_password: Password
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    tel_num = str(tel_num)
    if tel_num[0] != '1' or len(tel_num) < 11:
        return 'invalid_tel', 1, '请输入正确的手机号码或者密码'.decode('UTF-8')
    user_password = str(user_password)
    if len(user_password) < 6:
        return 'pin_pw_error', 1, '请输入正确的6位动态密码'.decode('UTF-8')
    return 'success', 0, 'validate complete'


def get_login_result(request_session, tel_num, user_password, picture_validate_code):
    """
    Login
    :param request_session: Requests session
    :param tel_num: Tel number
    :param user_password: Password
    :param picture_validate_code: validate code from image
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        uuid: str, The uuid if login is successful
    """
    try:
        response = request_session.post(url=LOGIN_EX_URL, params=get_login_result_param(),
                                        data=get_login_result_form(tel_num, user_password, picture_validate_code))
        if '5' in str(response.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(response.status_code), ""
        if response.status_code != 200:
            return 'request_error', 9, response.status_code, ""

        login_result = json.loads(response.text)
        if login_result['result'] != '0':
            return 'verify_error', 2, login_result['message'], ""
        return 'success', 0, "Get uid", login_result['uid']
    except Exception as e:
        return 'unknown_error', 9, "get_login_result failed: %s" % e, ""


def get_forward_result(request_session, uid):
    """
    Go to forward page and set uuid cookie
    :param request_session: Request session
    :param uid: UUID returned from get login result
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    try:
        forward_result = request_session.get(url=FORWARD_URL, params=get_forward_result_param(uid))
        if '5' in str(forward_result.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(forward_result.status_code)
        if forward_result.status_code != 200:
            return 'request_error', 9, forward_result.status_code
        return 'success', 0, "Get forward result complete"
    except Exception as e:
        return 'unknown_error', 9, "get_forward_result failed: %s" % e


def get_detail_personal_info(request_session):
    """
    Get personal info
    :param request_session: Request session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        personal_info_dict: dict, The personal info in dict format
    """
    try:
        response = request_session.get(url=DETAIL_PERSONAL_INFO_URL)
        if '5' in str(response.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(response.status_code), {}
        if response.status_code != 200:
            return 'request_error', 9, response.status_code, {}


        personal_info_result = json.loads(response.text)
        if personal_info_result['error']['code'] != 0:
            if personal_info_result['error']['code'] == -1:
                return 'outdated_sid', 9, personal_info_result['error']['message'], {}
            return 'request_error', 9, personal_info_result['error']['message'], {}
        realname_register = personal_info_result['value']['identInfo']
        if realname_register:
            realname_register = True
        else:
            realname_register = False
        personal_info_dict = {'full_name': personal_info_result['value']['name'],
                              'id_card': personal_info_result['value']['zjNum'],
                              'is_realname_register': realname_register,
                              'open_date': time_transform(personal_info_result['value']['creaateDate'], str_format="Ymd"),
                              'address': '',
                              }
        return 'success', 0, "Get personal info", personal_info_dict
    except Exception as e:
        return 'unknown_error', 9, "get_detail_personal_info failed: %s" % e, {}


def get_second_validate(request_session, tel_num):
    """
    Send second validate message
    :param request_session: Request session
    :param tel_num: Tel number
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        response: str, The check result
    """
    try:
        response = request_session.post(url=LOGIN_EX_URL, params=get_second_validate_param(tel_num))
        if '5' in str(response.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(response.status_code), ""
        if response.status_code != 200:
            return 'request_error', 9, response.status_code, ""
        return 'success', 0, "Get second validate", response.text
    except Exception as e:
        return 'unknown_error', 9, "get_second_validate failed: %s" % e, ""


def extract_second_validate_message_from_xhtml(xhtml_string):
    """
    Get sending second validate message result from target xhtml string
    :param xhtml_string: Response returned from get second validate
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    try:
        root = lxml.html.document_fromstring(xhtml_string)
        result_value = root.xpath('//*[@name="ret"]/@value')
        if len(result_value) > 0:
            message_value = root.xpath('//*[@name="message"]/@value')
            if result_value[0] == '1':
                error_msg = message_value[0]
                if u'系统不再下发' in error_msg:
                    return 'over_max_sms_error', 9, error_msg
                elif u'请30秒后再试' in error_msg:
                    return 'send_sms_too_quick_error', 2, message_value[0]
                elif u'无法为您所输入的手机号码发送动态密码，请核对后重新输入。' in error_msg:
                    return 'invalid_tel', 9, message_value[0]
                else:
                    return 'unknown_error', '9', error_msg
            elif result_value[0] != '0':
                return 'verify_error', 2, message_value[0]
            return 'success', 0, message_value[0]
        else:
            return 'xml_error', 9, "No ret Error"
    except Exception as e:
        return 'unknown_error', 9, "extract_second_validate_message_from_xhtml failed: %s" % e


def check_second_validate_result(request_session, tel_num, sms_validate_code):
    """
    Check the second validate
    :param request_session: Request session
    :param tel_num: Tel number
    :param sms_validate_code: validate code from SMS message
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        response: str, The check result
    """
    try:
        response = request_session.post(url=LOGIN_EX_URL,
                                        data=get_check_second_validate_form(tel_num, sms_validate_code))
        if '5' in str(response.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(response.status_code), ""
        if response.status_code != 200:
            return 'request_error', 9, response.status_code, ""
        return 'success', 0, "check second validate", response.text
    except Exception as e:
        return 'unknown_error', 9, "check_second_validate_result failed: %s" % e, ""


def extract_second_validate_uid_from_xhtml(xhtml_string):
    """
    Get detail bill from target xhtml string
    :param xhtml_string: Response returned from check_second_validate_result
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        uuid: str, The uuid if second validate is successful
    """
    try:
        root = lxml.html.document_fromstring(xhtml_string)
        result_value = root.xpath('//*[@name="ret"]/@value')
        if len(result_value) > 0:
            message_value = root.xpath('//*[@name="message"]/@value')
            uid_value = root.xpath('//*[@name="uid"]/@value')
            if result_value[0] != '0':
                return 'verify_error', 2, message_value[0], uid_value[0]
            return 'success', 0, message_value[0], uid_value[0]
        else:
            return 'xml_error', 9, "xpath_error:{}".format(xhtml_string), ""
    except Exception as e:
        return 'unknown_error', 9, "extract_second_validate_uid_from_xhtml failed: %s" % e, ""


def get_login_post_result(request_session, uuid):
    """
    Go to login post page and set uuid cookie
    :param request_session: Request session
    :param uuid: UUID returned from second validate result
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    try:
        login_post_result = request_session.post(url=LOGIN_POST_URL, data=get_login_post_result_form(uuid))
        if '5' in str(login_post_result.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(login_post_result.status_code)
        if login_post_result.status_code != 200:
            return 'request_error', 9, login_post_result.status_code
        return 'success', 0, "Get login post result complete"
    except Exception as e:
        return 'unknown_error', 9, "get_login_post_result failed: %s" % e


def get_current_month_detail_bill(request_session, start_date, end_date):
    """
    Request detail bill of current month
    :param request_session: Request session
    :param start_date: The beginning date of bill
    :param end_date: The last date of bill
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        detail_bill_result.: str, The request result
    """
    try:
        detail_bill_result = request_session.post(url=CURRENT_MONTH_DETAIL_BILL_URL,
                                                  data=get_current_month_detail_bill_form(start_date, end_date))
        if '5' in str(detail_bill_result.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(detail_bill_result.status_code), ""
        if detail_bill_result.status_code != 200:
            return 'request_error', 9, detail_bill_result.status_code, ""
        return 'success', 0, "Get login post result complete", detail_bill_result.text
    except Exception as e:
        return 'unknown_error', 9, "get_current_month_detail_bill failed: %s" % e, ""


def get_past_month_detail_bill(request_session, start_date, end_date):
    """
    Request detail bill of past month
    :param request_session: Request session
    :param start_date: The beginning date of bill
    :param end_date: The last date of bill
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        detail_bill_result.: str, The request result
    """
    try:
        detail_bill_result = request_session.post(url=PAST_MONTH_DETAIL_BILL_URL,
                                                  data=get_past_month_detail_bill_form(start_date, end_date))
        if '5' in str(detail_bill_result.status_code):
            return "website_busy_error", 9, u"site_servers error status_code:{}".format(detail_bill_result.status_code), ""
        if detail_bill_result.status_code != 200:
            return 'request_error', 9, detail_bill_result.status_code, ""
        return 'success', 0, "Get login post result complete", detail_bill_result.text
    except Exception as e:
        return 'unknown_error', 9, "get_past_month_detail_bill failed: %s" % e

def time_transform(time_str,bm='utf-8',str_format="%Y-%m-%d %H:%M:%S"):
    #print time_str
    if str_format == "Ymd":
        ymd = re.findall(r'(\d{2,4})', time_str.encode(bm))
        time_str = reduce(lambda x,y: x+"-"+y, ymd) + " 12:00:00"
    else:
        today_month = datetime.date.today().month
        today_year = datetime.date.today().year
        str_month = int(time_str[:2])
        if str_month > today_month:
            str_year = today_year - 1
        else:
            str_year = today_year
        time_str = str(str_year) + "-" + time_str
    str_format="%Y-%m-%d %H:%M:%S"
    time_type = time.strptime(time_str.encode(bm), str_format)

    return str(int(time.mktime(time_type)))

def time_format(time_str,**kwargs):
    exec_type=1
    time_str = time_str.encode('utf-8')

    if 'exec_type' in kwargs:
        exec_type = kwargs['exec_type']
    if (exec_type == 1):
        xx = re.match(r'(.*时)?(.*分)?(.*秒)?',time_str)
        h,m,s = 0,0,0
        if  xx.group(1):
            hh = re.findall('\d+', xx.group(1))[0]
            h = int(hh)
        if  xx.group(2):
            mm = re.findall('\d+', xx.group(2))[0]
            m = int(mm)
        if  xx.group(3):
            ss = re.findall('\d+', xx.group(3))[0]
            s = int(ss)
        real_time = h*60*60 + m*60 +s
    if (exec_type == 2):
        xx = re.findall(r'\d*', time_str)
        h, m, s = map(int,xx[::2])
        real_time = h*60*60 + m*60 +s

    return str(real_time)


def extract_current_detail_bill_from_javascript(js_string):
    """
    Get detail bill from target javascript string
    :param js_string: Response returned from get current/past month detail bill
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        detail_bill_list: list, The list of detail bill info
    """
    if js_string == "":
        return 'html_error', 9, "No detail bill data to extract", ""

    result_value = js_string.split("$")[0]
    if result_value != '0':
        if result_value == '1':
            return 'success', 0, u"暂无此详单类型的记录。", []
        elif result_value == '2':
            return 'request_error', 9, u"对不起，您输入的时间非法", []
        elif result_value == '10000':
            return "website_busy_error", 9, u"官网异常(由于长时间未操作，为了您的账户安全，请重新登录)", []
        else:
            return 'html_error', 9, "Unknown detail bill data to extract", []

    try:
        fetch_script_re = re.compile(u'<script .*?>(.*)</script>')
        if fetch_script_re is None:
            return 'html_error', 9, "No detail bill data to extract", []

        js_body = fetch_script_re.search(js_string).group(1)
        fetch_value_re = re.compile(u';value.*?=.*?(\[.*?\])";')
        value_body = fetch_value_re.search(js_body).group(1)
        detail_bill_list = ast.literal_eval(value_body)

        formal_detail_bill_list = list()
        for detail_bill in detail_bill_list:
            _tmp = {"call_from": detail_bill[2].decode('utf-8'), "call_time": time_transform(detail_bill[1].decode('utf-8')),
                    "call_to": "", "call_tel": detail_bill[4].decode('utf-8'),
                    "call_method": detail_bill[3].decode('utf-8'), "call_type": detail_bill[6].decode('utf-8'),
                    "call_cost": detail_bill[8].decode('utf-8'), "call_duration": time_format(detail_bill[5].decode('utf-8'), exec_type=2)}

            formal_detail_bill_list.append(_tmp)
        return 'success', 0, "Get detail bill", list(reversed(formal_detail_bill_list))
    except Exception as e:
        return "unknown_error", 9, "extract_detail_bill_from_javascript failed: %s" % e, []


def extract_past_detail_bill_from_javascript(js_string):
    """
    Get detail bill from target javascript string
    :param js_string: Response returned from get current/past month detail bill
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        detail_bill_list: list, The list of detail bill info
    """
    if js_string == "":
        return 'html_error', 9, "No detail bill data to extract", ""

    result_value = js_string.split("$")[0]
    if result_value != '0':
        if result_value == '1':
            return 'success', 0, u"暂无此详单类型的记录。", []
        elif result_value == '2':
            return 'request_error', 9, u"对不起，您输入的时间非法", []
        elif result_value == '10000':
            return "website_busy_error", 9, u"官网异常(由于长时间未操作，为了您的账户安全，请重新登录)", []
        else:
            return 'html_error', 9, "Unknown detail bill data to extract", []

    try:
        fetch_script_re = re.compile(u'<script .*?>(.*)</script>')
        if fetch_script_re is None:
            return 'html_error', 9, "No detail bill data to extract", []

        js_body = fetch_script_re.search(js_string).group(1)
        fetch_value_re = re.compile(u';value.*?=.*?(\[.*?\]);')
        value_body = fetch_value_re.search(js_body).group(1)
        detail_bill_list = ast.literal_eval(value_body)

        formal_detail_bill_list = list()
        for detail_bill in detail_bill_list:
            _tmp = {"call_from": detail_bill[2].decode('utf-8'), "call_time": time_transform(detail_bill[1].decode('utf-8')),
                    "call_to": "", "call_tel": detail_bill[4].decode('utf-8'),
                    "call_method": detail_bill[3].decode('utf-8'), "call_type": detail_bill[6].decode('utf-8'),
                    "call_cost": detail_bill[8].decode('utf-8'), "call_duration": time_format(detail_bill[5].decode('utf-8'), exec_type=2)}

            formal_detail_bill_list.append(_tmp)
        return 'success', 0, "Get detail bill", list(reversed(formal_detail_bill_list))
    except Exception as e:
        return "unknown_error", 9, "extract_detail_bill_from_javascript failed: %s" % e, []


if __name__ == "__main__":
    # from worker.crawler.china_mobile.SH.base_sh_crawler import *

    USER_ID = "15901735976"
    USER_PASSWORD = "191396"

    session = requests.session()

    # Login
    session.get(url="https://sh.ac.10086.cn/login")

    key, level, message, result = get_validate_image(session)
    with open("./worker/crawler/china_mobile/SH/validate.jpg", 'wb') as f:
        f.write(base64.b64decode(result))

    validate_code = "5bath8"

    key, level, message = get_validate_result(session, "15901735976", validate_code)

    # pprint(is_validate(USER_ID, USER_PASSWORD))

    key, level, message, result = get_login_result(session, USER_ID, USER_PASSWORD, validate_code)

    key, level, message = get_forward_result(session, result)

    # Personal Info
    key, level, message, result = get_detail_personal_info(session)

    # Second validate
    key, level, message, result = get_second_validate(session, USER_ID)

    key, level, message = extract_second_validate_message_from_xhtml(result)

    validate_code = ""

    key, level, message, result = check_second_validate_result(session, USER_ID, validate_code)

    key, level, message, result = extract_second_validate_uid_from_xhtml(result)

    key, level, message = get_login_post_result(session, result)

    # Detail bill
    import calendar

    current_time = datetime.datetime.now()
    current_year = current_time.year
    current_month = current_time.month

    day_count = calendar.monthrange(current_year, current_month)[1]
    target_start_date = "%s-%s-01" % (current_year, current_month)
    target_end_date = "%s-%s-%s" % (current_year, current_month, day_count)
    key, level, message, result = get_current_month_detail_bill(session, target_start_date, target_end_date)

    # from pprintpp import pprint

    for month_offset in range(0, 7):
        target_month = current_month - month_offset
        day_count = calendar.monthrange(current_year, target_month)[1]

        target_start_date = "%s-%s-01" % (current_year, target_month)
        target_end_date = "%s-%s-%s" % (current_year, target_month, day_count)
        key, level, message, result = get_past_month_detail_bill(session, target_start_date, target_end_date)

        # print(level)
        # pprint(result)
