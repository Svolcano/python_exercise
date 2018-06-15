# -*- coding: utf-8 -*-
import datetime
import re
import time
import traceback
import base64
import response_data

from dateutil.relativedelta import relativedelta
from lxml import etree
from base_request_param import mix_current_time

if __name__ == '__main__':
    import sys

    sys.path.append('../../../')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from base_info_crawler import *
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_mobile.chongqing.base_info_crawler import *

# const url
START_URL = "https://service.cq.10086.cn/httpsFiles/pageLogin.html"
ICS_SERVICE_URL = "http://service.cq.10086.cn/ics"
HTTPS_ICS_SERVICE_URL = "https://service.cq.10086.cn/ics"
LOGIN_URL = "https://cq.ac.10086.cn/SSO/loginbox"
AUTH_RETURN_URL = "http://service.cq.10086.cn/CHOQ/authentication/authentication_return.jsp"
SUCCESS_LOGIN_URL = "http://service.cq.10086.cn/ics?service=page/login&listener=getLoginInfo"

# const variable
XML_SESSION_TIMEOUT_INFO = "session is time out"

# const personal info url
MY_MOBILE_URL = "http://service.cq.10086.cn/myMobile/myMobile.html"

# const personal info variable
FORMAL_KEY_TO_CQ_KEY = {'full_name': 'NAME', 'is_realname_register': 'smzyz', 'open_date': 'STARTDATE'}
PERSONAL_INFO_EVENT_NAME_DICT = {'userInfo': "GRXX", "userInfo2": "GRXX", "starService": "XJFW", "new_uwer_info": "XFMX"}

