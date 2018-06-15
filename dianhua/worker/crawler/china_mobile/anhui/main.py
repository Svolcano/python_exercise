# -*- coding: utf-8 -*-
import datetime
import random
import re
import os
import execjs
import sys
import time
import traceback
from math import ceil
from lxml import etree
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, rrule

from tool import uifDecode
# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")
if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.spid = ""

    def get_login_verify_type(self, **kwargs):
        return 'Captcha'

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'captcha_verify']

    def send_login_verify_request(self, **kwargs):
        """
        Get validate image
        :param kwargs:
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # 新增对 spid 的变量化处理
        url = "https://ah.ac.10086.cn/login"
        headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Referer": "https://ah.ac.10086.cn/"
        }
        code, key, resp = self.post(url, headers=headers)
        if code != 0:
            return code, key, ''
        if u'IP地址访问网站受到限制' in resp.text:
            self.log("crawler", 'crawl_error', resp)
            return 9, "crawl_error", ""
        try:
            url = re.findall(r'replace\(\'(.*)\'\);', resp.text)[0]
        except:
            if "window.top.location" in resp.text:
                self.log("website", "website_busy_error", resp)
                return 9, "website_busy_error", ""
            error = traceback.format_exc()
            self.log("crawler", "html_error: 获取spid, 第一次请求解析失败{}".format(error), resp)
            return 9, 'html_error', ""
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://ah.ac.10086.cn/login"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ""
        try:
            et = etree.HTML(resp.text)
            spid_list = et.xpath("//*[@name='spid']/@value")
            self.spid = spid_list[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error: 获取spid, 第二次请求并解析失败 {}".format(error) , resp)
            return 9, "html_error", ""

        captcha_url = "https://ah.ac.10086.cn/common/image.jsp?l={}".format(random.random())
        code, key, resp = self.get(captcha_url)
        if code != 0:
            return code, key, ''
        try:
            list_b64_captcha = re.compile("imageCallBack\('.*,(.*)'\);").findall(resp.content)
            if len(list_b64_captcha) >= 1:
                b64_captcha = list_b64_captcha[0]
            else:
                if u'你操作图形码过于频繁,请稍后再试' in resp.text:
                    self.log("user",  "send_sms_too_quick_error", resp)
                    return 9, 'send_sms_too_quick_error', ""
                self.log("crawler", 'unknown_error', resp)
                return 9, 'unknown_error', ""
            return 0, 'success', b64_captcha
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, 'unknown_error', ""

    def enStr(self, pwd):
        js_path = "%s/enStr.js" % "/".join(os.path.abspath(__file__).split("/")[:-1])
        with open(js_path, 'r') as f:
            js_content = f.read()
            ctx = execjs.compile(js_content)
            new_pwd = ctx.call("enString", pwd)
            return new_pwd
        return ''

    def login(self, **kwargs):
        """
        Login process
            1. Check Validate Code
            2. Check ID/PW
            3. Request Login
            4. Request Set Uid Cookie
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        login_url = "https://ah.ac.10086.cn/Login"
        if self.spid == "":
            self.log("crawler", 'param_error: 获取spid失败', "")
            self.spid = "8a18cbc43f0dd7bd013f181c060f0001"
        try:
            login_data = {
                "type": "B",
                "formertype": "B",
                "backurl": "http://service.ah.10086.cn/LoginSso",
                "backurlflag": "https://ah.ac.10086.cn/4login/backPage.jsp",
                "errorurl": "https://ah.ac.10086.cn/4login/errorPage.jsp",
                "spid": self.spid,
                "RelayState": '',
                "login_type_ah": '',
                "mobileNum": kwargs['tel'],
                "login_pwd_type": "2",
                "loginBackurl": '',
                "loginType": "0",
                "timestamp": str(time.time() * 1000),
                "validCode": kwargs['captcha_code'],
                "servicePassword": "",
                "servicePassword": self.enStr(kwargs['pin_pwd']),
                "servicePassword_1": '',
                "smsValidCode": '',
                "smsValidCode": '',
                "validCode_state": True
            }
        except:
            error = traceback.format_exc()
            self.log("crawler", 'website_busy_error: {}'.format(error), "")
            return 9, "website_busy_error"

        code, key, resp = self.post(login_url, data=login_data)
        if code != 0:
            return code, key

        try:
            if re.search("location.replace\('(\S+)'\);</script>", resp.text):
                temp_url = re.search("location.replace\('(\S+)'\);</script>", resp.text).group(1)
                code, key = 0, ''
            elif u'code=2003' in resp.url:
                code, key = 2, 'verify_error'
            elif u'code=2009' in resp.url:
                code, key = 2, 'verify_error'
            elif u'code=2036' in resp.url:
                code, key = 1, 'pin_pwd_error'
            elif u'code=6000' in resp.url:
                code, key = 2, 'verify_error'
            elif u'%E7%B3%BB%E7%BB%9F%E6%AD%A3%E5%BF%99' in resp.text:
                # %E6%82%A8%E5%A5%BD%EF%BC%8C%E7%B3%BB%E7%BB%9F%E6%AD%A3%E5%BF%99%EF%BC%8C%E8%AF%B7%E7%A8%8D%E5%90%8E%E9%87%8D%E8%AF%95%E3%80%82
                # 您好，系统正忙，请稍后重试。
                # %E7%B3%BB%E7%BB%9F%E6%AD%A3%E5%BF%99
                # 系统正忙
                code, key = 9, 'website_busy_error'
            else:
                code, key = 9, 'login_param_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, 'unknown_error'

        if code != 0:
            if code == 9:
                self.log("crawler", key, resp)
            else:
                self.log("user", key, resp)
            return code, key

        code, key, resp = self.get(temp_url)
        if code != 0:
            return code, key
        try:
            if re.search('4login/backPage.jsp', resp.url):
                SAMLart = re.search("SAMLart=(.+?)&", resp.url).group(1)
            else:
                if u'当前的密码过于简单' in resp.text:
                    self.log('user', 'sample_pwd', resp)
                    return 1, 'sample_pwd'
                self.log("crawler", "login_param_error", resp)
                return 9, 'login_param_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, 'unknown_error'

        temp_data = {
                'SAMLart': SAMLart,
                'RelayState': '',
        }
        code, key, resp = self.post('http://service.ah.10086.cn/LoginSso', data=temp_data)
        if code != 0:
            return code, key
        try:
            if 'http://service.ah.10086.cn/index.html' in resp.text:
                return 0, 'success'
            else:
                self.log("crawler", "login_param_error", resp)
                return 9, 'login_param_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, 'unknown_error'

    def send_verify_request(self, **kwargs):
        """
        Send SMS verify code
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        send_verify_request_url = "http://service.ah.10086.cn/pub/sendSmPass"
        send_verify_request_data = {
                'opCode': 'EC20',
                'phone_No': '',
                '_': str(time.time()*1000)
        }
        code, key, resp = self.get(send_verify_request_url, params=send_verify_request_data)
        if code != 0:
            return code, key, ''
        try:
            sendsms_json_response = resp.json()
            if sendsms_json_response.get('result', '') == '0':
                return 0, 'success', ''
            elif sendsms_json_response.get('retCode', '') == '10110410005151003':
                self.log("crawler", "over_max_sms_error", resp)
                return 9, 'over_max_sms_error', ''
            else:
                self.log("crawler", "send_sms_error", resp)
                return 9, 'send_sms_error', ''
        except ValueError:
            error = traceback.format_exc()
            self.log('crawler', "json_error: "+error, resp)
            return 9, 'json_error', ''
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, 'unknown_error', ''

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        verify_url = "http://service.ah.10086.cn/pub/chkSmPass"
        verify_data = {
                'smPass': kwargs['sms_code'],
                'phone_No': '',
                '_': str(time.time()*1000)
        }
        code, key, resp = self.get(verify_url, params=verify_data)
        if code != 0:
            return code, key
        try:
            verify_json_response = resp.json()
            if verify_json_response.get('result', '') == '0':
                return 0, 'success'
            else:
                self.log("user", 'verify_error', resp)
                return 2, 'verify_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", "json_error: "+error, resp)
            return 9, 'json_error'

    def crawl_info(self, **kwargs):
        """
        Crawl user's personal info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        # Get Personal Info
        personal_info = {'full_name': '',
                         'id_card': '',
                         'is_realname_register': False,
                         'open_date': '',
                         'address': '',
                         }
        info_url = "http://service.ah.10086.cn/userInfo/qryUserinfo?_={}".format(time.time()*1000)
        code, key, resp = self.get(info_url)
        if code != 0:
            return code, key, personal_info
        try:
            info_json_response = resp.json()
            if info_json_response.get('result', '') == '0':
                status_flag, result = self.get_info(info_json_response)
                if status_flag:
                    return 0, 'success', result
                else:
                    self.log("crawler", "unknown_error: "+result, resp)
                    return 9, 'unknown_error', personal_info
            elif info_json_response.get('retCode', '') == '500013' or '未登录' in resp.text:
                return 9, 'website_busy_error', personal_info
            else:
                self.log("crawler", "unknown_error", resp)
                return 9, 'unknown_error', personal_info
        except ValueError:
            error = traceback.format_exc()
            self.log("crawler", 'json_error: '+error, resp)
            return 9, 'json_error', personal_info
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, 'unknown_error', personal_info

    def get_info(self, info_json_response):
        try:
            full_name = uifDecode(info_json_response.get('object', {}).get('cust_name', ''))
            id_card = ''
            is_realname_register = uifDecode(info_json_response.get('object', {}).get('user_appr_info', ''))
            open_date = uifDecode(info_json_response.get('object', {}).get('open_time', ''))
            address = ''
            return 1, {'full_name': full_name.encode('utf-8'),
                       'id_card': id_card,
                       'is_realname_register': str(u'已审核') == is_realname_register.encode('utf-8'),
                       'open_date': self.time_transform(open_date.encode('utf-8'), str_format="%Y-%m-%d"),
                       'address': address,
                       }
        except:
            error = traceback.format_exc()
            return 0, error

    def crawl_call_log(self, **kwargs):
        """
        Crawl user's detail bill info
            1. Get Current Month Detail Info
            2. Get Past Month Detail Info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        record_list = []
        today = datetime.date.today()
        pos_miss_list = []
        miss_list = []
        message_list = []
        # 暂时未做可能缺失
        for i in range(self.max_retry):
            level, key, message, result, response = self.request_per_month(today)
            if level != 0:
                continue
            else:
                record_list.extend(result)
                break
        else:
            self.log("crawler", key+message, response)
            now_month = datetime.datetime.now().strftime('%Y%m')
            message_list.append(key)
            miss_list.append(now_month)

        for previous_datetime in list(
            rrule(MONTHLY,
                  count=5,
                  bymonthday=-1,
                  dtstart=today + relativedelta(months=-5))):
            for i in range(self.max_retry):
                level, key, message, result, response = self.request_per_month(previous_datetime)
                if level != 0:
                    continue
                else:
                    record_list.extend(result)
                    break
            else:
                if message != "network_request_error":
                    self.log("crawler", key+message, response)
                now_month = '{}{}'.format(previous_datetime.year, '%02d' % previous_datetime.month)
                if level !=0 and message == 'no data':
                    pos_miss_list.append(now_month)
                elif level != 0:
                    message_list.append(key)
                    miss_list.append(now_month)
        if len(miss_list+pos_miss_list) == 6:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], miss_list, pos_miss_list
        return 0, 'success', record_list, miss_list, pos_miss_list

    def request_per_month(self, query_datetime, nowPage=1):
        data_list = []
        for now_type in range(1, 8):
            call_params = {
                'detailType': '20{}'.format(now_type),
                'startDate': '{0}{1}01'.format(query_datetime.year, str(query_datetime.month).zfill(2)),
                'endDate': '{0}{1}{2}'.format(query_datetime.year, str(query_datetime.month).zfill(2), str(query_datetime.day).zfill(2)),
                'nowPage': str(nowPage),
                'qryType': '',
                '_': str(time.time() * 1000),
            }
            call_url = "http://service.ah.10086.cn/qry/qryBillDetailPage"
            code, key, resp = self.get(call_url, params=call_params)
            year_month = "%d%02d" % (query_datetime.year, query_datetime.month)
            if code != 0:
                return code, key, "network_request_error", [], resp
            try:
                call_log_json = resp.json()
                total_page = int(ceil(int(call_log_json.get('object', {}).get('cdrVoice', {}).get('cdrVoiceTotal', '0')) / 50.0))
                # print total_page
            except:
                error = traceback.format_exc()
                return 9, 'json_error', "数据格式解析出错：%s" % error, [], resp
            if total_page > 0:
                level, key, message, result = self.get_call(call_log_json, year_month)
                if level != 0:
                    return level, key, message, result, resp
                data_list.extend(result)
            if nowPage == 1 and total_page > 1:
                for nowPage in range(2, total_page+1):
                    level, key, message, result, response = self.request_each_page(query_datetime, now_type, nowPage)
                    if level != 0:
                        return level, key, message, result, response
                    # 获取数据成功则将数据放到data_list中
                    # print now_type, year_month, len(result)
                    data_list.extend(result)
            # print now_type, year_month, len(data_list)
            # print data_list
        if not data_list:
            return 9, "success", "no data", [], resp
        return 0, "success", "", data_list, ''

    def request_each_page(self, query_datetime, now_type, nowPage):
        data = []
        call_params = {
            'detailType': '20{}'.format(now_type),
            'startDate': '{0}{1}01'.format(query_datetime.year, str(query_datetime.month).zfill(2)),
            'endDate': '{0}{1}{2}'.format(query_datetime.year, str(query_datetime.month).zfill(2), str(query_datetime.day).zfill(2)),
            'nowPage': str(nowPage),
            'qryType': '',
            '_': str(time.time() * 1000),
        }
        call_url = "http://service.ah.10086.cn/qry/qryBillDetailPage"
        for i in range(self.max_retry):
            code, key, resp = self.get(call_url, params=call_params)
            if code != 0:
                message = "network_request_error"
                continue
            try:
                call_log_json = resp.json()
            except:
                error = traceback.format_exc()
                message = u'json_error:{}'.format(error)
                continue
            year_month = "%d%02d" % (query_datetime.year, query_datetime.month)
            code, key, message, result = self.get_call(call_log_json, year_month)
            if code != 0:
                continue
            data.extend(result)
            return 0, "success", "请求成功", data, resp
        else:
            return code, key, message, [], resp

    def time_transform(self, time_str, str_format="%Y-%m-%d %H:%M:%S"):
        if str_format == "%Y-%m-%d":
            time_str += " 12:00:00"
        str_format = "%Y-%m-%d %H:%M:%S"
        time_type = time.strptime(time_str.encode('utf-8'), str_format)
        return str(int(time.mktime(time_type)))

    def time_format(self, time_str):
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
        return str(real_time)

    def get_call(self, call_log_json, year_month):
        call_log_list = list()
        # print year_month
        # print call_log_json
        try:
            result = int(call_log_json.get('result', 1))
            if result != 0:
                return 9, 'website_busy_error', "官网偶发异常{}".format(call_log_json), []
            step1 = call_log_json.get('object', {})
            if step1:
                step2 = step1.get('cdrVoice', {})
            else:
                return 9, "json_error", "step1获取并装载信息失败{}".format(call_log_json), []
            if step2:
                data_list = step2.get('cdrVoiceDetailList', [])
            else:
                return 9, "json_error", "step2获取并装载信息失败{}".format(call_log_json), []

            for call_log in data_list:
                record = {}
                callDate = call_log.get('callDate', '')
                record['call_time'] = self.time_transform(callDate)
                callTime = call_log.get('callTime', '')
                record['month'] = year_month
                record['call_duration'] = self.time_format(callTime.encode('utf-8'))
                record['call_type'] = call_log.get('callType', '')
                record['call_method'] = call_log.get('callModel', '')
                record['call_tel'] = call_log.get('callPhone', '')
                raw_call_from = call_log.get('callPlace', '')
                call_from, error = self.formatarea(raw_call_from)
                if not call_from:
                    call_from = raw_call_from
                    self.log("crawler", "{}{}".format(error, raw_call_from), "")
                record['call_from'] = call_from
                record['call_cost'] = call_log.get('callFee', '')
                record['call_to'] = ''
                call_log_list.append(record)
        except:
            error = traceback.format_exc()
            return 9, "unknown_error", "获取并装载信息失败{}{}".format(error, call_log_json), []
        return 0, "success", "成功", call_log_list

    def crawl_phone_bill(self, **kwargs):
        """
        bill_month      string  201612  账单月份
        bill_amount     string  10.00   账单总额
        bill_package    string  10.00   套餐及固定费
        bill_ext_calls  string  10.00   套餐外语音通信费
        bill_ext_data   string  10.00   套餐外上网费
        bill_ext_sms    string  10.00   套餐外短信费
        bill_zengzhifei string  10.00   增值业务费
        bill_daishoufei string  10.00   代收业务费
        bill_qita       string  10.00   其他费用
        """
        """
        http://service.ah.10086.cn/qry/qryMonthBillIndex?beginDate=201611&_=1493178412415
        """
        month_fee = []
        miss_list = []
        message_list= []
        today = datetime.date.today()
        month_bill_url = "http://service.ah.10086.cn/qry/qryMonthBillIndex"
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            # month_fee_data = {}
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            month_bill_data = {
                "beginDate": query_month,
                "_": str(int(time.time() * 1000))
            }
            for i in range(self.max_retry):
                code, key, resp = self.get(month_bill_url, params=month_bill_data)
                if code != 0:
                    msg = "network_request_error"
                    continue
                # print month_bill_req.text
                try:
                    month_bill_res = resp.json()
                    call_bill_list = month_bill_res.get('feeInfo', [])
                    month_fee_data = {}
                    month_fee_data['bill_month'] = query_month
                    if call_bill_list.get('sumFee', '') == "0.00":
                        msg = "no_data"
                        continue
                    month_fee_data['bill_amount'] = call_bill_list.get('sumFee', '')
                    month_fee_data['bill_package'] = call_bill_list.get('packageFee', '')
                    month_fee_data['bill_ext_calls'] = call_bill_list.get('voiceFee', '')
                    month_fee_data['bill_ext_data'] = call_bill_list.get('wlanFee', '')
                    month_fee_data['bill_ext_sms'] = call_bill_list.get('smsFee', '')
                    month_fee_data['bill_zengzhifei'] = call_bill_list.get('selfFee', '')
                    month_fee_data['bill_daishoufei'] = call_bill_list.get('spFee', '')
                    month_fee_data['bill_qita'] = call_bill_list.get('otherFee', '')
                    month_fee.append(month_fee_data)
                    break
                except:
                    error = traceback.format_exc()
                    msg = "json_error: " + error
                    continue
            else:
                if msg != "network_request_error":
                    self.log("crawler", msg, resp)
                miss_list.append(query_month)
                message_list.append(msg)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], miss_list
        return 0, "success", month_fee, miss_list


if __name__ == '__main__':

    c = Crawler()
    USER_ID = "18365169107"
    USER_PASSWORD = "135617"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
