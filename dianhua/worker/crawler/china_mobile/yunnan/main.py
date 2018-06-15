# -*- coding: utf-8 -*-
import json
import random
import traceback
import execjs
import sys
import os
import time
import datetime
import re
from dateutil.rrule import MONTHLY, rrule
from dateutil.parser import *
from dateutil.relativedelta import relativedelta

reload(sys)
sys.setdefaultencoding('utf8')


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
        self.rsa_m = ""
        self.rsa_e = ""
        self.cid = ""
        self.today = datetime.date.today()

    def get_login_verify_type(self, **kwargs):
        return ""

    def get_verify_type(self, **kwargs):
        return "SMS"

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def send_login_verify_request(self, **kwargs):
        #加密参数e&m
        rsa_parms_url = 'http://www.yn.10086.cn/service/actionDispatcher.do'
        data = {
            'reqUrl':'login',
            'busiNum':'LOGIN',
            'funNum':'getPublicKey',
        }
        code, key, resp = self.post(rsa_parms_url, data=data)
        if code != 0:
            return code, key, ""
        try:
            resp_json = resp.json()
            self.rsa_e = resp_json['resultObj']['e']
            self.rsa_m = resp_json['resultObj']['m']
        except:
            error =traceback.format_exc()
            self.log("crawler", "json_error:{}".format(error), resp)
            return 9, "json_error", ""

        for _ in range(self.max_retry):
            #获取captcha
            captcha_url = 'http://www.yn.10086.cn/service/imageVerifyCode?t=new'
            code, key, resp = self.get(captcha_url)
            if code != 0:
                return code, key, ""
            #打码
            codetype = 1004
            key, result, self.cid = self._dama(resp.content, codetype)
            if key == "success" and result != "":
                captcha_code = str(result)
                return 0, "success", captcha_code
            else:
                self.log("website", "website_busy_error: 打码失败{}".format(result), "")
                code, key = 9, "auto_captcha_code_error"
                continue
        else:
            return code, key, ""

    def enStr(self, pwd, e, m):
        js_path = '{}/RSA.js'.format(os.path.dirname(os.path.abspath(__file__)))
        with open(js_path, 'r') as f:
            new_pwd = execjs.compile(f.read()).call("RSA", pwd, e, m)
            return new_pwd

    def login(self, **kwargs):
        code, key, captcha_code = self.send_login_verify_request()
        #登录
        login_url = 'http://www.yn.10086.cn/service/actionDispatcher.do'
        try:
            mobile = self.enStr(kwargs['tel'], self.rsa_e, self.rsa_m)
            password = self.enStr(kwargs['pin_pwd'], self.rsa_e, self.rsa_m)
        except:
            error = traceback.format_exc()
            self.log("crawler", "param_error:{} tel:{} pin_pwd:{}".format(error, kwargs['tel'], kwargs['pin_pwd']), "")
            return 9, "website_busy_error"
        data = {
            "reqUrl": "login",
            "busiNum":"LOGIN",
            "operType":	"0",
            "mobile": mobile,
            "password": password,
            "verifyCode": captcha_code,
            "isSavePasswordVal": "0",
            "passwordType":	"1"
        }
        code, key, resp = self.post(login_url, data=data)
        if code != 0:
            return code, key
        try:
            resp_json = resp.json()
            resultMsg = resp_json.get('resultMsg')
        except:
            error = traceback.format_exc()
            self.log("crawler", "json_error:{}".format(error), "")
            return 9, "json_error"

        if "图片验证码输入错误" in resultMsg:  # logicCode = -4003
            self._dama_report(self.cid)
            self.log("user", "图片验证码错误", resp)
            return 9, "verify_error"
        elif "非本省手机号登录" in resultMsg:  # logicCode = -4002
            self.log("user", "非本省移动手机号登录", resp)
            return 9, "invalid_tel"
        elif "账户名与密码不匹配" in resultMsg:  # loginCode = -4002
            self.log("user", "账户名与密码不匹配", resp)
            return 9, "pin_pwd_error"
        elif "将被锁定" in resultMsg:
            self.log("user", "密码输入超过次数将被锁定", resp)
            return 9, "send_sms_too_quick_error"
        elif "密码输入超过次数账号已锁定" in resultMsg :
            self.log("user", "密码输入超过次数账号已锁定", resp)
            return 9, "account_locked"
        elif "userProductName" in resp.text and kwargs['tel'] in resp.text:
            return 0, "success"
        else:
            self.log("crawler", "未知错误", resp)   
            return 9, "unknown_error"

    def send_verify_request(self, **kwargs):
        get_cookies = 'http://www.yn.10086.cn/service/my/QDCX.html'
        code, key, resp = self.get(get_cookies)
        if code != 0:
            return code, key, ""
        #请求验证短信
        send_sms_url = 'http://www.yn.10086.cn/service/my/sms.do'
        data = {
            'busiNum': 'QDCX'
        }
        code, key, resp = self.post(send_sms_url, data= data)
        if code != 0:
            return code, key, ""
        if '"resultCode":"0"' and '"logicCode":"success"' in resp.text:
            return 0, "success", ""
        else:
            self.log("crawler", "二测验证短信发送失败", resp)
            return 9, "request_error", ""

    def verify(self, **kwargs):
        verify_url = 'http://www.yn.10086.cn/service/my/actionDispatcher.do'
        # year_month = "{}{:0>2}".format(self.today.year, self.today.month)
        month_list = list(
            rrule(MONTHLY,
                  count=1,
                  bymonthday=-1,
                  dtstart=self.today + relativedelta(months=-2)))
        i = month_list[0]
        data = {
            'reqUrl': 'QDCXQuery',
            'busiNum': 'QDCX',
            'queryMonth': '{}{:0>2}'.format(i.year, i.month),
            'queryItem': '1',
            'startDate': "{}-{:0>2}-01".format(i.year, i.month),
            'endDate': "{}-{:0>2}-{:0>2}".format(i.year, i.month, i.day),
            'operType': '3',
            'smsNum': kwargs['sms_code'],
            'confirmFlg':'1',
        }
        headers = {
            'Referer': 'http://www.yn.10086.cn/service/my/QDCX.html?t={}'.format(int(time.time()*1000)),
            'Host': 'www.yn.10086.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Tingyun-Id': 'p35OnrDoP8k;r=54614778',
        }
        code, key, resp = self.post(verify_url, data=data, headers=headers)
        if code != 0:
            return code, key
        try:
            resp_json = resp.json()
            systemCode = resp_json.get("systemCode")
            resultMsg = resp_json.get("resultMsg")
            resultCode = resp_json.get("resultCode")
            if systemCode == '-200009':
                self.log("user", "二次短信验证码错误", resp)
                return 9, "verify_error"
            elif "路窄人多，暂不能进行查询" in resultMsg:
                self.log("crawler", "website_busy_error:{}".format(resultMsg), resp)
                return 9, "website_busy_error"
            elif resultMsg == 'ok' and resultCode == '0':
                return 0, "success"
            elif resultMsg != "ok" and kwargs['tel'] in resp.text:
                self.log("user", "今日详单查询已达n次，明天再来吧！", resp)
                return 9, "over_query_limit"
            else:
                self.log("crawler", "未知错误", resp)
                return 9, "unknown_error"
        except:
            error = traceback.format_exc()
            self.log("crawler", "json_error:{}".format(error), "")
            return 9, "json_error"

    def monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        monthly_period_list = []
        for month_offset in range(0, length):
            monthly_period_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return monthly_period_list


    def crawl_call_log(self, **kwargs):
        call_logs, miss_list, pos_miss_list = [], [], []
        message, response = "", ""
        error_num = 0
        log_for_retrys = []
        retrys_limit = 4
        full_time = 60.0
        st_time = time.time()
        time_fee = 0
        rand_time = random.randint(20, 40) / 10.0
        month_list = list(
                rrule(MONTHLY,
                      count=5,
                      bymonthday=-1,
                      dtstart=self.today + relativedelta(months=-5)))
        month_list.append(self.today)
        month_retry_list = [("{}{:0>2}".format(i.year, i.month), '{:0>2}'.format(i.day), self.max_retry) for i in month_list]
        while month_retry_list:
            month, day, retrys = month_retry_list.pop(0)
            retrys -= 1
            if retrys < -retrys_limit:
                self.log("crawler", "重试次数完毕", "")
                miss_list.append(month)
                continue
            log_for_retrys.append((month, retrys, time_fee))

            # 第一次请求
            send_verify_url = 'http://www.yn.10086.cn/service/my/actionDispatcher.do'
            data = {
                'reqUrl': 'QDCXQuery',
                'busiNum': 'queryCkCs',
                'queryMonth': month,
                'queryItem': '1',
                'operType': '3'
            }
            code, key, resp = self.post(send_verify_url, data=data)
            if code != 0:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                else:
                    self.log("crawler", "第一步请求失败{}".format(key), resp)
                    miss_list.append(month)
                continue

            # 查询详单
            url = 'http://www.yn.10086.cn/service/my/actionDispatcher.do'
            data = {
                'reqUrl': 'QDCXQuery',
                'busiNum': 'QDCX',
                'queryMonth': month,
                'queryItem': '1',
                'startDate': "{}-{}-01".format(month[:4], month[4:7]),
                'endDate': "{}-{}-{:0>2}".format(month[:4], month[4:7], day),
                'operType': '3',
            }
            code, key, resp = self.post(url, data=data)
            if code != 0:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                else:
                    self.log("crawler", "获取详单失败{}".format(key), resp)
                    miss_list.append(month)
                continue

            code, key, msg, result = self.call_log_get(resp.text, month)
            if code == 0:
                if result:
                    call_logs.extend(result)
                else:
                    if retrys >= 0:
                        time_fee = time.time() - st_time
                        month_retry_list.append((month, day, retrys))
                    elif time_fee < full_time:
                        time.sleep(rand_time)
                        time_fee = time.time() - st_time
                        month_retry_list.append((month, day, retrys))
                    else:
                        self.log("crawler", "详单或许缺失", resp)
                        pos_miss_list.append(month)
                continue
            else:
                message, response = key, resp
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                else:
                    self.log("crawler", u"获取详单失败{}".format(key), resp)
                    miss_list.append(month)

        if message == "html_error":
            self.log("crawler", message, response)
            error_num += 1
        self.log("crawler", "重试记录：{}".format(log_for_retrys), "")
        self.log("crawler", "缺失: {}, 可能缺失: {}, 部分缺失: {}".format(miss_list, pos_miss_list, []), "")
        # print len(call_logs), "=call_logs条数"
        if len(pos_miss_list) + len(miss_list) == 6:
            if error_num > 0:
                return 9, "crawl_error", [], [], []
            else:
                return 9, "website_busy_error", [], [], []
        return 0, "success", call_logs, miss_list, pos_miss_list


    def call_log_get(self, text_resp, month):
        call_log = []
        try:
            resp_json = json.loads(text_resp)
            if "ok" not in resp_json.get("resultMsg"):
                self.log("crawler","website_busy_error:{}".format(resp_json.get("resultMsg")), text_resp)
                return 9, "website_busy_error", "", []
            else:
                callsInfoList = resp_json.get("resultObj").get("callsInfoList")
                for calls_info in callsInfoList:
                    single_call_log = {}
                    single_call_log['call_tel'] = calls_info.get("otherParty")
                    single_call_log['call_method'] = calls_info.get("callType")
                    call_from,error = self.formatarea(calls_info.get("visitAreaCode"))
                    if not call_from:
                        call_from = calls_info.get("visitAreaCode")
                    single_call_log['call_from'] = call_from
                    call_time = calls_info.get("startTime").replace("-", "/")
                    result, call_time = self.time_stamp(call_time)
                    if not result:
                        self.log("crawler", "时间转换失败{}{}".format(call_time,text_resp), "")
                        return 9, 'html_error', 'html_error when transform call_time to time_stamp : %s' % call_time, []
                    single_call_log['call_time'] = call_time
                    single_call_log['call_cost'] = calls_info.get("preFee")
                    single_call_log['call_type'] = calls_info.get("longType")
                    single_call_log['call_duration'] = self.time_format(calls_info.get("callTime"))
                    single_call_log['call_to'] = ""
                    single_call_log['month'] = month
                    call_log.append(single_call_log)
        except:
            error = traceback.format_exc()
            return 9, 'html_error', 'html_error when parse call log : %s' % error, []
        return 0, 'success', '成功', call_log

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

    def time_stamp(self, time_str):
        try:
            timeArray = time.strptime(time_str, "%Y/%m/%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            return True, str(timeStamp)
        except:
            error = traceback.format_exc()
            return False, error

    def crawl_info(self, **kwargs):
        user_info = {}
        get_info_url = 'http://www.yn.10086.cn/service/my/TCJYWCX_FJGN.html'
        code, key, resp = self.get(get_info_url)
        if code != 0:
            return code, key
        if kwargs['tel'] in resp.text:
            try:
                reg = re.compile("window\.top\.BmonPage\.commonCallBack\((.*?), 'compObshHeader'\)")
                result = reg.findall(resp.text)[0]
                resp_json = json.loads(result)
                user_info['full_name'] = resp_json.get('resultObj').get('userMsg').get("userName")
                user_info['id_card'] = resp_json.get('resultObj').get('userMsg').get("custIcNo")
                open_date_str = resp_json.get('resultObj').get('userMsg').get("userApplyDate")
                open_date = self.time_stamp(open_date_str.replace("-", "/"))
                if open_date[0]:
                    user_info['open_date'] = str(open_date[1])
                else:
                    user_info['open_date'] = ""
                user_info['address'] = ""
            except:
                error = traceback.format_exc()
                self.log("crawler", "解析用户数据失败：{}".format(error), resp)
                return 9, "html_error", {}
            return 0, "success", user_info
        else:
            self.log("crawler", "未知原因导致获取个人信息失败", resp)
            return 9, "html_error", {}

    def crawl_phone_bill(self, **kwargs):
        data_list, miss_list = [], []
        error_num = 0
        message = ""
        for query_month in list(self.monthly_period())[1:]:
            url = 'http://www.yn.10086.cn/service/my/actionDispatcher.do'
            data = {
                'reqUrl': 'GRZDQuery',
                'busiNum': 'ZDCX',
                'methodName': 'history',
                'queryMonth': query_month,
            }
            for _ in range(self.max_retry):
                code, key, resp = self.post(url,data=data)
                if code != 0:
                    message = "network_request_error"
                    continue
                if '"resultMsg":"ok"' not in resp.text:
                    message = "no_data"
                    continue
                try:
                    dict = json.loads(resp.text)
                    result_data = {}
                    result_data['bill_month'] = query_month
                    result_data['bill_amount'] = '%.1f' % (float(dict.get('resultObj').get('realBillInfo').get('accountBillInfo')[0].get('feeSum'))/100)
                    result_data['bill_package'] = '%.1f' % (float(dict.get('resultObj').get('realBillInfo').get('accountBillInfo')[0].get('fee'))/100)
                    result_data['bill_ext_calls'] = '%.1f' % (float(dict.get('resultObj').get('realBillInfo').get('accountBillInfo')[2].get('fee'))/100)
                    result_data['bill_ext_data'] = '%.1f' % (float(dict.get('resultObj').get('realBillInfo').get('accountBillInfo')[3].get('fee'))/100)
                    result_data['bill_ext_sms'] = '%.1f' % (float(dict.get('resultObj').get('realBillInfo').get('accountBillInfo')[4].get('fee'))/100)
                    result_data['bill_zengzhifei'] = '%.1f' % (float(dict.get('resultObj').get('realBillInfo').get('accountBillInfo')[5].get('fee'))/100)
                    result_data['bill_daishoufei'] = '%.1f' % (float(dict.get('resultObj').get('realBillInfo').get('accountBillInfo')[7].get('fee'))/100)
                    result_data['bill_qita'] = '%.1f' % (float(dict.get('resultObj').get('realBillInfo').get('accountBillInfo')[8].get('fee'))/100)
                    data_list.append(result_data)
                    break
                except:
                    message = traceback.format_exc()
                    continue
            else:
                if message != "network_request_error":
                    self.log("crawler","html_error:{}".format(message), "")
                    if message != "no_data":
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
    USER_ID = "18408726096"
    USER_PASSWORD = "125274"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
