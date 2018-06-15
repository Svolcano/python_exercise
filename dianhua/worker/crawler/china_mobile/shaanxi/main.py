# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import traceback
import base64
import calendar
import datetime
import random
import time
from lxml import etree
from scrapy.selector import Selector
from dateutil.relativedelta import relativedelta
import re
import HTMLParser
from request_params_security_js import security_js

if __name__ == '__main__':
    sys.path.append('../../../..')
from worker.crawler.base_crawler import BaseCrawler


CONST_URL_COOKIE_BEFORE_LOGIN = 'https://sn.ac.10086.cn/login'
CONST_URL_CAPTCHA_BEFORE_LOGIN = 'https://sn.ac.10086.cn/servlet/CreateImage'
CONST_URL_CAPTCHA_CHECK_BEFORE_LOGIN = 'https://sn.ac.10086.cn/servlet/CheckCode?code=%s'
CONST_URL_RSAPUBKEY_BEFORE_LOGIN = 'https://sn.ac.10086.cn/servlet/initRSAPubkey'
CONST_URL_LOGIN = 'https://sn.ac.10086.cn/loginAction'
CONST_URL_ADDUID = 'https://login.10086.cn/AddUID.action'
CONST_URL_SSO = 'https://login.10086.cn/SSOCheck.action'
CONST_URL_SSO_ARTIFACT = 'https://sn.ac.10086.cn/servlet/artifactRecv'

