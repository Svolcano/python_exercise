# -*- coding:utf-8 -*-

import base64
import datetime
import json
import re
import sys
import time
import traceback
from datetime import date

import lxml
import lxml.html

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA

from dateutil.relativedelta import relativedelta
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf8')


if __name__ == '__main__':
    sys.path.append('../../..')
    sys.path.append('../../../..')
    sys.path.append('..')
    sys.path.append('../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


class Crawler(BaseCrawler):

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
        return "SMS"

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        :param kwargs:
        :return:
        list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        return ['pin_pwd', 'sms_verify']

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
        # 获取登录cookies
        code, key, resp = self.get('https://gd.ac.10086.cn/login')
        if code != 0:
            return code, key, ""
        code, key, resp = self.get('https://gd.ac.10086.cn/ucs/ucs/weblogin.jsps?backURL=http://gd.10086.cn/commodity/index.shtml')
        if code != 0:
            return code, key, ''

        # 开始获取短信验证码
        url = "https://gd.ac.10086.cn/ucs/ucs/getSmsCode.jsps"
        data = {"mobile": kwargs['tel']}
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://gd.ac.10086.cn/ucs/ucs/weblogin.jsps?backURL=http://gd.10086.cn/commodity/index.shtml"
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key, ""
        resp_json = resp.json()
        res_code = resp_json.get('returnCode', '')
        if res_code == '1000':
            return 0, "success", ''
        elif res_code == '9999':
            self.log('user', 'send_sms_too_quick_error', resp)
            return 9, 'send_sms_too_quick_error', ''
        elif res_code == '1000030009' or res_code == '9080109999' or res_code == '1000050004':
            # '9999' "failMsg":"尊敬的客户：您的动态密码发送失败，请重新点击获取。如有疑问请及时联系在线客服哦，感谢您的支持！"
            # '1000030009' "failMsg":"数据格式出错:根据appId[501143, -1]在未找到能力管控过程[1000030009]"
            # '9080109999' Failed to invoke the method sendSmsRandomCode in the service com.asiainfo.gdm.ecop.common.provider.service.TSmstempService
            self.log("website", "website_busy_error", resp)
            return 9, 'website_busy_error', ''
        elif res_code == '9100060004':
            self.log("user", u"超过最大发送次数", resp)
            return 9, "over_max_sms_error", ""
        else:
            self.log("crawler", 'send_sms_error', resp)
            return 9, 'send_sms_error', ''

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
        login_form_url = "https://gd.ac.10086.cn/ucs/ucs/webForm.jsps"
        login_params = {
            "mobile": kwargs['tel'],
            "smsPwd": kwargs['sms_code'],
            "loginType": "1",
            "cookieMobile": "on",
            "backURL": "http://gd.10086.cn/commodity/index.shtml"
        }
        # Get first login cookies
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://gd.ac.10086.cn/ucs/ucs/weblogin.jsps?backURL=http://gd.10086.cn/commodity/index.shtml"
        }
        code, key, resp = self.post(login_form_url, data=login_params, headers=headers)
        if code != 0:
            return code, key
            # print response.text
        try:
            res_json = json.loads(resp.text)
            """
                {"backUrl":"","failMsg":"图形验证码错误，请重新输入！","returnCode":"9999"}
                {"backUrl":"","failMsg":"系统异常[commons.system.exception][9080179999]","returnCode":"9080179999"}
                {"backUrl":"http:\/\/gd.10086.cn\/commodity\/index.shtml","failMsg":"成功[0]","returnCode":"1000"}
            """
            return_code = res_json.get('returnCode')
            if "调用" in resp.text and '失败' in resp.text or '能力鉴权失败' in resp.text:
                key, level, message = 'website_busy_error', 9, "官网错误:{}".format(resp.text)
            elif return_code == '9080010007' or '动态密码错误' in resp.text:
                # 动态码输错不会使动态码失效, 但是服务密码错会使动态码失效
                key, level, message = 'verify_error', 2, "动态密码错误:{}".format(res_json)
            elif return_code == '1009999999':
                # {\"backUrl\":\"\",\"failMsg\":\"根据key[U_ID]未能在Map[{U_ID=null}]中查到对应值[1009999999]\",\"returnCode\":\"1009999999\"}
                key, level, message = 'website_busy_error', 9, "根据key[U_ID]未能在Map[{U_ID=null}]中"+"查到对应值:{}".format(res_json)
            elif '系统异常' in res_json.get('failMsg'):
                key, level, message = 'website_busy_error', 9, u"系统异常:{}".format(res_json)
            elif '调用服务失败' in res_json.get('failMsg'):
                key, level, message = 'website_busy_error', 9, u"调用服务失败:{}".format(res_json)
            elif '简单密码' in res_json.get('failMsg'):
                key, level, message = 'sample_pwd', 9, u"服务密码简单,请登录官方网站修改后查询:{}".format(res_json)
            elif res_json.get('returnCode') == "1000":
                key, level, message = 'success', 0, ''
            elif '后台从session中没有获取到验证码' in resp.text:
                key, level, message = 'website_busy_error', 9, 'request error:{},{}'.format(res_json, resp.request.headers)
            elif '锁定' in resp.text or '0336005004' == return_code:
                key, level, message = 'over_query_limit', 9, '账号被锁定{}'.format(resp.text)
            elif '客户鉴权失败' in resp.text or '0336005002' == return_code:
                key, level, message = 'login_param_error', 9, '客户鉴权失败{}'.format(resp.text)
            elif '应用无访问该能力的权限' in resp.text or '1000010060' == return_code:
                key, level, message = 'website_busy_error', 9, '未知原因导致: 应用无访问该能力的权限{}'.format(resp.text)
            elif '系统升级中' in resp.text or '1000060002' == return_code:
                key, level, message = 'website_maintaining_error', 9, '为更好提供服务，系统升级中，请稍候'
            elif '非法应用请求' in resp.text or '9080010013' == return_code:
                # 未输入短信验证码
                key, level, message = 'verify_error', 2, '非法应用请求'
            elif '构造服务' in resp.text or '1000010035' == return_code or 'SocketException' in resp.text or '1009999002' == return_code:
                key, level, message = 'website_busy_error', 9, '构造服务[checkWhiteBlackIpList]出错'
            elif '查询归属地失败' in resp.text:
                key, level, message = 'invalid_tel', 9, '查询归属地失败'
            else:
                key, level, message = 'expected_key_error', 9, "error_response:{}".format(res_json)
            if level != 0:
                if level in [1, 2]:
                    self.log("user", key, resp)
                elif key == 'website_busy_error' or key == 'over_query_limit':
                    self.log("website", key, resp)
                else:
                    self.log("crawler", key, resp)
                return level, key
            level, key, message = self.verify(**kwargs)
            if level != 0:
                return level, key
            return level, key
        except:
            msg = traceback.format_exc()
            self.log("crawler", 'unknown_error: '+msg, resp)
            return 9, 'unknown_error'

    def get_verify_type(self, **kwargs):
        """
        4二次验证方法类型
        :param kwargs:
        :return:
        """
        # print('登陆时 提交表单 实现')
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
        return 0, "success", ""

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
        query_date = datetime.datetime.today().strftime('%Y%m%d')
        url = "http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/index.jsps"
        data = {
            "servCode": "REALTIME_LIST_SEARCH",
            "operaType": "QUERY",
            "Payment_startDate": "{}000000".format(query_date),
            "Payment_endDate": "{}235959".format(query_date)
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Referer": "http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml",
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key, ""

        try:
            url_json = resp.json()
            content_url = url_json.get('content')
            headers = {"Referer": "http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml"}
            code, key, resp = self.get(content_url, headers=headers)
            if code != 0:
                return code, key, ""
            data = resp.text
            rt_channel = re.findall(r'"channel": "(.*?)"', data, re.S)[0]
            rt_st = re.findall(r'"st": "(.*?)"', data, re.S)[0]
            rt_sign = re.findall(r'"sign": "(.*?)"', data, re.S)[0]
            rt_token = re.findall(r'"token": "(.*?)"', data, re.S)[0]
            rt_appid = re.findall(r'"appid": "(.*?)"', data, re.S)[0]
            rt_backURL = re.findall(r'"backURL": "(.*?)"', data, re.S)[0]

            # 获取加密后的服务密码
            code, key, encrypt_text = self.get_encrypt(**kwargs)
            if code != 0:
                return code, key, ""

            post_data = {
                "mobile": kwargs['tel'],
                # "serPwd": kwargs['pin_pwd'],
                "encryptItems": encrypt_text,
                "saType": '2',
                "channel": rt_channel,
                "st": rt_st,
                "sign": rt_sign,
                "token": rt_token,
                "appid": rt_appid,
                "backURL": rt_backURL
            }
            send_data_url = "https://gd.ac.10086.cn/ucs/ucs/secondAuth.jsps"
            headers = {"X-Requested-With": "XMLHttpRequest", "Referer": content_url}
            code, key, resp = self.post(send_data_url, data=post_data, headers=headers)
            if code != 0:
                return code, key, ""
            resp_json = resp.json()
            return_code= resp_json.get('returnCode', '')
            if return_code == '1000':
                return 0, "success", ""
            elif return_code == '0337004003' or return_code == '0337004006':
                # 0337004006 用户原密码为简单密码
                self.log("user", "pin_pwd_error", resp)
                return 9, "pin_pwd_error", ""
            elif return_code == '0337004004' or u'被锁定' in resp.text:
                self.log("user", "over_query_limit", resp)
                return 9, "over_query_limit", ""
            elif return_code == '1000050004' or return_code == '1000050005'\
                    or return_code == '111' or '中间件调用失败' in resp.text:
                self.log("website", '服务调用失败:CRM服务[SERVICE_CRM_ccchkauthcheck]返回超时', resp)
                return 9, "website_busy_error", ""
            elif u"java" in resp.text and u"Exception" in resp.text:
                self.log("website", u"官网异常", resp)
                return 9, "website_busy_error", ""
            else:
                self.log("crawler", "unknown_error", resp)
                return 9, "unknown_error", ""
        except:
            error = traceback.format_exc()
            if u'/pmarketing/error/404.jsp' in resp.text or u'<span>用户登录' in resp.text or u'自定义查询详单' in resp.text:
                self.log("crawler", 'website_busy_error', resp)
                return 9, 'website_busy_error', ""
            else:
                self.log("crawler", "解析页面错误{}".format(error), resp)
                return 9, "unknown_error", ""


    # 服务密码加密
    def get_encrypt(self, **kwargs):
        """
            JSEncrypt 加密，用python 方式实现
        """
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
        }

        url = 'http://gd.ac.10086.cn/ucs/ucs/decryptToken/generate.jsps'
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ""

        decrypt_param = json.loads(resp.text)
        # 私钥
        random_key = decrypt_param['decryptToken']
        public_key = decrypt_param['publicKey']
        # 公钥
        publik_key = """-----BEGIN PUBLIC KEY-----
        {}
        -----END PUBLIC KEY-----""".format(public_key)

        serPwd = kwargs['pin_pwd']
        plain_text = 'serPwd:' + serPwd + '|randomKey:' + random_key;
        rsakey = RSA.importKey(publik_key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(plain_text.encode('utf-8')))

        return 0, 'success', cipher_text

    def crawl_info(self, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
            user_info_dict['full_name']
            user_info_dict['id_card']
            user_info_dict['open_date']
            user_info_dict['is_realname_register']
        """
        info = {}
        info['full_name'] = ""
        info['id_card'] = ""
        info['open_date'] = ""
        info['address'] = ""
        info['is_realname_register'] = True
        headers = {}
        url = 'http://gd.10086.cn/commodity/servicio/myService/queryservicecustomizationLeft.jsps'
        code, key, resp = self.post(url)
        if code != 0:
            return code, key, {}
        url = 'http://gd.10086.cn/commodity/servicio/myService/queryBaseInfo.jsps'
        code, key, resp = self.post(url, headers=headers)
        if code != 0:
            return code, key, {}
        code, key, resp = self.get('http://gd.10086.cn/my/myService/myBasicInfo.shtml', headers=headers)
        if code != 0:
            return code, key, {}
        # today = date.today()
        url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/mobileInfoQuery/index.jsps'
        data = {
            'operaType': 'QUERY',
            'servCode': 'MY_BASICINFO'
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key, {}
        try:
            doc = lxml.html.document_fromstring(resp.text)
            trs = doc.xpath("//table[@class='tb_b']//tr")
            info = {}
            status_key, level = 'crawl_error', 9
            info['full_name'] = trs[0].xpath('td')[1].text_content().strip() if len(trs[0].xpath('td')) > 1 else kwargs['full_name']
            info['id_card'] = trs[2].xpath('td')[1].text_content().strip()
            info['open_date'] = self.time_transform(trs[5].xpath('td')[1].text_content().strip(), str_format="%Y-%m-%d")
            info['is_realname_register'] = False
            info['address'] = ''
            realname = trs[2].xpath('td')[3].text_content().strip()
            if u'已' in realname:
                info['is_realname_register'] = True
            status_key, level, info = 'success', 0, info
        except:
            error = traceback.format_exc()
            self.log("crawler", 'crawl_error: '+error, resp)
            return 9, 'crawl_error', {}
        if level != 0:
            self.log("crawler", status_key, resp)
        return level, status_key, info

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        # print time_str
        if str_format == "%Y-%m-%d %H:%M:%S":
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
        time_type = time.strptime(time_str.encode(bm), str_format)
        return str(int(time.mktime(time_type)))

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

        url = "http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/index.jsps"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Referer": "http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml"
        }
        query_date = datetime.datetime.today().strftime('%Y%m%d')
        data = {
            "servCode":	"REALTIME_LIST_SEARCH",
            "operaType": "QUERY",
            "Payment_startDate": "{}000000".format(query_date),
            "Payment_endDate": "{}235959".format(query_date)
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            pass
        if isinstance(resp, str):
            pass
        else:
            if u"当天查询详单已达" in resp.text:
                self.log('website', 'over_query_limit', resp)
                return 9, "over_query_limit", [], [], []
        # print('获取详单历史')
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
                real_time = h*60*60 + m*60 + s
            if (exec_type == 2):
                xx = re.findall(r'\d*', time_str)
                h, m, s = map(int, xx[::2])
                real_time = h*60*60 + m*60 + s
            return str(real_time)
        
        # 获得请求通话记录所必须的rand值
        def get_rand_params(year_month):
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml",
                "Accept": "*/*"
            }
            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/query.jsps'
            data = {
                'month': '%s' % (year_month)
            }
            code, key, resp = self.post(url=url, data=data, headers=headers)
            if code != 0:
                return code, key, "", resp
            try:
                obj = json.loads(resp.text)
                rand = obj['attachment'][0]['value']
            except:
                if "登录" in resp.text:
                    self.log("crawler", "website_busy_error", resp)
                    return 9, "website_busy_error", "需要重新登录{}".format(resp.text), resp
                if "ucs.client.error" in resp.text:
                    self.log("crawler", 'website_busy_error', resp)
                    return 9, "website_busy_error", "请求失败{}".format(resp.text), resp
                self.log("crawler", 'json_error', resp)
                return 9, "json_error", "json_parse_error:{}".format(resp.text), resp
            return 0, '', rand, resp

        # 请求一个月的页面
        def get_pages(year_month):

            code, key, rand, resp_message = get_rand_params(year_month)
            if code != 0:
                return code, key, "", resp_message

            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/ajaxRealQuery.jsps'
            data = {
                'startTimeReal': '',
                'endTimeReal': '',
                'uniqueTag': rand,
                'month': '',
                'monthListType': '0',
                'isChange': ''
            }
                        
            headers = {"X-Requested-With": "XMLHttpRequest"}
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                return code, key, "network_request_error", resp
            question_set = [u"realtimelistsearch.timevalite.error", u'由于网络繁忙导致办理该业务未成功', u"系统错误视图", u"发生错误，请稍后再试。", u"ucs.client.error.notonline"]
            # ucs.client.error.notonline 登录超时
            web_flag = 0
            for q in question_set:
                if '新版详单查询失败，请稍后再试' in resp.text:
                    web_flag = 0
                else:
                    web_flag = 1 if q in resp.text else 0

            if web_flag:
                return 9, "website_busy_error", resp.text, resp

            # 每天只能查6次
            if u"请明天再来查询" in resp.text:
                self.log('website', 'over_query_limit', resp)
                return 9, 'over_query_limit', resp.text, resp 

            if 'ServiceFailException' in resp.text:
                if '新版详单查询失败，请稍后再试' in resp.text:
                    return 0, 'success', resp.text, resp
                return 9, 'website_busy_error', 'crawl call_log fails:{}'.format(resp .text), resp
            return 0, 'success', resp.text, resp

        # 处理一个月的数据
        def parse_call_record(json_str, year_month):
            """
            {
                u'becall': u'被叫',
                u'chargefee': u'0.00',
                u'contnum': u'18210637050',
                u'conttype': u'本地',
                u'giftfee': u'-',
                u'period': u'11秒',
                u'place': u'北京',
                u'taocantype': u'8元4G飞享套餐（省内）',
                u'time': u'12-08 10:24:03',
            }
            """
            records = []
            # {"content":{"leftTimes":"-2","successful":false,"totalTimes":"5"},"type":"initPage"}
            if '"leftTimes":"-2"' in json_str:
                return False, "success查询成功, 但是查询次数已超出限制"
            try:
                obj = json.loads(json_str)
                objs = obj['content']["realtimeListSearchRspBean"]['calldetail']["calldetaillist"]
            except:

                error = traceback.format_exc()
                if "新版详单查询失败，请稍后再试" in str(json_str):
                    return False, "success新版详单查询失败，请稍后再试"
                if "系统错误" in str(json_str) and "失败" in str(json_str):
                    return False, "website_busy_error{}".format(json_str)
                if "无查询结果" in str(json_str):
                    return False, "success无查询结果"
                if "发生错误，请稍后再试" in str(json_str):
                    return False, "website_busy_error{}".format(json_str)
                return False, "parse_json_err:{},json_str:{}".format(error, json_str)
            # 月度为空
            if len(objs) == 1 and not objs[0]['contnum']:
                return True, {}
            for _obj in objs:
                call_from_set = set()
                try:
                    record = {}
                    record['month'] = year_month
                    record['start_time'] = _obj['time']
                    record['call_time'] = self.time_transform(_obj['time'])
                    record['call_duration'] = time_format(_obj['period'])
                    record['call_tel'] = _obj['contnum']
                    record['call_cost'] = _obj['chargefee']
                    raw_call_from = _obj['place']
                    call_from, error = self.formatarea(raw_call_from)
                    if not call_from:
                        call_from = raw_call_from
                        call_from_set.add(raw_call_from)
                    record['call_from'] = call_from
                    record['call_to'] = ''
                    record['call_method'] = _obj['becall']
                    record['call_type'] = _obj['conttype']
                    records.append(record)
                except:
                    error = traceback.format_exc()
                    # print "转换时间格式失败%s"%error
                    return False, "转换时间格式失败%s" % error
                if call_from_set:
                    self.log("crawler", "call_from_set: {}".format(call_from_set), resp)
            return True, records

        today = date.today()
        records = []
        pos_miss_list = []
        miss_list = []
        message_list = []

        must_missing = today + relativedelta(months=-5)
        must_missing_year_month = '%d%02d' % (must_missing.year, must_missing.month)
        miss_list.append(must_missing_year_month)

        # 5个月数据处理 官网限制每天查询5次
        count_down_month = -5
        delta_months = [i for i in range(0, count_down_month,  -1)]
        for delta_month in delta_months:
            # 每个月都 max_retry
            for _ in xrange(1):
                query_date = today + relativedelta(months=delta_month)
                year_month = '%d%02d' % (query_date.year, query_date.month)
                # "201705"
                level, key, text, req = get_pages(year_month)
                if level == 0:
                    # 分析每个月的数据
                    parse_status, result = parse_call_record(text, year_month)
                    if not parse_status:
                        if "website" in result:
                            key, message = 'pos_miss', result
                        elif "success" in result:
                            # 失败, 但是错误被忽略
                            key, message = 'pos_miss', result
                        else:
                            key, message = 'json_error', result
                        continue
                    # 成功并且为空, 可能缺失
                    if parse_status and not result:
                        key, message = 'pos_miss', result
                        continue
                    if result:
                        records.extend(result)
                        break
                else:
                    key, message = key, text
                    continue
            else:
                if message != "network_request_error":
                    self.log("crawler", "{}\n{}".format(key, message), req)
                if key == 'pos_miss':
                    pos_miss_list.append(year_month)
                else:
                    message_list.append(key)
                    miss_list.append(year_month)
        if len(miss_list+pos_miss_list) == 6:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('pos_miss') or 0, message_list)
            if temp_list.count(0) > 0:
                return 9, "crawl_error", [], miss_list, pos_miss_list
            return 9, 'website_busy_error', [], miss_list, pos_miss_list
        return 0, 'success', records, miss_list, pos_miss_list

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
        month_fee = []
        miss_list = []
        message_list = []
        today = date.today()
        search_month = [x for x in range(-1, -6, -1)]
        month_bill_url1 = 'http://gd.10086.cn/commodity/servicio/nostandardserv/billSearch/judge.jsps'
        month_bill_url2 = 'http://gd.10086.cn/commodity/servicio/nostandardserv/billSearch/queryNewBill1.jsps'
        month_bill_data2 = {
            'servCode': 'BILL_SEARCH',
            'operaType': 'QUERY'
        }
        # 获取账单页面, 需要访问两个URL
        for query_month in search_month:
            month_fee_data = {}
            query_date = today + relativedelta(months=query_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)+'27'
            month_bill_data1 = {"date": query_month}
            for i in range(self.max_retry):
                code, key, resp = self.post(month_bill_url1, data=month_bill_data1)
                if code == 0:
                    break
            else:
                message_list.append(key)
                miss_list.append("%d%02d" % (query_date.year, query_date.month))
                continue
                # return 9, "website_busy_error", [], miss_list
            
            for i in range(self.max_retry):
                code, key, resp = self.post(month_bill_url2, data=month_bill_data2)
                if code != 0:
                    message = "network_request_error"
                    continue

                if u'新版账单查询失败' in resp.text or u'暂无新版账单数据，请稍后再试' in resp.text:
                    message = "no_data"
                    continue
                try:
                    month_fee_data['bill_month'] = "%d%02d" % (query_date.year, query_date.month)
                    selector = etree.HTML(resp.text)
                    bill_amount = selector.xpath('//span[@class="color_2"]/text()')[0]
                    bill_amount = re.findall('\d+.\d+', bill_amount)[0]
                    if bill_amount == u'0.00':
                        message = "no_data"
                        continue
                    else:
                        month_fee_data['bill_amount'] = bill_amount

                    bill_package = re.findall(r'套餐及固定费用</strong></td>\s+<td class="bg1">.*?</td>', resp.content)[0]
                    bill_package = re.findall('\d+.\d+', bill_package)

                    if not bill_package:
                        month_fee_data['bill_package'] = '0.00'
                    else:
                        month_fee_data['bill_package'] = bill_package[0]

                    bill_ext_calls = re.findall(r'语音通信费</td>\s+<td class="bg1">.*?</td>', resp.content)[0]
                    bill_ext_calls = re.findall('\d+.\d+', bill_ext_calls)

                    if not bill_ext_calls:
                        month_fee_data['bill_ext_calls'] = '0.00'
                    else:
                        month_fee_data['bill_ext_calls'] = bill_ext_calls[0]

                    bill_ext_data = re.findall(r'上网费</td>\s+<td>.*?</td>', resp.content)[0]
                    bill_ext_data = re.findall('\d+.\d+', bill_ext_data)

                    if not bill_ext_data:
                        month_fee_data['bill_ext_data'] = '0.00'
                    else:
                        month_fee_data['bill_ext_data'] = bill_ext_data[0]

                    bill_ext_sms = re.findall(r'短彩信</td>\s+<td class="bg1">.*?</td>', resp.content)[0]
                    bill_ext_sms = re.findall('\d+.\d+', bill_ext_sms)

                    if not bill_ext_sms:
                        month_fee_data['bill_ext_sms'] = '0.00'
                    else:
                        month_fee_data['bill_ext_sms'] = bill_ext_sms[0]

                    bill_zengzhifei = re.findall(r'增值业务费</strong></td>\s+<td>.*?</td>', resp.content)[0]
                    bill_zengzhifei = re.findall('\d+.\d+', bill_zengzhifei)

                    if not bill_zengzhifei:
                        month_fee_data['bill_zengzhifei'] = '0.00'
                    else:
                        month_fee_data['bill_zengzhifei'] = bill_zengzhifei[0]

                    bill_daishoufei = re.findall(r'代收费业务费用</strong></td>\s+<td class="bg1">.*?</td>', resp.content)[0]
                    bill_daishoufei = re.findall('\d+.\d+', bill_daishoufei)
                    if not bill_daishoufei:
                        month_fee_data['bill_daishoufei'] = '0.00'
                    else:
                        month_fee_data['bill_daishoufei'] = bill_daishoufei[0]

                    bill_qita = re.findall(r'其它（代他人付费等）</strong></td>\s+<td>.*?</td>', resp.content)[0]
                    bill_qita = re.findall('\d+.\d+', bill_qita)
                    if not bill_qita:
                        month_fee_data['bill_qita'] = '0.00'
                    else:
                        month_fee_data['bill_qita'] = bill_qita[0]
                except:
                    error = traceback.format_exc()
                    message = "html_error: " + error
                    continue
                month_fee.append(month_fee_data)
                break
            else:
                if message != "network_request_error":
                    self.log("crawler", message, resp)
                miss_list.append("%d%02d" % (query_date.year, query_date.month))
                message_list.append(key)
        if len(miss_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) > 0:
                return 9, "crawl_error", [], miss_list
            return 9, 'website_busy_error', [], miss_list
        return 0, "success", month_fee, miss_list


if __name__ == "__main__":
    c = Crawler()
    # USER_ID = "15999917956"
    # USER_PASSWORD = "19919619"
    USER_ID = "13724284044"
    USER_PASSWORD = "48849899"


    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
