# -*- coding: utf-8 -*-
import json
import random
import time
import traceback
import re
import execjs
import sys
import base64
import datetime
import os
from dateutil.relativedelta import relativedelta

reload(sys)
sys.setdefaultencoding("utf-8")

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler

class Crawler(BaseCrawler):
    """
    kwargs 包含
        'tel': str,
        'pin_pwd': str,
        'id_card': str,
        'full_name': unicode,
        'sms_code': str,
        'captcha_code': str
    """

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.key = ""
        self.login_data_url = ""

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        return
            list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        return ['pin_pwd', 'sms_verify']

    def get_login_verify_type(self, **kwargs):
        """
        告訴我登入的時候用什麼驗證
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        return "SMS"

    def enStr(self, data):
        js_path = "%s/enstr.js" % "/".join(os.path.abspath(__file__).split("/")[:-1])
        with open(js_path)as f:
            source = f.read()
        return execjs.compile(source).call('encryptByDES', data, self.key)

    def send_login_verify_request(self, **kwargs):
        """
        登入時，請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        time_stemp = str(int(time.time()*1000))
        start_url = "http://www.sc.10086.cn/service/login.html?url=index.html?ts={}".format(time_stemp)
        self.login_data_url = "html?ts={}".format(time_stemp)
        code, key, resp = self.get(start_url)
        if code != 0:
            return code, key, ""
        try:
            self.key = re.search(r'jsKey\"\:\"(.*)\"', resp.text).group(1)
        except:
            error = traceback.format_exc()
            self.log("crawler", 'website_busy_error: {}'.format(error), resp)
            return 9, "website_busy_error", ""
        codetype = '3004'
        for i in range(self.max_retry):
            # 获取图片
            url = "http://www.sc.10086.cn/service/actionDispatcher.do"
            data = {
                "reqUrl": "SC_VerCode",
                "busiNum": "SC_VerCode",
                "key": "LOGIN_PWD"
            }
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": start_url
            }
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                return code, key, ""
            try:
                if not resp.text.strip():
                    self.log("website", "官网返回数据为空!", resp)
                    return 9, "website_busy_error", ""
                data = resp.json()
                if data.get('resultCode') == '0':
                    key, result, cid = self._dama(base64.b64decode(data.get('resultObj')), codetype)
                    if key == "success" and result != "":
                        captcha_code = str(result).lower()
                    else:
                        return 9, key, ""
                else:
                    self.log("crawler", 'html_error: 图形验证码失败', resp)
                    return 9, "html_error", ""
            except:
                error = traceback.format_exc()
                if '"resultCode":"0"' in resp.text:
                    # 官网返回数据损坏
                    self.log("website", 'website_busy_error:{}'.format(error), resp)
                    return 9, 'website_busy_error', ''
                else:
                    self.log("crawler", 'html_error: {}'.format(error), resp)
                    return 9, "html_error", ""
            sms_url = "http://www.sc.10086.cn/service/sms.do"
            try:
                data = {
                    "busiNum": "SCLoginSMS",
                    "mobile": kwargs['tel'],
                    "smsType": "1",
                    "passwordType": "1",
                    "imgVerCode": self.enStr(captcha_code)
                }
            except:
                error = traceback.format_exc()
                self.log("crawler", 'param_error: {}{}'.format(error, captcha_code), "")
                return 9, 'website_busy_error', ""
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                # "Referer": "http://www.sc.10086.cn/service/login.html?url=index.html"
                "Referer": start_url
            }
            code, key, resp = self.post(sms_url, data=data, headers=headers)
            if code != 0:
                return code, key, ""
            try:
                result = resp.json()
                msg = result.get("resultCode")
                if msg == u'0':
                    return 0, "success", ""
                else:
                    if result.get('logicCode') == '402041207' or u'禁止继续获取' in resp.text:
                        self.log("crawler", 'over_max_sms_error', resp)
                        return 9, 'over_max_sms_error', ""
                    elif result.get('logicCode') == '4021010087' or u'查询用户信息出错' in resp.text:
                        self.log("crawler", 'invalid_tel', resp)
                        return 1, 'invalid_tel', ""
                    elif u'验证码不正确' in resp.text:
                        self._dama_report(cid)
                        self.log("crawler", 'verify_error 打码失败', resp)
                        continue
                    elif u'服务调用出错' in resp.text:
                        self.log("website", 'website_busy_error', resp)
                        return 9, 'website_busy_error', ""
                    else:
                        self.log("crawler", "send_sms_error: 验证验证码失败", resp)
                        return 9, "send_sms_error", ""
            except:
                error = traceback.format_exc()
                self.log("crawler", 'html_error: {}'.format(error), resp)
                return 9, 'html_error', ""
        else:
            self.log("user", 'verify_error 打码全部失败', resp)
            return 9, 'send_sms_error', ""

    def get_verify_type(self, **kwargs):
        """
        告訴我二次驗證用什麼驗證
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        return 'SMS'

    def login(self, **kwargs):
        login_url = "http://www.sc.10086.cn/service/actionDispatcher.do"
        try:
            data = {
                "reqUrl": "SCLogin",
                "busiNum": "SCLogin",
                "operType":	"0",
                "mobile": kwargs['tel'],
                "password": self.enStr(kwargs['pin_pwd']),
                "verifyCode": self.enStr(kwargs['sms_code']),
                "loginFormTab": "",
                "passwordType": "1",
                "url": self.login_data_url
            }
        except:
            error = traceback.format_exc()
            self.log("crawler", 'param_error: {}{}'.format(error, (kwargs['pin_pwd'], kwargs['sms_code'])), "")
            return 9, 'website_busy_error'
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.sc.10086.cn/service/login.html?url={}".format(self.login_data_url)
        }
        code, key, resp = self.post(login_url, data=data, headers=headers)
        if code != 0:
            return code, key
        try:
            result = resp.json()
            msg = result.get("logicCode")
            result_code = result.get("resultCode")
            if msg == '':
                if u'账户名与密码不匹配' in result.get('resultMsg'):
                    self.log("user", "账户名与密码不匹配", resp)
                    return 1, 'pin_pwd_error'
                if u'账号已锁定' in result.get('resultMsg'):
                    self.log("user", "密码输入超过次数账号已锁定", resp)
                    return 9, "over_query_limit"
                if u'CRM返回非JSON数据' in resp.text or u'调用ECP用户信息查询接口失败' in resp.text or u'系统繁忙' in resp.text\
                        or u"签名验证错误" in resp.text or u'CRM返回代码解析失败' in resp.text or u'服务调用出错' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    return 9, 'website_busy_error'
                if u'不允许办理' in result.get('resultMsg'):
                    self.log("user", "号码处于密码锁定日,不允许办理任何需要进行服务密码验证的业务", resp)
                    return 9, 'websiter_prohibited_error'
                if result_code != "0":
                    self.log("crawler", "或许有其他异常情况未被捕获", resp)
                    return 9, "unknown_error"
                return 0, 'success'
            elif msg == ['-3005', '-4029', '-4030', '-4005']:
                # -3005 errorMessage = "您的手机号码不存在，请确认后登录!";
                # -4029 errorMessage = "您的手机号码已停机状态，请恢复后登录!";
                # -4030 errorMessage = "短信密码仅支持四川移动用户!";
                # -4005 errorMessage = "您的手机号码已被列入黑名单，无法登录!";
                self.log("user", 'invalid_tel', resp)
                return 1, 'invalid_tel'
            elif msg in ['-4004']:
                # 4004 errorMessage = "您的IP地址已被列入黑名单，无法登录!";
                self.log("crawler", 'over_query_limit', resp)
                return 9, 'over_query_limit'
            elif msg in ['-4027', '-4006', '-4007']:
                # -4027 errorMessage = "您的短信密码在有效期范围内输入错误超过5次，请稍后重新获取!";
                # -4006 "您输入的短信验证码不正确，请重新输入
                # -4007 "短信验证码已失效，请重新获取"
                self.log("user", 'verify_error', resp)
                return 2, "verify_error"
            elif msg in ['-4028', '-4050']:
                # -4028 errorMessage = "短信密码已发送到您的手机，请稍后重新获取!";
                # -4050 errorMessage = "动态密码已发送到您的手机，1分钟后再重新获取!";
                self.log("user", 'send_sms_too_quick_error', resp)
                return 9, 'send_sms_too_quick_error'
            elif msg == '-4051' or msg == "-4002" or msg == '-4008':
                # -4051 errorMessage = "登陆用户过多，请稍后重试!";
                # -4002 "对不起，登录失败，请稍后再试!
                # -4008 短信验证码不存在，请获取短信验证码   不是短信错误, 或为偶发异常
                self.log("website", 'website_busy_error', resp)
                return 9, 'website_busy_error'
            else:
                self.log("crawler", 'unknown_error', resp)
                return 9, 'unknown_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", 'html_error: {}'.format(error), resp)
            return 9, 'html_error'

    def send_verify_img_request(self):

        verify_img_data = {
            "reqUrl": "SC_VerCode",
            "busiNum": "SC_VerCode",
            "key": "KET_XDCX_CODE"
        }
        verify_img_headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.sc.10086.cn/service/my/SC_MY_XDCX.html"
        }
        url = "http://www.sc.10086.cn/service/actionDispatcher.do"
        for i in range(self.max_retry):
            code, key, resp = self.post(url, data=verify_img_data, headers=verify_img_headers)
            if code != 0:
                return code, key, ""
            try:
                result = resp.json()
                if result.get("resultCode") == '0':
                    image_str = result.get('resultObj')
                else:
                    if u'禁止继续获取' in resp.text:
                        self.log("crawler", 'over_max_sms_error', resp)
                        return 9, 'over_max_sms_error', ""
                    self.log("crawler", 'send_sms_error', resp)
                    return 9, "send_sms_error", ""
            except:
                error = traceback.format_exc()
                self.log("crawler", 'send_sms_error: {}'.format(error), resp)
                return 9, 'send_sms_error', ""
            # 云打码
            codetype = '3004'
            key, result, cid = self._dama(base64.b64decode(image_str), codetype)
            if key == "success" and result != "":
                captcha_code = str(result).lower()
            else:
                self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                code, key = 9, "auto_captcha_code_error"
                continue
            # 验证
            url = "http://www.sc.10086.cn/service/actionDispatcher.do"
            checkout_img_data = {
                "reqUrl": "SC_VerCode",
                "busiNum": "SC_VerCode",
                "methodQuery": "validatVerCode",
                "key": "KET_XDCX_CODE",
                "code": captcha_code
            }
            checkout_img_headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": "http://www.sc.10086.cn/service/my/SC_MY_XDCX.html"
            }
            code, key, resp = self.post(url, data=checkout_img_data, headers=checkout_img_headers)
            if code != 0:
                return code, key, ""
            try:
                result = resp.json()
                if result.get('resultCode') != '0':
                    self.log("user", 'verify_error', resp)
                    code, key = 9, "auto_captcha_code_error"
                    self._dama_report(cid)
                    continue
                return 0, "success", captcha_code
            except:
                error = traceback.format_exc()
                self.log("crawler", 'json_error: {}'.format(error), resp)
                return 9, 'json_error', ""
        else:
            return 9, "auto_captcha_code_error", ""

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        verify_type = kwargs.get('verify_type', '')
        image_str = ''
        url = "http://www.sc.10086.cn/service/actionDispatcher.do"
        verify_sms_data = {
            "reqUrl": "SC_MY_XDCXQuery",
            "mothodQuery": "sendSMSCode",
            "async": "false"
        }
        verify_sms_headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.sc.10086.cn/service/my/SC_MY_XDCX.html"
        }
        code, key, resp = self.post(url, data=verify_sms_data, headers=verify_sms_headers)
        if code != 0:
            return code, key, ""
        try:
            result = resp.json()
            if result.get('resultCode') != '0':
                if u'禁止继续获取' in resp.text:
                    self.log("crawler", 'over_max_sms_error', resp)
                    return 9, 'over_max_sms_error', ""
                self.log("crawler", "send_sms_error", resp)
                return 9, "send_sms_error", ""
            return 0, "success", ""
        except:
            error = traceback.format_exc()
            self.log("crawler", 'send_sms_error: {}'.format(error), resp)
            return 9, 'send_sms_error', ""


    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        code, key, captcha_code = self.send_verify_img_request()
        if code != 0:
            return code, key
        url = "http://www.sc.10086.cn/service/actionDispatcher.do"
        # checkout_img_data = {
        #     "reqUrl": "SC_VerCode",
        #     "busiNum": "SC_VerCode",
        #     "methodQuery": "validatVerCode",
        #     "key": "KET_XDCX_CODE",
        #     "code":	kwargs['captcha_code']
        # }
        # checkout_img_headers = {
        #     "X-Requested-With": "XMLHttpRequest",
        #     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        #     "Referer": "http://www.sc.10086.cn/service/my/SC_MY_XDCX.html"
        # }
        # code, key, resp = self.post(url, data=checkout_img_data, headers=checkout_img_headers)
        # if code != 0:
        #     return code, key
        # try:
        #     result = resp.json()
        #     if result.get('resultCode') != '0':
        #         self.log("user", 'verify_error', resp)
        #         return 9, 'verify_error'
        # except:
        #     error = traceback.format_exc()
        #     self.log("crawler", 'json_error: {}'.format(error), resp)
        #     return 9, 'json_error'
        try:
            checkout_sms_data = {
                "reqUrl": "SC_MY_XDCXQuery",
                "mothodQuery": "smsverify",
                "smscode": self.enStr(kwargs['sms_code']),
                "yzmCode": captcha_code,
            }
        except:
            error = traceback.format_exc()
            self.log("crawler", 'param_error: {}'.format(error), "")
            return 9, 'website_busy_error'
        checkout_sms_headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.sc.10086.cn/service/my/SC_MY_XDCX.html"
        }
        code, key, resp = self.post(url, data=checkout_sms_data, headers=checkout_sms_headers)
        if code != 0:
            return code, key
        try:
            result = resp.json()
            if result.get('resultCode') != '0':
                self.log("user", 'verify_error', resp)
                return 9, 'verify_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", 'json_error: {}'.format(error), resp)
            return 9, 'json_error'
        return 0, "success"

    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式

        """
        user_info = {}
        url = "http://www.sc.10086.cn/service/my/SC_MY_ZHZL.html"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.sc.10086.cn/service/my/SC_MY_ZDCX.html"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, {}
        try:
            info_json = re.search(r"window\.top\.BmonPage\.commonBusiCallBack\((.*\}), ", resp.text).group(1)
            info_dict = json.loads(info_json)
            info_dict = info_dict['resultObj']['userInfo']['userInfo']
            user_info['address'] = info_dict['CONTACT_ADDRESS']
            user_info['full_name'] = info_dict['CUST_NAME']
            user_info['open_date'] = self.time_transform(info_dict['BILL_START_TIME'], str_format='%Y-%m-%d')
            user_info['id_card'] = ""
            if u'已登记' in info_dict['REAL_NAME_INFO']:
                user_info['is_realname_register'] = True
            else:
                user_info['is_realname_register'] = False
            return 0, "success", user_info
        except:
            error = traceback.format_exc()
            self.log("crawler", 'json_error: {}'.format(error), resp)
            return 9, 'json_error', {}

    @staticmethod
    def random_sleep(tm, modulus=3):
        time.sleep(random.uniform(tm / modulus / 1.5, 1.5 * tm / modulus))

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        """
        `call_tel` | string | 18202541892 | 电话号码 |
        | `call_cost` | string | 0.00 | 通话费用 |
        | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
        | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
        | `call_type` | string | 本地 | 通话类型（本地, 长途） |
        | `call_from` | string | 北京市 | 本机通话地 |
        | `call_to` | string | 长沙市 | 对方归属地 |
        | `call_duration` | integer | 300 | 通话时长(秒),
        """
        miss_list = []
        pos_miss_list = []
        result_list = []
        crawl_error = 0
        url = "http://www.sc.10086.cn/service/actionDispatcher.do"
        for search in self.__monthly_period():
            # search 201708
            data = {
                "reqUrl": "SC_MY_XDCXQuery",
                "detailBillType": "02",
                "date":	search
            }
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": "http://www.sc.10086.cn/service/my/SC_MY_XDCX.html"
            }
            start_time = time.time()
            end_time = start_time + 10
            aid_time_dict = dict()
            retry_times = self.max_retry
            log_for_retry = []
            while 1:
                log_for_retry.append((1, retry_times))
                retry_times -= 1
                code, key, resp = self.post(url, data=data, headers=headers)
                if code:
                    missing_flag = True
                elif u'用户申请了详单禁查，不允许查详单' in resp.text:
                    self.log("user", 'user_prohibited_error', resp)
                    return 9, "user_prohibited_error", [], [], []
                elif u'服务调用出错' in resp.text or u'CRM返回代码解析失败' in resp.text or '"resultCode":"1"' in resp.text:
                    missing_flag = True
                else:
                    flag = True
                    break
                now_time = time.time()
                if retry_times >= 0:
                    aid_time_dict.update({retry_times: time.time()})
                elif now_time < end_time:
                    loop_time = aid_time_dict.get(0, time.time())
                    left_time = end_time - loop_time
                    self.random_sleep(left_time)
                else:
                    flag = False
                    if missing_flag:
                        miss_list.append(search)
                    break
            self.log('crawler', '{}重试记录{}'.format(search, log_for_retry), '')
            if not flag:
                continue
            try:
                result_json = resp.json()
                result_obj = result_json['resultObj']['resultObj']['voiceList']
                if not len(result_obj):
                    pos_miss_list.append(search)
                    continue
                for i in result_obj:
                    result = {}
                    result['call_tel'] = i['otherParty']
                    result['call_cost'] = i['fee1']
                    # u'2017/07/05 18:01:45'
                    result['call_time'] = self.time_transform(i['startDate'])
                    result['call_method'] = i['trafficWay']
                    result['call_type'] = i['callClass']
                    raw_call_from = i['callPlace']
                    call_from, error = self.formatarea(raw_call_from)
                    if not call_from:
                        call_from = raw_call_from
                        # self.log("crawler", "{}-{}".format(error, raw_call_from), "")
                    result['call_from'] = call_from
                    result['call_to'] = ""
                    result['month'] = search
                    # 9秒
                    result['call_duration'] = self.time_format(i["duration"].encode('utf-8'))
                    result_list.append(result)
            except:
                crawl_error += 1
                message = traceback.format_exc()
                self.log("crawler", 'html_error: {}'.format(message), resp)
                miss_list.append(search)
                continue

            # for i in range(self.max_retry):
            #     code, key, resp = self.post(url, data=data, headers=headers)
            #     if code != 0:
            #         message = "network_request_error"
            #         continue
            #     try:
            #         if u'用户申请了详单禁查，不允许查详单' in resp.text:
            #             self.log("user", 'user_prohibited_error', resp)
            #             return 9, "user_prohibited_error", [], [], []
            #         if u'服务调用出错' in resp.text or u'CRM返回代码解析失败' in resp.text or '"resultCode":"1"' in resp.text:
            #             message = "network_request_error"
            #             continue
            #         result_json = resp.json()
            #         result_obj = result_json['resultObj']['resultObj']['voiceList']
            #         if result_obj == []:
            #             message = "no_data"
            #             continue
            #         for i in result_obj:
            #             result = {}
            #             result['call_tel'] = i['otherParty']
            #             result['call_cost'] = i['fee1']
            #             # u'2017/07/05 18:01:45'
            #             result['call_time'] = self.time_transform(i['startDate'])
            #             result['call_method'] = i['trafficWay']
            #             result['call_type'] = i['callClass']
            #             raw_call_from = i['callPlace']
            #             call_from, error = self.formatarea(raw_call_from)
            #             if not call_from:
            #                 call_from = raw_call_from
            #                 self.log("crawler", "{}-{}".format(error, raw_call_from), "")
            #             result['call_from'] = call_from
            #             result['call_to'] = ""
            #             result['month'] = search
            #             # 9秒
            #             result['call_duration'] = self.time_format(i["duration"].encode('utf-8'))
            #             result_list.append(result)
            #         break
            #     except:
            #         message = traceback.format_exc()
            #         continue
            # else:
            #     if message != "network_request_error":
            #         if message != 'no_data':
            #             crawl_error += 1
            #         self.log("crawler", 'html_error: {}'.format(message), resp)
            #     if message == "no_data":
            #         pos_miss_list.append(search)
            #     else:
            #         miss_list.append(search)
        self.log('crawler', '缺失：{}, 可能缺失：{}'.format(miss_list, pos_miss_list), '')
        if len(miss_list+pos_miss_list) == 6:
            if crawl_error == 0:
                return 9, "website_busy_error", result_list, miss_list, pos_miss_list
            return 9, 'crawler_error', result_list, miss_list, pos_miss_list
        return 0, "success", result_list, miss_list, pos_miss_list

    def time_transform(self, time_str, str_format="%Y/%m/%d %H:%M:%S"):
        # 个人信息: 2017-01-27
        # 时间 2017/12/12 12:12:12
        time_type = time.strptime(time_str, str_format)
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
        miss_list = []
        result_list = []
        crawl_error = 0
        url = "http://www.sc.10086.cn/service/actionDispatcher.do"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.sc.10086.cn/service/my/SC_MY_ZDCX.html"
        }
        FORMAT_DATA = 0.01
        for search in self.__monthly_period():
            data = {
                "reqUrl": "SC_MY_ZDCXQuery",
                "methodQuery": "personBillQuery",
                "date": search
            }
            for i in range(self.max_retry):
                code, key, resp = self.post(url, data=data, headers=headers)
                if code != 0:
                    message = "network_request_error"
                    continue
                if u'服务调用出错' in resp.text or u'CRM返回非JSON数据' in resp.text or '"resultCode":"1"' in resp.text:
                    message = "network_request_error"
                    continue
                try:
                    json_data = json.loads(resp.text)
                    json_base = json_data['resultObj']['billResult']['billInfoList']['billInfos'][0]
                    raw_data_list = json_base['detInfos']
                    raw_data_list = [str(int(x.get('FEE', 0)) * FORMAT_DATA) for x in raw_data_list]
                    result = {}
                    result['bill_month'] = json_base['YEAR_MONTH']
                    result['bill_amount'] = str(int(json_base.get('TOTAL_FEE', 0))*FORMAT_DATA)
                    result['bill_package'] = raw_data_list[0]
                    result['bill_ext_calls'] = raw_data_list[1]
                    result['bill_ext_data'] = raw_data_list[2]
                    result['bill_ext_sms'] = raw_data_list[3]
                    result['bill_zengzhifei'] = raw_data_list[4]
                    result['bill_daishoufei'] = raw_data_list[5]
                    result['bill_qita'] = raw_data_list[6]
                    result_list.append(result)
                    break
                except:
                    message = traceback.format_exc()
                    continue
            else:
                self.log("crawler", 'html_error: {}'.format(message), resp)
                if message != "network_request_error":
                    crawl_error += 1
                miss_list.append(search)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5:
            if crawl_error == 0:
                return 9, "website_busy_error", [], miss_list
        return 0, 'success', result_list, miss_list

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)


if __name__ == '__main__':
    c = Crawler()
    USER_ID = "18215591773"
    USER_PASSWORD = "125917"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
