#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import json
import random
import re
import sys
import time
import traceback
import datetime
import hashlib
import urllib

from dateutil.parser import *
from dateutil.relativedelta import relativedelta
from pwd_change import des_encode, pw_query

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

    def need_parameters(self, **kwargs):
        return ['pin_pwd']

    def get_login_verify_type(self, **kwargs):
        return ''

    def send_login_verify_request(self, **kwargs):
        # get cookies
        url = "http://hl.10086.cn/apps/login/unifylogin.html"
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, ''

        # check tel
        url = "http://hl.10086.cn/rest/common/validate/validateHLPhone/?phone_no={}".format(kwargs['tel'])
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json; charset=utf-8",
            "Referer": "http://hl.10086.cn/apps/login/unifylogin.html"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ''
        if u"校验成功" not in resp.text:
            self.log("user", u"手机号码校验失败", resp)
            return 1, "invalid_tel", ""

        st_captcha_time = time.time()
        for i in range(1,6):
            capture_url = 'http://hl.10086.cn/rest/authImg?type=0&rand=' + str(random.random())
            headers = {
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Referer": "http://hl.10086.cn/apps/login/unifylogin.html"
            }
            code, key, resp = self.get(capture_url, headers=headers)
            if code != 0:
                continue
            # 云打码
            codetype = 3004
            key, result, cid = self._dama(resp.content, codetype)
            self.cid = cid
            if key == "success" and result != "":
                captcha_code = str(result)
            else:
                self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                code, key = 9, "auto_captcha_code_error"
                continue
            # 验证图片
            url = "http://hl.10086.cn/rest/common/vali/valiImage?imgCode={}&_={}".format(captcha_code, int(time.time()*1000))
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://hl.10086.cn/apps/login/unifylogin.html"
            }
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                continue
            try:
                result = resp.json()
                retCode = result.get("retCode")
                if retCode not in ["000000", "0"]:
                    self._dama_report(self.cid)
                    end_captcha_time = time.time() - st_captcha_time
                    self.log("crawler", "验证图片第 {} 次,{} 错误 用时:'{}'s cid:'{}'".format(i,captcha_code,end_captcha_time,self.cid), resp)
                    code, key = 9, "auto_captcha_code_error"
                    continue
                return 0, "success", captcha_code
            except:
                error = traceback.format_exc()
                self.log("crawler", "解析结果错误{}".format(error), "")
                continue
        else:
            return code, key, ""

    def get_info(self, serviceName, channelId="12034"):
        tim = str(time.time())
        l_tim, r_tim = tim.split('.')
        r_tim = r_tim.ljust(3, '0')
        dd = l_tim + r_tim[:4]
        en_str = base64.b64encode(hashlib.md5(dd + 'CM_201606').hexdigest())
        ymd_hms_m = time.strftime("%Y%m%d%H%M%S", time.localtime(int(l_tim))) + r_tim[:4]
        ran = str(random.randint(100, 999)) + str(random.randint(100, 999))
        info = """{"serviceName":"%s","header":{"version":"1.0","timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId":"%s"}}""" % (
            serviceName, dd, en_str, ymd_hms_m + ran, channelId)
        return urllib.quote(info)

    def login(self, **kwargs):
        code, key, captcha_code = self.send_login_verify_request(tel=kwargs['tel'])
        if code != 0:
            return code, key

        url = "http://hl.10086.cn/rest/login/sso/doUnifyLogin/"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json; charset=UTF-8",
            "Referer": "http://hl.10086.cn/apps/login/unifylogin.html"
        }
        # key_url = 'http://hl.10086.cn/rest/rsa/new-key?_={}'.format(str(time.time()).replace('.', ''))
        key_url = 'http://hl.10086.cn/rest/rsa/aes-key?_={}'.format(str(time.time()).replace('.', ''))
        code, key, resp = self.get(key_url)
        if code != 0:
            return code, key

        try:
            json_data = resp.json()
            exponent = json_data['data']['exponent']
            modulus = json_data['data']['modulus']
            pass_word = des_encode(kwargs['pin_pwd'], modulus=modulus, exponent=exponent)

        except:
            error = traceback.format_exc()
            self.log("crawler", "加密密码失败{}".format(error), resp)
            return 9, "crawl_error"
        data = {
            "userName": kwargs['tel'],
            "passWord": pass_word,
            "pwdType": "01",
            "clientIP": captcha_code
        }
        code, key, resp = self.post(url, headers=headers, data=json.dumps(data))
        if code != 0:
            return code, key
        try:
            js = resp.json()
            code = js.get('retCode')
            msg = js.get('retMsg')
            if code == '2036' or code == "400000" or code == "9006":
                # 400000 输入的请求不合法
                # 9006 认证请求报文格式错误
                self.log("user", "账户密码不匹配", resp)
                return 9, "pin_pwd_error"
            elif code == '2046':
                self.log("user", "账户被锁定", resp)
                return 9, "account_locked"
            # "retCode":"800000","retMsg":"统一认证中心返回信息为null"
            elif code == '8014' or code == '800000' or code == "9008" or code == "5001" or code =='100000':
                # 9008 签名验证错误 不知道具体的原因是什么
                # 5001 ,100000 系统繁忙，请您稍后再试
                self.log("website", "系统繁忙", resp)
                return 9, "website_busy_error"
            elif code == "4005":
                self.log("user", "invalid_tel", resp)
                return 9, "invalid_tel"
            elif code == "000001":
                #前一步已经进行图片验证，不排除官网异常
                self.log("crawler", "运营商提示：{}".format(msg), resp)
                self._dama_report(self.cid)
                return 2, "verify_error"
            elif code != "000000":
                self.log("crawler", "未知原因错误", resp)
                return 9, "unknown_error"
            artifact = js.get('data')
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取artifact信息失败{}".format(error), resp)
            return 9, "crawl_error"
        url = "http://hl.10086.cn/rest/login/unified/callBack/"
        params = {
            "artifact": artifact,
            "backUrl": ""        # 这个就是空的
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://hl.10086.cn/apps/login/unifylogin.html"
        }
        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key
        if u"账号当前可用余额" not in resp.text:
            if u"没有访问权限，您尚未登录" in resp.text:
                self.log("website", "官网偶发异常", resp)
                return 9, "website_busy_error"
            self.log("crawler", "未知原因导致异常", resp)
            return 9, "unknown_error"
        # 再次登录
        url = "https://login.10086.cn/SSOCheck.action"
        params = {
            "channelID": "12034",
            "backUrl": "http://hl.10086.cn/apps/login/my.html"
        }
        headers= {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://hl.10086.cn/apps/login/my.html"
        }
        code, key, resp_login = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key
        url = "http://www1.10086.cn/web-Center/authCenter/assertionQuery.do"
        headers = {
            "Origin": "http://hl.10086.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://hl.10086.cn/apps/qry/bill-detail-query/bill-detail-query.html"
        }
        data = "requestJson=" + self.get_info("if008_query_user_assertion")
        code, key, resp_test = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        url = "http://www1.10086.cn/web-Center/authCenter/assertionQuery.do"
        data = "requestJson=" + self.get_info("if008_query_user_assertion")
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://hl.10086.cn/apps/qry/bill-detail-query/bill-detail-query.html"
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        if u"用户已登录" in resp.text:
            return 0, "success"
        elif u'8101' in resp.text or u'Artifact无效' in resp.text or u'无效的artifact' in resp.text or u'9999' in resp.text \
                or '"response_code":"0000"' in resp.text:
            self.log('website', 'website_busy_error', resp)
            self.log('website', '为什么会出现这种情况?', resp_login)
            self.log('website', '为什么会出现这种情况????', resp_test)
            return 9, 'website_busy_error'
        elif '"response_code":"-100"' in resp.text or u"连接超时" in resp.text:
            # "response_code":"-100"  连接超时
            self.log("crawler", u"连接超时", resp)
            return 9, 'website_busy_error'
        else:
            self.log("crawler", u"未知异常", resp)
            return 9, "unknown_error"


    def get_verify_type(self, **kwargs):
        return 'SMS'

    def send_verify_request(self, **kwargs):
        today = datetime.datetime.now()
        year_month = "{}{:0>2}".format(today.year, today.month)
        url = "http://hl.10086.cn/rest/qry/billdetailquery/s1526_1"
        params = {
            "select_type": "72",
            "cxfs":	"1",
            "timeStr1": "",
            "timeStr2": "",
            "time_string": year_month,
            "_": "{}".format(int(time.time()))
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://hl.10086.cn/apps/qry/bill-detail-query/bill-detail-query.html"
        }
        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key, ""

        url = "http://hl.10086.cn/rest/sms/sendSmsMsg"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json; charset=UTF-8",
            "Referer": "http://hl.10086.cn/apps/qry/bill-detail-query/bill-detail-query.html"
        }
        data = {
            "func_code": "000004",
            "sms_type": "2",
            "phone_no": kwargs['tel'],
            "sms_params": ""
        }
        code, key, resp = self.post(url, headers=headers, data=json.dumps(data))
        if code != 0:
            return code, key, ""
        if u"发送成功" in resp.text:
            return 0, "success", ''
        elif u'尊敬的用户,请勿在1分钟内重复下发短信' in resp.text:
            self.log("user", 'send_sms_too_quick_error', resp)
            return 9, 'send_sms_too_quick_error', ''
        elif u'短信下发失败，手机号码为空' in resp.text or '100001' in resp.text:
            self.log("user", 'invalid_tel', resp)
            return 9, 'invalid_tel', ''
        else:
            self.log("crawler", 'request_error', resp)
            return 9, 'request_error', ''

    def verify(self, **kwargs):
        url = "http://hl.10086.cn/rest/sms/checkSmsCode"
        headers = {
            "Referer": "http://hl.10086.cn/apps/qry/bill-detail-query/bill-detail-query.html",
            "X-Requested-With": "XMLHttpRequest"
        }
        params = {
            'func_code': '000004',
            'sms_type':	'2',
            'phone_no': '',
            'sms_code':	kwargs['sms_code'],
            '_': "{}".format(int(time.time()))
        }
        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key
        if u"输入正确" in resp.text:
            return 0, "success"
        elif u"输入错误" in resp.text:
            self.log("user", u"验证码输入错误", resp)
            return 9, "verify_error"
        elif u"获取短信验证码" in resp.text:
            self.log("crawler", u"尊敬的用户，请您获取短信验证码", resp)
            return 9, "website_busy_error"
        else:
            self.log("crawler", u"未知异常", resp)
            return 9, "unknown_error"

    def crawl_call_log(self, **kwargs):
        call_logs, miss_list, pos_miss_list = [], [], []
        error_num = 0
        # def getPscToken():
        #     getPscToken_url = "http://hl.10086.cn/rest/session/getPscToken/?_={}".format(int(time.time()))
        #     headers = {
        #         "X-Requested-With": "XMLHttpRequest",
        #         "Content-Type": "application/json; charset=utf-8",
        #         "Referer": "http://hl.10086.cn/apps/qry/bill-detail-query/bill-detail-query.html"
        #     }
        #     code, key, resp = self.get(getPscToken_url, headers=headers)
        #     if code != 0:
        #         return False, key, resp
        #     try:
        #         res_json = json.loads(resp.text)
        #     except:
        #         error = traceback.format_exc()
        #         self.log("crawler", error, resp)
        #         return False, error, resp
        #     if "000000" == res_json['retCode']:
        #         return True, res_json['data'], resp
        #     return True, "成功", resp


        aes_key_url = 'http://hl.10086.cn/rest/rsa/aes-key?_={}'.format(str(time.time()).replace("."," "))
        code,key,resp = self.get(aes_key_url)
        if code!= 0:
            return code ,key
        try:
            resp_json = resp.json()
            exponent = resp_json['data']['exponent']
            modulus = resp_json['data']['modulus']
            xuser_word = des_encode(kwargs['pin_pwd'],modulus=modulus,exponent=exponent)
        except:
            error = traceback.format_exc()
            self.log("crawler","加密密码2失败{}".format(error),resp)
            return 9 ,"crawl_error"

        message, response = "", ""
        month_retry_list = [(x, self.max_retry) for x in self.monthly_period(6, strf='%Y%m')]
        # for month in self.monthly_period(6, strf='%Y%m'):
        full_time = 60.0
        retrys_limit = 4
        st_time = time.time()
        time_fee = 0
        rand_time = random.randint(20, 40)/ 10.0
        log_for_retrys = []
        while month_retry_list:
            month, retrys = month_retry_list.pop(0)
            retrys -= 1
            if retrys < -retrys_limit:
                self.log("crawler", "重试次数完毕", "")
                miss_list.append(month)
                continue
            log_for_retrys.append((month, retrys, time_fee))

            # result, pscToken, r = getPscToken()
            # if not result:
            #     if retrys >= 0:
            #         time_fee += time.time() - st_time
            #         month_retry_list.append((month, retrys))
            #     elif time_fee < full_time:
            #         time.sleep(rand_time)
            #         time_fee += time.time() - st_time
            #         month_retry_list.append((month, retrys))
            #     else:
            #         self.log("crawler", u"获取信息错误", r)
            #         miss_list.append(month)
            #     continue
            # xuser_word = pw_query(kwargs['pin_pwd'], pscToken).encode('utf8')
            re_url = "http://hl.10086.cn/apps/qry/bill-detail-query/bill-detail-query-attr.html"
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "http://hl.10086.cn/apps/qry/bill-detail-query/bill-detail-query.html"
            }
            params = {
                "select_type": "72",
                "time_string": month,
                "feny_flag": "N",
                # "xuser_word": kwargs['pin_pwd'],
                "xuser_word": xuser_word,
                "recordPass":"",
                "{}".format(random.random()): ""
            }

            code, key, resp = self.get(re_url, headers=headers, params=params)
            if code != 0:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, retrys))
                else:
                    self.log("crawler", u"获取前置url失败{}".format(key), resp)
                    miss_list.append(month)
                continue
            url = "http://hl.10086.cn/rest/qry/billdetailquery/channelQuery"
            params = {
                "select_type": "72",
                "time_string": month,
                "xuser_word": xuser_word,
                "recordPass":"",
                "_": "{}".format(int(time.time()))
            }
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": re_url
            }
            code, key, resp = self.get(url, headers=headers, params=params)
            if code != 0:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, retrys))
                else:
                    self.log("crawler", u"获取详单失败{}".format(key), resp)
                    miss_list.append(month)
                continue
            code, key, msg, result = self.call_log_get(resp.text, month)
            if code == 0:
                if result:
                    call_logs.extend(result)
                else:
                    if retrys >= 0:
                        time_fee = time.time() - st_time
                        month_retry_list.append((month, retrys))
                    elif time_fee < full_time:
                        time.sleep(rand_time)
                        time_fee = time.time() - st_time
                        month_retry_list.append((month, retrys))
                    else:
                        self.log("crawler", u"详单或许缺失", resp)
                        pos_miss_list.append(month)
                continue
            else:
                message, response = key, resp
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, retrys))
                else:
                    self.log("crawler", u"获取详单失败{}".format(key), resp)
                    miss_list.append(month)
        if message == "html_error":
            self.log("crawler", message, response)
            error_num += 1

        self.log("crawler", "重试记录{}".format(log_for_retrys), "")
        self.log("crawler", "缺失: {}, 可能缺失: {}, 部分缺失: {}".format(miss_list, pos_miss_list, []), "")
        if len(pos_miss_list) + len(miss_list) == 6:
            if error_num > 0:
                return 9, "crawl_error", [], [], []
            else:
                return 9, "website_busy_error", [], [], []
        return 0, "success", call_logs, miss_list, pos_miss_list

    def call_log_get(self, text_resp, month):
        call_log = []
        if "errCode:10111109814220003" in text_resp:
            self.log("user", "不允许查询开户前的详单", "")
            return 0, "success", "", []
        try:
            js = json.loads(text_resp)
            if "java.lang.NullPointerException" in text_resp:
                return 9, "website_busy_error", "", []
            text_list = js.get("data").get("detailList")[0].get("DETAIL_LINES")
            for text in text_list:
                single_call_log = {}
                info_list = text
                if len(info_list) < 4:
                    continue
                # '2017/11/01 03:39:48', '北京', '主叫', '10086', '1分58秒', '国内异地主叫', '标准资费', '0.00', '2G网络', ''
                #    0                     1     2       3         4        5             6         7        8       9
                single_call_log['call_tel'] = info_list[3]
                single_call_log['call_cost'] = info_list[7]
                call_time = info_list[0]
                result, call_time = self.time_stamp(call_time)
                if not result:
                    self.log("crawler", "转换时间失败{}{}".format(call_time, text_resp), "")
                    return 9, 'html_error', 'html_error when transform call_time to time_stamp : %s' % call_time, []
                single_call_log['call_time'] = call_time
                single_call_log['month'] = month
                single_call_log['call_method'] = info_list[2]
                single_call_log['call_type'] = info_list[5]
                raw_call_from = info_list[1]
                call_from, error = self.formatarea(raw_call_from)
                if not call_from:
                    call_from = raw_call_from
                single_call_log['call_from'] = call_from
                single_call_log['call_to'] = ''
                single_call_log['call_duration'] = self.time_format(info_list[4])
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
        tel_info = {}
        url = "http://www1.10086.cn/web-Center/interfaceService/custInfoQry.do"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        data = "requestJson=" + self.get_info("if007_query_user_info", "0001")
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key, {}
        try:
            js = resp.json()
            code = js.get("result").get("response_code")
            if code == "0000":
                info = js.get("result").get("data").get("userInfo")
                tel_info['address'] = info.get("userAddr")
                # 20170207143512
                open_date_str = info.get("userBegin")
                open_date = self.time_stamp(open_date_str[:4]+'/'+open_date_str[4:6]+'/'+open_date_str[6:8]+' '+open_date_str[8:10]+":"+open_date_str[10:12]+":"+open_date_str[12:])
                if open_date[0]:
                    tel_info['open_date'] = open_date[1]
                else:
                    tel_info['open_date'] = ""
                tel_info['id_card'] = ''
                tel_info['full_name'] = info.get("userName")
            else:
                self.log("crawler", "未知原因导致获取个人信息失败", resp)
                return 9, "html_error", {}
        except:
            error = traceback.format_exc()
            self.log("crawler", u"解析用户信息失败{}".format(error), resp)
            return 9, "html_error", {}
        return 0, "success", tel_info

    def crawl_phone_bill(self, **kwargs):
        miss_list = []
        data_list = []
        error_num = 0
        message = ""
        for month in list(self.monthly_period())[1:]:
            for i in range(self.max_retry):
                url = "http://hl.10086.cn/rest/qry/billquery/qryBillHome?user_seq=000003&yearMonth={}&_={}".format(month, int(time.time()))
                code, key, resp = self.get(url)
                if code != 0:
                    message = "network_error"
                    continue
                try:
                    js = resp.json()
                    dd = js.get("data").get("ROOT").get("BODY").get("OUT_DATA").get("PCAS_03")
                    data = {}
                    data['bill_month'] = month
                    data['bill_amount'] = str(float(dd.get("PCAS_03_12").get("REAL_FEE", "0.0"))/100)
                    data['bill_package'] = str(float(dd.get("PCAS_03_01").get("REAL_FEE", "0.0"))/100)
                    data['bill_ext_calls'] = str(float(dd.get("PCAS_03_02").get("REAL_FEE", "0.0"))/100)
                    data['bill_ext_data'] = str(float(dd.get("PCAS_03_04").get("REAL_FEE", "0.0"))/100)
                    data['bill_ext_sms'] = str(float(dd.get("PCAS_03_05").get("REAL_FEE", "0.0"))/100)
                    data['bill_zengzhifei'] = str(float(dd.get("PCAS_03_06").get("REAL_FEE", "0.0"))/100)
                    data['bill_daishoufei'] = str(float(dd.get("PCAS_03_09").get("REAL_FEE", "0.0"))/100)
                    data['bill_qita'] = str(float(dd.get("PCAS_03_10").get("REAL_FEE", "0.0"))/100)
                    data_list.append(data)
                    break
                except:
                    error = traceback.format_exc()
                    message = u"解析账单数据失败{}".format(error)
                    continue
            else:
                if message != "network_error":
                    error_num += 1
                miss_list.append(month)
        if len(miss_list) == 5:
            if error_num > 0:
                return 9, "crawl_error", [], []
            else:
                return 9, "website_busy_error", [], []
        return 0, "success", data_list, miss_list

    def monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        monthly_period_list = []
        for month_offset in range(0, length):
            monthly_period_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return monthly_period_list

if __name__ == "__main__":
    c = Crawler()
    USER_ID = "13846194712"
    USER_PASSWORD = "514387"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
