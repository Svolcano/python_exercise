# -*- coding: utf-8 -*-

import base64
import calendar
import datetime
import json
import random
import re
import sys
import time
import traceback
from datetime import date

from Crypto.Cipher import AES
from dateutil.relativedelta import relativedelta
from lxml import etree

import response_data
from des_js import des_encode

# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf-8")


if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from base_crawler import BaseCrawler
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
    錯誤等級
        0: 成功
        1: 帳號密碼錯誤
        2: 認證碼錯誤
        9: 其他錯誤
    """

    def __init__(self, **kwargs):
        """
        初始化
        """
        super(Crawler, self).__init__(**kwargs)
        self.err_code = 0
        self.err_desc = "success"
        self.err_msg = "success"
        # 传递参数
        self.url = ""
        self.jsessionid = ""
        self.startDate, self.endDate = "", ""

    def _logg(self, key):
        user_err = ["login_param_error", "invalid_tel", "pin_pwd_error", "verify_error", "user_name_error", "user_id_error", "over_max_sms_error", "send_sms_too_quick_error", "reusable_sms", "over_query_limit", "user_prohibited_error"]
        crawler_err = ["json_error", "xml_error", "html_error", "expected_key_error", "request_error", "data_incomplete", "crawl_error", "send_sms_error", "unknown_error", "crawler_failed"]
        website_err = ["website_busy_error", "website_maintaining_error", "websiter_prohibited_error", "invalid_sid", "outdated_sid"]
        if key in user_err:
            return "login_param_error"
        elif key in website_err:
            return "website_busy_error"
        else:
            if key not in crawler_err:
                self.log("crawl_error", "未知的状态码分类{}".format(key), "")
                return "crawl_error"
            return "crawl_error"

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        return
            list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        return ['pin_pwd', 'sms_verify', 'captcha_verify']

    def get_login_verify_type(self, **kwargs):
        """
        告訴我登入的時候用什麼驗證
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        return "Captcha"

    def send_login_verify_request(self, **kwargs):
        """
        登入時，請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # self.session.cookies.clear()
        image_url = 'https://jx.ac.10086.cn/common/image.jsp'
        payload = {
            'l': "%.10f" % (random.random() * 1000000)
        }
        headers = {
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "https://jx.ac.10086.cn/login"
        }
        code, key, resp = self.get(image_url, params=payload, headers=headers)
        if code != 0:
            return code, key, ""
        return 0, "success", base64.b64encode(resp.content)

    def get_verify_type(self, **kwargs):
        """
        告訴我二次驗證用什麼驗證
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        return 'SMSCaptcha'

    def login(self, **kwargs):
        first_url = "https://jx.ac.10086.cn/login"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.jx.10086.cn/__index.html"
        }
        code, key, resp = self.get(first_url, headers=headers)
        if code != 0:
            return code, key
        try:
            selector = etree.HTML(resp.text)
            login_sid = selector.xpath('//*[@id="normal-user"]/input[3]/@value')[0]
            login_spid = selector.xpath('//*[@id="normal-user"]/input[7]/@value')[0]
        except:
            error = traceback.format_exc()
            # "未获取到关键参数"
            self.log("crawler", "unknown_error: "+error, resp)
            return 9, "unknown_error"
        # print type(str(login_sid)),type(str(login_spid))
        login_url = "https://jx.ac.10086.cn/Login"
        try:
            login_data = {
                "from": "yanhuang",
                "sid": login_sid,
                "type": 'B',
                "backurl": "https://jx.ac.10086.cn/4login/backPage.jsp",
                "errorurl": "https://jx.ac.10086.cn/4login/errorPage.jsp",
                "spid": login_spid,
                "RelayState": "type=A;backurl=http://www.jx.10086.cn/my/;nl=3;loginFrom=null;refer=null",
                "mobileNum": des_encode(kwargs['tel']),
                "servicePassword": des_encode(kwargs['pin_pwd']),
                "smsValidCode": "",
                "validCode": kwargs['captcha_code'],
            }
        except:
            error = traceback.format_exc()
            #  "密码加密失败{}".format(error)
            self.log("crawler", 'param_error: '+error, resp)
            return 9, "param_error"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://jx.ac.10086.cn/login"
        }
        code, key, resp = self.post(login_url, data=login_data, headers=headers)
        if code != 0:
            return code, key

        if not resp.history:
            if 'SAMLart' in resp.text:
                """
                验证是否登录：
                """
                selector = etree.HTML(resp.text)
                SAMLart = selector.xpath('//input[@name="SAMLart"]/@value')[0]
                verify_url = "http://www.jx.10086.cn/my/"
                verify_data = {
                    "SAMLart": SAMLart,
                    "RelayState": "type=A;backurl=http://www.jx.10086.cn/my/;nl=3;loginFrom=null;refer=null"
                }
                code, key, verify_req = self.post(verify_url, data=verify_data)
                if code != 0:
                    return code, key
                # print verify_req.text
                if u'网龄' in verify_req.text:
                    return 0, "success"
                self.log("crawler", 'unknown_error', verify_req)
                return 9, 'unknown_error'
            else:
                self.log("crawler", "expected_key_error", verify_req)
                return 9, 'expected_key_error'
        else:
            if u'尊敬的用户，你输入的验证码错误，请重新输入！' in resp.text:
                key, level, message = 'verify_error', 2, "验证码错误"
            elif u'尊敬的用户，您输入的手机号码或用户名不存在，请您确认后重试' in resp.text:
                key, level, message = 'invalid_tel', 1, "手机号错误"
            elif u'请确认您的账号，保管好您的密码' in resp.text:
                key, level, message = 'pin_pwd_error', 1, "密码错误"
            elif u'请不要重复登录！' in resp.text:
                self.logout()
                key, level, message = "website_busy_error", 9, '查询过于频繁,请半小时后再试'
            elif u'需30分钟后再登录' in resp.text:
                key, level, message = "website_busy_error", 9, '您的账号因非正常退出，需30分钟后再登录'
            elif u'BOSS系统' in resp.text:
                key, level, message = "website_busy_error", 9, '运营商系统异常, 请稍后再试{}'.format(resp.text)
            else:
                key, level, message = "unknown_error", 9, "get unknown_err：%s" % resp.text
        self.log("crawler", key, resp)
        return level, key

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        params1_url = "http://service.jx.10086.cn/service/showBillDetail!queryShowBillDatailN.action?menuid=000200010003"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.jx.10086.cn/my/"
        }
        code, key, resp = self.get(params1_url, headers=headers)
        if code != 0:
            return code, key, ""
        cookies = resp.headers['Set-Cookie']
        jsessionids = re.search(r"JSESSIONID=(.*?);", cookies)
        try:
            self.jsessionid = jsessionids.group(1)
            params2_data = {}
            selector = etree.HTML(resp.text)
            params2_data['SAMLRequest'] = selector.xpath('//input[@name="SAMLRequest"]/@value')[0]
            params2_data['RelayState'] = selector.xpath('//input[@name="RelayState"]/@value')[0]
            params2_url = "https://jx.ac.10086.cn/POST"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "http://service.jx.10086.cn/service/showBillDetail!queryShowBillDatailN.action?menuid=000200010003"
            }
        except:
            error = traceback.format_exc()
            self.log("crawler", 'html_error: '+error, resp)
            return 9, "html_error", ""
        code, key, resp = self.post(params2_url, data=params2_data, headers=headers)
        if code != 0:
            return code, key, ""
        try:
            params3_data = {}
            selector = etree.HTML(resp.text)
            params3_data['displayPics'] = ''
            params3_data['displayPic'] = selector.xpath('//input[@name="displayPic"]/@value')[0]
            params3_data['RelayState'] = selector.xpath('//input[@name="RelayState"]/@value')[0]
            params3_data['isEncodeMobile'] = selector.xpath('//input[@name="isEncodeMobile"]/@value')[0]
            params3_data['isEncodePassword'] = selector.xpath('//input[@name="isEncodePassword"]/@value')[0]
            params3_data['SAMLart'] = selector.xpath('//input[@name="SAMLart"]/@value')[0]
            params3_data['menuid'] = selector.xpath('//input[@name="menuid"]/@value')[0]
            params3_url = "http://service.jx.10086.cn/service/showBillDetail!queryShowBillDatailN.action"
        except:
            error = traceback.format_exc()
            self.log("crawler", 'html_error: '+error, resp)
            return 9, "html_error", ""
        code, key, resp = self.post(params3_url, data=params3_data)
        if code != 0:
            return code, key, ""
        try:
            selector = etree.HTML(resp.text)
            self.sms_sid = selector.xpath('//*[@id="loginForm"]/input[7]/@value')[0]
            self.sms_spid = selector.xpath('//*[@id="loginForm"]/input[4]/@value')[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", 'xml_error: '+error, resp)
            return 9, "xml_error", ''

        send_sms_url = "https://jx.ac.10086.cn/SMSCodeSend"
        send_sms_data = {
            'mobileNum': kwargs['tel'],
            'errorurl': 'http://service.jx.10086.cn/service/common/ssoPrompt.jsp',
            'spid': self.sms_spid
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.jx.10086.cn/service/checkSmsPassN.action?menuid=000200010003"
        }
        code, key, resp = self.post(send_sms_url, data=send_sms_data, headers=headers)
        if code != 0:
            return code, key, ""
        if resp.history:
            if '短信验证码已发送到您的手机，请注意查收' in resp.text:
                return self.send_login_verify_request()
            else:
                self.log("crawler", "unknown_error", resp)
                return 9, "unknown_error", ""
        else:
            self.log("crawler", "unknown_error", resp)
            return 9, "unknown_error", ""

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        """
        第二种验证方式:
        servicePassword:440678
        validCode:crh3
        Submit2:确定
        type:B
        loginStatus:B
        loginFlag:false
        spid:ff8080812a38aae6012a38b4796c0004
        backurl:http://service.jx.10086.cn/service/backAction.action?menuid=000200010003
        errorurl:http://service.jx.10086.cn/service/common/ssoPrompt.jsp
        sid:39397B32E3123B0D36D0F4AA9D10EC99
        mobileNum:15070876044
        ssoImageUrl:https://jx.ac.10086.cn/common/image.jsp
        menuid:000200010003
        """
        check_sms_url = "https://jx.ac.10086.cn/Login"
        check_sms_data = {
            "smsValidCode": kwargs['sms_code'],
            "validCode": kwargs['captcha_code'],
            "submitBtn": u'确定',
            "type": 'A',
            "loginStatus": 'A',
            "loginFlag": 'false',
            "spid": self.sms_spid,
            "backurl": 'http://service.jx.10086.cn/service/backAction.action?menuid=000200010003',
            "errorurl": 'http://service.jx.10086.cn/service/common/ssoPrompt.jsp',
            "sid": self.sms_sid,
            "mobileNum": '15070876044',
            "ssoImageUrl": 'https://jx.ac.10086.cn/common/image.jsp',
            "ssoSmsUrl": 'https://jx.ac.10086.cn/SMSCodeSend',
            "menuid": '000200010003'
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.jx.10086.cn/service/checkSmsPassN.action?menuid=000200010003"
        }
        code, key, resp = self.post(check_sms_url, data=check_sms_data, headers=headers)
        if code != 0:
            return code, key
        # print resp.history,resp.text

        if resp.history:
            if u'尊敬的用户，短信验证码不存在，请您稍后再试！'in resp.text:
                key, level, message = "verify_error", 2, "短信码不存在：%s" % resp.text
            elif u'对不起，您输入的附加码错误，请重新输入' in resp.text:
                key, level, message = "verify_error", 2, "附加码错误：%s" % resp.text
            elif u'请不要重复登录！' in resp.text:
                key, level, message = "website_busy_error", 9, '查询过于频繁,请半小时后再试'
            elif u"BOSS未知错误" in resp.text:
                key, level, message = "website_busy_error", 9, '运营商BOSS系统异常{}'.format(resp.text)
            else:
                key, level, message = 'expected_key_error', 9, "失败：%s" % resp.text
            self.logout()
            self.log(self._logg(key), key, resp)
            return level, key
        else:
            if 'location.replace' in resp.text:
                try:
                    self.call_log_url = re.search(r"<script>location.replace\('(.*?)'\);</script>", resp.text).group(1)
                    return 0, "success"
                except:
                    error = traceback.format_exc()
                    self.log("crawler", "html_error: "+error, resp)
                    return 9, "html_error"
            else:
                self.log("crawler", "param_error", resp)
                return 9, "param_error"

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
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://service.jx.10086.cn/service/queryPersonalInfoN.action?menuid=000200030004"
        }
        realname_register_url = "http://www.jx.10086.cn/my/queryXXNew2.do"
        code, key, resp = self.post(realname_register_url, headers=headers)
        if code != 0:
            return code, key, {}
        # print resp.text
        """
        {'full_name': full_name,
        'id_card': id_card,
        'is_realname_register': is_realname_register,
        'open_date': open_date}
        """
        try:
            realname_register_res = json.loads(resp.text)
            user_info['full_name'] = realname_register_res['name']
            user_info['open_date'] = self.time_transform(realname_register_res['cdate'], str_format="%Y-%m-%d")
            user_info['id_card'] = realname_register_res.get('regn', '')
            user_info['address'] = realname_register_res['addr']
            if user_info['id_card']:
                user_info['is_realname_register'] = True
            else:
                user_info['is_realname_register'] = False
        except:
            error = traceback.format_exc()
            self.log("crawler", 'json_error: '+error, resp)
            return 9, "json_error", {}

        return 0, "success", user_info

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
        同一手机号限定半小时只能登录查一次详单
        """
        self.miss_list, self.pos_miss_list = [], []
        headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "https://jx.ac.10086.cn/Login"
            }
        code, key, resp = self.get(self.call_log_url, headers=headers)
        if code != 0:
            return code, key, [], self.miss_list, self.pos_miss_list
        today = date.today()
        call_log = []
        call_log_url = "http://service.jx.10086.cn/service/showBillDetail!billQueryCommit.action"
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            startDate = "%d%02d01" % (query_date.year, query_date.month)
            endDay = calendar.monthrange(query_date.year, query_date.month)[1]
            endDate = "%d%02d%s" % (query_date.year, query_date.month, endDay)
            clientDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            requestStartTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S.%f')[:-3]
            self.startDate, self.endDate = startDate, endDate
            call_log_data = {
                'billType': '202',
                'startDate': startDate,
                'endDate': endDate,
                'clientDate': clientDate,
                'menuid': '00890201',
                'requestStartTime': requestStartTime,
            }
            # print call_log_data
            headers = {"X-Requested-With": "XMLHttpRequest"}
            for i in range(self.max_retry):
                code, key, resp = self.post(call_log_url, data=call_log_data, headers=headers)
                if code != 0:
                    continue
                year_month = "%d%02d" % (query_date.year, query_date.month)
                key, level, message, res = self.call_log_get(resp, year_month)
                if level == 0:
                    call_log.extend(message)
                    break
        return 0, "success", call_log, self.miss_list, self.pos_miss_list

    def logout(self):
        logout_url = "https://login.10086.cn/logout.htm?backUrl=http://www.10086.cn/jx/index_791_791.html"
        """https://jx.ac.10086.cn/logout"""
        code, key, resp = self.get(logout_url)
        # 请求成功失败对本次查询无影响
        self.session.cookies.clear()

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        # 个人信息: 20170127
        if str_format == "%Y-%m-%d":
            time_str = time_str[:4]+'-'+time_str[4:6]+'-'+time_str[6:]+" 12:00:00"
        if str_format == "%Y-%m-%d %H:%M:%S":
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

    def time_format(self, ):
        pass

    def repl(self, stt):
        # 用于将 u"\\u1234\\u4321" 转为 u"\u1234\u4321"
        stt = stt.decode('unicode-escape')
        return stt

    def call_log_get(self, response, year_month):
        """
        | `update_time` | string | 更新时间戳 |
        | `call_cost` | string | 爬取费用 |
        | `call_time` | string | 通话起始时间 |
        | `call_method` | string | 呼叫类型（主叫, 被叫） |
        | `call_type` | string | 通话类型（本地, 长途）  |
        | `call_from` | string | 本机通话地 |
        | `call_to` | string | 对方归属地 |
        | `call_duration` | string | 通话时长 |
        """
        # totalcount 记录数
        upper_layer, response = response, response.text
        for i in range(self.max_retry):
            if 'totalcount="0"' in response:
                key, level, data, response = "no_data", 0, [], upper_layer
                continue
            records = []
            selector = etree.HTML(response.decode('utf-8'))
            l_total_record_count = selector.xpath("//*[@id='totalvalue']/text()")
            if l_total_record_count:
                total_record_count = int(l_total_record_count[0])
            else:
                key, level, data, response = "unknown_error", 9, "数据非预期, 无法继续%s" % response, upper_layer
            if total_record_count > 20:
                jsessionid = self.jsessionid
                if not jsessionid:
                    # 参数 jsessionid 是从获取登录验证码时获取的, 无法获取response
                    self.miss_list.append(year_month)
                    return "unknown_error", 9, "未知错误获取jsessionid失败%s" % self.jsessionid, ""
                headers = {
                    "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest"
                }
                origin_url = "http://service.jx.10086.cn/service/dwr/engine.js?_{}".format(int(time.time() * 1000))
                code, key, resp = self.get(origin_url, headers=headers)
                if code != 0:
                    return key, code, "", ""

                if "_origScriptSessionId" in resp.text:
                    ssid_list = re.search(r'_origScriptSessionId = \"(.*)\"', resp.text)
                    ssid = str(ssid_list.group(1)) + str(random.randint(100, 999))
                else:
                    key, level, data, response = "unknown_error", 9, "未知错误获取 origScriptSessionId 失败test:%s" % resp.text, resp
                    continue
                clientdate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                clientdate = clientdate.split()[0]+'%20'+clientdate.split()[1]
                self.url = "/service/showBillDetail!queryIndex.action?billType=202&startDate={}&endDate={}&clientDate={}&menuid=00890201&requestStartTime=".format(self.startDate, self.endDate, clientdate)
                # 必須頂格寫, 不能有空格在前面, 或者可以用\n來換行
                line1 = "callCount=1\npage={url}\nhttpSessionId={jsessionid}\nscriptSessionId={ssid}\nc0-scriptName=queryBill\nc0-methodName=getHtml\n"
                line2 = "c0-id=0\nc0-param0=number:0\nc0-param1=number:{total_record_count}\nc0-param2=boolean:false\nbatchId=0"
                data = (line1 + line2).format(url=self.url, jsessionid=jsessionid, ssid=ssid, total_record_count=total_record_count)
                url = "http://service.jx.10086.cn/service/dwr/call/plaincall/queryBill.getHtml.dwr"
                code, key, resp = self.post(url, data=data, headers={'Content-type': 'text/plain;', "Accept": "*/*"})
                if code != 0:
                    key, level, data, response = key, code, "网络错误", resp
                    continue
                try:
                    html = resp.text
                    str_data = re.search(r"\{(.*?)\}", html, re.S)
                    str_data = str_data.group(1)
                    str_data = "{\"\"\""+str_data+"\"\"\"}"
                    data = eval(str_data)
                    str_list = list(data)[0]
                    list_data = eval("{"+str_list+"}")
                    # data = list_data["list"]
                    records = []
                    for i in list_data["list"]:
                        data = {}
                        data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        data['call_cost'] = self.repl(i[8])
                        data['call_time'] = self.time_transform(self.repl(i[0]))
                        data['call_method'] = self.repl(i[2])
                        data['call_type'] = self.repl(i[5])
                        data['call_from'] = self.repl(i[1])
                        data['call_to'] = ''
                        data['call_tel'] = self.repl(i[3])
                        data['month'] = year_month
                        # data['call_duration'] = self.repl(i[4])
                        duration = self.repl(i[4])
                        ret = re.findall('\d+', duration)
                        if len(ret) == 3:
                            data['call_duration'] = str(int(ret[0])*3600+int(ret[1])*60+int(ret[2]))
                        elif len(ret) == 2:
                            data['call_duration'] = str(int(ret[0])*60+int(ret[1]))
                        else:
                            data['call_duration'] = str(ret[0])
                        records.append(data)
                        key, level, data, response = "success", 0, records, resp
                    return key, level, data, response
                except:
                    error = traceback.format_exc()
                    key, level, data, response = "unknown_error", 9, error, resp
                    continue
            try:
                call_form = selector.xpath('//table[@id="datatable"]/tr')
                # print call_form
                for item in call_form[1:]:
                    data = {}
                    data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    data['call_cost'] = item.xpath('.//td[9]/text()')[0]
                    data['call_time'] = self.time_transform(item.xpath('.//td[1]/text()')[0])
                    data['call_method'] = item.xpath('.//td[3]/text()')[0]
                    data['call_type'] = item.xpath('.//td[6]/text()')[0]
                    data['call_from'] = item.xpath('.//td[2]/text()')[0]
                    data['call_to'] = ''
                    data['call_tel'] = item.xpath('.//td[4]/text()')[0]
                    data['month'] = year_month
                    duration = item.xpath('.//td[5]/text()')[0]
                    ret = re.findall('\d+', duration)
                    if len(ret) == 3:
                        data['call_duration'] = str(int(ret[0])*3600+int(ret[1])*60+int(ret[2]))
                    elif len(ret) == 2:
                        data['call_duration'] = str(int(ret[0])*60+int(ret[1]))
                    else:
                        data['call_duration'] = str(ret[0])
                    records.append(data)
                return "success", 0, records, upper_layer
            except:
                error = traceback.format_exc()
                key, level, data, response = "html_error", 9, error, upper_layer
                continue
        else:
            if key == 'no_data':
                self.log("crawler", key+data, resp)
                self.pos_miss_list.append(year_month)
            else:
                self.log("crawler", key+data, response)
                self.miss_list.append(year_month)
        return key, level, data, response

    # def month_bill(self, **kwargs):
    #     today = date.today()
    #     month_bill_data = {}
    #     # month_bill_data['accNum'] = self.tel
    #     month_bill_data['requestStartTime'] = ''
    #     month_bill_data['menuid'] = '00890104'
    #     month_bill_data['queryMonth'] = '%d%02d' % (today.year, today.month)
    #     month_bill_data['s'] = random.random()
    #     month_bill_url = "http://service.jx.10086.cn/service/queryWebPageInfo.action"
    #     headers = {
    #         "Accept": "*/*",
    #         "X-Requested-With": "XMLHttpRequest"
    #     }
    #     code, key, resp = self.post(month_bill_url, data=month_bill_data, headers=headers)
    #     if code != 0:
    #         return code, key
    #     if level != 0:
    #         self.log("request_error", message, month_bill_req)
    #         return key, level, message, []
    #     if u"myData = new Array" in month_bill_req.text:
    #         return "success", 0, "get info", self.bill_log(month_bill_req.text)
    #     elif "PRIV_NOT_ALLOW" in month_bill_req.text:
    #         return "user_exit", 9, "用户未登录", []
    #     else:
    #         return "unknown_error", 9, 'unknown_err:%s' % month_bill_req.text, []

    def bill_log(self, response):
        # 目前返回一个列表，元素为一个字典，键暂定费用及月份
        records = []
        today = date.today()
        ret = re.search(r"var myData = new Array(.+)", response).group(1)
        bill_data = re.findall(r'\d+\.\d{2}', ret)
        search_month = [x for x in range(-1, -7, -1)]
        for item in search_month:
            data = {}
            query_date = today + relativedelta(months=item)
            data['update_time'] = "%d%02d" % (query_date.year, query_date.month)
            data['call_cost'] = bill_data[abs(item)-1]
            records.append(data)
        return records

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        # today = datetime.datetime.now().strftime('%Y%m')
        miss_list = []
        for searchMonth in self.__monthly_period(5, '%Y%m'):
            crawl_phone_bill_data = {
                'queryMonth': searchMonth,
                's': random.random()
            }
            headers = {
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest"
            }
            URL_PHONE_BILL = 'http://service.jx.10086.cn/service/queryWebPageInfo.action'
            for i in range(self.max_retry):
                code, key, resp = self.get(URL_PHONE_BILL, params=crawl_phone_bill_data, headers=headers)
                message = "网络错误"
                if code != 0:
                    continue
                key, level, message, result = response_data.phone_bill_data(resp.text, searchMonth)
                # print result
                if level != 0:
                    continue
                if result:
                    phone_bill.append(result)
                    break
            else:
                miss_list.append(searchMonth)
                self.log("request_error", message, resp)
        return 0, 'success', phone_bill, miss_list

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset+1)).strftime(strf)

if __name__ == '__main__':
    c = Crawler()
    # USER_ID = "15070871111"
    USER_ID = "15070876044"
    # USER_PASSWORD = "440677"
    USER_PASSWORD = "440678"

    # self_test

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # print c.crawl_call_log()
    # print c.month_bill()

    # print c.aes_encrypt('578020')
    # print c.bill_log()