# const detail bill url
DETAIL_BILL_URL = "http://service.cq.10086.cn/myMobile/detailBill.html"


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.image_validate_count = 0

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_login_verify_type(self, **kwargs):
        return 'SMS'

    def get_verify_type(self, **kwargs):
        return ''

    def send_login_verify_request(self, **kwargs):
        # self.session.cookies.clear()
        # Go to Login Page
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.cq.10086.cn/httpsFiles/pageLogin.html"
        }
        code, key, resp = self.get(START_URL, headers=headers)
        if code != 0:
            return code, key, ""
        verify_type = kwargs.get('verify_type', '')

        if verify_type in ['', 'sms']:
            url = "https://service.cq.10086.cn/ics"
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "Referer": "https://service.cq.10086.cn/httpsFiles/pageLogin.html",
            }
            data = {
                "service": "ajaxDirect/1/login/login/javascript/"
                , "pagename": "login"
                , "eventname": "interfaceSendSMS"
                , "cond_SERIAL_NUMBER": kwargs['tel']
                , "ajaxSubmitType": "post"
                , "ajax_randomcode": mix_current_time()
            }
            code, key, resp = self.post(url, headers=headers, params=data)
            if code != 0:
                return code, key, ""
            try:
                if u'获取短信验证码过于频繁' in resp.text:
                    self.log("user", 'send_sms_too_quick_error', resp)
                    return 9, 'send_sms_too_quick_error', ''
                if '"FLAG":"true"' not in resp.text:
                    self.log("crawler", u"未知原因发送短信失败", resp)
                    return 9, "send_sms_error", ""
            except:
                error = traceback.format_exc()
                self.log("crawler", u"解析短信发送结果失败".format(error), resp)
                return 9, "html_error", ""

        return 0, "success", ''


    def increase_image_validate_count(self):
        """
        Increase the time count when request a new validate image
        :return: None
        """
        self.image_validate_count += 1

    def reset_image_validate_count(self):
        """
        Reset the time count when request a new validate image
        :return: None
        """
        self.image_validate_count = 0

    def login(self, **kwargs):
        """
        Login process
            1. Request SSO Login
            2. Request Start Event
            3. Request Login Box
            4. Request Auth Return
            5. Request Return Success
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        for i in range(self.max_retry):
            codetype = '3004'
            code, key, resp = get_validate_image(self)
            if code != 0:
                continue
            # 云打码
            key, result, cid = self._dama(resp.content, codetype)
            # print result, cid, "***---***" * 10
            if key == "success" and result != "":
                captcha_code = str(result)
            else:
                self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                code, key = 9, "auto_captcha_code_error"
                continue
            # Input Validation Check
            level, key, message = is_validate(kwargs['tel'], kwargs['pin_pwd'], captcha_code, self)
            if level != 0:
                self.log("crawler", str(key) + ": " + message, "")
                return level, key

            # Request SSO Login
            headers = {
                'Referer': 'https://service.cq.10086.cn/httpsFiles/pageLogin.html',
                'Origin': 'https://service.cq.10086.cn',
                'Host': 'service.cq.10086.cn',
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
            }

            params = get_sso_login_param(kwargs['tel'], kwargs['pin_pwd'], captcha_code, kwargs['sms_code'])

            code, key, resp = self.post(HTTPS_ICS_SERVICE_URL, headers=headers, params=params)
            if code != 0:
                return code, key
            if '"RESULT":"0"' not in resp.text:
                # 如返回{"RESULTINFO":"","RESULT":"-1"}，则大概率为访问过于频繁导致的
                if "短信随机码不正确或已过期" in resp.text or "短信验证码输入错误" in resp.text:
                    self.log("user", 'verify_error', resp)
                    return 9, 'verify_error'
                if "超过限制" in resp.text:
                    # 您在24小时之内登录短信验证码错误超过限制，请24小时之后再试
                    self.log("user", "短信错误次数超限制", resp)
                    return 9, 'over_query_limit'
                if '"WhitenumFLAG":"false","FLAG":"false"' in resp.text:
                    self.log("crawler", "login_param_error", resp)
                    return 1, 'login_param_error'
                if "验证码不正确" in resp.text:
                    self.log("website", "打码失败", resp)
                    self._dama_report(cid)
                    code, key = 9, "auto_captcha_code_error"
                    continue
                self.log("crawler", 'login_param_error', resp)
                return 2, 'login_param_error'
            break
        else:
            return code, key
        self.reset_image_validate_count()
        # 将二次验证移至这里:
        url = "http://service.cq.10086.cn/ics"
        data = {
            "service": "ajaxDirect/1/secondValidate/secondValidate/javascript/",
            "pagename": "secondValidate",
            "eventname": "checkSMSINFO",
            "cond_USER_PASSSMS": base64.b64encode(kwargs['pin_pwd']),
            "cond_CHECK_TYPE": "DETAIL_BILL",
            "cond_loginType": "0",
            "ajaxSubmitType": "post",
            "ajax_randomcode": mix_current_time()
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://service.cq.10086.cn/myMobile/detailBill.html"
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key
        if u'验证成功' not in resp.text:
            self.log("user", 'pin_pwd_error', resp)
            return 9, 'pin_pwd_error'
        return 0, 'success'

    def is_session_timeout(self, data_string):
        """
        Check if the session timeout keyword is in the target string
        :param data_string: Response returned by various of requests
        :return: True/False
        """
        if XML_SESSION_TIMEOUT_INFO in data_string:
            self.reset_image_validate_count()
            return True
        return False

    def crawl_info(self, **kwargs):
        """
        Crawl user's personal info
            1. Go to Personal Info Page
            2. Get Good IDs
            3. Push Local IP to Cookie
            4. Get Personal Info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        # Go to Personal Info Page
        event_name = "userInfo2"

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.cq.10086.cn/"
        }
        code, key, resp = self.get(MY_MOBILE_URL, headers=headers)
        if code != 0:
            return code, key, {}

        detail_bill_good_ename = "XFMX"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://service.cq.10086.cn/myMobile/detailBill.html"
        }
        code, key, resp_good_id = self.post(ICS_SERVICE_URL, headers=headers, params=get_good_id_param(detail_bill_good_ename))
        if code != 0:
            return code, key, {}
        # Push Local IP to Cookie
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        code, key, resp = self.get(ICS_SERVICE_URL, params=get_ip_to_cookie_param(), headers=headers)
        if code != 0:
            return code, key, {}

        # Extract Good ID from XML
        if self.is_session_timeout(resp_good_id.text):
            # self.log("crawl_error", "session is time out", request_good_id_result)
            return 9, "outdated_sid", {}

        level, key, message, result = get_good_id_from_xml(resp_good_id.text)
        if level != 0:
            self.log("crawler", "{}: {}".format(key, message), resp_good_id)
            return level, key, {}
        else:
            good_id = result

        # Push Local IP to Cookie

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        code, key, resp = self.get(ICS_SERVICE_URL, params=get_ip_to_cookie_param(), headers=headers)
        if code != 0:
            return code, key, {}
        # Get Personal Info
        good_ename = PERSONAL_INFO_EVENT_NAME_DICT[event_name]
        good_name = PERSONAL_INFO_GOOD_NAME_DICT[good_ename]
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://service.cq.10086.cn/myMobile/myMobile.html"
        }
        code, key, resp = self.get(ICS_SERVICE_URL, headers=headers, params=get_personal_info_param(event_name, good_ename, good_id, good_name))
        if code != 0:
            return code, key, {}
        # Extract Personal Info from Personal Info Result
        if self.is_session_timeout(resp.text):
            return 9, "outdated_sid", {}

        code, key, message, result = get_personal_info_from_xml(resp.text)
        if code != 0:
            return code, key, {}

        personal_info_dict = dict()
        for key in FORMAL_KEY_TO_CQ_KEY:
            personal_info_dict[key] = result.get(FORMAL_KEY_TO_CQ_KEY[key], "")
        personal_info_dict["open_date"] = self.time_transform(personal_info_dict["open_date"], str_format="%Y-%m-%d")
        personal_info_dict["address"] = ""
        if personal_info_dict['is_realname_register'] == '1':
            personal_info_dict['is_realname_register'] = True
        else:
            personal_info_dict['is_realname_register'] = False

        personal_info_dict['id_card'] = ''
        return 0, 'success', personal_info_dict

    def send_verify_request(self, **kwargs):
        """
        Send SMS verify code
            1. Go to Detail Info Page
            2. Trigger Second Validation
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # Go to Detail Info Page
        event_name = "new_uwer_info"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.cq.10086.cn/myMobile/myMobile.html"
        }
        code, key, resp = self.get(DETAIL_BILL_URL, headers=headers)
        if code != 0:
            return code, key, ""
        # Get Good IDs
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://service.cq.10086.cn/myMobile/detailBill.html"
        }
        code, key, resp = self.post(ICS_SERVICE_URL, headers=headers, params=get_good_id_param(PERSONAL_INFO_EVENT_NAME_DICT[event_name]))
        if code != 0:
            return code, key, ""
        # Push Local IP to Cookie
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        code, key, resp = self.get(ICS_SERVICE_URL, params=get_ip_to_cookie_param(), headers=headers)
        if code != 0:
            return code, key, ""
        # Trigger Second Validation(Send SMS Validate Code to Cellphone)
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://service.cq.10086.cn/myMobile/detailBill.html"
        }
        code, key, resp = self.post(ICS_SERVICE_URL, headers=headers, params=get_second_validation_param())
        if code != 0:
            return code, key, ""
        if self.is_session_timeout(resp.text):
            return 9, "outdated_sid", ""
        return 0, 'success', ''

    def verify(self, **kwargs):
        """
        Check SMS validate code
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        # Check SMS Validate Code
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://service.cq.10086.cn/myMobile/detailBill.html"
        }
        code, key, resp_data = self.post(ICS_SERVICE_URL, headers=headers, params=get_check_sms_info_param(kwargs['sms_code']))
        if code != 0:
            return code, key
        # Push Local IP to Cookie
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }

        code, key, resp_ip = self.get(ICS_SERVICE_URL, params=get_ip_to_cookie_param(), headers=headers)
        if code != 0:
            return code, key
        # Extract SMS Validate Result
        if self.is_session_timeout(resp_data.text):
            return 9, "outdated_sid"
        code, key, err = get_second_validate_result_from_xml(resp_data.text)
        if code != 0:
            if code in [1, 2]:
                self.log("user", "{}: {}".format(key, err), resp_data)
            else:
                self.log("crawler", "{}: {}".format(key, err), resp_data)
        return code, key

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        # 12-06 09:57:32
        if time_str == '':
            return ''
        if str_format == "%Y-%m-%d %H:%M:%S" and len(time_str) == 14:
            today_month = datetime.date.today().month
            today_year = datetime.date.today().year
            str_month = int(time_str[:2])
            if str_month > today_month:
                str_year = today_year - 1
            else:
                str_year = today_year
            time_str = str(str_year) + "-" + time_str
        if str_format == "%Y-%m-%d":
            time_str += " 12:00:00"
        str_format = "%Y-%m-%d %H:%M:%S"
        time_type = time.strptime(time_str.encode('utf-8'), str_format)
        return str(int(time.mktime(time_type)))

    def time_format(self, time_str, **kwargs):
        time_str = time_str.encode('utf-8')
        if 'exec_type' in kwargs:
            exec_type = kwargs['exec_type']
        if (exec_type == 1):
            # print "********"
            # print time_str
            # print "********"
            xx = re.match(r'(.*时)?(.*分)?(.*秒)?', time_str)
            h, m, s = 0, 0, 0
            if xx.group(1):
                hh = re.findall('\d+', xx.group(1))[0]
                h = int(hh)
            if xx.group(2):
                mm = re.findall('\d+', xx.group(2))[0]
                m = int(mm)
            if xx.group(3):
                ss = re.findall('\d+', xx.group(3))[0]
                s = int(ss)
            real_time = h * 60 * 60 + m * 60 + s
        if (exec_type == 2):
            xx = re.findall(r'\d*', time_str)
            h, m, s = map(int, xx[::2])
            real_time = h * 60 * 60 + m * 60 + s
        return str(real_time)

    def crawl_call_log(self, **kwargs):
        """
        Crawl user's detail bill info
            1. Get Good IDs
            2. Get Detail Info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        # Get Good IDs
        pos_miss_list = []
        miss_list = []
        detail_bill_good_ename = "XFMX"
        message_list = []
        headers = {
            "Accept": "application/xml, text/xml, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://service.cq.10086.cn/myMobile/detailBill.html"
        }
        code, key, resp = self.post(ICS_SERVICE_URL, headers=headers, params=get_good_id_param(detail_bill_good_ename))
        if code != 0:
            return code, key, [], miss_list, pos_miss_list

        # Extract Good ID from XML
        if self.is_session_timeout(resp.text):
            return 9, "outdated_sid", [], miss_list, pos_miss_list

        level, key, message, result = get_good_id_from_xml(resp.text)
        if level != 0:
            self.log("crawler", "{}: {}".format(key, message), resp)
            return level, key, [], miss_list, pos_miss_list
        else:
            good_id = result

        # Get Detail Info
        current_time = datetime.datetime.now()
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://service.cq.10086.cn/myMobile/detailBill.html"
        }
        detail_bill_list = list()
        for month_offset in range(0, 6):
            year_month = (current_time - relativedelta(months=month_offset)).strftime('%Y%m')
            for i in range(self.max_retry):
                code, key, resp = self.post(ICS_SERVICE_URL, params=get_detail_bill_param(year_month, good_id), headers=headers)
                if code != 0:
                    message = "network_request_error"
                    continue
                # Extract Detail Info
                if self.is_session_timeout(resp.text):
                    key = "outdated_sid"
                    message = "会话超时"
                    continue

                level, key, message, result = get_detail_bill_from_xml(resp.text)
                # 无详单
                if "NO DATA" in message and key == "success":
                    self.log("crawler", "记录NO DATA信息", resp)
                    continue
                if key == 'expected_key_error' and message == u'用户的详单查询月份小于用户的开户月份':
                    break
                # 从xml中获取call_log失败
                if level != 0:
                    self.log("crawler", "记录call_log获取失败信息", resp)
                    continue
                # 从result中构造结果集
                try:
                    temp = []
                    call_from_set = set()
                    for record in result:
                        raw_call_from = record['c1']
                        call_from, error = self.formatarea(raw_call_from)
                        if not call_from:
                            call_from = raw_call_from
                            call_from_set.add(raw_call_from)
                            # self.log("crawler", "{} {}".format(error, call_from), "")
                        _tmp = {
                            "month": year_month,
                            "call_from": call_from,
                            "call_time": self.time_transform(record['c0']),
                            "call_to": "",
                            "call_tel": record['c3'],
                            "call_method": record['c2'],
                            "call_type": record['c5'],
                            "call_cost": record['c7'],
                            "call_duration": self.time_format(record['c4'], exec_type=1)}
                        temp.append(_tmp)
                    if call_from_set:
                        self.log("crawler", "call_from_set: {}".format(call_from_set), "")
                    detail_bill_list.extend(temp)
                    break
                except:
                    error = traceback.format_exc()
                    key, level, message = "unknown_error: "+error, 9, "转换时间单位失败%s" % error
                    continue
            else:
                if  message != "network_request_error":
                    self.log("crawler", "{}{}".format(key, message), resp)
                if "NO DATA" in message and key == 'success':
                    pos_miss_list.append(year_month)
                if level != 0 and "NO DATA" not in message:
                    message_list.append(key)
                    miss_list.append(year_month)
        if len(miss_list +pos_miss_list) == 6:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('outdated_sid') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', detail_bill_list, miss_list, pos_miss_list
            else:
                return 9, 'crawl_error', detail_bill_list, miss_list, pos_miss_list
        if not detail_bill_list:
            self.log("crawler", "获取数据为全空", "")
        return 0, "success", detail_bill_list, miss_list, pos_miss_list

    def crawl_phone_bill(self, **kwargs):
        miss_list = []
        phone_bill = list()
        message_list = []
        crawl_phone_bill_good_ename = 'WDZD'
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            crawl_phone_bill_data = {
                'service': 'ajaxDirect/1/myMobile/myMobile/javascript/',
                'pagename': 'myMobile',
                'eventname': 'getUserBill2',
                'cond_QUERY_DATE': searchMonth,
                'cond_GOODS_ID': get_good_id_param(crawl_phone_bill_good_ename)
            }
            # print get_good_id_param(crawl_phone_bill_good_ename)
            URL_PHONE_BILL = 'http://service.cq.10086.cn/ics'
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "Referer": "http://service.cq.10086.cn/myMobile/queryBill.html"
            }
            for i in range(self.max_retry):
                code, key, resp = self.post(URL_PHONE_BILL, data=crawl_phone_bill_data, headers=headers)
                if code != 0:
                    message = "network_request_error"
                    continue
                level, key, message, result = response_data.phone_bill_data(resp.text, searchMonth)
                # print result
                if level != 0:
                    continue
                if result:
                    phone_bill.append(result)
                    break
            else:
                if message != "network_request_error":
                    self.log("crawler", "{}: {}".format(key, message), resp)
                message_list.append(key)
                miss_list.append(searchMonth)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('outdated_sid') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', phone_bill, miss_list
            else:
                return 9, "crawl_error", phone_bill, miss_list
        return 0, 'success', phone_bill, miss_list

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)


if __name__ == '__main__':
    # from worker.crawler.main import *
    c = Crawler()

    USER_ID = "15826472370"
    USER_PASSWORD = "088616"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
