# -*- coding: utf-8 -*-
import threading
import traceback
import sys
import time
import re
from Queue import Queue
from threading import Thread

import execjs
import random
# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")
from enStr import get_num_pwd
from datetime import date
import datetime
from lxml import etree
from dateutil.relativedelta import relativedelta

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
        self.pin_pwd_error_times = 0

        self.scriptSessionId = "AA0CBE9FB90164F9E0E55CF74FCC9338249"
        self.Captcha = ''

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        return
            list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        return ['pin_pwd', 'sms_verify']

    def get_login_verify_type(self, **kwargs):
        # return "SMSCaptcha"
        return 'SMS'

    def format_dataString(self, data_str):
        return reduce(lambda x, y: x + "\n" + y, map(lambda x: x.strip(), data_str.split("\n")))

    def send_login_verify_request(self, **kwargs):
        url = "http://www.189.cn/dqmh/ssoLink.do?method=skip&platNo=10015&toStUrl=http://jx.189.cn/SsoAgent?returnPage=xdcx"
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, ""
        try:
            self.exponent = re.findall(r"exponent = \"(.*)\";", resp.text)[0]
            self.modulus = re.findall(r"modulus = \"(.*)\";", resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error: 获取加密用参数失败 {}".format(error), resp)
        # 获取SessionId
        url = "http://jx.189.cn/public/common/control/dwr/engine.js"
        headers = {"Referer": "http://jx.189.cn/service/bill/customerbill/index.jsp?bill=detail"}
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ""
        try:
            self.scriptSessionId = re.findall(r"_origScriptSessionId = \"(.*?)\";", resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error: {}".format(error), resp)
            return 9, "html_error", ""
        # 获取图片
        verify_type = kwargs.get('verify_type', '')
        # if verify_type in ['', 'captcha']:
        #
        #     url = "http://jx.189.cn/public/v4/common/control/page/image.jsp"
        #     headers = {"Referer": "http://jx.189.cn/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url="}
        #     code, key, resp = self.get(url, headers=headers)
        #     if code != 0:
        #         return code, key, ""
        #     img_str = base64.b64encode(resp.content)

        codetype = 3004
        for i in range(self.max_retry):
            url = "http://jx.189.cn/public/v4/common/control/page/image.jsp"
            headers = {"Referer": "http://jx.189.cn/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url="}
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key, ""
            try:
                key, result, cid = self._dama(resp.content, codetype)
            except:
                msg = traceback.format_exc()
                self.log('crawler', u'打码失败:{}'.format(msg), '')
                continue
            if key == "success" and result != "":
                self.Captcha = str(result).lower()
                break
            else:
                continue
        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error', ''

        # if verify_type in ['', 'sms']:
        # batchId 官网中, 每执行一步计数加一, 不传递则无法执行, 目前不检查有效性, 传1即可
        url = "http://jx.189.cn/dwr/call/plaincall/Service.excute.dwr"
        data = """
            callCount=1
            page=/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url=
            httpSessionId=
            scriptSessionId={scriptSessionId}
            c0-scriptName=Service
            c0-methodName=excute
            c0-id=0
            c0-param0=string:SEND_LOGIN_RANDOM_PWD
            c0-param1=boolean:false
            c0-e1=string:{num}
            c0-e2=string:CR0
            c0-e3=string:001
            c0-e4=string:no
            """.format(num=kwargs['tel'], scriptSessionId=self.scriptSessionId) + """c0-param2=Object_Object:{RECV_NUM:reference:c0-e1, SMS_OPERTYPE:reference:c0-e2, RAND_TYPE:reference:c0-e3, need_val:reference:c0-e4}
            batchId=2"""
        headers = {"Referer": "http://jx.189.cn/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url="}
        code, key, resp = self.post(url, data=self.format_dataString(data), headers=headers)
        if code != 0:
            return code, key, ""
        return 0, "success", ''

    def get_verify_type(self, **kwargs):
        """
        告訴我二次驗證用什麼驗證
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        """采用跳过短信、身份证验证方式"""
        return 'SMS'

    def login(self, **kwargs):
        # 图形/短信/登录, url, headers一致, 定义一次
        url = "http://jx.189.cn/dwr/call/plaincall/Service.excute.dwr"
        # 获取area_code
        headers = {"Referer": "http://jx.189.cn/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url="}
        data = """callCount=1
        page=/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url=
        httpSessionId=
        scriptSessionId={scriptSessionId}
        c0-scriptName=Service
        c0-methodName=excute
        c0-id=0
        c0-param0=string:GET_USER_TYPE
        c0-param1=boolean:false
        c0-e1=string:{phone_num}
        """.format(phone_num=kwargs['tel'], scriptSessionId=self.scriptSessionId) + """c0-param2=Object_Object:{user_no:reference:c0-e1}
        batchId=0
        """
        code, key, resp = self.post(url, data=self.format_dataString(data), headers=headers)
        if code != 0:
            return code, key

        try:
            area_code = re.findall(r"s1\['area_code'\]=\"(.{4})\";", resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取地区码失败{}".format(error), resp)
            return 9, "request_error"
        if area_code == "":
            self.log("crawler", "获取地区码失败!!", resp)
            return 9, "unknown_error"
        # 验证图形验证码
        headers = {"Referer": "http://jx.189.cn/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url="}
        data = """callCount=1
        page=/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url=
        httpSessionId=
        scriptSessionId={scriptSessionId}
        c0-scriptName=Service
        c0-methodName=excute
        c0-id=0
        c0-param0=string:WB_TEST_VALIDCODE
        c0-param1=boolean:false
        c0-e1=string:{captcha_code}
        """.format(captcha_code=self.Captcha, scriptSessionId=self.scriptSessionId)+"""c0-param2=Object_Object:{valid_code_input:reference:c0-e1}
        batchId=3
        """
        code, key, resp = self.post(url, data=self.format_dataString(data), headers=headers)
        if code != 0:
            return code, key
        if '\'WB_TEST_VALIDCODE\':"OK"' not in resp.text:
            self.log("user", "verify_error", resp)
            return 2, "verify_error"
        # 验证短信
        en_sms, en_phone_num = get_num_pwd(kwargs['sms_code'], kwargs['tel'], self.modulus, self.exponent)
        data = """callCount=1
            page=/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url=
            httpSessionId=
            scriptSessionId={scriptSessionId}
            c0-scriptName=Service
            c0-methodName=excute
            c0-id=0
            c0-param0=string:MWB_WT_USERLOGIN
            c0-param1=boolean:false
            c0-e1=string:22
            c0-e2=string:80000045
            c0-e3=string:{en_sms}
            c0-e4=string:{en_phone_num}
            c0-e5=string:{area_code}
            c0-e6=string:1
            """.format(area_code=area_code, scriptSessionId=self.scriptSessionId, en_sms=en_sms, en_phone_num=en_phone_num)+"""c0-param2=Object_Object:{LOGIN_TYPE:reference:c0-e1, LOGIN_PRODUCT_ID:reference:c0-e2, LOGIN_PASSWD:reference:c0-e3, LOGIN_NAME:reference:c0-e4, AREA_CODE:reference:c0-e5, MY_CHECK_FLAG:reference:c0-e6}
            batchId=4
        """
        code, key, resp = self.post(url, data=self.format_dataString(data), headers=headers)
        if code != 0:
            return code, key
        if 'flag:"0"' not in resp.text:
            if "msg:null" in resp.text or "\u5931\u8D25\u539F\u56E0\uFF1A\u60A8\u8F93\u5165\u7684\u77ED\u4FE1\u5BC6\u7801\u9519\u8BEF" in resp.text:
                # "\u5931\u8D25\u539F\u56E0\uFF1A\u60A8\u8F93\u5165\u7684\u77ED\u4FE1\u5BC6\u7801\u9519\u8BEF" 失败原因：您输入的短信密码错误
                # 当确实是验证码错误时, 会有msg=null, 其他错误msg为具体的错误信息
                # 当flag='-1'时,  msg为: 失败原因：您输入的短信密码错误！
                self.log("user", "verify_error", resp)
                return 9, "verify_error"
            # 失败原因：登录失败，不存在此用户！
            if u'\u5931\u8D25\u539F\u56E0\uFF1A\u767B\u5F55\u5931\u8D25\uFF0C\u4E0D\u5B58\u5728\u6B64\u7528\u6237\uFF01' in resp.text:
                self.log("user", "invalid_tel", resp)
                return 9, "invalid_tel"
            if u'对不起，您已经连续3次输错密码，此用户今日内已不允许登录，请明日再试' in resp.text or '\u5BF9\u4E0D\u8D77\uFF0C\u60A8\u5DF2\u7ECF\u8FDE\u7EED3\u6B21\u8F93\u9519\u5BC6\u7801\uFF0C\u6B64\u7528\u6237\u4ECA\u65E5\u5185\u5DF2\u4E0D\u5141\u8BB8\u767B\u5F55\uFF0C\u8BF7\u660E\u65E5\u518D\u8BD5\uFF01' in resp.text:
                self.log('user', 'account_locked', resp)
                return 9, 'account_locked'
            if u'对不起，您的登录密码是初始化密码，请拨打10001按3-1-2号键或到营业厅更改您的密码后再试' in resp.text or '\u5BF9\u4E0D\u8D77\uFF0C\u60A8\u7684\u767B\u5F55\u5BC6\u7801\u662F\u521D\u59CB\u5316\u5BC6\u7801\uFF0C\u8BF7\u62E8\u625310001\u63093' in resp.text:
                self.log('user', 'verify_error', resp)
                return 9, 'verify_error'
            if u'未实名认证' in resp.text or '\u672A\u5B9E\u540D\u8BA4\u8BC1' in resp.text:
                self.log("user", u"用户未实名制", resp)
                return 9, 'real_name_registration_error'
            self.log("crawler", "unknown_error", resp)
            return 9, "unknown_error"
        try:
            login_par = re.findall('s1.COL1="(.*?)";', resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error{}".format(error), resp)
            return 9, "html_error"
        # 登录
        data = """callCount=1
            page=/public/v4/logon/loginPop.jsp?from_sc=service_login&ret_url=
            httpSessionId=
            scriptSessionId={scriptSessionId}
            c0-scriptName=Service
            c0-methodName=excute
            c0-id=0
            c0-param0=string:QUERY_ADSL_URL
            c0-param1=boolean:false
            c0-e1=string:80000045
            c0-e2=string:{phone_num}
            c0-e3=string:{area_code}
            c0-e4=string:{login_par}
            """.format(area_code=area_code, phone_num=kwargs['tel'], login_par=login_par, scriptSessionId=self.scriptSessionId)+"""c0-param2=Object_Object:{PRODUCT_ID:reference:c0-e1, ACC_NBR:reference:c0-e2, LAN_CODE:reference:c0-e3, COL1:reference:c0-e4}
            batchId=5
        """
        code, key, resp = self.post(url, data=self.format_dataString(data), headers=headers)
        if code != 0:
            return code, key
        return 0, "success"

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        time.sleep(random.randint(5, 8))
        url = "http://jx.189.cn/dwr/call/plaincall/Service.excute.dwr"
        data = """callCount=1
            page=/2017/details.jsp
            httpSessionId=
            scriptSessionId={scriptSessionId}
            c0-scriptName=Service
            c0-methodName=excute
            c0-id=0
            c0-param0=string:DETAILS_SERVICE
            c0-param1=boolean:false
            c0-e1=string:SEND_SMS_CODE
            """.format(scriptSessionId=self.scriptSessionId) + """c0-param2=Object_Object:{method:reference:c0-e1}
            batchId=1
        """
        code, key, resp = self.post(url, data=self.format_dataString(data))
        if code != 0:
            return code, key, ""
        if u'CODE:"1"' in resp.text:
            return 0, "success", ""
        elif u'CODE:"-2"' in resp.text:
            self.log("crawler", "over_max_sms_error", resp)
            return 9, "over_max_sms_error", ""
        elif u'CODE:"-3"' in resp.text:
            self.log("crawler", "send_sms_too_quick_error", resp)
            return 9, "send_sms_too_quick_error", ""
        else:
            self.log("crawler", "send_sms_error", resp)
            return 9, "send_sms_error", ""

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        today = date.today().strftime('%Y%m')
        data = """callCount=1
                    page=/2017/details.jsp
                    httpSessionId=
                    scriptSessionId={scriptSessionId}
                    c0-scriptName=Service
                    c0-methodName=excute
                    c0-id=0
                    c0-param0=string:DETAILS_SERVICE
                    c0-param1=boolean:false
                    c0-e1=string:{search_month}
                    c0-e2=string:7
                    c0-e3=string:{sms_code}
                    c0-e4=string:QRY_DETAILS_BY_LOGIN_NBR
                    """.format(sms_code=kwargs['sms_code'], search_month=today, scriptSessionId=self.scriptSessionId) + """c0-param2=Object_Object:{month:reference:c0-e1, query_type:reference:c0-e2, valid_code:reference:c0-e3, method:reference:c0-e4}
                    batchId=3
                """
        url = "http://jx.189.cn/dwr/call/plaincall/Service.excute.dwr"
        headers = {"Referer": "http://jx.189.cn/2017/details.jsp"}
        code, key, resp = self.post(url, data=self.format_dataString(data), headers=headers)
        if code != 0:
            return code, key
        if "\u77ED\u4FE1\u9A8C\u8BC1\u7801\u9519\u8BEF!" in resp.text:
            self.log('user', u'验证码错误', resp)
            return 9, "verify_error"
        else:
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
        realname_register_url = "http://jx.189.cn/service/account/seeInfo.jsp"
        code, key, resp = self.get(realname_register_url)
        if code != 0:
            return code, key, {}
        try:
            selector = etree.HTML(resp.text)
            # with open('info.py','w')as f:
            #     f.write(resp.text)
            user_info['full_name'] = selector.xpath('//*[@id="CUST_NAME"]/@value')[0]
            user_info['id_card'] = selector.xpath('//*[@id="CERT_NUM"]/@value')[0]
            user_info['open_date'] = ''
            address = re.findall(u'id="CUST_ADDR" >(.*?)</textarea>',resp.text)
            user_info['address'] = address[0] if address else ''
            if user_info['id_card']:
                user_info['is_realname_register'] = True
            else:
                user_info['is_realname_register'] = False
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error : %s' % error, resp)
            return 9, 'html_error', {}
        return 0, "success", user_info

    def get_search_list(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        search_list = []
        for month_offset in range(0, length):
            search_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return search_list

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        # kwargs['tel'] = '17379139120'
        tail_tel_num = ['0', '2', '3', '6', '9']
        if kwargs['tel'][-1] in tail_tel_num:
            self.sms_code = kwargs['sms_code']
            return self.new_crawl_call_log()

        missing_list = []
        crawl_num = 0
        possibly_missing_list = []
        call_log = []
        url = "http://jx.189.cn/dwr/call/plaincall/Service.excute.dwr"
        headers = {"Referer": "http://jx.189.cn/2017/details.jsp"}
        search_month = [x for x in range(0, -6, -1)]
        today = date.today()
        page_retry_times =[]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            # batchId = 20 - each_month
            data = """callCount=1
                     page=/2017/details.jsp
                     httpSessionId=
                     scriptSessionId={scriptSessionId}
                     c0-scriptName=Service
                     c0-methodName=excute
                     c0-id=0
                     c0-param0=string:DETAILS_SERVICE
                     c0-param1=boolean:false
                     c0-e1=string:{search_month}
                     c0-e2=string:7
                     c0-e3=string:{sms_code}
                     c0-e4=string:QRY_DETAILS_BY_LOGIN_NBR
                     """.format(search_month=query_month, sms_code=kwargs['sms_code'],
                                scriptSessionId=self.scriptSessionId) + """c0-param2=Object_Object:{month:reference:c0-e1, query_type:reference:c0-e2, valid_code:reference:c0-e3, method:reference:c0-e4}
                     batchId=3
             """
            page_retry_times.append((self.format_dataString(data),query_month,self.max_retry))

        log_for_retry_request = []
        st_time = time.time()
        et_time = st_time + 20
        rand_time = random.randint(3, 5)

        while page_retry_times:
            message = ''
            data,m_query_month,m_retry_times = page_retry_times.pop(0)
            log_for_retry_request.append((m_query_month,m_retry_times))
            m_retry_times -= 1

            # first_page_retry_times = self.max_retry
            # while True:
            #     first_page_retry_times -= 1
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                now_time = time.time()
                if m_retry_times > 0:
                    page_retry_times.append((data,m_query_month,m_retry_times))
                elif now_time < et_time:
                    page_retry_times.append((data, m_query_month, m_retry_times))
                    time.sleep(rand_time)
                else:
                    message = "network_request_error"
            code, key, result = self.call_log_get(resp.text, m_query_month)

            if code != 0:
                message = "{}\n{}".format(key, result)
            else:
                if result:
                    call_log.extend(result)
                else:
                    message = "no_data"
            if message != "network_request_error":
                self.log("crawler", message, "")
                if message == "no_data" or message.startswith('website_busy_error'):
                    if m_query_month not in possibly_missing_list:
                        possibly_missing_list.append(m_query_month)
                else:
                    if message == "":
                        pass
                    else:
                        crawl_num += 1
                        if m_query_month not in missing_list:
                            missing_list.append(m_query_month)

        self.log("crawler","重试记录：{}".format(log_for_retry_request),"")
        # print('missing_list:{}'.format(missing_list))
        # print('possibly_missing_list:{}'.format(possibly_missing_list))
        if len(missing_list + possibly_missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list, []
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list, []
        return 0, "success", call_log, missing_list, possibly_missing_list, []

    def call_log_get(self, response, query_month):
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
        # 将多余信息去除
        try:
            js_row = response.split('DWR-REPLY')[1].split('dwr.engine')[0]
            final_data = []
            if "NullPointerException" in response or "\u7CFB\u7EDF\u8C03\u7528\u5F02\u5E38" in response or 'CODE:"-9999"' in response or 's1' not in response:
                # "\\u7CFB\\u7EDF\\u8C03\\u7528\\u5F02\\u5E38" 系统调用异常
                return 9, "website_busy_error", []

            if js_row != ' ':
                ctx = execjs.compile(js_row + """function aa(){
                    return s1;
                }""")
                raw_data = ctx.call("aa")
                for item in raw_data:
                    data = {}
                    data['call_tel'] = item['called']
                    data['call_method'] = item['callType']
                    data['call_cost'] = item['totalFee']
                    data['call_duration'] = item['times_int']
                    # data['call_from'] = item['callAddr']

                    raw_call_from = item['callAddr'].strip()
                    call_from, error = self.formatarea(raw_call_from)
                    if call_from:
                        data['call_from'] = call_from
                    else:
                        # self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                        data['call_from'] = raw_call_from

                    data['call_type'] = item['tonghuatype']
                    timeArray = time.strptime(item['callStartTime'], "%Y/%m/%d %H:%M:%S")
                    data['call_time'] = str(int(time.mktime(timeArray)))
                    data['month'] = query_month
                    data['call_to'] = ''
                    final_data.append(data)
            return 0, "success", final_data
        except:
            error = traceback.format_exc()
            return 9, "unknown_error", error

    def new_crawl_call_log(self):
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        # 部分缺失月份
        part_missing_month_list = []

        self.crawl_error = 0
        # 爬虫队列
        self.work_queue = Queue()
        self.work_queue_info = Queue()
        # 重试队列
        self.crawl_again_queue = Queue()
        self.crawl_again_info_queue = Queue()
        # 详单数据
        self.data_queue = Queue()
        self._runing = threading.Event()
        self._runing.set()

        self.last_month = Queue()

        searchMonth = self.get_search_list(6)
        [self.work_queue.put((x, 0)) for x in searchMonth]

        control_work_queue = Thread(target=self.control_work_queue, args=(self.work_queue, 'main', 0.2))
        control_work_queue.start()

        control_again_queue = Thread(target=self.control_work_queue,
                                     args=(self.crawl_again_queue, "crawl_again", random.uniform(2, 3.5)))
        control_again_queue.start()

        self.work_control()

        control_work_queue.join()
        control_again_queue.join()

        again_queue_last = []
        part_miss_set = set()
        miss_set = set()

        # return 0
        while not self.last_month.empty():
            work_one = self.last_month.get()
            search_month_str = work_one[0]
            miss_set.add(search_month_str)
            again_queue_last.append(work_one)

        while not self.crawl_again_queue.empty():
            work_one = self.crawl_again_queue.get()
            search_month_str = work_one[0]
            miss_set.add(search_month_str)
            again_queue_last.append(work_one)

        again_list = []
        while not self.crawl_again_info_queue.empty():
            work_one = self.crawl_again_info_queue.get()
            # search_month_str = work_one[0]
            again_list.append({work_one[0]: work_one[1]})

        self.log("crawler", "重试队列: {}".format(again_list), "")
        self.log("crawler", "重试剩余: {}".format(again_queue_last), "")
        missing_month_list = [miss_x for miss_x in miss_set]
        missing_month_list.sort(reverse=True)
        part_missing_list = [x for x in part_miss_set]
        part_missing_list.sort(reverse=True)

        self.log("crawler", "缺失记录: {} 部分缺失: {}".format(missing_month_list, part_missing_list), "")
        data_list = []
        while not self.data_queue.empty():
            data_list.append(self.data_queue.get())

        if len(missing_month_list) == 6:
            if self.crawl_error > 0:
                return 9, "crawl_error", [], missing_month_list, possibly_missing_list, part_missing_list
            else:
                return 9, "website_busy_error", [], missing_month_list, possibly_missing_list, part_missing_list
        return 0, "success", data_list, missing_month_list, possibly_missing_list, part_missing_list

    def control_work_queue(self, work_queue, work_name="main", sleep_time=0):
        while self._runing.is_set():
            if not work_queue.empty():
                get_page_data_params = work_queue.get()
                self.get_page_data(*get_page_data_params)
                if work_name != 'main':
                    self.crawl_again_info_queue.put(get_page_data_params)

                if work_name != "main":
                    time.sleep(0)
            # 将控制权移交出去
            time.sleep(sleep_time)

    def get_page_data(self, year_month, retry_times):
        retry_times_limit = 5
        data = """callCount=1
                 page=/2017/details.jsp
                 httpSessionId=
                 scriptSessionId={scriptSessionId}
                 c0-scriptName=Service
                 c0-methodName=excute
                 c0-id=0
                 c0-param0=string:DETAILS_SERVICE
                 c0-param1=boolean:false
                 c0-e1=string:{search_month}
                 c0-e2=string:7
                 c0-e3=string:{sms_code}
                 c0-e4=string:QRY_DETAILS_BY_LOGIN_NBR
                 """.format(search_month=year_month, sms_code=self.sms_code,
                            scriptSessionId=self.scriptSessionId) + """c0-param2=Object_Object:{month:reference:c0-e1, query_type:reference:c0-e2, valid_code:reference:c0-e3, method:reference:c0-e4}
                 batchId=3
         """

        retry_times += 1
        url = "http://jx.189.cn/dwr/call/plaincall/Service.excute.dwr"
        headers = {"Referer": "http://jx.189.cn/2017/details.jsp"}

        code, key, resp = self.post(url, data=self.format_dataString(data), headers=headers)
        if code == 0:
            code02, key02, result = self.call_log_get(resp.text, year_month)
            if code02 == 0:
                if result:
                    [self.data_queue.put(x) for x in result]
                    return
                else:
                    self.log('crawler', u'详单为空', resp)
            else:
                self.log('crawler', result, resp)
                self.crawl_error += 1
        if retry_times <= retry_times_limit:
            self.crawl_again_queue.put((year_month, retry_times))
        else:
            self.last_month.put((year_month, retry_times))
        return

    def work_control(self):
        must_stop_time = 40
        time_limit = 30
        empty_time_limit = 20

        st_time = time.time()
        break_time = st_time + time_limit
        empty_break_time = st_time + empty_time_limit
        must_break_time = st_time + must_stop_time

        while True:
            now_time = time.time()
            time.sleep(0)
            if self.work_queue.empty() and self.crawl_again_queue.empty() and now_time > empty_break_time:
                self.log("crawler", "break 1 {} {}".format(st_time, now_time), "")
                break
            if now_time > break_time and self.work_queue.empty():
                self.log("crawler", "break 2 {} {}".format(st_time, now_time), "")
                break
            if now_time > must_break_time:
                self.log("crawler", "break 3 {} {}".format(st_time, now_time), "")
                break
            time.sleep(0)

        self._runing.clear()

    def crawl_phone_bill(self, **kwargs):
        # return 0, "success", [], []
        #备用方案
        # month_bill_url = "http://jx.189.cn/service/bill/customerbill/consumptionAnalysisNew.jsp"
        # try:
        #     resp = self.session.get(month_bill_url)
        # except:
        #     error = traceback.format_exc()
        #     return "request_error", 9, error, []
        #
        missing_list = []
        crawl_num = 0
        today = date.today()
        search_month = [x for x in range(0, -6, -1)]
        month_fee =[]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            month_bill_url = "http://jx.189.cn/service/bill/e_billing/?month="+query_month
            for retry in xrange(self.max_retry):
                code, key, resp = self.get(month_bill_url)
                if u"中国电信江西分公司客户账单" not in resp.text:
                    # self.log('crawler', 'html_error', resp)
                    pass
                else:
                    break
            else:
                if "/service/service_login.jsp" in resp.text:
                    self.log('crawler', "user_exit", resp)
                elif u"对不起，账单查询失败！" in resp.text:
                    self.log("website", "账单查询失败", resp)
                else:
                    self.log('crawler', "unknown_error", resp)
                missing_list.append(query_month)
                continue
                # with open('bill.py','w') as file:
                #     file.write(resp.text)
            month_fee_data = {}
            try:
                month_fee_data['bill_month'] = query_month
                month_fee_data['bill_amount'] = re.findall(u"本期费用合计:</b><span class='td_div_span2'>(\d+\.\d+)</span>元</td>", resp.text)[0]
                if month_fee_data['bill_amount'] == '0.00':
                    missing_list.append(query_month)
                    continue
                month_fee_data['bill_package'] = ''
                month_fee_data['bill_ext_calls'] = ''
                month_fee_data['bill_ext_data'] = ''
                month_fee_data['bill_ext_sms'] = ''
                month_fee_data['bill_zengzhifei'] = ''
                month_fee_data['bill_daishoufei'] = ''
                month_fee_data['bill_qita'] = ''
                month_fee.append(month_fee_data)
            except:
                error = traceback.format_exc()
                self.log('crawler', "html_error : %s" % error, resp)
                crawl_num += 1
                missing_list.append(query_month)
                continue

        if len(missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', month_fee, missing_list
            return 9, 'website_busy_error', month_fee, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, "success", month_fee, missing_list


if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17379139120"
    # USER_ID = "17379139234"
    # USER_PASSWORD = "332266"
    USER_PASSWORD = "021931"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # print(c.crawl_call_log())
    # print c.send_login_verify_request(tel=USER_ID, pin_pwd=USER_PASSWORD)