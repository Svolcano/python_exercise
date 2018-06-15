# -*- coding: utf-8 -*-

import base64
import datetime,time
import traceback
import re
import json
import lxml.html
import sys
reload(sys)
sys.setdefaultencoding("utf8")

try:
    from worker.crawler.china_mobile.SD.base_request_param import *
except:
    from base_request_param import *

# URL for Login
MAIN_LOGON_URL = "https://sd.ac.10086.cn/portal/mainLogon.do"
PORTAL_SERVLET_URL = "https://sd.ac.10086.cn/portal/servlet/CookieServlet"
LOGIN_IMAGE_URL = "https://sd.ac.10086.cn/portal/login/briefValidateCode.jsp"
LOGIN_URL = "https://sd.ac.10086.cn/portal/servlet/LoginServlet"
SSO_LOGIN_URL = "http://www.sd.10086.cn/eMobile/loginSSO.action"

# URL for Second Validate
SECOND_VALIDATE_IMAGE_URL = "http://www.sd.10086.cn/eMobile/RandomCodeImage"
SECOND_VALIDATE_SMS_URL = "http://www.sd.10086.cn/eMobile/sendSms.action"
CHECK_SECOND_VALIDATE_URL = "http://www.sd.10086.cn/eMobile/checkSmsPass_commit.action"

# URL for Personal Info
PERSONAL_INFO_URL = "http://www.sd.10086.cn/eMobile/qryCustInfo_result.action"

# URL for Detail Info
DETAIL_BILL_URL = "http://www.sd.10086.cn/eMobile/queryBillDetail_detailBillAjax.action"


# Login Functions
def get_login_cookie(self):
    """
    Set cookies for login process
    :param request_session: Requests session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    try:
        code, key, resp = self.post(MAIN_LOGON_URL, data=get_main_logon_do_form())
        if code != 0:
            return code, key
        headers = {
                "Accept": "*/*",
                "Referer": "https://sd.ac.10086.cn/portal/mainLogon.do"
            }
        code, key, resp = self.get(PORTAL_SERVLET_URL, params=get_login_cookie_param(5), headers=headers)
        if code != 0:
            return code, key
        code, key, resp = self.get(PORTAL_SERVLET_URL, params=get_login_cookie_param(1))
        if code != 0:
            return code, key
        return 0, 'success'
    except:
        error = traceback.format_exc()
        self.log('crawler', 'unknown_error:{}'.format(error), resp)
        return 9, 'unknown_error'

def get_login_validate_image(self):
    """
    Get validate image for login
    :param request_session: Requests session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        image_str: str, Raw byte of Captcha in base64 format, return "" if fail
    """
    headers = {
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "https://sd.ac.10086.cn/portal/mainLogon.do"
        }
    code, key, resp = self.get(LOGIN_IMAGE_URL, params=get_login_image_param(), headers=headers)
    if code != 0:
        return code, key, ''
    return code, key, base64.b64encode(resp.content)


def get_login_result(self, tel_num, user_password, image_validate_code):
    """
    Process login
    :param request_session: Requests session
    :param tel_num: Tel number
    :param user_password: User's password
    :param image_validate_code: validate code from image
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    code, key, resp = self.post(LOGIN_URL, data=get_login_result_form(tel_num, user_password, image_validate_code))
    if code != 0:
        return code, key
    if resp.text != "0":
        if '登录过程中输入参数不合法' in resp.text:
            self.log('website', 'website_busy_error', resp)
            return 9, "website_busy_error"
        elif '密码认证不正确，请重新进行验证' in resp.text:
            self.log('user', 'pin_pwd_error', resp)
            return 1, 'pin_pwd_error'
        self.log('crawler', 'request_error', resp)
        return 9, 'request_error'
    return 0, 'success'


