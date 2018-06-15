# -*- coding: utf-8 -*-

import datetime
import time
import execjs
import json
import calendar
import ast
import re
import traceback
import os

from dateutil.relativedelta import relativedelta
from lxml import etree

import sys
import random
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.image_validate_count = 0

    def get_login_verify_type(self, **kwargs):
        return 'SMS'

    def get_verify_type(self, **kwargs):
        return ''

    def need_parameters(self, **kwargs):
        return ['pin_pwd']

    def send_login_verify_request(self, **kwargs):
        """
        Get validate image
        :param kwargs:
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # Go to Login Page
        start_url = "https://sh.ac.10086.cn/login"
        code, key, resp = self.get(start_url)
        if code != 0:
            return code, key, ''

        url = "https://sh.ac.10086.cn/loginjt?act=1&telno={}".format(kwargs["tel"])
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://sh.ac.10086.cn/login"
        }

        code, key, resp = self.post(url, headers=headers)
        if code != 0:
            return code, key, ''
        try:
            if u"<title>登录_上海移动官方网站</title>" in resp.text:
                for history in resp.history:
                    self.log("crawler", "上海移动, 请求短信异常跳转", history)

                self.log("website", "website_busy_error", resp)
                return 9, "website_busy_error", ''
            desc = resp.json()
            if u'无法为您所输入的手机号码发送动态密码，请核对后重新输入' in desc:
                self.log('user', 'invalid_tel', resp)
                return 1, "invalid_tel", ""

            if str(desc["result"]) == '0':
                return 0, "success", ""
            elif str(desc["result"]) == '1':
                if u"非移动用户请先注册互联网账号" in resp.text:
                    self.log("user", "login_param_error", resp)
                    return 1, "login_param_error", ""
                elif u"签名验证错误" in resp.text:
                    self.log('website', "website_busy_error", resp)
                    return 9, "website_busy_error", ""
                else:
                    self.log("crawler", "send_sms_error", resp)
                    return 9, "send_sms_error", ""
            else:
                self.log("crawler", "send_sms_error", resp)
                return 9, "send_sms_error", ""
        except:
            error = traceback.format_exc()
            self.log('crawler', 'json_error:{}'.format(error), resp)
            return 9, "json_error", ""

    def emp_str(self, unemp_str):
        js_path = "%s/run.js" % "/".join(os.path.abspath(__file__).split("/")[:-1])
        with open(js_path, 'r') as f:
            source = f.read()
        return execjs.compile(source).call('enString', unemp_str)

    def login(self, **kwargs):
        code, key, message, resp = self.get_login(**kwargs)

        if code != 0:
            if key in ['verify_error', 'pin_pwd_error']:
                self.log('user', message, resp)
            elif key == 'website_busy_error':
                self.log('website', 'website_busy_error', resp)
            else:
                self.log('crawler', message, resp)
        return code, key

    # 函数封装方便记录日志
    def get_login(self, **kwargs):
        """
        Login process
            1. Check Validate Code
            2. Check ID/PW
            3. Request Login
            4. Request Set Uid Cookie
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """

        try:
            data = {
                "telno": self.emp_str(kwargs["tel"]),
                "source": "wsyyt",
                "password": self.emp_str(kwargs["pin_pwd"]),
                # 对动态短信加密
                "dtm": self.emp_str(kwargs["sms_code"]),
                "decode": 1,
                "ctype": 1,
                "authLevel": 5
            }

        except:
            error = traceback.format_exc()
            return 9, 'website_busy_error', 'website_busy_error:{}'.format(error), ''

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://sh.ac.10086.cn/login"
        }
        url = "https://sh.ac.10086.cn/loginjt?act=2"

        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key, '', resp
        if u"<title>登录_上海移动官方网站</title>" in resp.text:
            self.log("website", "website_busy_error", resp)
            return 9, "website_busy_error", '', resp
        try:
            msg = resp.json()
            if msg["message"] != u"成功":
                if u"短信随机码不正确" in msg["message"]:
                    return 9, "verify_error", u"verify_error：短信随机码不正确或已过期，请重新获取", resp
                if u"账户名与密码不匹配" in msg["message"]:
                    return 9, "pin_pwd_error", u"pin_pwd_error：您的账户名与密码不匹配，请重新输入", resp
                if u'系统繁忙' in msg["message"]:
                    return 9, "website_busy_error", u"官网繁忙", resp
                if u'登录_上海移动官方网站' in resp.text:
                    return 9, "website_busy_error", u"偶发需要重新登录", resp
                if u'签名验证错误' in resp.text:
                    return 9, 'website_busy_error', u'偶发异常, 签名验证错误', resp
                if u'统一认证连接异常' in resp.text or u'统一认证中心自定义异常' in resp.text or u'门户统一认证接口调用失败' in resp.text:
                    return 9, 'website_busy_error', u'统一认证连接异常', resp
                if u'账号已锁定' in resp.text:
                    return 9, 'over_query_limit', u'账号已锁定', resp
                if u'手机号码不正确' in msg["message"]:
                    return 9, 'invalid_tel', u'手机号错误', resp
                return 9, 'unknown_error', u"unknown_error：动态码验证失败", resp
        except:
            error = traceback.format_exc()
            return 9, "json_error", "json_error:{}".format(error), resp

        back_url = "http://www.sh.10086.cn/sh/wsyyt/ac/jtforward.jsp?source=wysso&uid={}&tourl=http%3A%2F%2Fwww.sh.10086.cn%2Fsh%2Fservice%2F".format(
            msg["uid"])
        try:
            url = "https://login.10086.cn/AddUID.action?"
            data = {
                "channelID": "00210",
                "Artifact": msg["artifact"],
                "TransactionID": msg["transactionID"],
                "backUrl": back_url
            }
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "https://sh.ac.10086.cn/login"
            }

            code, key, resp = self.get(url, params=data, headers=headers)
            if code != 0:
                return code, key, '', resp
            url = "http://www.sh.10086.cn/sh/wsyyt/action?act=index.get_user"
            code, key, resp = self.post(url)
            if code != 0:
                return code, key, '', resp
        except:
            error = traceback.format_exc()
            return 9, "unknown_error", "unknown_error{}".format(error), resp
        return 0, 'success', "", resp

    def send_verify_request(self, **kwargs):
        # Trigger Second Validation(Send SMS Validate Code to Cellphone)
        # return 0, 'success', ''
        pass

    def verify(self, **kwargs):
        # return 0, 'success'
        pass

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        if str_format == "Ymd":
            ymd = re.findall(r'(\d{2,4})', time_str.encode(bm))
            time_str = reduce(lambda x, y: x + "-" + y, ymd) + " 12:00:00"
        else:
            today_month = datetime.date.today().month
            today_year = datetime.date.today().year
            str_month = int(time_str[:2])
            if str_month > today_month:
                str_year = today_year - 1
            else:
                str_year = today_year
            time_str = str(str_year) + "-" + time_str
        str_format = "%Y-%m-%d %H:%M:%S"
        time_type = time.strptime(time_str.encode(bm), str_format)

        return str(int(time.mktime(time_type)))

    def time_format(self, time_str, **kwargs):
        exec_type = 1
        time_str = time_str.encode('utf-8')

        if 'exec_type' in kwargs:
            exec_type = kwargs['exec_type']
        if (exec_type == 1):
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

    def crawl_info(self, **kwargs):
        """
        Crawl user's personal info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        try:
            url = "http://www.sh.10086.cn/sh/wsyyt/action?act=myarea.getinfoManageMore"
            code, key, resp = self.get(url)
            if code != 0:
                return code, key, {}
            try:
                personal_info_result = json.loads(resp.text)
            except:
                error = traceback.format_exc()
                self.log('crawler', 'json_error：{}'.format(error), resp)
                return 9, 'json_error', {}
            if personal_info_result['error']['code'] != 0:
                if personal_info_result['error']['code'] == -1:
                    self.log('crawler', 'outdated_sid', resp)
                    return 9, 'outdated_sid', {}
                self.log('crawler', 'request_error', resp)
                return 9, 'request_error', {}
            realname_register = personal_info_result['value']['identInfo']
            if realname_register:
                realname_register = True
            else:
                realname_register = False
            personal_info_dict = {'full_name': personal_info_result['value']['name'],
                                  'id_card': personal_info_result['value']['zjNum'],
                                  'is_realname_register': realname_register,
                                  'open_date': self.time_transform(personal_info_result['value']['creaateDate'],
                                                                   str_format="Ymd"),
                                  'address': ''}
            return 0, 'success', personal_info_dict
        except:
            error = traceback.format_exc()
            self.log('crawler', 'unknown_error:{}'.format(error), resp)
            return 9, 'unknown_error', {}

    def extract_current_detail_bill_from_javascript(self, js_string, month):
        """
        Get detail bill from target javascript string
        :param js_string: Response returned from get current/past month detail bill
        :return:
            status_key: str, The key of status code
            code: int, Error code
            message: unicode, Error Message
            detail_bill_list: list, The list of detail bill info
        """
        if js_string == "":
            return 9, 'html_error', "html_error", []

        result_value = js_string.split("$$")[0]
        # print type(result_value)
        # print result_value

        if result_value != "0":
            if result_value == '1':
                return 0, 'success', u"暂无此详单类型的记录", []
            elif result_value == '2':
                return 9, 'request_error', u"request_error:对不起，您输入的时间非法", []
            elif result_value == '10000':
                return 9, "website_busy_error", u"官网异常(由于长时间未操作，为了您的账户安全，请重新登录)", []
            else:
                return 9, 'html_error', "html_error", []

        try:
            try:
                fetch_value_re = re.search(r';value.*?=.*?(\[.*?\]);', js_string, re.S)
                if fetch_value_re:
                    value_body = fetch_value_re.group(1)
                    detail_bill_list = ast.literal_eval(value_body)
                else:
                    return 9, "website_busy_error", "website_busy_error", []
            except Exception:
                # 当月详单与历史详单解析不同。
                fetch_value_re = re.search(r';value.*?=.*?(\[.*?\])\";', js_string, re.S)
                if fetch_value_re:
                    value_body = fetch_value_re.group(1)
                    detail_bill_list = ast.literal_eval(value_body)
                else:
                    return 9, "website_busy_error", "website_busy_error", []

            formal_detail_bill_list = list()
            for detail_bill in detail_bill_list:
                raw_call_from = detail_bill[2].decode('utf-8')
                call_from, error = self.formatarea(raw_call_from)
                if not call_from:
                    call_from = raw_call_from
                _tmp = {"call_from": call_from,
                        "call_time": self.time_transform(detail_bill[1].decode('utf-8')),
                        "call_to": "", "call_tel": detail_bill[4].decode('utf-8'),
                        "call_method": detail_bill[3].decode('utf-8'), "call_type": detail_bill[6].decode('utf-8'),
                        "call_cost": detail_bill[8].decode('utf-8'),
                        "month": month,
                        "call_duration": self.time_format(detail_bill[5].decode('utf-8'), exec_type=2)}

                formal_detail_bill_list.append(_tmp)
            return 0, 'success', '', list(reversed(formal_detail_bill_list))
        except:
            error = traceback.format_exc()
            return 9, "unknown_error", 'unknown_error:{}'.format(error), []

    def crawl_call_log(self, **kwargs):
        """
        Crawl user's detail bill info
            1. Get Current Month Detail Info
            2. Get Past Month Detail Info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        missing_list = []
        possibly_missing_list = []
        detail_info_list = list()
        err_dict = {'crawl_error': 0, 'website_busy_error': 0}
        # Get Current Month Detail Info
        current_time = datetime.datetime.now()
        month_offset_retrys = [(x, self.max_retry) for x in range(0, 6)]
        log_for_retry_requests = []
        full_time = 60.0
        time_fee = 0
        st_time = time.time()
        et_time = st_time + full_time
        max_retry_stop_time = 0
        more_retry = 3
        while month_offset_retrys:
            local_st = time.time()
            month_offset, retry_time = month_offset_retrys.pop(0)
            retry_time -= 1

            year_month = (current_time - relativedelta(months=month_offset))
            day_count = calendar.monthrange(year_month.year, year_month.month)[1]
            start_date = "%s-01" % year_month.strftime('%Y-%m')
            end_date = "%s-%s" % (year_month.strftime('%Y-%m'), day_count)

            if retry_time < -more_retry:
                missing_list.append(year_month.strftime("%Y%m"))
                self.log("crawler", "{} 重试仍缺失".format(year_month.strftime("%Y%m")), "")
                continue

            log_for_retry_requests.append((year_month.strftime("%Y%m"), retry_time, time_fee))

            if not month_offset:
                # 当月详单
                url = "http://www.sh.10086.cn/sh/wsyyt/busi/historySearch.do?method=getOneBillDetailAjax"
                data = {
                    "startDate": start_date,
                    "searchStr": "-1",
                    "r": time.time(),
                    "isCardNo": 0,
                    "index": 0,
                    "gprsType": "",
                    "endDate": end_date,
                    "billType": "NEW_GSM",
                    "jingque": "",
                }
            else:
                # 历史详单
                url = "http://www.sh.10086.cn/sh/wsyyt/busi/historySearch.do?method=getFiveBillDetailAjax"
                data = {
                    "startDate": start_date,
                    "searchStr": "-1",
                    "r": time.time(),
                    "isCardNo": 0,
                    "index": 0,
                    "gprsType": "",
                    "filterValue": "",
                    "filterfield": "输入对方号码：",
                    "endDate": end_date,
                    "billType": "NEW_GSM"
                }

            missing_month = year_month.strftime('%Y%m')
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "*/*",
                "Referer": "http://www.sh.10086.cn/sh/wsyyt/busi/2002_14.jsp"
            }
            try:
                code, key, resp = self.post(url, data=data, headers=headers)
                message = "network_request_error"
                if code == 0:
                    if u'您已经申请了”关闭详单查询“的功能' in resp.text:
                        self.log('user', 'user_prohibited_error', resp)
                        return 9, 'user_prohibited_error', [], [], []
                    if u'暂时不能查询详单' in resp.text:
                        self.log('website', 'websiter_prohibited_error', resp)
                        return 9, 'websiter_prohibited_error', [], [], []
                    if u'未进行实名制登记' in resp.text:
                        self.log('user', 'real_name_registration_error', resp)
                        return 9, 'real_name_registration_error', [], [], []
                    code, key, message, result = self.extract_current_detail_bill_from_javascript(resp.text, missing_month)
                    if code == 0:
                        if result:
                            detail_info_list += result
                            continue
                        # 两次为空则添加到缺失列表
                        # else:
                        #     if page_retry == 0 and missing_month not in possibly_missing_list:
                        #         self.log('crawler', '没有详单记录', resp)
                        #         possibly_missing_list.append(missing_month)
                        #         break
                if retry_time >= 0:
                    local_fee = time.time() - local_st
                    time_fee += local_fee
                    month_offset_retrys.append((month_offset, retry_time))
                    max_retry_stop_time = time.time()
                elif time_fee < full_time:
                    free_time = et_time - max_retry_stop_time
                    len_month_offset_retrys = len(month_offset_retrys) or 1
                    rand_time = ((free_time / more_retry) / len_month_offset_retrys) - 0.3
                    if rand_time < 1:
                        rand_time = random.randint(11, 28) / 10.0
                    time.sleep(rand_time)
                    local_fee = time.time() - local_st
                    time_fee += local_fee
                    month_offset_retrys.append((month_offset, retry_time))
                else:
                    if code == 0 and not result:
                        self.log("crawler", "没有详单记录", resp)
                        possibly_missing_list.append(missing_month)
                        continue
                    elif key == 'website_busy_error':
                        self.log('website', 'website_busy_error', resp)
                        err_dict['website_busy_error'] += 1
                    elif message != "network_request_error":
                        self.log('crawler', message, resp)
                        err_dict['crawl_error'] += 1
                    if missing_month not in missing_list:
                        missing_list.append(missing_month)

            except:
                error = traceback.format_exc()
                self.log('crawler', 'unknown_error:'.format(error), '')
                err_dict['crawl_error'] += 1
                if missing_month not in missing_list:
                    missing_list.append(missing_month)
        missing_list.sort(reverse=True)
        possibly_missing_list.sort(reverse=True)
        self.log("crawler", "记录重试请求情况{}".format(log_for_retry_requests), "")
        if len(missing_list + possibly_missing_list) == 6:
            if err_dict['crawl_error'] > 0:
                return 9, 'crawl_error', [], missing_list, possibly_missing_list
            return 9, 'website_busy_error', [], missing_list, possibly_missing_list

        return 0, "success", detail_info_list, missing_list, possibly_missing_list

    # 解析当前月份的账单
    def get_phone_bill(self, get_his_req, bill_month):
        """
        bill_month	    string	201612	账单月份
        bill_amount     string	10.00	账单总额
        bill_package	string	10.00	套餐及固定费
        bill_ext_calls	string	10.00	套餐外语音通信费
        bill_ext_data	string	10.00	套餐外上网费
        bill_ext_sms	string	10.00	套餐外短信费
        bill_zengzhifei	string	10.00	增值业务费
        bill_daishoufei	string	10.00	代收业务费
        bill_qita       string	10.00	其他费用
        #self.session.headers()
        """

        bill_month = bill_month
        bill_amount = re.findall(r"<b>费用合计：(.*?)</b></div>", get_his_req)
        bill_package = re.findall(r"套餐及固定费</p></span></td> <td style='text-align:left;padding-left:40px;'>(.*?)</td>",
                                  get_his_req)
        bill_ext_calls = re.findall(
            r">套餐外语音通信费</p></span></td> <td style='text-align:left;padding-left:40px;'>(.*?)</td>", get_his_req)
        bill_ext_data = re.findall(r"套餐外上网费</p></span></td> <td style='text-align:left;padding-left:40px;'>(.*?)</td>",
                                   get_his_req)
        bill_ext_sms = re.findall(r"套餐外短彩信费</p></span></td> <td style='text-align:left;padding-left:40px;'>(.*?)</td>",
                                  get_his_req)
        bill_zengzhifei = re.findall(r"增值业务费</p></span></td> <td style='text-align:left;padding-left:40px;'>(.*?)</td>",
                                     get_his_req)
        bill_daishoufei = re.findall(
            r"代收费业务费用</p></span></td> <td style='text-align:left;padding-left:40px;'>(.*?)</td>", get_his_req)
        bill_qita = re.findall(r"其他费用</p></span></td> <td style='text-align:left;padding-left:40px;'>(.*?)</td>",
                               get_his_req)

        bill_dict = {
            "bill_month": bill_month,
            "bill_amount": bill_amount[0] if bill_amount else '',
            "bill_package": bill_package[0] if bill_package else '',
            "bill_ext_calls": bill_ext_calls[0] if bill_ext_calls else '',
            "bill_ext_data": bill_ext_data[0] if bill_ext_data else '',
            "bill_ext_sms": bill_ext_sms[0] if bill_ext_sms else '',
            "bill_zengzhifei": bill_zengzhifei[0] if bill_zengzhifei else '',
            "bill_daishoufei": bill_daishoufei[0] if bill_daishoufei else '',
            "bill_qita": bill_qita[0] if bill_qita else '',
        }
        return bill_dict

    def crawl_phone_bill(self, **kwargs):
        """
        bill_month	    string	201612	账单月份
        bill_amount     string	10.00	账单总额
        bill_package	string	10.00	套餐及固定费
        bill_ext_calls	string	10.00	套餐外语音通信费
        bill_ext_data	string	10.00	套餐外上网费
        bill_ext_sms	string	10.00	套餐外短信费
        bill_zengzhifei	string	10.00	增值业务费
        bill_daishoufei	string	10.00	代收业务费
        bill_qita       string	10.00	其他费用
        #self.session.headers()
        """
        month_fee = []
        missing_list = []
        today_month = datetime.date.today().month
        today_year = datetime.date.today().year
        crawl_error_num = 0
        # 历史账单
        get_his_bill = "http://www.sh.10086.cn/sh/wsyyt/busi/historySearch.do?method=FiveBillAllNewAjax"
        # 当月账单
        get_his_bill_new = "http://www.sh.10086.cn/sh/wsyyt/busi/historySearch.do?method=getFiveBillAllNewBillDetail"
        # 先前计算六个月,同时计算年份
        for n in range(0, 6):
            if (today_month - n) > 0:
                mon = (today_month - n)
                yea = today_year
            else:
                mon = 12 + (today_month - n)
                yea = today_year - 1
            # 历史账单参数
            his_data = {
                "dateTime": str(yea) + "年" + str(mon).rjust(2, '0') + "月",
                "tab": "tab" + str(n) + "_15",
                "isPriceTaxSeparate": "null",
                "showType": "0",
                "r": time.time() * 100
            }
            # 当月账单参数
            new_data = {
                "r": time.time() * 100
            }
            try:
                missing_month = str(yea) + str(mon).rjust(2, '0')
                headers = {
                    "Referer": "http://www.sh.10086.cn/sh/wsyyt/busi/2002_15.jsp",
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "*/*",
                }
                for item in xrange(self.max_retry):
                    if not n:
                        # 当月账单
                        url = get_his_bill_new
                        data = new_data
                    else:
                        # 历史账单
                        url = get_his_bill
                        data = his_data
                    code, key, resp = self.post(url, data=data, headers=headers)
                    if code == 0:
                        break
                else:
                    # self.log('crawler', 'request_error', resp)
                    if missing_month not in missing_list:
                        missing_list.append(missing_month)
                    continue
            except:
                error = traceback.format_exc()
                # print "网页获取失败"
                self.log('crawler', 'unknown_error:{}'.format(error), resp)
                crawl_error_num += 1
                if missing_month not in missing_list:
                    missing_list.append(missing_month)
                continue
            try:
                # 历史账单
                jstext = resp.json()
            except:
                # 解析当月账单
                try:
                    bill_month = str(yea) + str(mon).rjust(2, '0')
                    bill_dict = self.get_phone_bill(resp.text.encode('utf-8'), bill_month)
                    month_fee.append(bill_dict)
                    continue
                except:
                    error = traceback.format_exc()
                    self.log('crawler', 'html_error：{}'.format(error), resp)
                    crawl_error_num += 1
                    if missing_month not in missing_list:
                        missing_list.append(missing_month)
                    continue
            try:
                if jstext['result'] != '1':
                    text = jstext['message']
                    et = etree.HTML(text, parser=etree.HTMLParser(encoding='utf-8'))
                    p = et.xpath("//table[@class='cost_detail']/tr/td[2]")
                    all_fee = et.xpath("//table[@class='fy_information_ul']/tbody/tr[1]/td[2]/strong")
                    gr = re.match(r'.*?(\d*\.\d{2})', all_fee[0].text)
                    all_fee_num = gr.group(1)
                    bill_month = str(yea) + str(mon).rjust(2, '0')
                    bill_amount = all_fee_num
                    bill_package = p[0].text[1:]
                    bill_ext_calls = p[5].text[1:]
                    bill_ext_data = p[1].text[1:]
                    bill_ext_sms = p[6].text[1:]
                    bill_zengzhifei = p[2].text[1:]
                    bill_daishoufei = p[7].text[1:]
                    bill_qita = p[3].text[1:]

                    bill_dict = {
                        "bill_month": bill_month,
                        "bill_amount": bill_amount,
                        "bill_package": bill_package,
                        "bill_ext_calls": bill_ext_calls,
                        "bill_ext_data": bill_ext_data,
                        "bill_ext_sms": bill_ext_sms,
                        "bill_zengzhifei": bill_zengzhifei,
                        "bill_daishoufei": bill_daishoufei,
                        "bill_qita": bill_qita,
                    }
                else:
                    # print "当月无账单"
                    bill_dict = {}
                    if missing_month not in missing_list:
                        missing_list.append(missing_month)
                        self.log('crawler', '没有账单记录', resp)
                    continue
            except:
                error = traceback.format_exc()
                # print "xpath 解析失败"
                self.log('crawler', 'xml_error:{}'.format(error), resp)
                crawl_error_num += 1
                if missing_month not in missing_list:
                    missing_list.append(missing_month)
                continue
                # return "xml_error", 9, "xml error%s" % error, []
            month_fee.append(bill_dict)

        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in missing_list and missing_list.remove(now_month)
        if len(missing_list) == 5:
            if crawl_error_num > 0:
                return 9, 'crawl_error', [], missing_list
            return 9, 'website_busy_error', [], missing_list
        return 0, "success", month_fee, missing_list


if __name__ == '__main__':
    # from worker.crawler.main import *
    c = Crawler()
    USER_ID = "15901735976"
    USER_PASSWORD = "203974"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # a = c.emp_str(USER_ID)
    # b = c.emp_str(USER_PASSWORD)
    #
    # print(a, b)
    """
    # unit test
    pprint(c.send_login_verify_request())

    validate_code = ""
    pprint(c.login(tel=USER_ID, pin_pwd=USER_PASSWORD, captcha_code=validate_code))

    pprint(c.send_verify_request(tel=USER_ID))

    validate_code = ""
    pprint(c.verify(tel=USER_ID, sms_code=validate_code))

    pprint(c.crawl_info())
    pprint(c.crawl_call_log())
    """
