# -*- coding: utf-8 -*-
import calendar
import re
import time
import json
import base64
import random
import datetime
import traceback
import math
import os
import sys
reload(sys)
sys.setdefaultencoding("utf8")

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA

from dateutil.relativedelta import relativedelta
from datetime import date


'''TODO:
    * pass the normal flow
    * logging the import step and info to the file for debugging
    * test session funciton
    * handle normal error case as possible as you can
    * handle any unexpected exception case
'''

if __name__ == '__main__':
    sys.path.append('../../../')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from api.util import get_tel_info
else:
    from worker.crawler.base_crawler import BaseCrawler
    from api.util import get_tel_info

"""
2017-12-01
    从详单处点击登录
    http://shop.10086.cn/i/?f=billdetailqry
"""

class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.send_time = None
        self.is_shandong = False
        self.shandong_has_now_data = False
        self.log_sleep_time = False

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_login_verify_type(self, **kwargs):
        """
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 两种都要
        """
        return 'SMS'

    def get_verify_type(self, **kwargs):
        """
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
        """
        return 'SMS'

    def send_login_verify_request(self, **kwargs):
        """
        登入時，請求發送短信，或是下載圖片
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        def parse_response(response):
            if response.text == '0': # server fail return 'error', success return '0'
                # the duration between two sms verification should be more than 60 sec
                self.send_time = time.time() # keep the first sms verification time
                return 0, 'success', ''
            elif response.text == '1':
                message = u'对不起，短信随机码暂时不能发送，请一分钟以后再试'
                return 9, 'send_sms_too_quick_error', message
            elif response.text == '2':
                message = u'短信下发数已达上限，您可以使用服务密码方式登录！(也有可能是手机已停机)。'
                return 9, 'over_max_sms_error', message
            elif response.text == '3':
                message = u'对不起，短信发送次数过于频繁'
                return 9, 'send_sms_too_quick_error', message
            elif response.text == '4005':
                message = u'手机号码有误，请重新输入'
                return 1, 'invalid_tel', message
            else:
                message = u'发送验证码错误'
                return 9, 'send_sms_error', message

        url = 'https://login.10086.cn/sendRandomCodeAction.action'
        data = {
            'userName': kwargs['tel'],
            'type': '01',
            'channelID': '12003'
        }

        headers = {
            'Host': 'login.10086.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://login.10086.cn',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://login.10086.cn/html/login/login.html?channelID=12002&backUrl=http%3A%2F%2Fshop.10086.cn%2Fmall_100_100.html%3Fforcelogin%3D1',
        }

        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key, ''

        code, key, message = parse_response(resp)
        if code != 0:
            msg = '{}:{}'.format(key, message)
            time.sleep(40)
            self.log('user', msg, resp)

        return code, key, ''

    def get_encrypt(self, **kwargs):
        url = "https://login.10086.cn/platform/js/encrypt.js?resVer=20141125"
        headers = {
            "Accept": "*/*",
            "Referer": "https://login.10086.cn/html/login/login.html"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key
        try:
            public_key = re.findall("var key = \"(.*?)\";", resp.text, re.S)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", error, resp)
            return 9, "website_busy_error"
        publik_key = """-----BEGIN PUBLIC KEY-----
                {}
                -----END PUBLIC KEY-----""".format(public_key)

        serPwd = kwargs['pin_pwd']
        rsakey = RSA.importKey(publik_key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(serPwd.encode('utf-8')))
        return 0, cipher_text

    def login(self, **kwargs):
        """
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
        """
        def parse_response(response):
            try:
                ret_data = response.json()
                error_msg = ret_data['desc']
                error_code = ret_data['code']
                ret_text = response.text
                if error_code != '0000':
                    if error_code in ['6001', '6002']:
                        status_key = 'verify_error'
                        code = 9
                    elif error_code in ['2036']:
                        status_key = 'pin_pwd_error'
                        code = 9
                    elif error_code in ['8014'] or u'系统繁忙' in ret_text:
                        status_key = 'website_busy_error'
                        code = 9
                    elif error_code in ['2046', '8009'] or u'密码输入超过次数账号已锁定' in ret_text:
                        status_key = 'over_query_limit'
                        code = 9
                    else:
                        status_key = 'login_param_error'
                        code = 9
                    return code, status_key, error_msg, ''
                return 0, 'success', '', ret_data
            except ValueError:
                error_msg = traceback.format_exc()
                return 9, 'json_error', 'json_error:{}'.format(error_msg), ''
            except:
                error_msg = traceback.format_exc()
                return 9, 'unknown_error', 'unknown_error:{}'.format(error_msg), ''
        try:
            code, result = self.get_encrypt(**kwargs)
            if code != 0:
                return code, result
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密失败{}".format(error), "")
            return 9, "website_busy_error"
        url = 'https://login.10086.cn/login.htm'
        params = {
            'accountType': '01',
            'account': kwargs['tel'],
            'password': result,
            'pwdType': '01',
            'smsPwd': kwargs['sms_code'],
            'inputCode': '',
            'backUrl': 'http://shop.10086.cn/i/sso.html',
            'rememberMe': '0',
            'channelID': '12003',
            'protocol': 'https:',
        }

        headers = {
            'Host': 'login.10086.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://login.10086.cn/html/login/login.html',
        }

        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key

        code, key, message, ret_data = parse_response(resp)
        if code != 0:
            time.sleep(40)
            if key in ['verify_error', 'pin_pwd_error', 'login_param_error', 'over_query_limit']:
                self.log('user', key, resp)
            else:
                self.log('crawler', message, resp)
            return code, key

        url = '{}'.format(ret_data['assertAcceptURL'])
        params = {
            'artifact': '{}'.format(ret_data['artifact']),
            'backUrl': 'http://shop.10086.cn/i/',
        }

        headers = {
            'Host': 'shop.10086.cn',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }

        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key

        return 0, 'success'

    def get_img(self):
        url = 'http://shop.10086.cn/i/authImg'
        params = {
            't': str(random.random()),
        }

        headers = {
            'Host': 'shop.10086.cn',
            'Referer': 'http://shop.10086.cn/i/?f=billdetailqry&welcome={}'.format(int(time.time() * 1000)),
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key, ''
        # image_str = base64.b64encode(resp.content)
        return 0, "success", resp

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        def parse_response(response, mode='Captcha'):
            if "404 Not Found" in response.text:
                self.log('website', 'website_busy_error', response)
                return 9, 'website_busy_error'
            if mode == 'sms':
                try:
                    ret_data = json.loads(response.text[1:-1])
                    error_code = ret_data['retCode']
                    if error_code != '000000':
                        error_msg = ret_data['retMsg']
                        if error_msg == u'业务异常':
                            self.log('website', 'website_busy_error', response)
                            return 9, 'website_busy_error'
                        elif u"单位时间内下发短信次数过多" in error_msg:
                            self.log('user', 'send_sms_too_quick_error', response)
                            return 9, 'send_sms_too_quick_error'
                        self.log('crawler', 'send_sms_error', response)
                        return 9, 'send_sms_error'
                except ValueError:
                    error_msg = traceback.format_exc()
                    self.log('crawler', 'json_error:{}'.format(error_msg), response)
                    return 9, 'json_error'
                except:
                    error_msg = traceback.format_exc()
                    self.log('crawler', 'unknown_error:{}'.format(error_msg), response)
                    return 9, 'unknown_error'
            return 0, 'success'

        verify_type = kwargs.get('verify_type', '')
        image_str = ''

        if verify_type in ['', 'captcha']:
            for i in range(self.max_retry):
                code, key, resp = self.get_img()
                if code != 0:
                    continue

                # 云打码
                codetype = '3006'
                key, result, cid = self._dama(resp.content, codetype)
                # print result, cid, "***---***"*10
                if key == "success" and result != "":
                    captcha_code = str(result)
                else:
                    self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                    return 9, key, result
                # 验证图形验证码
                url = "http://shop.10086.cn/i/v1/res/precheck/{}".format(kwargs['tel'])
                params = {
                    "captchaVal": captcha_code,
                    "_": str(int(time.time() * 1000))
                }
                headers = {"X-Requested-With": "XMLHttpRequest"}
                code, key, resp = self.get(url, params=params, headers=headers)
                if code != 0:
                    continue
                try:
                    json_result = resp.json()
                    result_code = json_result.get("retCode")
                    if result_code == "000000":
                        self.captcha_code = captcha_code
                        break
                    else:
                        self.log("website", "云打码失败!", resp)
                        self._dama_report(cid)
                        continue
                except:
                    error = traceback.format_exc()
                    self.log("crawler", "获取图形结果失败: {}".format(error), resp)
                    return 9, "json_error", ""
            else:
                self.log("crawler", "重试次数耗尽", "")
                return 9, "website_busy_error", ""

        if verify_type in ['', 'sms']:
            wait_sec = 60 - time.time() + self.send_time
            if wait_sec < 0:
                wait_sec = 0
            time.sleep(wait_sec)
            url = 'https://shop.10086.cn/i/v1/fee/detbillrandomcodejsonp/{}'.format(kwargs['tel'])
            params = {
                '_': str(int(time.time()*1000)),
                'callback': '',
            }

            headers = {
                'Host': 'shop.10086.cn',
                'Referer': 'http://shop.10086.cn/i/?f=billdetailqry',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
            }

            code, key, resp = self.get(url, headers=headers, params=params)
            if code != 0:
                return code, key,  ''

            code, key = parse_response(resp, mode='sms')
            if code != 0:
                time.sleep(40)
                return code,  key,  ''

        #self.log('INFO', message, resp)
        return 0, 'success', image_str

    def verify(self, **kwargs):
        """
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
        """
        def parse_response(response):
            try:
                if response.text[0] == '(':
                    ret_data = json.loads(response.text[1:-1])
                else:
                    ret_data = json.loads(response.text)
                error_msg = ret_data.get('retMsg', 0)
                error_code = ret_data.get('retCode', 0)
                if error_code == '000000':
                    return 0, 'success', ''
                elif error_code == '570005':
                    return 9, "verify_error", "用户短信验证码输入错误{}".format(error_msg)
                elif error_code == u'499999!':
                    # 499999 用户验证码(图形/短信)输入错误
                    return 2, 'verify_error', error_msg
                elif error_msg == 0 or error_code == 0 or error_code == '570007' or u'系统繁忙' in error_msg:
                    return 9, "website_busy_error", "{}".format(response)
                else:
                    return 9, 'verify_error', error_msg
            except ValueError:
                if u'输入项中不能包含非法字符' in response.text:
                    return 2, 'verify_error', u'输入项中不能包含非法字符'
                error_msg = traceback.format_exc()
                return 9, 'json_error', 'json_error:{}'.format(error_msg)
            except:
                error_msg = traceback.format_exc()
                return 9, 'unknown_error', 'unknown_error:{}'.format(error_msg)

        url = 'https://shop.10086.cn/i/v1/fee/detailbilltempidentjsonp/{}'.format(kwargs['tel'])
        params = {
            '_': str(int(time.time() * 1000)),
            'callback': '',
            'pwdTempSerCode': base64.b64encode(kwargs['pin_pwd'].encode('utf-8')),
            'pwdTempRandCode': base64.b64encode(kwargs['sms_code'].encode('utf-8')),
            'captchaVal': self.captcha_code
        }

        headers = {
            'Host': 'shop.10086.cn',
            'Referer': 'http://shop.10086.cn/i/?f=billdetailqry&welcome={}'.format(int(time.time()*1000)),
            }

        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key

        code, key, message = parse_response(resp)
        if code != 0:
            if 'verify_error' in key:
                self.log('user', key, resp)
            elif 'website_busy_error' in key:
                self.log('website', 'website_busy_error', resp)
            else:
                self.log('crawler', message, resp)
            time.sleep(40)

        ###self.log('INFO', message, response)
        return code, key

    def crawl_info(self, **kwargs):
        """
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        def parse_response(response):
            try:
                ret_data = response.json()
                error_code = ret_data['retCode']
                if error_code == "2005":
                    # {"data":[],"retCode":"2005","retMsg":"您当前的手机号已停机，因此不能查询客户资料，感谢您使用中国移动网上商城","sOperTime":"20180119001335"}
                    return 0, "success", "手机号已停机", {}
                if error_code != '000000':
                    # error_msg = ret_data['retMsg']
                    return 9, 'crawl_error', 'get_crawl_info_fail', {}
                info = ret_data['data']
                user_info = {}
                name = info.get('name','')
                if name:
                    user_info[u'full_name'] = name
                else:
                    user_info[u'full_name'] = ''
                # user_info[u'open_date'] = info.get('inNetDate','')
                open_date = info.get('inNetDate', '')
                if re.search(r"\d*-\d*-\d*$", open_date):
                    str_format = "%Y-%m-%d"
                else:
                    str_format = "%Y%m%d%H%M%S"
                user_info[u'open_date'] = self.time_transform(time_str=open_date, str_format=str_format)
                user_info[u'is_realname_register'] = True
                user_info[u'id_card'] = ''
                add = info.get('address', '')
                if add:
                    user_info[u'address'] = add
                else:
                    user_info[u'address'] = ''
                return 0, 'success', '', user_info
            except ValueError:
                error_msg = traceback.format_exc()
                return 9, 'json_error', 'json_error:{}'.format(error_msg), {}
            except:
                error_msg = traceback.format_exc()
                return 9, 'unknown_error', 'unknown_error:{}'.format(error_msg), {}

        url = 'http://shop.10086.cn/i/v1/cust/info/{}'.format(kwargs['tel'])
        params = {
            '_' : str(int(time.time()*1000))
        }

        headers = {
            'Host': 'shop.10086.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'no-store, must-revalidate',
            'pragma': 'no-cache',
            'Content-Type': '*',
            'If-Modified-Since': '0',
            'expires': '0',
            'Referer': 'http://shop.10086.cn/i/?f=billdetailqry&welcome={}'.format(int(time.time() * 1000)),
        }

        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key, {}

        code, key, message, data_dict = parse_response(resp)
        if code != 0:
            self.log('crawler', message, resp)

        return code,  key,  data_dict

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        """
        call_time 格式化
        return
            call_time: str, 时间戳(秒)，eg：'1494577393'
        """
        time_str = time_str.encode(bm)
        if re.findall(r"(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})", time_str):
            time_str = reduce(lambda x,y : x+'-'+y, time_str.split(' ')[0].split('/'))+" "+time_str.split(" ")[1]
        if len(re.findall(r"(\d{2,4})",time_str)) == 5:
            today_month = datetime.date.today().month
            today_year = datetime.date.today().year
            str_month = int(time_str[:2])
            if str_month > today_month:
                str_year = today_year - 1
            else:
                str_year = today_year
            time_str = str(str_year) + "-" + time_str
        if len(re.findall(r"(\d{2,4})",time_str)) == 6:
            time_str_list = re.findall(r"(\d{2,4})", time_str)
            time_str = reduce(lambda x,y : x+'-'+y, time_str_list[0:3]) + " " + reduce(lambda x,y : x+':'+y, time_str_list[3:])
        time_type = time.strptime(time_str, str_format)
        return str(int(time.mktime(time_type)))

    def duration_format(self, time):
        """
        call_duration 格式化
        return:
            call_duration: str, 秒，eg: '128'
        """
        call_duration = ""
        time_list = re.findall(r'\d+', time.replace('.0',''))
        if len(time_list) == 1:
            call_duration = int(time_list[0])
        elif len(time_list) == 2:
            call_duration = int(time_list[0])*60 + int(time_list[1])
        elif len(time_list) == 3:
            call_duration = int(time_list[0])*60*60 + int(time_list[1])*60 + int(time_list[2])
        return str(call_duration)

    # 获取某个月份的第一天和最后一天的时间戳。
    def getMonthFirstDayAndLastDay(self, year=None, month=None):

        # 获取当月第一天的星期和当月的总天数
        firstDayWeekDay, monthRange = calendar.monthrange(int(year), int(month))

        # 获取当月的第一天
        firstDay = self.time_transform(year + '-' + month + '-01 00:00:00')
        lastDay = str(datetime.date(year=int(year), month=int(month), day=monthRange)) + ' 23:59:59'
        lastDay = self.time_transform(lastDay)
        return firstDay, lastDay

    def from_call_time_get_month(self, call_time, month):
        if call_time:
            try:
                time_obj = time.localtime(int(call_time))
                month_str = time.strftime("%Y%m", time_obj)
                return month_str
            except:
                error = traceback.format_exc()
                self.log("crawler", "使用 {} 获取 month_str 失败: {}".format(call_time, error), "")
                return month
        else:
            return month

    def extract_call_log(self, message, mon):
        """
        05秒
        02分34秒
        09分04秒
        9分08秒
        00秒
        """
        call_logs = []

        firstDay, lastDay = self.getMonthFirstDayAndLastDay(year=mon[:4], month=mon[-2:])
        for log in message:
            call_log = {}
            call_time = log.get('startTime')
            if call_time is None:
                self.log("website", "官网下发数据为....:\n{}".format(log), "")
                continue
            call_log[u'call_time'] = self.time_transform(call_time)
            # 因为山东的详单周期为 10: 10.27~11.26 该处理导致缺失数据
            # if int(call_log[u'call_time']) < int(firstDay) or \
            #                 int(call_log[u'call_time']) > int(lastDay):
            #     continue
            call_duration = log.pop('commTime')
            call_log[u'call_tel'] = log.pop('anotherNm')
            call_log[u'call_cost'] = log.pop('commFee')
            call_log[u'call_method'] = log.pop('commMode')
            call_log[u'call_type'] = log.pop('commType')
            call_log[u'call_duration'] = self.duration_format(call_duration)
            raw_call_from = log.pop('commPlac')
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                call_log[u'call_from'] = call_from
            else:
                call_log[u'call_from'] = raw_call_from
            call_log[u'call_to'] = ''
            month_str = self.from_call_time_get_month(call_log[u'call_time'], mon)
            call_log[u'month'] = month_str
            now_time = datetime.datetime.now().strftime("%Y%m")
            if self.is_shandong and not self.shandong_has_now_data:
                if now_time == month_str:
                    self.shandong_has_now_data = True
                    self.log("crawler", '有当月数据', "")
            call_logs.append(call_log)
        # if call_from_set:
        #     self.log("crawler", "call_from_set: {}".format(call_from_set), "")
        return call_logs

    def get_previous_month(self, year, month):
        #获取上个月月份数字
        previous = datetime.date(year,int(month),1)-datetime.timedelta(days= 1)
        return previous.year, str(previous.month).zfill(2)

    def get_next_month(self, year, month, next_num=1, format="%Y%m"):
        #获取下个月月份数字
        now_month = datetime.date(int(year), int(month), 1)
        next_month = now_month - relativedelta(months=-next_num)
        return next_month.strftime(format)

    def get_year_month(self, number, first_param=0):
        month_list = []
        for each_month in xrange(first_param, number, -1):
            today = datetime.date.today()
            query_date = today + relativedelta(months=each_month)
            month_list.append("%d%02d" % (query_date.year, query_date.month))
        return month_list

    def get_search_list(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        search_list = []
        for month_offset in range(0, length):
            search_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return search_list

    def rebulid_miss_list(self, missing_month_list, possibly_missing_list, part_missing_month_list):
        part_set = set(part_missing_month_list)
        missing_set = set(missing_month_list)
        possibly_set = set(possibly_missing_list)

        possibly_set = possibly_set - part_set - missing_set
        missing_set = missing_set - part_set

        part_missing_month_list = list(part_set)
        part_missing_month_list.sort(reverse=True)

        missing_month_list = list(missing_set)
        missing_month_list.sort(reverse=True)

        possibly_missing_list = list(possibly_set)
        possibly_missing_list.sort(reverse=True)
        return missing_month_list, possibly_missing_list, part_missing_month_list

    def crawl_call_log(self, **kwargs):
        """
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        province_name = get_tel_info(kwargs['tel'][:7])
        if u'山东' == province_name.get('province'):
            self.is_shandong = True

        # 缺失月份
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        # 部分缺失月份
        part_missing_month_list = []
        self.all_retry = []
        self.retry_last = []
        # 错误列表
        err_dict = {'crawl_error': 0, 'website_busy_error': 0, 'user_prohibited_error': 0,
                    'user_multiple_loggedin_error': 0}
        year = datetime.date.today().year
        month = str(datetime.date.today().month).zfill(2)
        total_call_logs = []


        search_list = self.get_search_list()
        for year_month_str in search_list:
            year_month = year_month_str
            year = year_month[:4]
            month = year_month[4:]
            try:
                key = ""
                key, message, part_missing_list = self.get_call_log_by_month(kwargs['tel'], year, month, province_name=province_name)
            except ValueError:
                error_msg = traceback.format_exc()
                self.log('crawler', '{}:{}'.format(key, error_msg), '')
                if year_month not in missing_month_list:
                    missing_month_list.append(year_month)
                err_dict['crawl_error'] += 1
                continue
            except:
                error_msg = traceback.format_exc()
                self.log('crawler', '{}:{}'.format(key, error_msg), '')
                if year_month not in missing_month_list:
                    missing_month_list.append(year_month)
                err_dict['crawl_error'] += 1
                continue
            if part_missing_list:
                part_missing_month_list.extend(part_missing_list)
            # 月份递减
            # year, month = self.get_previous_month(year, month)
            if key != 'success':
                # return key, 9, message, []
                # 如果出错按缺失处理
                if year_month not in missing_month_list:
                    missing_month_list.append(year_month)
                if key in ['website_busy_error', 'website_maintaining_error', 'websiter_prohibited_error']:
                    err_dict['website_busy_error'] += 1
                elif key =='user_multiple_loggedin_error':
                    err_dict['user_multiple_loggedin_error'] += 1
                elif key == 'user_prohibited_error':
                    err_dict['user_prohibited_error'] += 1
                else:
                    err_dict['crawl_error'] += 1

            if not message:
                # 如果为空则按可能缺失月份处理
                if year_month not in possibly_missing_list:
                    possibly_missing_list.append(year_month)
                continue
            # call_logs = [self.extract_call_log(x, year_month) for x in message]
            try:
                call_logs = self.extract_call_log(message, year_month)
            except:
                error_m = traceback.format_exc()
                self.log('crawler', 'crawl_error:{}'.format(error_m), '')
                continue
            if call_logs == []:
                missing_month_list.append(year_month)
                self.log('website', '详单记录重复，月份：{}， 数据--{} '.format(year_month, message), '')
            else:
                total_call_logs.extend(call_logs)

        if self.shandong_has_now_data:
            now_month = datetime.datetime.now().strftime("%Y%m")
            if now_month in missing_month_list:
                missing_month_list.remove(now_month)
            part_missing_month_list.append(now_month)
        # 重新构造missing_month_list 和 possibly_missing_list
        missing_month_list, possibly_missing_list, part_missing_month_list = self.rebulid_miss_list(missing_month_list, possibly_missing_list, part_missing_month_list)

        self.log("crawler",
                 "记录缺失列表:\n 缺失:{}\n可能缺失:{}\n部分缺失:{}".format(
                     missing_month_list,
                     possibly_missing_list,
                     part_missing_month_list
                 ), "")

        file_path = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1])
        now = datetime.datetime.now()
        year_month_day = now.strftime("%m_%d")
        # log_file = "{}{}old_retry_log_{}.txt".format(file_path, os.path.sep, year_month_day)

        # try:
        #     with open(log_file, 'a+')as f:
        #         f.write("tel: {} sid:{}".format(kwargs['tel'], self.kwargs.get('sid', '未获取到sid')))
        #         f.write("\n")
        #         f.write(str(tuple(self.all_retry)))
        #         f.write("\n")
        #         f.write(str(tuple(self.retry_last)))
        #         f.write("\n\n")
        # except:
        #     error = traceback.format_exc()
        #     self.log("crawler", "旧版本写入日志文件失败: {}".format(error), "")

        if len(missing_month_list)+len(possibly_missing_list) == 6:
            # 按value对err_dict 排序,取出错最多的
            if err_dict['user_prohibited_error'] > 0:
                return 9, 'user_prohibited_error', [], missing_month_list, possibly_missing_list, part_missing_month_list
            elif err_dict['user_multiple_loggedin_error'] > 0:
                return 9, 'user_multiple_loggedin_error', [], missing_month_list, possibly_missing_list, part_missing_month_list
            elif err_dict['crawl_error'] > 0:
                return 9, 'crawl_error', [], missing_month_list, possibly_missing_list, part_missing_month_list
            return 9, 'website_busy_error', [], missing_month_list, possibly_missing_list, part_missing_month_list

        # print('missing_month_list,', missing_month_list)
        # print('possibly_missing_list,', possibly_missing_list)
        return 0, "success", total_call_logs, missing_month_list, possibly_missing_list, part_missing_month_list

    def parse_response(self, response):
        if '404 Not Found' in response.text:
            return 0, [], 'website_busy_error', u'网站正在改版中...，现在不能查询:{}'.format(response.status_code)

        try:
            if response.text[0] == '(':
                ret_data = json.loads(response.text[1:-1])
            else:
                ret_data = json.loads(response.text)
        except:
            error = traceback.format_exc()
            return 0, [], 'json_error', 'json_error:{}'.format(error)

        error_code = ret_data['retCode']
        # print year,month,error_code
        # 错误码 '520001' 临时身份凭证不存在 在商城-四川/云南中,在网页上首次点击查询的月份或将报出该错误码,对后续查询无影响

        if error_code != '000000':
            error_msg = ret_data['retMsg']
            if error_code == '3035':
                # 云南官网异常, 营业厅有数据,但是商城报错 '3035' 超出查询范围 偶尔成功,可以直接拿到所有的数据
                return 0, [], 'website_busy_error', error_msg
            if error_code == '500003' or error_code == '500000' or error_code == '500010' \
                    or '您没有登录或者当前登录状态下您无权进行此项操作' in error_msg:
                return 0, [], 'website_busy_error', '登录会话已失效,请重新登录:{}'.format(error_msg)
            if '您选择时间段没有详单记录' in error_msg or '不支持此类实时详单查询' in error_msg:
                return 0, [], 'success', '没有详单记录'
            if '临时身份凭证不存在' in error_msg:
                # 二次验证未通过。
                # return 0, [], 'user_multiple_loggedin_error', error_msg
                return 0, [], 'website_busy_error', error_msg
            if '详单查询异常' in error_msg:
                return 0, [], 'website_busy_error', error_msg
            if '不受理详单查询' in error_msg:
                return 0, [], 'website_busy_error', error_msg
            if '不能查询详单' in error_msg:
                return 0, [], 'website_busy_error', error_msg
            if '详单禁查' in error_msg:
                return 0, [], 'user_prohibited_error', error_msg
            if '系统' in error_msg and '稍后' in error_msg:
                return 0, [], 'website_busy_error', error_msg
            if '正在进行流量控制' in error_msg:
                return 0, [], 'website_maintaining_error', error_msg
            if '不可查询' in error_msg or error_code == '2026' or '账户异常' in error_msg:
                return 0, [], 'websiter_prohibited_error', error_msg
            if 'error' in error_msg:
                return 0, [], 'website_busy_error', error_msg
            if error_code == '500002':
                # 输入手机号码为非移动号码，请确认  非移动号码无法下发短信, 登录就无法完成
                return 0, [], "website_busy_error", error_msg
            # 贵州移动返回了一次数据， retMsg为乱码   error_code为2004
            if not ret_data['data'] and error_code == '2004':
                return 0, [], 'website_busy_error', error_msg
            return 0, [], 'crawl_error', 'get_call_log_fail:{}'.format(response.text)

        # 月初详单为空，记录数为零
        if ret_data.get('totalNum', 0) == 0:
            # self.log('crawler', 'success', response)
            return 0, [], 'success', '详单为空'
        log_count = ret_data.get('totalNum', 0)
        logs = []
        if ret_data.get('data', []) != None:
            for log in ret_data.get('data', []):
                logs.append(log)
        return log_count, logs, 'success', '详单为空'

    def get_call_log_error(self, key, message, resp):
        if key in ['website_busy_error', 'website_maintaining_error', 'websiter_prohibited_error']:
            self.log('website', key, resp)
        #            已在别处登录  、                  该用户办理了详单禁查业务
        elif key in ['user_multiple_loggedin_error', 'user_prohibited_error']:
            self.log('user', key, resp)
        else:
            # message = status_key : message
            self.log('crawler', message, resp)

    def get_call_log_by_month(self, tel, year, month, province_name=None):
        part_missing = []
        call_logs = []

        url = 'https://shop.10086.cn/i/v1/fee/detailbillinfojsonp/{}'.format(tel)
        params = {
            '_': str(int(time.time() * 1000)),
            'callback': '',
            'curCuror': 1,
            'step': '100',
            'qryMonth': '{}{}'.format(year, month),
            'billType': '02',
        }
        headers = {
            # 'Connection': 'keep-alive',
            'Host': 'shop.10086.cn',
            'Referer': 'http://shop.10086.cn/i/?f=billdetailqry',
        }
        message = u"请求失败"

        time_limit = 9.0
        st_time = time.time()
        et_time = st_time + time_limit
        sig_flg = False
        first_page_retry_times = self.max_retry
        #
        rand_sleep = random.randint(30, 50) / 10.0
        log_count = 0
        while True:
            first_page_retry_times -= 1
            # self.log("crawler", "首页记录时间{}".format(time.time()), "")
            code, key, resp = self.get(url, headers=headers, params=params)
            if code == 0:
                log_count, logs, key, message = self.parse_response(resp)
                if key == 'success' and logs:
                    call_logs.extend(logs)
                    break
            self.all_retry.append(('{}{}'.format(year, month), 0))
            if code == 0:
                self.get_call_log_error(key, message, resp)
            now_time = time.time()
            if first_page_retry_times > 0:
                continue
            elif now_time < et_time:
                time.sleep(rand_sleep)
            else:
                self.retry_last.append(("{}{}".format(year, month), 0))
                if not isinstance(resp, str):
                    if resp.status_code == 404:
                        key = "website_busy_error"
                        message = '登录会话已失效,请重新登录'
                sig_flg = True
                break
        if sig_flg:
            self.log("crawler", "获取页面失败", resp)
            return key, call_logs, []

        if log_count <= 100:
            return "success", call_logs, []
        page_num = int(math.ceil(log_count / 100.0))

        page_list = list(range(1, page_num))
        page_and_retry = [(page, self.max_retry) for page in page_list]

        log_for_retry_request = []
        while page_and_retry:
            page, retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((page, retry_times))
            retry_times -= 1
            params = {
                '_': str(int(time.time() * 1000)),
                'callback': '',
                'curCuror': page*100+1,
                'step': '100',
                'qryMonth': '{}{}'.format(year, month),
                'billType': '02',
            }
            # self.log("crawler", "分页记录时间{}".format(time.time()), "")
            code, key, resp = self.get(url, headers=headers, params=params)
            if code == 0:
                log_count, logs, key, message = self.parse_response(resp)
                if key == 'success' and logs:
                    call_logs.extend(logs)
                    continue
            self.all_retry.append(('{}{}'.format(year, month), page))
            now_time = time.time()
            if retry_times > 0:
                page_and_retry.append((page, retry_times))
            elif now_time < et_time:
                len_page_retry = len(page_and_retry) or 1
                rand_sleep = time_limit / len_page_retry
                if rand_sleep < 1:
                    rand_sleep = random.randint(10, 20) / 10.0
                page_and_retry.append((page, retry_times))
                time.sleep(rand_sleep)
            else:
                self.retry_last.append(("{}{}".format(year, month), page))
                # 当不是当前月份, 将下个月也加入部分缺失列表
                if code == 0:
                    self.get_call_log_error(key, message, resp)
                current_date = datetime.datetime.now().strftime("%Y%m")
                if self.is_shandong:
                    part_missing.append('{}{}'.format(year, month))
                    if current_date != '{}{}'.format(year, month):
                        next_month = self.get_next_month(year, month)
                        part_missing.append(next_month)
                else:
                    part_missing.append('{}{}'.format(year, month))
        self.log("crawler", "{}重试记录: {}".format(month, log_for_retry_request), "")
        if part_missing:
            return key, call_logs, part_missing
        return key, call_logs, []

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
        """
        # 缺失月份
        missing_month_list = []
        def parse_response(response):
            try:
                month_bill_res = response.json()
                call_bill_list = month_bill_res.get('data',[])
                for each in call_bill_list:
                    month_fee_data = {}
                    result_list = each.get('billMaterials',[])
                    month_fee_data['bill_month'] = each.get('billMonth', '')
                    if each.get('billFee', '') in ["-0", "0.00"]:
                        missing_month_list.append(month_fee_data['bill_month'])
                        continue
                    month_fee_data['bill_amount'] = each.get('billFee', '0.00')
                    month_fee_data['bill_package'] = result_list[0].get('billEntriyValue', '0.00')
                    month_fee_data['bill_ext_calls'] = result_list[1].get('billEntriyValue', '0.00')
                    month_fee_data['bill_ext_data'] = result_list[2].get('billEntriyValue', '0.00')
                    month_fee_data['bill_ext_sms'] = result_list[3].get('billEntriyValue', '0.00')
                    month_fee_data['bill_zengzhifei'] = result_list[4].get('billEntriyValue', '0.00')
                    month_fee_data['bill_daishoufei'] = result_list[5].get('billEntriyValue', '0.00')
                    month_fee_data['bill_qita'] = result_list[6].get('billEntriyValue', '0.00')
                    month_fee.append(month_fee_data)
            except ValueError:
                error_msg = traceback.format_exc()
                return 9, 'json_error', 'json_error:{}'.format(error_msg), []
            except:
                error_msg = traceback.format_exc()
                return 9, 'unknown_error', 'unknown_error:{}'.format(error_msg), []
            return 0, "success", u"爬取月度账单成功", month_fee

        month_fee =[]
        today = date.today()
        query_date = today + relativedelta(months=-5)
        query_month = "%d%02d"%(query_date.year, query_date.month)
        url = "http://shop.10086.cn/i/v1/fee/billinfo/{}".format(kwargs['tel'])
        params = {
            "bgnMonth":"%d%02d"%(today.year, today.month),
            "endMonth":query_month,
            "_":str(int(time.time()*1000))
        }

        headers = {
            'Host': 'shop.10086.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control':'no-store, must-revalidate',
            'pragma':'no-cache',
            'Content-Type':'*',
            'If-Modified-Since':'0',
            'expires':'0',
            'Referer':'http://shop.10086.cn/i/?f=billdetailqry&welcome={}'.format(int(time.time() * 1000)),
        }

        for _ in xrange(self.max_retry):
            code_a, key, resp = self.get(url, headers=headers, params=params)
            if code_a == 0:
                code, key, message, data_list = parse_response(resp)
                if code == 0:
                    if data_list:
                        return code, key, data_list, missing_month_list
                    else:
                        message = '账单为空'
        else:
            if code_a == 0:
                if code == 0:
                    self.log('website', message, resp)
                else:
                    self.log('crawler', message, resp)
            # 六个月账单为一次请求，如果出错，按全部缺失处理。
            missing_month_list = self.get_year_month(-6, -1)
            if key in ['json_error', 'unknown_error']:
                return 9, "crawl_error", [], missing_month_list
            return 9, "website_busy_error", [], missing_month_list

if __name__ == '__main__':
    # tel = sys.argv[1]
    # pin_pwd = sys.argv[2]
    # # 其他省份-江西
    # tel = "15070876044"
    # pin_pwd = "440678"
    # # 北京
    # tel = "18201526155"
    # pin_pwd = "551625"
    # pin_pwd = "122344"
    # # 贵州
    # tel = "18275130919"
    # pin_pwd = "678534"
    # 黑龙江
    # tel = "13846194712"
    # pin_pwd = "186972"
    # # 吉林
    # tel = "15943910614"
    # pin_pwd = "193164"
    # 内蒙古
    # tel = "15849852933"
    # pin_pwd = "712469"
    # # 山西
    # tel = "15903551769"
    # pin_pwd = "193579"
    # # 四川
    # tel = "18215591773"
    # pin_pwd = "125917"
    # # 云南
    # tel = "18408726096"
    # pin_pwd = "685103"
    # 广州
    # tel = '15999917956'
    # pin_pwd = '19919619'
    # 湖北
    # tel = '15072498067'
    # pin_pwd = '102907'

    # 山东
    # tel = '15762559079'
    # pin_pwd = '348017'

    # # 广西
    # tel = '18277398591'
    # pin_pwd = '472982'

    # 福建
    # tel = '13720833802'
    # pin_pwd = '488498'
    tel = '18301495516'
    pin_pwd = '332266'
    c = Crawler()
    c.self_test(tel=tel, pin_pwd=pin_pwd)
    # print(c.get_search_list(6))
    # print c.from_call_time_get_month("1512216669", "201710")
    # print c.get_next_month(2017, "12")
    # print get_tel_info("15762559079")
    # c.get_encrypt(tel=tel, pin_pwd=pin_pwd)