def get_prior_cookie(self):
    """
    Set cookies after login process
    :param request_session: Requests session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    return self.get('http://www.sd.10086.cn/eMobile/jsp/common/prior.jsp')


def get_attribute_id(self):
    """
    Get attribute id for SSO Login
    :param request_session: Requests session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        result: str, response from PORTAL_SERVLET_URL
    """
    return self.get(PORTAL_SERVLET_URL, params=get_login_cookie_param(2))


def extract_attribute_id_from_code(code_string):
    """
    Extract attribute ID from get_attribute_id
    :param code_string: Code in string format
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        value_body: str, attribute ID
    """
    try:
        if code_string is None:
            return 9, 'request_error', "request_error", ""

        if "onNoLoging" in code_string:
            return 9, 'request_error', "request_error", ""
        fetch_value_re = re.compile(u'var a.*?=.*?\'(.*?)\';')
        value_body = fetch_value_re.search(code_string).group(1)
        return 0, 'success', 'Get login result', value_body
    except :
        error = traceback.format_exc()
        return 9, 'unknown_error', 'unknown_error:{} '.format(error), ""


def get_sso_login_cookie(self, attribute_id):
    """
    SSO login and set cookie with Attribute ID
    :param request_session: Request Session
    :param attribute_id: Attribute ID from get_attribute_id
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        result: str, Result from SSO LOGIN
    """
    headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "http://www.sd.10086.cn/eMobile/jsp/common/prior.jsp"
            }
    return self.get(SSO_LOGIN_URL, params=get_sso_login_param(attribute_id), headers=headers)

def extract_person_info_table_border_from_html(xhtml_string):
    """
    Check if the response request is an html with error message, and try to extract the keyword
    :param xhtml_string: String that might be an html
    :return: The error message. '0' if not a html or no error message
    """
    if u'您要办理的业务需要通过短信随机码认证之后才能访问' in xhtml_string:
        return u'您要办理的业务需要通过短信随机码认证之后才能访问'

    root = lxml.html.document_fromstring(xhtml_string)
    try:
        error_message = root.xpath('//div[@class="personInfo_tableBorder"]/text()')[0].replace("\r", "")
        error_message = error_message.replace("\n", "").replace("\t", "")
        if error_message == "":
            return "0"
        return error_message
    except:
        return "0"


def extract_sso_login_result_from_html(xhtml_string):
    """
    Extract the SSO login result from get_sso_login_cookie
    :param xhtml_string: html string from get_sso_login_cookie
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    try:
        error_message = extract_person_info_table_border_from_html(xhtml_string)
        if error_message != '0':
            if '登录过程中输入参数不合法' in error_message:
                return "website_busy_error", 9, '官网异常{}'.format(xhtml_string)
            return 'request_error', 9, "sso login{}".format(error_message)
        return 'success', 0, "Get sso login"
    except Exception as e:
        return 'unknown_error', 9, "extract_sso_login_result failed %s" % e


# Second Validate Functions
def send_second_validate_sms(self):
    """
    Send SMS for second validate
    :param request_session: Request Session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    return self.post(SECOND_VALIDATE_SMS_URL, params=send_second_validate_sms_param())


def extract_send_second_validate_sms_result_from_dict(self,resp ):
    """
    Extract SMS sending result from get_second_validate_sms
    :param dict_string: Dict in string format. EX: u'{"returnArr":[["error","您的短信随机码已经发送，请注意查收！"]]}'
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Request result
    """

    try:
        second_validate_result_dict = json.loads(resp.text)
    except:
        error = traceback.format_exc()
        self.log('crawler','json_error:{}'.format(error), resp)
        return 9, 'json_error'
    if 'returnArr' not in second_validate_result_dict:
        self.log('crawler', 'expected_key_error', resp)
        return 9, 'expected_key_error'

    if second_validate_result_dict['returnArr'][0][1] == u"您的短信随机码已经发送，请注意查收！":
        return 0, 'success'
    elif second_validate_result_dict['returnArr'][0][1] == u"对不起，获取验证码失败，请重新获得！":
        self.log('crawler', 'send_sms_error', resp)
        return 9, 'send_sms_error'
    else:
        self.log('crawler', 'request_error', resp)
        return 9, 'request_error'



def get_second_validate_image(self):
    """
    Get validate image for second validate
    :param request_session: Requests session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        image_str: str, Raw byte of Captcha in base64 format, return "" if fail
    """
    headers = {
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "http://www.sd.10086.cn/eMobile/checkPassword.action?menuid=billdetails"
    }
    code, key, resp = self.get(SECOND_VALIDATE_IMAGE_URL, params=get_second_validate_image_param(), headers=headers)
    if code != 0:
        return code, key, ''
    return code, key, base64.b64encode(resp.content)


def get_second_validate_result(self, captcha_code, sms_code):
    """
    Process second validate
    :param request_session: Request session
    :param captcha_code: Validate code from image
    :param sms_code: Validate code from SMS
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    return self.post(CHECK_SECOND_VALIDATE_URL, params=get_second_validate_result_param(captcha_code, sms_code))


def extract_second_validate_result_from_html(self, resp):
    """
    Extract second validate result from get_second_validate_result
    :param html_string: html in string format
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
    """
    try:
        html_string = resp.text
        if 'errorMessage' not in html_string:
            return 0, 'success'
        root = lxml.html.document_fromstring(html_string)
        error_message = root.xpath('//ul[@class="errorMessage"]/li/span/text()')[0]
        self.log('user', 'verify_error', resp)
        return 2, 'verify_error'
    except :
        error = traceback.format_exc()
        self.log('crawler', 'unknown_error:{}'.format(error), resp)
        return 9, 'unknown_error'


