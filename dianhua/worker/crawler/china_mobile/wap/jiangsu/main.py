# -*- coding:utf-8 -*-
import traceback
import execjs
import os
import re
import time
import random
import datetime
import json
from datetime import date
from dateutil.relativedelta import relativedelta

import sys
reload(sys)
sys.setdefaultencoding('utf8')


if __name__ == '__main__':
    sys.path.append('..')
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    sys.path.append('../../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


class Crawler(BaseCrawler):
    def __init__(self,**kwargs):
        super(Crawler,self).__init__(**kwargs)
        self.new_pin_pwd = ""
        self.today = datetime.date.today()

    def get_login_verify_type(self, **kwargs):
        return "SMS"

    def get_verify_type(self,**kwargs):
        return "SMS"

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def request_captcha(self):
        """
        url:http://wap.js.10086.cn/index.html
        :return:
        """
        code, key = "", ""
        for _ in range(self.max_retry):
            captcha_url = 'http://wap.js.10086.cn/imageVerifyCode.do'
            params = {
                't': random.random(),
                'imgReqSeq':'51fb5670c51943538061c03093619e5e3506'
            }
            code, key, resp = self.get(captcha_url, params= params)
            if code != 0:
                return code, key, ""

            #打码
            codetype = 1004
            key, result, self.cid = self._dama(resp.content, codetype)
            if key == "success" and result != "":
                captcha_code = str(result)
                return 0, "success", captcha_code
            else:
                self.log("website", "website_busy_error:打码失败{}".format(result), "")
                code, key = 9, "auto_captcha_code_error"
                continue
        else:
            return code, key, ""

    def enStr(self,pwd):
        js_path = '{}/RSA.js'.format(os.path.dirname(os.path.abspath(__file__)))
        with open(js_path,'r') as f:
            new_pin_pwd = execjs.compile(f.read()).call("RSA", pwd,"1234567890")
            return new_pin_pwd

    def send_login_verify_request(self, **kwargs):
        send_sms_url = 'http://wap.js.10086.cn/actionDispatcher.do'
        data = {
            'browserUA': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'busiNum': 'SMSLoginConfirm',
            'mobile': kwargs['tel'],
            'operNum': 'sendSMS',
            'reqUrl': 'SMSLoginConfirm',
            'ver': 't'
        }
        code, key, resp = self.post(send_sms_url, data=data)
        if code != 0:
            return code, key, ""
        if 'resultMsg":"系统流程处理正常' in resp.text:
            return 0, "success",""
        else:
            self.log("crawler", "登录短信发送未知错误", resp)
            return 9, "send_sms_error", ""

    def login_sms_verify(self, sms_code, tel):
        # 获取加密
        try:
            new_sms_code = self.enStr(sms_code)
        except:
            error = traceback.format_exc()
            self.log("crawler", "param_error sms_code:{} error:{}".format(sms_code, error), "")
            return 9, "website_busy_error", ""

        login_sms_url = 'http://wap.js.10086.cn/actionDispatcher.do'
        data = {
            'browserUA': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'busiNum':'SMSLoginConfirm',
            'mobile': tel,
            'operNum': 'confirmSMS',
            'password': self.new_pin_pwd,
            'reqUrl':'SMSLoginConfirm',
            'smsCode':  new_sms_code,
            'ver':'t',
        }
        code, key, resp = self.post(login_sms_url, data=data)
        if code != 0:
            return code, key, ""
        if 'resultMsg":"短信验证码输入错误,请重新输入' in resp.text:
            #短信5min内3次有效
            self.log("user", "短信验证码输入错误", resp)
            return 9, "verify_error", resp
        elif 'resultMsg":"对不起，登录失败，请稍后再试' in resp.text and 'errorCode":"-2232' in resp.text:
            self.log("user", "登录密码错误", resp)
            return 1, "pin_pwd_error", resp
        elif '"resultCode":"1"' in resp.text and 'continue":false' in resp.text:
            self.log("user", "login_param_error", resp)
            return 9, "login_param_error", resp
        elif 'resultMsg":"系统流程处理正常' in resp.text and 'resultCode":"0' in resp.text and 'continue":true' in resp.text and 'success":true' in resp.text:
            second_login_verify_url = 'http://wap.js.10086.cn/actionDispatcher.do'
            data = {
                'reqUrl':'indextopnewBarQuery',
                'ver':'t',
                'browserUA':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'
            }
            code, key, resp = self.post(second_login_verify_url, data = data)
            if code != 0:
                return code, key, ""
            if 'isLogin":true' in resp.text:
                return 0, "success", resp
            else:
                self.log("website", "未知原因登陆失败不排除官网异常", resp)
                return 9, "website_busy_error", resp
        else:
            self.log("crawler", "登录短信验证未知错误", resp)
            return 9, "unknown_error", resp

    def login(self,**kwargs):
        """
        :param kwargs:
        :return:
        """
        code, key, captcha_code = self.request_captcha()
        #获取加密
        try:
            self.new_pin_pwd = self.enStr(kwargs['pin_pwd'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "param_error pin_pwd:{} error:{}".format(kwargs['pin_pwd'], error), "")
            return 9, "website_busy_error"

        #登录
        login_url = 'http://wap.js.10086.cn/actionDispatcher.do'
        data = {
            'browserUA':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'busiNum':'login',
            'imgReqSeq':'51fb5670c51943538061c03093619e5e3506',
            'isSavePasswordVal':'1',
            'isSms':'0',
            'loginType':'0',
            'mobile':kwargs['tel'],
            'password':self.new_pin_pwd,
            'reqUrl':'loginTouch',
            'ver':'t',
            'verifyCode':captcha_code,
        }
        code, key, resp = self.post(login_url,data=data)
        if code != 0:
            return code, key
        try:
            json_resp = resp.json()
            resultMsg = json_resp.get('resultMsg')
            resultCode = json_resp.get('resultCode')
            errorCode = json_resp.get('errorCode')
        except:
            error = traceback.format_exc()
            self.log("crawler", "json_error:{}".format(error), resp)
            return 9, "json_error"
        if "您输入的验证码不正确" in resultMsg and resultCode == "1":
            self._dama_report(self.cid)
            self.log("uer", "图片验证码错误", resp)
            return 2, "verify_error"
        elif "登录失败，请稍后再试" in resultMsg and errorCode == "":
            self.log("user", "非移动号码", resp)
            return 1, "invalid_tel"
        elif "对不起，登录失败，请稍后再试" in resultMsg and "BSP10001" in errorCode:
            code, key, resp = self.login_sms_verify(kwargs['sms_code'], kwargs['tel'])
            if code == 0:
                return 0, "success"
            if key in ["verify_error", "pin_pwd_error"]:
                self.log("user", key, resp)
                return code, key
            else:
                self.log("crawler", key, resp)
                return code, key
        else:
            self.log("crawler", "未知错误", resp)
            return 9, "unknown_error"

    def send_verify_request(self,**kwargs):
        send_verify_url = 'http://wap.js.10086.cn/actionDispatcher.do'
        data = {
            'browserUA':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'busiNum':'QDCX',
            'reqUrl':'smsVerifyCode',
        }
        code, key, resp = self.post(send_verify_url,data=data)
        if code != 0:
            return code, key, ""
        if 'resultMsg":"系统流程处理正常' in resp.text:
            return 0, "success", ""
        else:
            return 9, "unknown_error", ""

    def verify(self,**kwargs):
        verify_url = 'http://wap.js.10086.cn/actionDispatcher.do'
        year_month = "{}{:0>2}".format(self.today.year, self.today.month)
        data = {
            'browserUA':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'busiNum':'QDCX',
            'confirm_smsPassword':kwargs['sms_code'],
            'confirmFlg':'1',
            'currentPage':'1',
            'password_str':'',
            'queryItem':'1',
            'queryMonth': year_month,
            'reqUrl':'billDetailTQry',
            'ver':'t',
        }
        code, key, resp = self.post(verify_url,data=data)
        if code != 0:
            return code, key
        if 'resultMsg":"系统忙，请稍候再试' in resp.text and 'c":"-200009' in resp.text:
            self.log("user", "短信验证码错误", resp)
            return 9, "verify_error"
        if 'resultMsg":"系统流程处理正常' in resp.text and 'continue":true' in resp.text:
            return 0, "success"
        else:
            self.log("crawler", "未知错误", resp)
            return 9, "unknown_error"

    def crawl_info(self,**kwargs):
        """
        WAP 没有个人信息
        """
        return 9, "unknown_error", {}

    def monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        monthly_period_list = []
        for month_offset in range(0, length):
            monthly_period_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return monthly_period_list

    def crawl_call_log(self,**kwargs):
        """
        获取详单历史
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        call_logs, miss_list, pos_miss_list = [], [], []
        message, response = '', ''
        error_num = 0
        log_for_retrys = []
        retrys_limit = 0
        full_time = 60.0
        st_time = time.time()
        time_fee = 0.0
        rand_time = random.randint(20,40)/10.0
        month_retry_list = [(x, self.max_retry) for x in self.monthly_period(6, strf='%Y%m')]
        while month_retry_list:
            every_month, retry = month_retry_list.pop(0)
            retry -= 1
            if retry < retrys_limit:
                self.log("crawler", "重试次数完毕", "")
                miss_list.append(every_month)
                continue
            log_for_retrys.append((every_month,retry,time_fee))
            #请求详单
            crawl_call_log_url = 'http://wap.js.10086.cn/actionDispatcher.do'
            data = {
                'browserUA':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
                'busiNum':'QDCX',
                'currentPage':'1',
                'password_str':'',
                'queryItem':'1',
                'queryMonth':every_month,
                'reqUrl':'billDetailTQry',
                'ver':'t',
            }
            code, key, resp = self.post(crawl_call_log_url, data=data)
            if code != 0:
                if retry >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((every_month, retry))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((every_month, retry))
                else:
                    self.log("crawler", "多次重试失败", "")
                    miss_list.append(every_month)
                continue
            code, key, msg, result = self.call_log_get(resp.text, every_month)
            if code == 0:
                if result:
                    call_logs.extend(result)
                else:
                    if retry >= 0:
                        time_fee = time.time() - st_time
                        month_retry_list.append((every_month, retry))
                    elif time_fee < full_time:
                        time.sleep(rand_time)
                        time_fee = time.time() - st_time
                        month_retry_list.append((every_month, retry))
                    else:
                        self.log("crawler", "详单或许缺失", resp)
                        pos_miss_list.append(every_month)
                continue
            else:
                message, response = key, resp
                if retry >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((every_month, retry))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((every_month, retry))
                else:
                    self.log("crawler", u"获取详单失败{}".format(key), resp)
                    miss_list.append(every_month)
        if message == "html_error":
            self.log("crawler", message, response)
            error_num += 1
        self.log("crawler", "重试记录：{}".format(log_for_retrys), "")
        self.log("crawler", "缺失: {}, 可能缺失: {}, 部分缺失: {}".format(miss_list, pos_miss_list, []), "")
        if len(pos_miss_list) + len(miss_list) == 6:
            if error_num > 0:
                return 9, "crawl_error", [], [], []
            else:
                return 9, "website_busy_error", [],[],[]
        return 0, "success", call_logs, miss_list, pos_miss_list

    def time_stamp(self, time_str):
        try:
            timeArray = time.strptime(time_str, "%Y/%m/%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            return True, str(timeStamp)
        except:
            error = traceback.format_exc()
            return False, error

    def split_time(self,time_str):
        line = time_str.split(":")
        seconds = int(line[0]) * 3600 + int(line[1]) * 60 + int(line[2])
        return seconds

    def call_log_get(self,resp,month):
        """
         `call_tel` | string | 18202541892 | 电话号码 |
        | `call_cost` | string | 0.00 | 通话费用 |
        | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
        | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
        | `call_type` | string | 本地 | 通话类型（本地, 长途） |
        | `call_from` | string | 北京市 | 本机通话地 |
        | `call_to` | string | 长沙市 | 对方归属地 |
        | `call_duration` | integer | 300 | 通话时长(秒),
        :param resp:
        :param month:
        :return:
        """
        call_log = []
        if 'continue":false' in resp:
            self.log("website", "website_busy_error:二次验证通过但未返回数据", resp)
            return 9, "website_busy_error", "", []
        try:
            dict = json.loads(resp)
            gsmBillDetailList = dict.get('resultObj').get('gsmBillDetailList')
            for every_dict in gsmBillDetailList:
                single_call_log = {}
                single_call_log['call_tel'] = every_dict.get('otherParty')
                single_call_log['call_method'] = every_dict.get('callType')
                call_from, error = self.formatarea(every_dict.get("visitArear"))
                if not call_from:
                    call_from = every_dict.get("visitArear")
                single_call_log['call_from'] = call_from
                call_time = every_dict.get("startTime").replace("-", "/")
                result, call_time = self.time_stamp(call_time)
                if not result:
                    self.log("crawler", "时间转换失败{}{}".format(call_time, resp), "")
                    return 9, 'html_error', 'html_error when transform call_time to time_stamp : %s' % call_time, []
                single_call_log['call_time'] = call_time
                single_call_log['call_cost'] = '%.2f' % (float(every_dict.get('chFee')))
                single_call_log['call_type'] = every_dict.get('roamType')
                single_call_log['call_duration'] = str(self.split_time(every_dict.get('callDuration')))
                single_call_log['call_to'] = ""
                single_call_log['month'] = month
                call_log.append(single_call_log)
        except:
            error = traceback.format_exc()
            return 9, 'html_error', 'html_error when parse call log : %s' % error, []
        return 0, 'success', '成功', call_log

    def crawl_phone_bill(self,**kwargs):
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
        :param kwargs:
        :return:
        """
        data_list, miss_list = [],[]
        today = date.today()
        error_num = 0
        message = ''
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            url = 'http://wap.js.10086.cn/actionDispatcher.do'
            data = {
                'beginDate':query_month,
                'browserUA':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
                'busiNum':'ZDCX',
                'reqUrl':'billBusinessQuery',
                'ver':'t',
            }
            for _ in range(self.max_retry):
                code, key, resp = self.post(url,data=data)
                if code != 0:
                    message = "network_request_error"
                    continue
                if 'resultMsg":"系统流程处理正常' not in resp.text and 'continue":true' not in resp.text:
                    message = 'no_data'
                    continue
                try:
                    dicts = json.loads(resp.text)
                    a = dicts.get('resultObj').get('billBean')
                    result_data = {}
                    set_key = set(['bill_month','bill_amount','bill_package','bill_ext_calls','bill_ext_data','bill_ext_sms','bill_zengzhifei','bill_daishoufei','bill_qita'])
                    result_data['bill_month'] = query_month
                    result_data['bill_amount'] ='%.2f' % (float(a.get('billRetDetail').get('totalFee'))/100)
                    lists = a.get('caky').get('cakys')
                    for every_list in lists:
                        if "套餐及固定费" in every_list.get('cakyName'):
                            result_data['bill_package'] = '%.2f' % (float(every_list.get('cakyFee'))/100)
                        if "短信、彩信费" in every_list.get('cakyName'):
                            result_data['bill_ext_sms'] = '%.2f' % (float(every_list.get('cakyFee'))/100)
                        if "语音通信费" in every_list.get('cakyName'):
                            result_data['bill_ext_calls'] = '%.2f' % (float(every_list.get('cakyFee'))/100)
                        if "上网费" in every_list.get('cakyName'):
                            result_data['bill_ext_data'] = '%.2f' % (float(every_list.get('cakyFee'))/100)
                        if "增值业务费" in every_list.get('cakyName'):
                            result_data['bill_zengzhifei'] = '%.2f' % (float(every_list.get('cakyFee'))/100)
                        if "代收费业务费" in every_list.get('cakyName'):
                            result_data['bill_daishoufei'] = '%.2f' % (float(every_list.get('cakyFee'))/100)
                    for extra_keys in list(set_key - set(result_data.keys())):
                        result_data[extra_keys] = "0.00"
                    data_list.append(result_data)
                    break
                except:
                    message = traceback.format_exc()
                    continue
            else:
                if message != "network_request_error":
                    self.log("crawler", "html_error:{}".format(message), "")
                    error_num += 1
                miss_list.append(query_month)
                break
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5 and error_num > 0:
            return 9, "crawl_error", [], miss_list
        return 0, "success", data_list, miss_list

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "15094393043"
    USER_PASSWORD = "340393"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
