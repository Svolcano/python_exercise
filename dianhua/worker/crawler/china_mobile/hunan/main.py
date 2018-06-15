# -*- coding:utf-8 -*-

"""
@version: v1.0
@author: xuelong.liu
@license: Apache Licence
@contact: xuelong.liu@yulore.com
@software: PyCharm
@file: main.py
@time: 12/21/16 2:16 PM
"""
import base64
import sys
import urllib
import re
import hashlib
import time
import random

from datetime import date
from dateutil.relativedelta import relativedelta
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
reload(sys)
sys.setdefaultencoding('utf8')

import datetime
import json
import traceback

if __name__ == '__main__':
    sys.path.append('..')
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from base_common import BaseCommon
    from crawler.base_crawler import BaseCrawler
    from base_request_param import RequestParam
    from exec_hunan import strEnc
    from security_encode import DES
else:
    from worker.crawler.china_mobile.hunan.base_common import BaseCommon
    from worker.crawler.china_mobile.hunan.base_request_param import RequestParam
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_mobile.hunan.exec_hunan import strEnc
    from worker.crawler.china_mobile.hunan.security_encode import DES


class Crawler(BaseCrawler):
    """
    用装饰器,分别封装了
        1> 底层log,便于单个爬虫的bug 排查
        2> 默认异常抛出, 代码复用
    """
    def __init__(self, **kwargs):
        """
            kwargs 包含
                'tel': str,
                'pin_pwd': str,
                'user_id': str,
                'user_name': unicode,
                'sms_code': str,
                'captcha_code': str
            錯誤等級
                0: 成功
                1: 帳號密碼錯誤
                2: 認證碼錯誤
                9: 其他錯誤
        """
        super(Crawler, self).__init__(**kwargs)
        # self.err = False
        # self.err_desc = "success"
        # self.err_msg = ""
        # self.err_code = 0

    # def set_err_log(self, is_err=False, err_desc="success", err_code=0, err_msg=""):
    #     self.err, self.err_desc, self.err_code, self.err_msg = is_err, err_desc, err_code, err_msg

    def get_login_verify_type(self, **kwargs):
        """
        1登陆时验证方法类型
        :param kwargs:
        :return:
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        # print('登陆时验证方法类型')
        return "SMS"

    def _logg(self, key):
        user_err = ["login_param_error", "invalid_tel", "pin_pwd_error", "verify_error", "user_name_error", "user_id_error", "over_max_sms_error", "send_sms_too_quick_error", "reusable_sms", "over_query_limit", "user_prohibited_error"]
        crawler_err = ["json_error", "xml_error", "html_error", "expected_key_error", "request_error", "data_incomplete", "crawl_error", "send_sms_error", "unknown_error", "crawler_failed"]
        website_err = ["website_busy_error", "website_maintaining_error", "websiter_prohibited_error", "invalid_sid", "outdated_sid"]
        if key in user_err:
            return "user"
        elif key in website_err:
            return "website"
        else:
            if key not in crawler_err:
                self.log("crawler", "unknown_error: "+"未知的状态分类", "")
                return "crawler"
            return "crawler"

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        :param kwargs:
        :return:
        list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        # print('用list告訴我你需要哪些欄位')
        return ['pin_pwd', 'sms_verify']

    def check_tel_num(self, **kwargs):
        """
        只能检查出是否为移动用户, 官网对此请求无校验, 作用不大, 暂时不内置
        :param kwargs:
        :type kwargs:
        :return:-1, 网络异常, 0, true, 9, false
        :rtype:
        """
        url = "https://login.10086.cn/chkNumberAction.action"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://login.10086.cn/login.html?channelID=12034&backUrl=http%3A%2F%2Fwww.hn.10086.cn%2Fservice%2Fstatic%2Findex.html"
        }
        data = {"userName": kwargs.get('tel')}
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return -1, ""
        if resp.text == 'true':
            return 0, "true"
        else:
            return 9, resp.text

    def send_login_verify_request(self, **kwargs):
        """
        2宇登陆 准备 获取验证信息
        登入時，請求發送短信，或是下載圖片，或是同時發送請求
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
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
        data = {
            "userName": kwargs['tel'],
            "type": "01",
            "channelID": "12034",
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://login.10086.cn/login.html?channelID=12034&backUrl=http%3A%2F%2Fwww.hn.10086.cn%2Fservice%2Fstatic%2Findex.html"
        }
        code, key, resp = self.post("https://login.10086.cn/sendRandomCodeAction.action", headers=headers, data=data)
        if code != 0:
            return code, key, ""
        code, key, message = parse_response(resp)
        if code != 0:
            msg = '{}:{}'.format(key, message)
            self.log('user', msg, resp)
        return code, key, ''

    def get_encrypt(self, **kwargs):
        url = "https://login.10086.cn/platform/js/encrypt.js?resVer=20141125"
        headers = {
            "Accept": "*/*",
            "Referer": "https://login.10086.cn/login.html?channelID=12034&backUrl=http%3A%2F%2Fwww.hn.10086.cn%2Fservice%2Fstatic%2Findex.html"
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
        3登陆时 提交表单 实现
        :param kwargs:
            'tel': str,
            'pin_pwd': str,
            'user_id': str,
            'user_name': unicode,
            'sms_code': str,
            'captcha_code': str
        :return:
        登入時，請求發送短信，或是下載圖片，或是同時發送請求
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        # print('登陆时 提交表单 实现')
        # Building headers
        # 密码加密
        try:
            code, result = self.get_encrypt(**kwargs)
            if code != 0:
                return code, result
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密失败{}".format(error), "")
            return 9, "website_busy_error"
        timestamp = str(int(time.time())) + str(random.randint(100, 999))
        login_params = {
            "accountType": "01",
            "account": kwargs['tel'],
            "password": result,
            "pwdType": "01",
            "smsPwd": kwargs['sms_code'],
            "inputCode": "",
            "backUrl": "http://www.hn.10086.cn/service/static/index.html",
            "rememberMe": "0",
            "channelID": "12034",
            "protocol": "https:",
            "timestamp": timestamp,
        }
        # Get first login cookies
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://login.10086.cn/login.html?channelID=12034&backUrl=http%3A%2F%2Fwww.hn.10086.cn%2Fservice%2Fstatic%2Findex.html",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        url = "https://login.10086.cn/login.htm"
        code, key, resp = self.get(url, headers=headers, params=login_params)
        if code != 0:
            return code, key
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

        code, key, message, ret_data = parse_response(resp)
        if code != 0:
            if key in ['verify_error', 'pin_pwd_error', 'login_param_error', 'over_query_limit']:
                self.log('user', key, resp)
            else:
                self.log('crawler', message, resp)
            return code, key
        url = ret_data['assertAcceptURL']
        params = {
            "backUrl": 'http://www.hn.10086.cn/service/static/index.html',
            "artifact": ret_data['artifact']
        }
        # *请确认backUrl*
        for i in range(self.max_retry):
            code, key, resp = self.get(url, params=params)
            if code != 0:
                self.log("crawler", "正在进行第{}重试....".format(i+1), resp)
                continue
            else:
                break
        else:
            return code, key

        # 统一登录跳转至湖南移动验证流程
        def get_timestamp():
            return str(int(time.time()*1000))

        def get_digest(timestamp):
            digest = base64.b64encode(hashlib.md5(timestamp + "CM_201606").hexdigest())
            return digest

        def get_conversationId(timestamp):
            x = time.localtime(int(timestamp[:10]))
            time_str = time.strftime('%Y %m %d %H %M %S', x)
            fullYear, month, date, hours, minutes, seconds = time_str.split()
            milliseconds = timestamp[10:]
            if len(milliseconds) != 3:
                milliseconds = "{:0<3}".format(milliseconds)
            full_time_str = reduce(lambda x, y: x + y, [fullYear, month, date, hours, minutes, seconds, milliseconds])
            rand1 = str(random.randint(0, 999))
            if len(rand1) != 3:
                rand1 = "{:0<3}".format(rand1)
            rand2 = str(random.randint(0, 999))
            if len(rand2) != 3:
                rand1 = "{:0<3}".format(rand2)
            rand = rand1 + rand2
            conversationId = full_time_str + rand
            return conversationId

        def inner_log(resp, inner_code="0000"):
            try:
                js = resp.json()
                result = js.get("result", {})
                if result.get("response_code") != inner_code:
                    self.log("crawler", "出现未知错误, 但应该不会影响后续执行", resp)
            except:
                error = traceback.format_exc()
                self.log("crawler", "跳转验证部分异常"+error, resp)

        # 跳转前验证 注意, 在跳转过程中请始终保证headers存在Content-Type, 以确保服务器可以正常识别接收的数据
        url = "http://www1.10086.cn/web-Center/authCenter/assertionQuery.do"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.hn.10086.cn/service/static/index.html",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        timestamp = get_timestamp()
        data = "requestJson=" + urllib.quote(
            '{"serviceName":"if008_query_user_assertion","header":{"version":"1.0","timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId":"12034"}}'
            % (timestamp, get_digest(timestamp), get_conversationId(timestamp)))
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        inner_log(resp)

        url = "http://www1.10086.cn/web-Center/authCenter/checkUserLogin.do"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.hn.10086.cn/service/static/index.html"
        }
        timestamp = get_timestamp()
        data = "requestJson=" + urllib.quote(
            '{"serviceName":"","header":{"version":"1.0","timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId":"12034"}}'
            % (timestamp, get_digest(timestamp), get_conversationId(timestamp))
        )
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        inner_log(resp)
        # 该URL 可不被请求, 但是当出现未知错误时可以将其打开查看与官网的异同
        # url = "http://www1.10086.cn/web-Center/interfaceService/custInfoQry.do"
        # headers = {
        #     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        #     "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        # }
        # timestamp = get_timestamp()
        # data = "requestJson="+urllib.quote(
        #            '{"serviceName":"if007_query_user_info","header":{"version":"1.0","timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId": "0001"}}'
        #            % (timestamp, get_digest(timestamp), get_conversationId(timestamp))
        #            )
        #
        # code, key, resp = self.post(url, headers=headers, data=data)
        # if code != 0:
        #     return code, key
        # inner_log(resp)

        # url = "http://www1.10086.cn/web-Center/interfaceService/realFeeQry.do"
        # headers = {
        #     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        #     "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        # }
        # timestamp = get_timestamp()
        # data = "requestJson="+urllib.quote(
        #     '{"serviceName":"if007_query_fee","header":{"version":"1.0","timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId":"0001"}}'
        #     % (timestamp, get_digest(timestamp), get_conversationId(timestamp))
        # )
        # code, key, resp = self.post(url, headers=headers, data=data)
        # if code != 0:
        #     return code, key
        # inner_log(resp)

        # 跳转  如果遇到该跳转总是失败, 请检查 [[注释] [*请确认backUrl*]]
        url = "https://login.10086.cn/SSOCheck.action"
        headers = {"Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"}
        params = {
            "channelID": "00731",
            "backUrl": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        }
        code, key, resp = self.post(url, headers=headers, params=params)
        if code != 0:
            return code, key
        if not resp.history:
            self.log("website", "跳转失败不影响, 直接请求'http://www.hn.10086.cn/service/static/index.html'即可", resp)
            url = "http://www.hn.10086.cn/service/static/index.html"
            headers = {"Referer": "http://www.10086.cn/index/hn/index_731_731.html"}
            code, key, resp =self.get(url, headers=headers)
            if code != 0:
                return code, key



        # 跳转后验证
        url = "http://www1.10086.cn/web-Center/interfaceService/custInfoQry.do"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        }
        timestamp = get_timestamp()
        data = "requestJson="+urllib.quote(
            '{"serviceName":"if007_query_user_info","header":{"version":"1.0","timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId":"0001"}}'
            % (timestamp, get_digest(timestamp), get_conversationId(timestamp))
        )
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        inner_log(resp)


        timestamp = get_timestamp()
        url = "http://www1.10086.cn/web-Center/authCenter/checkUserLogin.do"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        }
        data = "requestJson=" + urllib.quote(
            '{"serviceName":"","header":{"version":"1.0","timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId":"12034"}}'
            % (timestamp, get_digest(timestamp), get_conversationId(timestamp))
        )
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        inner_log(resp)

        # url = "http://www1.10086.cn/web-Center/interfaceService/realFeeQry.do"
        # headers = {
        #     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        #     "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        # }
        # timestamp = get_timestamp()
        # data = "requestJson=" + urllib.quote(
        #     '{"serviceName":"if007_query_fee","header":{"version": "1.0", "timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId": "0001"}}'
        #     % (timestamp, get_digest(timestamp), get_conversationId(timestamp))
        #     )
        # code, key, resp = self.post(url, headers=headers, data=data)
        # if code != 0:
        #     return code, key
        # inner_log(resp)

        url = "http://www.hn.10086.cn/service/ics/componant/queryLoginInfo"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        }
        params = {
            "ajaxSubmitType": "post",
            "ajax_randomcode": "0.2991063980672004"
        }
        cookies = {"0.2991063980672004": "0"}
        code, key, resp = self.post(url, headers=headers, params=params, cookies=cookies)
        if code != 0:
            return code, key

        # log queryLoginInfo
        if kwargs['tel'] not in resp.text:
            self.log("crawler", "未知原因导致响应超出预期", resp)
            return 9, "website_busy_error"


        url = "http://www.hn.10086.cn/service/ics/detailBillQuery/cacheCurrentMonthDetailBill"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        }
        params = {
            "ajax_randomcode": "0.4176160274452263",
            "ajaxSubmitType": "post"
        }
        cookies = {
            "0.4176160274452263": "0"
        }
        code, key, resp = self.post(url, headers=headers, params=params, cookies=cookies)
        if code != 0:
            return code, key

        url = "http://www.hn.10086.cn/service/ics/detailBillQuery/queryUserBrand"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        }
        params = {
            "ajax_randomcode": "0.4068799713497062",
            "ajaxSubmitType": "post"
        }
        cookies = {"0.4068799713497062": "0"}
        code, key, resp = self.post(url, headers=headers, params=params, cookies=cookies)
        if code != 0:
            return code, key
        if kwargs['tel'] not in resp.text:
            self.log("crawler", "未知原因导致响应超出预期", resp)
            return 9, "website_busy_error"
        return 0, "success"

    def get_verify_type(self, **kwargs):
        """
        4二次验证方法类型
        :param kwargs:
        :return:
        """
        # print('登陆时 提交表单 实现')
        # return "SMS"
        url = "http://www.hn.10086.cn/service/ics/componant/initTelQCellCore"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        }
        params = {
            "tel": kwargs['tel'],
            "ajaxSubmitType": "post",
            "ajax_randomcode": "0.004990372424608092"
        }
        cookies = {"0.004990372424608092": "0"}
        code, key, resp = self.post(url, headers=headers, params=params, cookies=cookies)
        if code != 0:
            self.log("crawler", "未知异常导致没有返回数据", resp)
            return ""
        # 由于无法确定该请求错误是否影响后续执行, 只记录, 不中断执行
        try:
            js = resp.json()
            resultCode = str(js.get('resultCode'))
            if resultCode != "0":
                self.log("crawler", "请求初始化二次验证框失败, 不知道该错误是否影响后续运行", resp)
        except:
            error = traceback.format_exc()
            self.log("crawler", "无需处理, 该请求只是为了验证"+error, resp)
        return ""

    def send_verify_request(self, **kwargs):
        """
        5欲 二次验证  获取信息
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # print('二次验证,获取信息')
        headers = {"Referer": "http://www.hn.10086.cn/newservice/static/myMobile/detailBillQuery.html"}
        cookies = {"0.9461358208494027": "0"}
        code, key, resp = self.post(RequestParam.GET_SMS_URL_READY % kwargs["tel"], headers=headers, cookies=cookies)
        if code != 0:
            return code, key, ""
        code, key, resp = self.post(RequestParam.GET_SMS_URL % kwargs["tel"], headers=headers, cookies=cookies)
        if code != 0:
            return code, key, ""
        if resp.text.strip() == "":
            self.log("crawler", "website_busy_error", resp)
            return 9, "website_busy_error", ""

        try:
            stp_json = json.loads(resp.text)
            if stp_json.has_key("X_RESULTCODE") and str(stp_json.get("X_RESULTCODE")) == "-1":
                key, level = "unknown_error", 9

            if "短信密码已经发送到您的手机，5分钟之内有效" in stp_json.get("message").encode('utf-8'):
                return 0, "success", ""
            elif "短信密码5分钟之内有效，请不要重复获取" in stp_json.get("message").encode('utf-8'):
                key, level = "reusable_sms", 2
            else:
                key, level = "unknown_error", 9
            self.log(self._logg(key), key, resp)
            return level, key, ""
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, "unknown_error", ""

    def verify(self, **kwargs):
        """
        6二次登陆 提交 实现
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """

        # print('二次登陆 提交 实现')
        headers = {"Referer": "http://www.hn.10086.cn/newservice/static/myMobile/detailBillQuery.html"}
        cookies = {"0.012645535304207867": "0"}
        code, key, resp = self.post(RequestParam.SMS_URL % (kwargs['sms_code'], kwargs['tel']), headers=headers, cookies=cookies)
        if code != 0:
            return code, key
        try:
            if json.loads(resp.text)["CHECK_TAG"] == "0":
                return 0, 'success'
            else:
                self.log("crawler", "unknown_error", resp)
                return 9, 'unknown_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, 'unknown_error'

    def crawl_info(self, **kwargs):
        """
        获取用户信息
        :param kwargs:
        :return:
            爬取帳戶資訊
            return
                status_key: str, 狀態碼金鑰，參考status_code
                level: int, 錯誤等級
                message: unicode, 詳細的錯誤信息
                info: dict, 帳戶信息，參考帳戶信息格式
        """
        params = {
            "operType": "QUERY",
            "goodsName": "客户基本资料查询与修改",
            "goodsId": "10001945",
            "ajaxSubmitType": "post",
            "ajax_randomcode": "0.012645535304207867"
        }
        headers = {
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/myMobile-basicInfoQueryModify.html",
            'X-Requested-With': 'XMLHttpRequest'
        }
        cookies = {"0.012645535304207867": "0"}
        code, key, resp = self.post(RequestParam.GET_USER_INFO, params=params, headers=headers, cookies=cookies)
        if code != 0:
            return code, key, {}

        # 预判断json数据是否可以被正常解析
        try:
            temp = json.loads(resp.text)
            if temp.get('X_RESULTINFO', '') == 'ok':
                if not temp.get('basicInfo', ''):
                    self.log("website", "website_busy_error", resp)
                    return 9, "website_busy_error", {}
            else:
                self.log("crawler", "unknown_error", resp)
                return 9, "unknown_error", {}
            is_ok, user_info_dict = self.get_user_info(user_info=resp)
            if is_ok:
                return 0, "success", user_info_dict
            else:
                self.log("crawler", "json_error: "+user_info_dict, resp)
                return 9, 'json_error', {}
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, "unknown_error", {}

    def crawl_call_log(self, **kwargs):
        """
        获取详单历史
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        #
        url = "http://www.hn.10086.cn/service/ics/componant/initSmsCodeAndServicePwd"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"
        }
        cookies = {"0.012645535304207867": "0"}
        try:
            pwd = strEnc(kwargs['pin_pwd'], kwargs['tel'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "密码加密失败!".format(error), "")
            return 9, "website_busy_error", [], [], []

        data = {
            "smsCode": "undefined",
            "servicePwd": pwd,
            "requestTel": kwargs['tel'],
            "ajaxSubmitType": "post",
            "ajax_randomcode": "0.012645535304207867"
        }
        code, key, resp = self.post(url, headers=headers, data=data, cookies=cookies)
        if code != 0:
            return code, key, [], [], []

        url = "http://www.hn.10086.cn/service/ics/componant/initQueryMonthInfo"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html"

        }
        params = {
            "num": "6",
            "ajaxSubmitType": "post",
            "ajax_randomcode":	"0.012645535304207867"
        }
        cookies = {"0.012645535304207867": "0"}
        code, key, resp = self.post(url, headers=headers, params=params, cookies=cookies)
        if code != 0:
            return code, key, [], [], []



        # print('获取详单历史')
        pos_miss_list = []
        miss_list = []
        message_list = []
        # def time_transform(time_str,bm='utf-8',str_format="%Y-%m-%d %H:%M:%S"):
        #     #print time_str
        #     time_type = time.strptime(time_str.encode(bm), str_format)
        #     return str(int(time.mktime(time_type)))

        def time_format(time_str, **kwargs):
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

        def structured_data(response, year_month):
            if "-997" in response.text or u'服务调用异常' in response.text or "-998" in response.text:
                # -998  BOSS.APP层出现未知情况，Head和Data均无数据返回!，请确认BOSS.APP服务是否正在重启
                return 9, "website_busy_error", "服务调用异常", []
            try:
                data = json.loads(response.text)
            except:
                error = traceback.format_exc()
                key, level, message, result = "json_error", 9, "数据解析失败{}{}".format(error, response.text), []
                return level, key, message, result
            result = []

            if data.has_key('billVoice'):
                if not data['billVoice'].has_key('result'):
                    key, level, message, result = "unknown_error", 9, "获取详单未知异常\n{}".format(response.text), []
                    return level, key, message, result

                for tr in data['billVoice']['result']:
                    # 本月有详单, 则有该字段(IMSI_NUMBER)
                    if tr.has_key('IMSI_NUMBER'):
                        raw_call_from = tr['RSRV_STR2']
                        call_from_, error = self.formatarea(raw_call_from)
                        if not call_from_:
                            call_from_ = raw_call_from
                            self.log("crawler", "{}-{}".format(error, raw_call_from), "")
                        (
                            call_method, call_from, call_cost,
                            call_duration, call_time, call_tel,
                            call_to, call_type
                        ) = (
                            tr['RSRV_STR3'], call_from_, tr['RSRV_STR8'],
                            tr['CALL_DURATION'], tr['RSRV_STR1'], tr['RSRV_STR4'],
                            "", tr['ROAM_TYPE']
                        )
                        result.append({
                            "call_method": call_method, "call_from": call_from, "call_cost": call_cost,
                            "call_duration": time_format(call_duration), "call_time": self.time_transform(call_time), "call_tel": call_tel,
                            "call_to": call_to, "call_type": call_type, "month": year_month
                        })
                    else:
                        key, level, message, result = "no_call_log", 9, "请求成功, 但返回数据为空"+response.text, []
                        return level, key, message, result
                return 0, 'success', '成功', result
            else:
                key, level, message, result = "unknown_error", 9, "获取详单未知异常\n{}".format(response.text), []
                return level, key, message, result

        temp = BaseCommon().generator_time()
        month_retrys = [(x, self.max_retry) for x in temp]
        time_fee = 0
        full_time = 40.0
        rand_time = random.randint(20, 40) / 10.0
        st_time = time.time()
        crawler_error = 0
        data_list = []
        log_for_retrys = []
        retrys_limit = -4
        while month_retrys:
            month_obj, retrys = month_retrys.pop(0)
            retrys -= 1
            year, month, beginDate, endDate, timestamp = month_obj
            year_month = year + month.zfill(2)
            if retrys < retrys_limit:
                self.log("crawler", "重试完成", "")
                miss_list.append(year_month)
                continue
            log_for_retrys.append((year_month, retrys, time_fee))
            details_params = {
                "yearMonth": year_month,
                "startDay": beginDate,
                "endDay": endDate,
                "detailBillType": "1001",
                "caller": "0",
                "called": "0",
                "queryTel": "undefined",
                # "queryTel": "",
                "operType": "QUERY",
                "goodsName": "详单查询",
                "goodsId": "10001542",
                "ajaxSubmitType": "post",
                "ajax_randomcode": "0.012645535304207867",
            }
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://www.hn.10086.cn/service/static/myMobile/detailBillQuery.html",
            }
            cookies = {"0.012645535304207867": "0"}

            data = []

            code, key, resp = self.get(RequestParam.GET_CAL_LOG, params=details_params, headers=headers, cookies=cookies)
            now_month = details_params.get("yearMonth")
            if code != 0:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                else:
                    self.log("crawler", "多次重试失败", "")
                    miss_list.append(now_month)
                continue
            try:
                level, key, message, data = structured_data(resp, year_month)
            except:
                error = traceback.format_exc()
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                else:
                    self.log("crawler", "{}".format(error), resp)
                continue

            if level != 0:
                crawler_error += 1
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                else:
                    self.log("crawler", "{}\n{}".format(key, message), resp)
                    if key == "no_call_log":
                        pos_miss_list.append(now_month)
                    miss_list.append(now_month)
                continue
            data_list.extend(data)

        self.log("crawler", "重试记录{}".format(log_for_retrys), "")
        if len(miss_list+pos_miss_list) == 6:

            if crawler_error == 0:
                return 9, 'website_busy_error', [], miss_list, pos_miss_list
            else:
                return 9, 'crawl_error', [], miss_list, pos_miss_list
        return 0, 'success', data_list, miss_list, pos_miss_list

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        # print time_str
        time_type = time.strptime(time_str.encode(bm), str_format)
        return str(int(time.mktime(time_type)))

    def get_user_info(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
            user_info_dict['full_name']
            user_info_dict['id_card']
            user_info_dict['open_date']
            user_info_dict['is_realname_register']
        """
        try:
            ui = json.loads(kwargs["user_info"].text)
            user_info_dict = {}
            user_info_dict['full_name'] = ui.get('basicInfo').get('custName')
            user_info_dict['is_realname_register'] = True if ui.get('basicInfo').get('PSPT_TYPE') else False
            user_info_dict['open_date'] = self.time_transform(ui.get('basicInfo').get('OPEN_DATE'))
            # print 'open_time',self.time_transform(user_info_dict['open_date'])
            user_info_dict['address'] = ""
            user_info_dict['id_card'] = ""

            return True, user_info_dict
        except:
            error = traceback.format_exc()
            return False, error

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
        http://www.hn.10086.cn/service/ics/monthBillQuery/queryMonthBill?yearMonth=201703&operType=QUERY&goodsId=10001638&goodsName=%E8%B4%A6%E5%8D%95%E6%9F%A5%E8%AF%A2&ajaxSubmitType=post&ajax_randomcode=0.9345453186608987
        """
        month_fee = []
        today = date.today()
        miss_list = []
        message_list = []
        month_bill_url = "http://www.hn.10086.cn/service/ics/monthBillQuery/queryMonthBill?"
        search_month = [x for x in range(0,-6,-1)]
        for each_month in search_month:
            month_fee_data = {}
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d"%(query_date.year, query_date.month)
            random_tmp = str(random.random())
            month_bill_data = {
                "yearMonth":query_month,
                "operType":"QUERY",
                "goodsId":"10001638",
                "goodsName":"账单查询",
                "ajaxSubmitType":"post",
                "ajax_randomcode":random_tmp
            }

            month_bill_url_tmp = month_bill_url+urllib.urlencode(month_bill_data)
            cookies = {random_tmp: "0"}
            headers = {'X-Requested-With': 'XMLHttpRequest', "Referer": "http://www.hn.10086.cn/service/static/myMobile/monthBillQuery.html"}
            for i in range(self.max_retry):
                code, key, resp = self.post(month_bill_url_tmp, headers=headers, cookies=cookies)
                if code != 0:
                    msg = key
                    continue

                if '系统繁忙，请稍后再试' in resp.text:
                    msg = "website_busy_error"
                    continue
                try:
                    month_bill_res = resp.json()
                    if month_bill_res.get('totalFee', '') in ['0.00', '']:
                        msg = "no_data"
                        continue
                    call_bill_list = month_bill_res.get('billInfo', [])
                    month_fee_data = {}
                    month_fee_data['bill_month'] = query_month
                    month_fee_data['bill_amount'] = month_bill_res.get('totalFee', '')
                    month_fee_data['bill_package'] = call_bill_list[0].get('FEE2', '')
                    month_fee_data['bill_ext_calls'] = call_bill_list[1].get('FEE2', '')
                    month_fee_data['bill_ext_data'] = call_bill_list[2].get('FEE2', '')
                    month_fee_data['bill_ext_sms'] = call_bill_list[3].get('FEE2', '')
                    month_fee_data['bill_zengzhifei'] = call_bill_list[4].get('FEE2', '')
                    month_fee_data['bill_daishoufei'] = call_bill_list[5].get('FEE2', '')
                    month_fee_data['bill_qita'] = call_bill_list[6].get('FEE2', '')
                    # 如果都为空则不添加到集合
                    if month_fee_data['bill_amount'] == '':
                        break
                    month_fee.append(month_fee_data)
                    break
                except:
                    error = traceback.format_exc()
                    msg = "json_error: " + error
                    continue
            else:
                if msg == "website_busy_error":
                    self.log("website", msg, resp)
                else:
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


if __name__ == "__main__":
    c = Crawler()
    USER_ID = "13507439530"
    # USER_PASSWORD = "157350"
    USER_PASSWORD = "847832"

    # self_test
    # USER_ID = "18301495516"
    # USER_PASSWORD = "332266"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # c.send_login_verify_request(tel="18301495516", pin_pwd=USER_PASSWORD)
    # temp = BaseCommon().generator_time()
    # month_retrys = [(x, 3) for x in temp]
    # print month_retrys