# Personal Info Functions
def get_personal_info(self):
    """
    Get personal info
    :param request_session: Request session
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        result: unicode, The request result
    """
    return self.post(PERSONAL_INFO_URL, params=get_personal_info_param())


def extract_personal_info_from_dict(self, resp):
    """
    Extract needed personal info data from get_personal_info, and form a dict
    :param dict_string: dict in string format
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        personal_info_dict: dict, The personal info in dict format
    """
    try:
        dict_string = resp.text
        # Convert string to dict
        info_result_dict = json.loads(dict_string)
    except :
        error = traceback.format_exc()
        error_message = extract_person_info_table_border_from_html(dict_string)
        if error_message != '0':
            self.log('crawler', "outdated_sid:{}".format(error), resp)
            return 9, "outdated_sid", {}
        self.log('crawler', "json_error:{}".format(error), resp)
        return 9, 'json_error', {}

    # Check keyword
    if 'returnArr' not in info_result_dict:
        self.log('crawler', "request_error", resp)
        return 9, 'request_error', {}
    if not isinstance(info_result_dict['returnArr'], list):
        self.log('crawler', "request_error", resp)
        return 9, 'request_error', {}

    try:
        # Extract needed personal info
        full_name = info_result_dict['returnArr'][0][1]
        id_card = info_result_dict['returnArr'][1][3]
        is_realname_register = info_result_dict['returnArr'][1][2]
        if is_realname_register != "":
            is_realname_register = True
        else:
            is_realname_register = False
        open_date = info_result_dict['returnArr'][2][3]
        address = info_result_dict['returnArr'][2][1]

        return 0, 'success', {'full_name': full_name, 'id_card': id_card,
                                                       'is_realname_register': is_realname_register,
                                                       'open_date': time_transform(open_date, str_format='Ym'),
                                                       'address': address
                                                       }
    except:
        error = traceback.format_exc()
        self.log('crawler', "unknown_error:{}".format(error), resp)
        return 9, 'unknown_error', {}


# Detail Bill Functions
def get_detail_bill_result(self, start_date, end_date):
    """
    Get detail bill
    :param request_session: Request session
    :param start_date: start day of detail bill
    :param end_date: end day of detail bill (start day and end day must within the same month)
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        result: unicode, The request result
    """
    headers = {
        "X-Requested-With": "XMLHttpRequest"
    }
    return self.post(DETAIL_BILL_URL, params=get_detail_bill_param(start_date, end_date), headers=headers)

def time_transform(time_str,bm='utf-8',str_format="%Y-%m-%d %H:%M:%S"):
    if str_format == "Ym":
        time_str = time_str.encode(bm)
        xx = re.match(r'(.*年)?(.*月)?(.*日)?',time_str)
        time_str_list = []
        if xx.group(1):
            yy = re.findall('\d+', xx.group(1))[0]
            time_str_list.append(yy)
        if xx.group(2):
            mm = re.findall('\d+', xx.group(2))[0]
            time_str_list.append(mm)
        if xx.group(3):
            dd = re.findall('\d+', xx.group(3))[0]
            time_str_list.append(mm)
        else:
            # 没有日 取月中15号
            time_str_list.append('15')
        time_str = reduce(lambda x,y: x+"-"+y, time_str_list) + " 12:00:00"
    str_format="%Y-%m-%d %H:%M:%S"
    time_type = time.strptime(time_str.encode(bm), str_format)
    
    return str(int(time.mktime(time_type)))

def time_format(time_str,**kwargs):
    exec_type=1
    time_str = time_str.encode('utf-8')
    
    if 'exec_type' in kwargs:
        exec_type = kwargs['exec_type']
    if (exec_type == 1):
        #print time_str
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

