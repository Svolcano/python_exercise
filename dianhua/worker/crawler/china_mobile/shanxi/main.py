# -*- coding: utf-8 -*-
import random
import sys
import os

import datetime
import execjs
import re
import traceback

import time

from dateutil.relativedelta import relativedelta
from lxml import etree

import sys

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
        self.ref_login_sms_url = ""
        self.sms_spid = ""
        self.login_refer_url = ""

    def get_login_verify_type(self, **kwargs):
        return "SMS"

    def get_verify_type(self, **kwargs):
        return "SMS"

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def send_login_verify_request(self, **kwargs):
        # 获取登录cookies
        get_login_url = 'https://sx.ac.10086.cn/login'
        code, key, resp = self.get(get_login_url)
        if code != 0:
            return code, key, ""
        """
        next_url = ""
        if not resp.text.strip():
            return 9, "unknown_error", ""
        try:
            next_url = re.search(r'replace\(\'(.*)\'\)', resp.text).group(1)
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error: "+error, resp)
            return 9, "html_error", ""
        headers = {"Referer": "https://sx.ac.10086.cn/login"}
        code, key, resp = self.get(next_url, headers=headers)
        if code != 0:
            return code, key, ""
        """
        try:
            replace_url = re.findall(r"location.replace\(\'(.*?)\'\)", resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error: {}".format(error), resp)
            return 9, "html_error", ""
        headers = {"Referer": get_login_url}
        code, key, resp = self.get(replace_url, headers=headers)
        if code != 0:
            return code, key, ""

        self.login_refer_url = resp.url
        if not resp.text.split():
            self.log("website", "官网下发数据为空", resp)
            return 9, "website_busy_error", ""
        try:
            et = etree.HTML(resp.text)
            self.sms_spid = et.xpath("//input[@id='spid']/@value")[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取spid失败{}".format(error), resp)
            return 9, "html_error", ""
        # 获取短信验证码
        data = {
            "mobileNum": kwargs['tel'],
            "errorurl":	"https://sx.ac.10086.cn/4login/errorPage.jsp",
            "name":	"menhu",
            "validCode": "0000",
            "isCheckImage":	"false",
            "displayPic": "0",
            "spid": self.sms_spid
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            # "Referer": self.ref_login_sms_url
            "Referer": replace_url
        }
        post_sms_url = "https://sx.ac.10086.cn/SMSCodeSend"
        code, key, resp = self.post(post_sms_url, headers=headers, data=data)
        if code != 0:
            return code, key, ""
        if u'短信验证码已发送' in resp.text:
            return 0, "success", ""
        elif u'获取短信验证码太频繁' in resp.text or u'操作频繁' in resp.text:
            self.log("user", u"获取短信验证码太频繁", resp)
            return 9, 'send_sms_too_quick_error', ""
        elif u'已达到1小时最多能获取短信验证码的次数' in resp.text:
            self.log("user", u"已达到1小时最多能获取短信验证码的次数", resp)
            return 9, 'send_sms_too_quick_error', ""
        elif u'您已达到1天最多能获取短信验证码的次数' in resp.text:
            self.log("user", u"您已达到1天最多能获取短信验证码的次数", resp)
            return 9, 'over_max_sms_error', ""
        elif u'发送短信失败' in resp.text:
            self.log("website", u"发送短信失败", resp)
            return 9, 'send_sms_error', ""
        else:
            self.log("crawler", "send_sms_error", resp)
            return 9, "send_sms_error", ""

    def enStr(self, pwd, code=0):
        js_path = "%s/enStr.js" % "/".join(os.path.abspath(__file__).split("/")[:-1])
        with open(js_path, 'r') as f:
            js_content = f.read()
            ctx = execjs.compile(js_content)
            new_pwd = ctx.call("enString", pwd, code)
            return new_pwd
        return ''

    def login(self, **kwargs):
        login_url = "https://sx.ac.10086.cn/Login"
        try:
            data = {
                "type": "C",
                "backurl": "https://sx.ac.10086.cn/4login/backPage.jsp",
                "errorurl": "https://sx.ac.10086.cn/4login/errorPage.jsp",
                "spid": self.sms_spid,
                "RelayState": "",
                "webPassword": "",
                "mobileNum": kwargs['tel'],
                "displayPic": "",
                "isValidateCode": "",
                "isCheckImage": "false",
                "mobileNum_temp": kwargs['tel'],
                "servicePassword": self.enStr(kwargs['pin_pwd']),
                "smsValidCode": kwargs['sms_code'],
                "validCode": "%B5%E3%BB%F7%BB%F1%C8%A1"
            }
        except:
            error = traceback.format_exc()
            self.log("crawler", "param_error: {} . password was {}".format(error, kwargs['pin_pwd']), "")
            return 9, "website_busy_error"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            # "Referer": self.ref_login_sms_url
            "Referer": self.login_refer_url
        }
        code, key, resp = self.post(login_url, data=data, headers=headers)
        if code != 0:
            return code, key
        if resp.history:
            if u'6002' in resp.text or u'验证码不存在' in resp.text or u'尊敬的用户，请您输入正确的短信验证码后重试' in resp.text or u'验证码已失效' in resp.text or u'验证码错误' in resp.text:
                self.log("user", 'verify_error', resp)
                return 9, "verify_error"
            # pwd = chaochao960813!! 会出现请求报文格式错误
            elif u'账户名与密码不匹配' in resp.text or u'请求报文格式错误' in resp.text:
                self.log("user", 'pin_pwd_error', resp)
                return 9, 'pin_pwd_error'
            elif u'密码过于简单' in resp.text:
                self.log("user", 'sample_pwd', resp)
                return 9, 'sample_pwd'
            elif u'请确认您的密码' in resp.text or u'密码有误' in resp.text:
                self.log("user", 'pin_pwd_error', resp)
                return 9, 'pin_pwd_error'
            elif u'该用户名为空' in resp.text or u'手机号码或宽带号不存在' in resp.text or u'手机号码或宽带号无权登录' in resp.text or u'该号码非IMS用户' in resp.text or u'非山西号码' in resp.text or u'号码不存在' in resp.text:
                self.log("user", 'invalid_tel', resp)
                return 1, 'invalid_tel'
            elif u'IP被列入黑名单' in resp.text or u'IP登录过于频繁暂时被限制登录' in resp.text:
                # IP登录过于频繁暂时被限制登录
                self.log("crawler", 'crawler_failed', resp)
                return 9, 'crawler_failed'
            elif u'该用户被列入黑名单' in resp.text or u'被锁定' in resp.text or u'密码锁定' in resp.text or u'被限制登录' in resp.text:
                self.log("user", 'over_query_limit', resp)
                return 9, 'over_query_limit'
            elif u'系统繁忙，请您稍后重试' in resp.text or u'未知错误，请您稍后重试' in resp.text or u'BOSS响应超时' in resp.text or u'登录签名验证错误' in resp.text:
                self.log("website", 'website_busy_error', resp)
                return 9, 'website_busy_error'
            elif not resp.text.strip():
                self.log("user", 'pin_pwd_error', resp)
                return 9, 'pin_pwd_error'
            elif u'登录多次错误' in resp.text:
                self.log("user", "连续错误次数过多", resp)
                return 9, "send_sms_too_quick_error"
            else:
                self.log("crawler", "未知错误", resp)
                return 9, "unknown_error"
        if not resp.text.strip():
            self.log("website", u"官网下发数据为空", resp)
            return 9, "website_busy_error"
        try:
            url = re.findall(r"location.replace\(\'(.*?)\'\)", resp.text)[0]
        except:
            error = traceback.format_exc()
            if 'code=9001' in resp.text:
                self.log('user', 'verify_error:{}'.format(error), resp)
                return 9, 'verify_error'
            self.log("crawler", 'html_error: {}'.format(error), resp)
            return 9, 'html_error'
        #
        # url = "https://sx.ac.10086.cn/4login/backPage.jsp"
        # data = {}
        # try:
        #     et = etree.HTML(resp.text)
        #     kv_list = et.xpath("//*[@type='hidden']")
        #     for i in kv_list:
        #         data[i.xpath('./@name')[0]] = i.xpath('./@value')[0]
        # except:
        #     error = traceback.format_exc()
        #     self.log("crawler", 'html: {}'.format(error), resp)
        #     return 9, 'html_error'
        # headers = {
        #     "Content-Type": "application/x-www-form-urlencoded",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        #     "Referer": "https://sx.ac.10086.cn/Login"
        # }
        # code, key, resp = self.post(url, data=data, headers=headers)
        # if code != 0:
        #     return code, key
        headers = {"Referer": "https://sx.ac.10086.cn/Login"}
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key

        try:
            SAMLart = re.findall(r"parent.callBackurl\(\'(.*)\'\)", resp.text)[0]
        except:
            if resp.text.strip() == '':
                self.log("website", '官网返回空数据', resp)
                return 9, 'website_busy_error'
            error = traceback.format_exc()
            self.log("crawler", '获取SAMLart失败: {}'.format(error), resp)
            return 9, 'html_error'

        url = "http://service.sx.10086.cn/my/"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }
        data = {
            "SAMLart": SAMLart,
            "RelayState": ""
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key

        url = "http://service.sx.10086.cn/login/toLoginSso.action"
        data = {}
        try:
            if not resp.text.strip():
                self.log("website", u"官网下发数据为空", resp)
                return 9, "website_busy_error"

            et = etree.HTML(resp.text)
            for i in et.xpath("//input"):
                data[i.xpath("./@name")[0]] = i.xpath("./@value")[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", 'html_error: {}'.format(error), resp)
            return 9, 'html_error'
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.sx.10086.cn/my/"
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key
        if kwargs['tel'] in resp.text:
            return 0, "success"
        else:
            self.log("crawler", "登陆失败: website_busy_error", resp)
            return 9, "website_busy_error"

    def send_verify_request(self, **kwargs):
        # Trigger Second Validation(Send SMS Validate Code to Cellphone)
        # return 0, 'success', ''
        xd_url = "http://service.sx.10086.cn/my/xd.html"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.sx.10086.cn/my/hfcx.html"
        }
        code, key, resp = self.get(xd_url, headers=headers)
        if code != 0:
            return code, key, ""
        image_url = "http://service.sx.10086.cn/checkimage.shtml"
        headers = {
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "http://service.sx.10086.cn/my/xd.html"
        }
        codetype = '3004'
        for i in range(self.max_retry):
            code, key, resp = self.get(image_url, headers=headers)
            if code != 0:
                return code, key, ""
            # 打码
            key, result, cid = self._dama(resp.content, codetype)
            if key == "success" and result != "":
                captcha_code = str(result)
            else:
                self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                return 9, key, ""
            # 验证图形验证码:
            verify_imgage_url = "http://service.sx.10086.cn/enhance/operate/pwdModify/checkRandCode.action"
            data = {"seccodeverify": captcha_code}
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": "http://service.sx.10086.cn/my/xd.html",
                "X-Requested-With": "XMLHttpRequest"
            }
            code, key, resp = self.post(verify_imgage_url, data=data, headers=headers)
            if code != 0:
                # if not isinstance(resp, str):
                #     print resp.text, resp.status_code
                #     pass
                return code, key, ""
            try:
                if u"非法字符" in resp.text:
                    # "asc" 属于非法字符, 输入非法字符会报该异常
                    self.log("crawler", 'verify_error', resp)
                    self._dama_report(cid)
                    continue
                verify_image_resp = resp.json()
                if verify_image_resp.get('retCode') == '0':
                    break
                else:
                    self.log("crawler", 'verify_error', resp)
                    self._dama_report(cid)
                    continue
            except:
                error = traceback.format_exc()
                self.log("crawler", 'json_error: {}'.format(error), resp)
                return 9, 'json_error', ""
        else:
            self.log("crawler", "verify_error 打码全部失败", resp)
            return 9, 'verify_error', ""

        # SMS code
        sms_url = "http://service.sx.10086.cn/enhance/operate/pwdModify/sendRandomPwd.action"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://service.sx.10086.cn/my/xd.html"
        }
        code, key, resp = self.post(sms_url, headers=headers)
        if code != 0:
            return code, key, ""
        try:
            is_ok = resp.json()['retMsg']
            if is_ok == 'ok!':
                return 0, "success", ""
            elif u'请稍后重新下发短信' in is_ok:
                self.log("crawler", "send_sms_too_quick_error", resp)
                return 9, "send_sms_too_quick_error", ""
            else:
                self.log("crawler", "send_sms_error", resp)
                return 9, "send_sms_error", ""
        except:
            error = traceback.format_exc()
            self.log("crawler", 'send_sms_error: {}'.format(error), resp)
            return 9, "send_sms_error", ""


    def verify(self, **kwargs):
        # return 0, 'success'
        verify_url = "http://service.sx.10086.cn/enhance/operate/pwdModify/randomPwdCheck.action"
        try:
            data = {"randomPwd": self.enStr(kwargs['sms_code'], 1)}
        except:
            error = traceback.format_exc()
            self.log("crawler", "param_error: {}, {}".format(error, kwargs['sms_code']), "")
            return 9, "website_busy_error"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://service.sx.10086.cn/my/xd.html"
        }
        code, key, resp = self.post(verify_url, data=data, headers=headers)
        if code != 0:
            return code, key
        try:
            result = resp.json()
            verify_data = result.get("validFlag", "")
            verify_msg = result.get("retMsg", "")
            if verify_data == '0':
                return 0, "success"
            elif verify_data == '1':
                self.log("user", "verify_error", resp)
                return 9, "verify_error"
            elif u'服务调用出错' in resp.text:
                self.log("website", u"服务调用出错", resp)
                return 9, "website_busy_error"
            else:
                if verify_msg == u'请输入手机号':
                    self.log("crawler", "outdated_sid", resp)
                    return 9, 'outdated_sid'
                elif u'您输入的验证码错误次数超过5次' in verify_msg:
                    self.log("crawler", "verify_error", resp)
                    return 9, 'verify_error'
                self.log("crawler", "unknown_error", resp)
                return 9, 'unknown_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", "json_error: {}".format(error), resp)
            return 9, 'json_error'

    def crawl_info(self, **kwargs):
        """
        Crawl user's personal info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            code: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        user_info_url = "http://service.sx.10086.cn/my/grzl.html"
        code, key, resp = self.get(user_info_url)
        if code != 0:
            return code, key, {}
        user_info = {}
        try:
            et = etree.HTML(resp.text)
            user_info['full_name'] = et.xpath("//th[@name='userName']/text()")[0]
            user_info['address'] = et.xpath("//textarea[@class='textarea-w1']/text()")[0]
            user_info['id_card'] = et.xpath("//td[@name='userPhone']/parent::*/th/text()")[0]
            date_str = et.xpath("//div[@class='col-w1-title']/span/b/text()")[0]
            date_struct_time = time.strptime(reduce(lambda x, y: x + y, re.findall(r"\d+", date_str)), '%Y%m%d')
            user_info['open_date'] = "%d" % int(time.mktime(date_struct_time))
            user_info['is_realname_register'] = True
        except:
            error = traceback.format_exc()
            self.log("crawler", 'html_error: {}'.format(error), resp)
            return 9, 'html_error', {}
        return 0, "success", user_info

    def __monthly_period(self, length=6):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield current_time - relativedelta(months=month_offset)

    def time_transform(self, time_str, str_format="%Y-%m-%d %H:%M:%S"):
        today_month = datetime.date.today().month
        today_year = datetime.date.today().year
        str_month = int(time_str[:2])
        if str_month > today_month:
            str_year = today_year - 1
        else:
            str_year = today_year
        time_str = str(str_year) + "-" + time_str
        str_format = "%Y-%m-%d %H:%M:%S"
        time_type = time.strptime(time_str, str_format)
        return str(int(time.mktime(time_type)))

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

    def crawl_call_log(self, **kwargs):
        miss_list = []
        pos_miss_list = []
        result_list = []
        get_data_url = "http://service.sx.10086.cn/enhance/fee/queryDetail/queryDetail!queryLocalDetail22.action"
        crawl_error = 0

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://service.sx.10086.cn/my/xd-2.html",
            "X-Requested-With": "XMLHttpRequest"
        }

        # 请求详单参数列表
        page_and_retry = []
        for query_date in self.__monthly_period():
            data = {
                "beginMonth": query_date.strftime('%Y-%m-%d'),
                "endMonth": query_date.strftime('%Y%m%d'),
                "detailType": "2",
                "zqType": "1"
            }
            query_month = query_date.strftime('%Y%m')

            page_and_retry.append((data, query_month, self.max_retry))
        st_time = time.time()
        et_time = st_time + 30
        log_for_retry_request = []
        while page_and_retry:
            # 是否需要重试标示
            flag = True
            m_data, m_query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            code, key, resp = self.post(get_data_url, data=m_data, headers=headers)
            if code == 0:
                flag = False
                if '该用户申请详单禁查' in resp.text:
                    self.log('user', '用户申请详单禁查', resp)
                    return 9, 'user_prohibited_error', result_list, miss_list, pos_miss_list
                try:
                    month_data = []
                    et = etree.HTML(resp.text)
                    et_data = et.xpath('//div[@id="aaaa"]/table[2]/tbody/tr')
                    for i in et_data:
                        result_data = {}
                        data_list = i.xpath('./td/text()')
                        len_data_list = len(data_list)
                        if len_data_list == 8 or len_data_list == 7:
                            result_data['call_time'] = self.time_transform(data_list[0])
                            result_data['call_duration'] = self.time_format(data_list[4])
                            result_data['call_tel'] = data_list[3]
                            result_data['call_cost'] = data_list[7] if len_data_list == 8 else data_list[6]
                            result_data['call_to'] = ''
                            raw_call_from = data_list[1]
                            call_from, error = self.formatarea(raw_call_from)
                            if not call_from:
                                call_from = raw_call_from
                                self.log("crawler", "{}-{}".format(error, call_from), resp)
                            result_data['call_from'] = call_from
                            result_data['call_method'] = data_list[2]
                            result_data['call_type'] = data_list[5]
                            result_data['month'] = m_query_month
                            month_data.append(result_data)
                except:
                    message = traceback.format_exc()
                    flag = True
                    crawl_error += 1
                    self.log('crawler', 'html_error:{}'.format(message),resp)

                if flag:
                    pass
                elif month_data:
                    result_list.extend(month_data)
                    continue
                elif not et_data:
                    self.log("crawler", 'crawl_error: 网页无数据', resp)
                    flag = True
                else:
                    # 无通话记录
                    self.log("crawler", 'crawl_error: 有框架无数据', resp)
                    pos_miss_list.append(m_query_month)
                    continue

            if flag:
                now_time = time.time()
                if m_retry_times > 0:
                    page_and_retry.append((m_data, m_query_month, m_retry_times))
                elif now_time < et_time:
                    rand_sleep = random.randint(2, 4)
                    if m_retry_times > -10:
                        page_and_retry.append((m_data, m_query_month, m_retry_times))
                        time.sleep(rand_sleep)
                    else:
                        miss_list.append(m_query_month)
                else:
                    miss_list.append(m_query_month)
        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        if len(miss_list+pos_miss_list) == 6:
            if crawl_error > 0:
                return 9, "crawl_error", [], [], []
            else:
                return 9, "website_busy_error", [], [], []
        return 0, "success", result_list, miss_list, pos_miss_list

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
        for query_date in self.__monthly_period():
            url = "http://service.sx.10086.cn/monthbill/tofeeBillIndex.action"
            query_month = query_date.strftime("%Y%m")
            params = {"startMonth": query_month}
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "http://service.sx.10086.cn/my/zd.html"
            }
            for i in range(self.max_retry):
                code, key, resp = self.post(url, headers=headers, params=params)
                if code != 0:
                    message = "network_request_error"
                    continue
                if u'受理失败' in resp.text:
                    message = "no_data"
                    continue
                try:
                    et = etree.HTML(resp.text)
                    et_table = et.xpath("//table[@class='bill-table6']/tr/td/b/span/text()")
                    ext_table = et.xpath("//table[@class='bill-table6']/tr/td/span/text()")
                    result_data = {}
                    result_data['bill_month'] = query_month
                    result_data['bill_amount'] = et_table[9]
                    result_data['bill_package'] = et_table[0]
                    result_data['bill_ext_calls'] = ext_table[0]
                    result_data['bill_ext_data'] = ext_table[1]
                    result_data['bill_ext_sms'] = ext_table[2]
                    result_data['bill_zengzhifei'] = et_table[2]
                    result_data['bill_daishoufei'] = et_table[3]
                    result_data['bill_qita'] = et_table[4]
                    result_list.append(result_data)
                    break
                except:
                    message = traceback.format_exc()
                    continue
            else:
                if message != "network_request_error":
                    self.log("crawler", "html_error: {}".format(message), resp)
                    if message != 'no_data':
                        crawl_error += 1
                miss_list.append(query_month)
                break
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5 and crawl_error > 0:
            return 9, "crawl_error", [], miss_list
        return 0, "success", result_list, miss_list

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "15903551769"
    # USER_ID = "15903551768"
    USER_PASSWORD = "193579"
    # USER_PASSWORD = "chaochao960813!!"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # print(c.enStr(USER_PASSWORD))