CONST_URL_SMS_GET_BEFORE_CALL_LOG = 'http://service.sn.10086.cn/app'
CONST_URL_SMS_VERIFY_BEFORE_CALL_LOG = 'http://service.sn.10086.cn/app'
CONST_URL_CALL_LOG = 'http://service.sn.10086.cn/app'
CONST_URL_PERSONAL_INFO = ''
CONST_URL_BILL = ''


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
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
        # print(u'登陆时验证方法类型')
        return ""

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        :param kwargs:
        :return:
        list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        # print(u'用list告訴我你需要哪些欄位')
        return ['pin_pwd']

    def send_login_verify_request(self, **kwargs):
        """
        2宇登陆 准备 获取验证信息
        登入時，請求發送短信，或是下載圖片，或是同時發送請求
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # print(u'欲登陆 准备 获取验证信息')
        headers = {
            "Referer": "http://www.10086.cn/sn/index_290_290.html"
        }
            # send captcha
        code, key, resp = self.get(CONST_URL_COOKIE_BEFORE_LOGIN, headers=headers)
        if code != 0:
            return code, key, ''
        headers = {
            "Referer": "http://sn.ac.10086.cn/uiue/login_max.jsp?message=%B5%C7%C2%BC%CA%A7%B0%DC&userName={}".format(
                kwargs["tel"])
        }
        for i in range(self.max_retry+3):
            code, key, resp = self.get(CONST_URL_CAPTCHA_BEFORE_LOGIN, headers=headers)
            if code != 0:
                continue
            headers_check_captche = {
                "Referer": "https://sn.ac.10086.cn/loginAction",
                "Accept": "application/json;charset=utf-8"
            }
            # 云打码
            codetype = 3004
            key, result, cid = self._dama(resp.content, codetype)

            if key == "success" and result != "":
                captcha_code = str(result)
            else:
                self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                code, key = 9, "auto_captcha_code_error"
                continue
            # 验证
            code, key, resp = self.get(CONST_URL_CAPTCHA_CHECK_BEFORE_LOGIN % captcha_code,
                                       headers=headers_check_captche)
            if code != 0:
                continue

            if resp.text != "0":
                self.log('user', 'verify_error', resp)
                code, key = 9, "auto_captcha_code_error"
                self._dama_report(cid)
                continue
            return 0, "success", captcha_code
        else:
            return code, key, ""

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
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        # print(u'登陆时 提交表单 实现')
        # Building headers
        # check Code and Get first login RSAPubkey

        code, key, captcha_code = self.send_login_verify_request(tel=kwargs['tel'])
        if code != 0:
            return code, key

        headers_RSAPubkey = {
            "Host": "sn.ac.10086.cn",
            "Referer": "https://sn.ac.10086.cn/login",
            "Content-Type": "application/json;charset=utf-8"
        }

        code, key, resp = self.post(CONST_URL_RSAPUBKEY_BEFORE_LOGIN, headers=headers_RSAPubkey)
        if code != 0:
            return code, key

        try:
            res_json = resp.json()
            modulus = res_json["modulus"]
            exponent = res_json["exponent"]
            pwd = kwargs["pin_pwd"]
            security_pwd = security_js(exponent, modulus, pwd)
        except:
            error = traceback.format_exc()
            self.log('crawler', 'json_error:{}'.format(error), resp)
            return 9, 'json_error'
        data = {
            "userName": kwargs["tel"],
            "toUrl": "http://www.sn.10086.cn/my/account/",
            "fromUrl": "uiue/login_max.jsp",
            "loginType": "1",
            "verifyCode": captcha_code,
            "password": security_pwd,
            "OrCookies": "1"
        }
        # Get login cookies
        headers_login = {"Referer": "https://sn.ac.10086.cn/login"}
        code, key, resp = self.post(CONST_URL_LOGIN, data=data, headers=headers_login)
        if code != 0:
            return code, key

        params = {
            "channelID": "00290",
            "backUrl": "http://service.sn.10086.cn:80/app?service=page/MyMainPage&listener=initPage&MENU_ID=&loginType=1",
        }
        code, key, resp = self.get('https://login.10086.cn/SSOCheck.action', params=params)
        if code != 0:
            return code, key
        if resp.history:
            for his in resp.history:
                if "artifact=-1" in his.text:
                    self.log("crawler", "未知原因错误", his)
                    return 9, "login_param_error"
        self.ref_url = resp.url
        return 0, 'success'

    def get_verify_type(self, **kwargs):
        """
        4二次验证方法类型
        :param kwargs:
        :return:
        """
        # print(u'登陆时 提交表单 实现')
        return "SMS"

    def send_verify_request(self, **kwargs):
        """
        5欲 二次验证  获取信息
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # print(u'二次验证,获取信息')
        headers = {
            'Host': 'service.sn.10086.cn',
            'Referer': self.ref_url,
        }
        params = {
            "ajaxSubmitType": "get",
            "ajax_randomcode": str(random.random()),
            "service": "ajaxDirect/1/MyMobileSendSms/MyMobileSendSms/javascript/null",
            "eventname": "sendSMS",
            "serialNumber": kwargs["tel"],
            "partids": "null",
            "pagename": "MyMobileSendSms"
        }

        code, key, resp = self.get(CONST_URL_SMS_GET_BEFORE_CALL_LOG, params=params, headers=headers)
        if code != 0:
            return code, key, ''

        code, key, message = self.get_send_verify_request(resp)
        if code != 0:
            if 'website_busy_error' in key:
                self.log('website', 'website_busy_error', resp)
            else:
                self.log('crawler',  message, resp)
        return code, key, ''

    def get_send_verify_request(self, response):
        try:
            response.encoding = 'utf-8'
            tree_x = etree.HTML(str(response.text).strip())
            data_list = tree_x.xpath("//*[@id='dataset']/text()")
            if data_list:
                data = data_list[0]
            else:
                try:
                    msg = re.search(r'<DATASETDATA id="dataset">(.*?)</DATASETDATA>', response.text)
                    if msg:
                        text = msg.group(1)
                        is_ok = re.search(r'SMSDESC\":\"(.*?)\"', text)
                        if is_ok:
                            is_ok = is_ok.group(1)
                        if is_ok != 'ok':
                            if u'网络繁忙' in response.text:
                                return 9, "website_busy_error", u"发送短信失败，失败原因"
                            if u'短信验证码已经下发,在1分钟内不能重复下发' in response.text:
                                self.log("crawler", "请求短信过快", response)
                                return 9, "send_sms_too_quick_error", ""
                            return 9, "send_sms_error", u"send_sms_error:请求发送验证码未知错误"
                        else:
                            return 0, "success", u"get two Auth cookies"
                    return 9, "send_sms_error", u"send_sms_error:请求发送验证码xml数据非预期"
                except:
                    error = traceback.format_exc()
                    return 9, "xml_error", u"xml_error:请求发送验证码失败,{}".format(error)
            # self.user_info_dict = eval(list)[0]
        except etree.XMLSyntaxError:
            error = traceback.format_exc()
            return 9, "xml_error", u"xml_error:请求发送验证码失败 {}".format(error)
        except:
            error = traceback.format_exc()
            return 9, "unknown_error", u"unknown_error:请求发送验证码失败{}".format(error)
        if eval(data)[0]['SMSDESC'] != 'ok':
            if u'网络繁忙' in response.text:
                return 9, "website_busy_error", u"发送短信失败，失败原因：" 
            return 9, 'send_sms_error', 'send_sms_error'
        return 0, "success", u"get two Auth cookies"

    def verify(self, **kwargs):
        """
        6二次登陆 提交 实现
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """

        # print(u'二次登陆 提交 实现')
        params = {
            "ajaxSubmitType": "get",
            "ajax_randomcode": str(random.random()),
            "service": "ajaxDirect/1/MyMobileSendSms/MyMobileSendSms/javascript/null",
            "eventname": "forgotPwd",
            "partids": "null",
            "pagename": "MyMobileSendSms",
            "SMS_NUMBER": kwargs["sms_code"]
        }
        try:
            code, key, resp = self.get(CONST_URL_SMS_VERIFY_BEFORE_CALL_LOG, params=params)
            if code != 0:
                return code, key
            resp.encoding = 'utf-8'
            tree_x = etree.XML(str(resp.text.decode("utf-8")))
            data_list = tree_x.xpath("//*[@id='dataset']/text()")[0]
            if not data_list.strip():
                self.log("crawler", "未知异常", resp)
                return 9, "xml_error"
            if eval(data_list)[0]['SMSDESC'] != 'ok':
                self.log('crawler', 'verify_error', resp)
                return 2, 'verify_error'
        except:
            error = traceback.format_exc()
            self.log('crawler', 'xml_error:{}'.format(error), resp)
            return 9, 'xml_error'

        return 0, 'success'

    def crawl_info(self, **kwargs):
        """
        获取用户信息
        :param kwargs:
        :return:
            爬取帳戶資訊
            return
                status_key: str, 狀態碼金鑰，參考status_code
                code: int, 錯誤等級
                message: unicode, 詳細的錯誤信息
                info: dict, 帳戶信息，參考帳戶信息格式
        """
        # print(u'获取用户信息')
        url = 'http://service.sn.10086.cn/app'
        crawl_info_data = {
            'service': 'page/PersonalInfoQuery',
            'listener': 'initPage',
            'type': '5',
            'random': str(random.random()),
        }

        try:
            code, key, r = self.get(url, params=crawl_info_data)
            if code != 0:
                return code, key, {}

            full_name = Selector(text=r.text).xpath('//*[@id="CUST_NAME"]/@value').extract()
            id_card = Selector(text=r.text).xpath('//*[@id="PSPT_ID"]/@value').extract()
            is_realname_register = Selector(text=r.text).xpath('//*[@id="RSRV_TAG5"]/@value').extract()
            open_date = Selector(text=r.text).xpath('//*[@id="OPEN_DATE"]/@value').extract()
            address = Selector(text=r.text).xpath('//*[@id="HOME_ADDRESS"]/@value').extract()
            user_info_dict = {'full_name': ''.join(full_name),
                              'id_card': ''.join(id_card),
                              'is_realname_register': u'已登记' in is_realname_register,
                              'open_date': self.time_transform(''.join(open_date)),
                              'address': ''.join(address),
                              }
            return 0, "success", user_info_dict
        except :
            error = traceback.format_exc()
            self.log('crawler', 'unknown_error:{}'.format(error), '')
            return 9, "unknown_error",  {}

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        # 12-06 10:26:18
        # print time_str
        if str_format == "%m-%d %H:%M:%S":
            today_month = datetime.date.today().month
            today_year = datetime.date.today().year
            str_month = int(time_str[:2])
            if str_month > today_month:
                str_year = today_year - 1
                # print '前一年%s'%str_year
            else:
                str_year = today_year
            time_str = str(str_year) + "-" + time_str

        str_format = "%Y-%m-%d %H:%M:%S"
        time_type = time.strptime(time_str.encode(bm), str_format)
        return str(int(time.mktime(time_type)))

    def random_sleep(self, tm, page=1, modulus=3):
        time.sleep(random.uniform(tm/page/modulus/3, 1.5 * tm/page/modulus))

    def crawl_call_log(self, **kwargs):
        """
        获取详单历史
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """

        # print(u'获取详单历史')
        def deal_data(time_garams):
            year, month, beginDate, endDate, timestamp = time_garams
            details_params = {
                "ajaxSubmitType": "get",
                "CUST_INFO": "%BF%CD%BB%A7%D0%C5%CF%A2",
                "service": "ajaxDirect/1/DetailedQuery/DetailedQuery/javascript/refushBusiSearchResult",
                "BILL_TYPE": "201",
                "MONTH_DAY": None,
                "MONTH": year + month.zfill(2),
                "eventname": "queryAll",
                # "pagination_iPage": 1,
                # "2017-01-31 00:00:00"
                "LAST_MONTH_DAY": year + "-" + month.zfill(2) + "-" + endDate + " 00:00:00",
                "partids": "refushBusiSearchResult",
                "ajax_randomcode": "0.3045126060946193",
                "pagename": "DetailedQuery",
                "SHOW_TYPE": "0"
            }
            details_params_page = {
                "ajaxSubmitType": "get",
                "service": "ajaxDirect/1/DetailedQuery/DetailedQuery/javascript/refushBusiSearchResult",
                "eventname": "queryAll",
                "pagination_iPage": "",
                "partids": "refushBusiSearchResult",
                "ajax_randomcode": "0.3045126060946193",
                "pagename": "DetailedQuery",
            }
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
            }
            for item in xrange(self.max_retry):
                code, key, resp = self.get(CONST_URL_CALL_LOG, params=details_params, headers=headers)
                if code == 0:
                    res = str(resp.text.decode("utf-8"))
                    if "xml version" not in res:
                        # self.log('ERROR', 'crawl_error', res, response)
                        return 9, 'request_error',  u'request_error', [], resp
                    if "#32593;&amp;#32476;&amp;#32321;&amp;#24537;&amp;#65292;&amp;#35831;\
                                            &amp;#31245;&amp;#21518;&amp;#20877;&amp;#35797;" in res:
                        # print u"是空的， 月份为: %s" %month
                        if item == 0:
                            continue
                        else:
                            return 0, 'success', '没有详单记录', [], resp
                    else:
                        break
            else:
                return code, key, key, [], resp
            try:
                tree_y = etree.HTML(res)
                content_html_elements = tree_y.xpath("//*[@id='refushBusiSearchResult']/text()")[0]
                ehtml = etree.HTML(content_html_elements)
            except:
                msg_err = traceback.format_exc()
                return 9, 'html_error', 'html_error: {}'.format(msg_err), [], resp
            call_result = []
            start_time = time.time()
            end_time = start_time + 10
            aid_time_dict = dict()
            if ehtml.xpath("//*[@class='PageLeft']/text()"):
                all_page = ehtml.xpath("//*[@class='PageLeft']/text()")[0].strip().split()[2]
                page_list = list(range(1, int(all_page) + 1))
                page_and_retry = [(page, self.max_retry) for page in page_list]
                log_for_retry = []
                while page_and_retry:
                    page, retry_times = page_and_retry.pop(0)
                    details_params_page["pagination_iPage"] = str(page)
                    log_for_retry.append((page, retry_times))
                    retry_times -= 1
                    code, key, resp = self.get(CONST_URL_CALL_LOG, params=details_params_page, headers=headers)
                    if not code:
                        res_temp = str(resp.text.decode('utf-8'))
                        if 'xml version' in res_temp:
                            try:
                                tree_temp = etree.HTML(res_temp)
                            except:
                                now_time = time.time()
                                msg_err = traceback.format_exc()
                                self.log("crawler", 'html_error in deal_data : {}'.format(msg_err), resp)
                                if retry_times >= 0:
                                    page_and_retry.append((page, retry_times))
                                    aid_time_dict.update({retry_times: time.time()})
                                elif now_time < end_time:
                                    page_and_retry.append((page, retry_times))
                                    loop_time = aid_time_dict.get(0, time.time())
                                    left_time = end_time - loop_time
                                    self.random_sleep(left_time, len(page_and_retry))
                                else:
                                    self.part_missing_list.append('{}{}'.format(year, month.zfill(2)))
                                continue
                            content_html_elements_page = tree_temp.xpath("//*[@id='refushBusiSearchResult']/text()")[0]
                            call_data = structured_data(content_html_elements_page)
                            if call_data:
                                call_result.extend(call_data)
                                continue
                    now_time = time.time()
                    if retry_times >= 0:
                        page_and_retry.append((page, retry_times))
                        aid_time_dict.update({retry_times: time.time()})
                    elif now_time < end_time:
                        page_and_retry.append((page, retry_times))
                        loop_time = aid_time_dict.get(0, time.time())
                        left_time = end_time - loop_time
                        self.random_sleep(left_time, len(page_and_retry))
                    else:
                        self.part_missing_list.append('{}{}'.format(year, month.zfill(2)))
                self.log('crawler', '{}{}重试记录:{}'.format(year, month, log_for_retry), '')
            else:
                details_params_page["pagination_iPage"] = str(1)
                retry_times = self.max_retry
                while 1:
                    retry_times -= 1
                    code, key, resp = self.get(CONST_URL_CALL_LOG, params=details_params_page, headers=headers)
                    if not code:
                        res_temp = str(resp.text.decode("utf-8"))
                        if 'xml version' in res_temp:
                            try:
                                tree_temp = etree.HTML(res_temp)
                            except:
                                now_time = time.time()
                                msg_err = traceback.format_exc()
                                self.log("crawler", 'html_error in deal_data : {}'.format(msg_err), resp)
                                if retry_times >= 0:
                                    aid_time_dict.update({retry_times: time.time()})
                                    continue
                                elif now_time < end_time:
                                    loop_time = aid_time_dict.get(0, time.time())
                                    left_time = end_time - loop_time
                                    self.random_sleep(left_time)
                                    continue
                                else:
                                    break
                            content_html_elements_page = tree_temp.xpath("//*[@id='refushBusiSearchResult']/text()")[0]
                            call_data = structured_data(content_html_elements_page)
                            if call_data:
                                call_result.extend(call_data)
                                break
                    now_time = time.time()
                    if retry_times >= 0:
                        aid_time_dict.update({retry_times: time.time()})
                        continue
                    elif now_time < end_time:
                        loop_time = aid_time_dict.get(0, time.time())
                        left_time = end_time - loop_time
                        self.random_sleep(left_time)
                    else:
                        break
            return 0, 'success', '', call_result, ''
            #     for i in xrange(1, int(all_page) + 1):
            #         details_params_page["pagination_iPage"] = str(i)
            #         for item in xrange(self.max_retry):
            #             code, key, resp = self.get(CONST_URL_CALL_LOG, params=details_params_page, headers=headers)
            #             if code != 0:
            #                 self.random_sleep()
            #                 continue
            #                 # return code, key, key, call_result, resp
            #
            #             res_temp = str(resp.text.decode("utf-8"))
            #             if "xml version" not in res_temp:
            #                 # return 9, 'request_error', 'request_error', call_result, resp
            #                 self.log("crawler", "发生错误！xml version{}".format(res_temp), resp)
            #                 self.random_sleep()
            #                 continue
            #             try:
            #                 tree_temp = etree.HTML(res_temp)
            #             except:
            #                 msg_err = traceback.format_exc()
            #                 # return 9, 'html_error', 'html_error: {}'.format(msg_err), call_result, resp
            #                 self.log("crawler", 'html_error in deal_data : {}'.format(msg_err), resp)
            #                 self.random_sleep()
            #                 continue
            #
            #             content_html_elements_page = tree_temp.xpath("//*[@id='refushBusiSearchResult']/text()")[0]
            #             call_data = structured_data(content_html_elements_page)
            #             if call_data:
            #                 call_result.extend(call_data)
            #                 break
            #         else:
            #             if not call_data:
            #                 # 如果为空则不添加到详单列表,只记录一次。
            #                 self.log('crawler', 'success', resp)
            #             self.part_missing_list.append(year + month.zfill(2))
            # else:
            #     details_params_page["pagination_iPage"] = str(1)
            #     for item in range(self.max_retry):
            #         code, key, resp = self.get(CONST_URL_CALL_LOG, params=details_params_page,headers= headers)
            #         if code != 0:
            #             return code, key, key, [], resp
            #         res_temp = str(resp.text.decode("utf-8"))
            #         if "xml version" not in res_temp:
            #             return 9, 'request_error', 'request_error', [], resp
            #         try:
            #             tree_temp = etree.HTML(res_temp)
            #         except:
            #             msg_err = traceback.format_exc()
            #             return 9, 'html_error', 'error: {}'.format(msg_err), [], resp
            #         content_html_elements_page = tree_temp.xpath("//*[@id='refushBusiSearchResult']/text()")[0]
            #         call_data = structured_data(content_html_elements_page)
            #         if call_data:
            #             call_result.extend(call_data)
            #             break
            #     else:
            #         self.log('crawler', 'success', resp)
            #
            # return 0, 'success', '', call_result, ''

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

        def generator_dict(title):
            def zip_data(list_data_values):
                list_data_source = dict(zip(title, list_data_values))
                list_data_source["call_to"] = ""
                list_data = dict(map(lambda (k, v): (k, v.strip()), list_data_source.items()))
                list_data['call_time'] = self.time_transform(list_data['call_time'], str_format="%m-%d %H:%M:%S")
                list_data['call_duration'] = time_format(list_data['call_duration'])
                raw_call_from = list_data['call_from']
                call_from, error = self.formatarea(raw_call_from)
                if not call_from:
                    call_from = raw_call_from
                list_data['call_from'] = call_from
                return list_data

            return zip_data

        def structured_data(data):
            title_params_mapping = {
                u"起始时间": "call_time",
                u"通信地点": "call_from",
                u"通信方式": "call_method",
                u"对方号码": "call_tel",
                u"通信时长": "call_duration",
                u"通信类型": "call_type",
                u"实收费": "call_cost",
                u"套餐优惠": "call_to",
            }

            ehtml = etree.HTML(data)
            table_lable_source = ehtml.xpath("//*[@id='table']/thead/tr/th/text()")
            table_lable = [title_params_mapping[v] for v in table_lable_source]
            zip_data = generator_dict(table_lable)
            finish_result = map(zip_data, [v.xpath("./td/text()") for v in ehtml.xpath("//*[@id='table']/tbody/tr")])
            return finish_result

        # 缺失月份
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        self.part_missing_list = []
        message_list = []
        temp = self.generator_time()
        call_log_result = []

        for i in temp:
            year, month, beginDate, endDate, timestamp = i
            year_month = '{}{:0>2}'.format(year, month)
            try:
                code_a, key_a, message_a, call_log_data, response_a = deal_data(i)
                if code_a != 0:
                    self.log('crawler', message_a, response_a)
                    if year_month not in missing_month_list:
                        message_list.append(key_a)
                        missing_month_list.append(year_month)
                    continue
                if call_log_data:
                    for m in call_log_data:
                        m['month'] = year_month
                    call_log_result.extend(call_log_data)
                else:
                    self.log('crawler',message_a,response_a)
                    if year_month not in possibly_missing_list:
                        possibly_missing_list.append(year_month)
            except:
                error = traceback.format_exc()
                self.log('crawler', 'unknown_error:{}'.format(error), '')
                # return 'unknown_error', 9, "获取或解析数据失败%s" % error, [], missing_month_list, possibly_missing_list
                if year_month not in missing_month_list:
                    message_list.append('unknown_error')
                    missing_month_list.append(year_month)

        part_set = set(self.part_missing_list)
        miss_set = set(missing_month_list)
        poss_set = set(possibly_missing_list)

        miss_set = miss_set - part_set - poss_set
        poss_set = poss_set - part_set


        missing_month_list = list(miss_set)
        possibly_missing_list = list(poss_set)
        part_missing_list = list(part_set)

        missing_month_list.sort(reverse=True)
        possibly_missing_list.sort(reverse=True)
        part_missing_list.sort(reverse=True)

        self.log("crawler", "缺失列表: {}, 可能缺失: {}, 部分缺失: {}".format(
            missing_month_list, possibly_missing_list, part_missing_list), "")

        if len(missing_month_list+possibly_missing_list) == 6:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], missing_month_list, possibly_missing_list, part_missing_list
            else:
                return 9, 'crawl_error', [], missing_month_list, possibly_missing_list, part_missing_list
        return 0, 'success', call_log_result, missing_month_list, possibly_missing_list, part_missing_list

    @staticmethod
    def get_YMD():
        dtime = datetime.datetime.now().strftime('%Y-%m-%d').split('-')
        return int(dtime[0]), int(dtime[1]), int(dtime[2])

    def generator_time(self):
        year, month, today = self.get_YMD()
        mt = [m for m in xrange(1, 13)]
        sm_i = mt.index(month)
        em_i = mt.index(month) - 5

        if em_i < 0:
            all_month = map(lambda x: str(x), mt[em_i:] + mt[:sm_i])
            old_year = len(mt[em_i:])
        else:
            old_year = 0
            all_month = [str(m) for m in xrange(mt[em_i], month)]

        all_month_day = [str(calendar.monthrange(year, int(m))[1]) for m in all_month]
        begin_day_list = ["1"] * len(all_month)
        all_year = [str(year - 1)] * old_year + [str(year)] * (len(all_month) - old_year)

        timestamp_list = [str(time.time())] * len(all_month)

        temp = zip(all_year, all_month, begin_day_list, all_month_day, timestamp_list)
        temp.append((str(year), str(month), u"1", str(today), str(time.time())))
        return temp

    def deal_url(url):
        params_temp = []
        url_params = url.split("?")
        flag_temp = ([params_temp.append(temp.split("=")) for temp in url_params[1].split("&")], 0) if len(
            url_params) == 2 else ("", 1)
        flag = flag_temp[1]
        return flag, url_params[0], dict(params_temp)

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        params = {
            'tel': kwargs['tel']
        }
        # 缺失月份
        missing_month_list = []
        message_list = []
        for month in self.__monthly_period(6, '%Y%m'):
            params['month'] = month
            # 账单访问出错或为空需要重试
            for item in xrange(self.max_retry):
                code, key, result = self.crawl_month_bill(**params)
                if code == 0 and result:
                    phone_bill.append(result)
                    break
            else:
                message_list.append(key)
                missing_month_list.append(month)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in missing_month_list and missing_month_list.remove(now_month)
        if len(missing_month_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], missing_month_list
        return 0, 'success', phone_bill, missing_month_list

    def crawl_month_bill(self, **kwargs):
        month_bill_url = 'http://service.sn.10086.cn/app'
        params = {
            'DATE_LASTACCT': self.get_last_day_of_month().strftime('%Y-%m-%d 00:00:00'),
            'DATE_THISACCT': self.get_first_day_of_month().strftime('%Y-%m-%d 00:00:00'),
            'MONTH': kwargs['month'],
            'ajaxSubmitType': 'get',
            'ajax_randomcode': str(random.random()),
            'eventname': 'querybyOtherMonth',
            'pagename': 'MyBillQuery',
            'partids': 'resultShow',
            'service': 'ajaxDirect/1/MyBillQuery/MyBillQuery/javascript/resultShow'
        }
        code, key, resp = self.get(month_bill_url, params=params)
        if code != 0:
            return code, key, []
        resp.encoding = 'utf-8'

        month_bill = {
            'bill_month': kwargs['month'],
            'bill_amount': '',
            'bill_package': '',
            'bill_ext_calls': '',
            'bill_ext_data': '',
            'bill_ext_sms': '',
            'bill_zengzhifei': '',
            'bill_daishoufei': '',
            'bill_qita': ''
        }

        try:
            html_parser = HTMLParser.HTMLParser()
            resp_content = html_parser.unescape(resp.text)

            fee = re.findall(u'本期费用合计：</td>\s*<td>\s*￥([\d.]+)\s*</td>', resp_content)
            if fee:
                month_bill['bill_amount'] = fee[0]
            else:
                return 9, 'success', []

            fee = re.findall(u'套餐及固定费</span>\s*</td>\s*<td>\s*￥([\d.]+)<span', resp_content)
            if fee:
                month_bill['bill_package'] = fee[0]

            fee = re.findall(u'语音费</span>\s*</td>\s*<td>\s*￥([\d.]+)<span', resp_content)
            if fee:
                month_bill['bill_ext_calls'] = fee[0]

            fee = re.findall(u'上网费</span>\s*</td>\s*<td>\s*￥([\d.]+)<span', resp_content)
            if fee:
                month_bill['bill_ext_data'] = fee[0]

            fee = re.findall(u'短彩信费</span>\s*</td>\s*<td>\s*￥([\d.]+)<span', resp_content)
            if fee:
                month_bill['bill_ext_sms'] = fee[0]

            fee = re.findall(u'增值业务费</span>\s*</td>\s*<td>\s*￥([\d.]+)<span', resp_content)
            if fee:
                month_bill['bill_zengzhifei'] = fee[0]

            fee = re.findall(u'代收费</span>\s*</td>\s*<td>\s*￥([\d.]+)<span', resp_content)
            if fee:
                month_bill['bill_daishoufei'] = fee[0]

            fee = re.findall(u'其他费用</span>\s*</td>\s*<td>\s*￥([\d.]+)<span', resp_content)
            if fee:
                month_bill['bill_qita'] = fee[0]
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error:{}'.format(error), resp)
            return 9, 'html_error', []

        return 0, 'success', month_bill

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

    # 获取月第一天
    def get_first_day_of_month(self, d=datetime.date.today()):
        year = d.year
        month = d.month
        return datetime.date(year, month, 1)

    # 获取月最后一天
    def get_last_day_of_month(self, d=datetime.date.today()):
        year = d.year
        month = d.month
        days = calendar.monthrange(year, month)[1]
        return datetime.date(year, month, 1) + datetime.timedelta(days=days - 1)


if __name__ == "__main__":
    c = Crawler()
    USER_ID = "18709257665"
    USER_PASSWORD = "530101"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # print c.generator_time()