def extract_detail_bill_from_dict(dict_string, year_month, self_obj=None):
    """
    Extract needed detail bill from get_detail_bill_result, and form a list
    :param dict_string: Dict in string format
    :return:
        status_key: str, The key of status code
        level: int, Error level
        message: unicode, Error Message
        formal_detail_bill_list: list, The list of detail bill info
    """

    # Transform string into Dict
    if dict_string.strip() == "":
        return 9, "website_busy_error", "官网返回空字符", []
    try:
        if u"首次登录" in dict_string:
            return 9, "pin_pwd_error", "首次登录: {}".format(dict_string), []
        bill_result_dict = json.loads(dict_string)
    except:
        error = traceback.format_exc()
        error_message = extract_person_info_table_border_from_html(dict_string)
        if error_message != '0':
            return 9, "outdated_sid", "outdated_sid:{}", format(error), []
        return 9, 'unknown_error', "unknown_error:{}".format(error), []

    # Check if needed keys are available
    if 'bdp' not in bill_result_dict:
        return 9, 'request_error', "request_error", []
    if 'billdata' not in bill_result_dict['bdp']:
        return 9, 'request_error', "request_error", []
    if bill_result_dict['bdp']['billdata'] is None:
        return 0, 'success', "No data in target month", []

    # Get detail bills
    formal_detail_bill_list = list()
    for daily_data_dict in reversed(bill_result_dict['bdp']['billdata']):
        # Check keyword
        if 'strlist' not in daily_data_dict:
            return 9, 'request_error', "request_error", []
        if daily_data_dict['strlist'] is None:
            return 9, 'request_error', "request_error", []
        if 'datevalue' not in daily_data_dict:
            return 9, 'request_error', "request_error", []

        # Extract detail bill
        try:
            detail_bill_result_list = daily_data_dict['strlist']

            for detail_bill in reversed(detail_bill_result_list):
                raw_call_from = detail_bill[1]
                call_from, error = self_obj.formatarea(raw_call_from)
                if not call_from:
                    call_from = raw_call_from
                    self_obj.log("crawler", "{}-{}".format(error, raw_call_from), "")
                _tmp = {"call_from": call_from, "call_time": time_transform(daily_data_dict['datevalue'] + " " + detail_bill[0]),
                        "call_to": "", "call_tel": detail_bill[3].decode('utf-8'),
                        "call_method": detail_bill[2], "call_type": detail_bill[5],
                        "call_cost": detail_bill[7], "call_duration": time_format(detail_bill[4]), 'month':year_month}
                formal_detail_bill_list.append(_tmp)
        except :
            message = traceback.format_exc()
            return "unknown_error", 9, "unknown_error:{}".format(message), []

    return 0, 'success', "Get detail bill", formal_detail_bill_list


if __name__ == '__main__':
    pass
    """
    # from worker.crawler.china_mobile.SD.base_sd_crawler import *
    USER_ID = "15762559079"
    USER_PASSWORD = "172509"

    session = requests.session()

    session.get("https://sd.ac.10086.cn/login/")

    key, level, message = get_login_cookie(session)

    key, level, message, result = get_login_validate_image(session)
    with open("./worker/crawler/china_mobile/SD/validate.jpg", 'wb') as f:
        f.write(base64.b64decode(result))

    validate_code = "5740"
    key, level, message = get_login_result(session, USER_ID, USER_PASSWORD, validate_code)

    key, level, message = get_prior_cookie(session)

    key, level, message, result = get_attribute_id(session)

    key, level, message, result = extract_attribute_id_from_code(result)

    key, level, message, result = get_sso_login_cookie(session, result)

    key, level, message = extract_sso_login_result_from_html(result)

    # Basic Info
    basic_info = session.post('http://www.sd.10086.cn/eMobile/ajax_userBalance.action?menuid=index',
                              data=get_balance_left_form(USER_ID))
    pprint(basic_info.text)

    # Personal Info
    key, level, message = send_second_validate_sms(session)

    key, level, message = extract_send_second_validate_sms_result_from_dict(message)

    key, level, message, result = get_second_validate_image(session)
    with open("./worker/crawler/china_mobile/SD/validate.jpg", 'wb') as f:
        f.write(base64.b64decode(result))

    validate_code = "sspm"
    sms_validate_code = "647900"

    key, level, message = get_second_validate_result(session, validate_code, sms_validate_code)
    key, level, message = extract_second_validate_result_from_html(message)
    pprint(message)

    key, level, message, result = get_personal_info(session)

    key, level, message, result = extract_personal_info_from_dict(result)
    pprint(result)

    # Detail Bill
    import calendar
    from dateutil.relativedelta import relativedelta

    current_time = datetime.datetime.now()

    detail_info_list = list()
    for month_offset in range(0, 7):
        year_month = (current_time - relativedelta(months=month_offset))

        day_count = calendar.monthrange(year_month.year, year_month.month)[1]
        target_start_date = "%s01000000" % year_month.strftime('%Y%m')
        target_end_date = "%s%s235959" % (year_month.strftime('%Y%m'), day_count)

        key, level, message, result = get_detail_bill_result(session, target_start_date, target_end_date)

        # Extract detail info from javascript
        key, level, message, result = extract_detail_bill_from_dict(result)

        detail_info_list += result

    pprint(detail_info_list)
    """
