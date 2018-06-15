# -*- coding: utf-8 -*-

import requests
import base64
import traceback
import sys
import time
import socket
import re
reload(sys)
sys.setdefaultencoding("utf8")

from fake_useragent import UserAgent
from datetime import date
from lxml import etree
from dateutil.relativedelta import relativedelta

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
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': UserAgent().chrome})

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        return
            list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        return [ 'pin_pwd','captcha_verify']

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
        self.session.cookies.clear()
        image_url = 'https://hb.ac.10086.cn/SSO/img'
        payload ={
            "codeType":'0',
            "rand":str(time.time()*1000)
        }
        try:
            image_req = self.session.get(image_url, params=payload)
        except:
            error = traceback.format_exc()
            return "crawl_error", 9, "get image_code failed:%s" %error, ""
        if image_req.status_code == 200:
            return "success", 0, "", base64.b64encode(image_req.content)
        else:
            return "request_error", 9, "爬取失败,状态码：%d"%image_req.status_code, ''

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
        first_url = "https://hb.ac.10086.cn/SSO/loginbox?service=servicenew&style=mymobile&continue=http://www.hb.10086.cn/servicenew/index.action"
        try:
            first_req = self.session.get(first_url)
        except:
            error = traceback.format_exc()
            return "request_error", 9, "请求失败:%s"%error
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(("8.8.8.8", 80))
        # myaddr = s.getsockname()[0]
        # myname = socket.getfqdn(socket.gethostname())
        # myaddr = socket.gethostbyname(myname)
        # print myaddr
        login_url = "https://hb.ac.10086.cn/SSO/loginbox"
        login_data ={
            "accountType":'0',
            "username":kwargs['tel'],
            "passwordType":'1',
            "password":kwargs['pin_pwd'],
            "smsRandomCode":'',
            "emailusername":'请输入登录帐号',
            "emailpassword":'',
            "validateCode":kwargs['captcha_code'],
            "action":'/SSO/loginbox',
            "style":'mymobile',
            "service":'servicenew',
            "continue":'http://www.hb.10086.cn/servicenew/index.action',
            "submitMode":'login',
            # "guestIP":myaddr
        }
        try:
            login_req = self.session.post(login_url, data = login_data, allow_redirects=True)
        except:
            error = traceback.format_exc()
            return "request_error", 9, "模拟登录url请求失败:%s"%error
        if login_req.status_code == 200:
            if 'SAMLart' in login_req.text:
                try:
                    selector = etree.HTML(login_req.text)
                    RelayState = selector.xpath('//input[@name="RelayState"]/@value')[0]
                    SAMLart = selector.xpath('//input[@name="SAMLart"]/@value')[0]
                    artifact = selector.xpath('//input[@name="artifact"]/@value')[0]
                    accountType = selector.xpath('//input[@name="accountType"]/@value')[0]
                    PasswordType = selector.xpath('//input[@name="PasswordType"]/@value')[0]
                except:
                    error = traceback.format_exc()
                    return "html_error", 9, "Xpath数据提取出错:%s"%error
                cookie_url = "http://www.hb.10086.cn/servicenew/postLogin.action?timeStamp=" + str(time.time()*1000)
                cookie_data ={
                    "RelayState":RelayState,
                    "SAMLart":SAMLart,
                    "artifact":artifact,
                    "accountType":accountType,
                    "PasswordType":PasswordType,
                    "errorMsg":'',
                    "errFlag":'',
                    "telNum":''
                }
                try:
                    cookie_req = self.session.post(cookie_url, data=cookie_data)
                except:
                    error = traceback.format_exc()
                    return "login_param_error", 9, "登录失败：%s"%error
                if cookie_req.history:
                    verify_url = "http://www.hb.10086.cn/my/balance/qryBalance.action"
                    verify_req = self.session.get(verify_url)
                    if u'月份详单' in verify_req.text:
                        return "success", 0, "login success"
                    return 'unknown_error', 9, "登录失败：%s"%verify_req.text
                return 'unknown_error', 9, "登录失败：%s"%cookie_req.text
            elif u'输入验证码有误，请重新输入' in login_req.text:
                return 'verify_error', 2, "验证码错误"
            elif u'您的账户名与密码不匹配，请重新输入' in login_req.text:
                return 'invalid_tel', 1, "手机号/密码错误"
            else:
                return "unknown_error", 9, "get unknown_err：%s"%login_req.text
        else:
            return "unknown_error", 9, "login_err:%d"%login_req.status_code

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        send_sms_url = "http://www.hb.10086.cn/my/account/smsRandomPass!sendSmsCheckCode.action? "
        send_sms_data = {
            "menuid":"myDetailBill"
        }
        try:
            send_sms_req = self.session.post(send_sms_url, data = send_sms_data)
        except:
            error = traceback.format_exc()
            return "crawl_error", 9, "send sms_code failed:%s" %error, ""
        if send_sms_req.status_code == 200 and '"result":"1"' in send_sms_req.text:
            return "success", 0, "发送短信成功", ""
        return "unknown_error", 9, "短信发送失败：%s"%send_sms_req.text, ""

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        """
        详单验证改版,改为每个月均需短信验证码
        """
        today = date.today()
        query_month = "%d%02d"%(today.year, today.month)
        check_sms_url = "http://www.hb.10086.cn/my/billdetails/billDetailQry.action?postion=outer"
        check_sms_data ={
            "detailBean.billcycle":query_month,
            "detailBean.selecttype":"0",
            "detailBean.flag":"GSM",
            "menuid":"myDetailBill",
            "groupId":"tabs3",
            "detailBean.password":kwargs['pin_pwd'],
            "detailBean.chkey":kwargs['sms_code']
        }
        try:
            check_sms_req = self.session.post(check_sms_url, data = check_sms_data)
        except:
            error = traceback.format_exc()
            return "login_param_error", 9, error
        if check_sms_req.status_code == 200:
            if u'您输入的服务密码或短信验证码错误或者过期'in check_sms_req.text:
                return "verify_error", 2, "短信码/服务密码错误：%s"%check_sms_req.text
            elif u'中国移动通信客户详单' in check_sms_req.text:
                return "success", 0, "验证成功"
            else:
                return 'expected_key_error', 9, "失败：%s"%check_sms_req.text
        else:
            return "unknown_error", 9, "验证失败:%d"%check_sms_req.status_code

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
        user_info_url = "http://www.hb.10086.cn/my/account/basicInfoAction.action"
        try:
            user_info_req = self.session.get(user_info_url)
        except:
            error = traceback.format_exc()
            return "request_error", 9, error,{}
        if user_info_req.status_code == 200:
            """
            {'full_name': full_name,
            'id_card': id_card,
            'is_realname_register': is_realname_register,
            'open_date': open_date}
            """
            try:
                selector = etree.HTML(user_info_req.text)
                user_info['full_name'] = selector.xpath('//tbody/tr[1]/td[1]/text()')[0].replace('\r\n','').replace('\t','').replace(' ','')
                user_info['open_date'] = selector.xpath('//tbody/tr[5]/td[2]/text()')[0]
                user_info['id_card'] = selector.xpath('//tbody/tr[4]/td[2]/text()')[0]
                user_info['addr'] = selector.xpath('//tbody/tr[6]/td[1]/text()')[0]
            except:
                error = traceback.format_exc()
                return "html_error", 9, "Xpath数据提取出错:%s"%error, {}
            if user_info['id_card']:
                user_info['is_realname_register'] = True
            else:
                user_info['is_realname_register'] = False
            return "success", 0, "get info", user_info
        else:
            return "request_error", 9, "用户信息爬取失败：%d"%user_info_req.status_code,{}

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        today = date.today()
        call_log = []
        call_log_url = "http://www.hb.10086.cn/my/billdetails/billDetailQry.action?postion=outer"
        search_month = [x for x in range(0,-6,-1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d"%(query_date.year, query_date.month)
            call_log_data = {
                "detailBean.billcycle":query_month,
                "detailBean.selecttype":"0",
                "detailBean.flag":"GSM",
                "menuid":"myDetailBill",
                "groupId":"tabs3",
                "detailBean.password":kwargs['pin_pwd'],
                "detailBean.chkey":kwargs['sms_code']
            }
            try:
                call_log_req = self.session.post(call_log_url, data = call_log_data)
            except:
                error = traceback.format_exc()
                return "request_error", 9, error, []
            if call_log_req.status_code == 200:
                if u'您输入的服务密码或短信验证码错误或者过期'in call_log_req.text:
                    return "verify_error", 2, "短信码/服务密码错误：%s"%call_log_req.text, []
                elif u'中国移动通信客户详单' in call_log_req.text:
                    data = self.call_log_get(call_log_req.text)
                    if data:
                        call_log.extend(data)
                else:
                    return 'expected_key_error', 9, "爬取失败：%s"%call_log_req.text, []
            else:
                return "request_error", 9, "详单爬取失败：%d"%call_log_req.status_code, []
        return "success", 0, "get call_log", call_log

    def call_log_get(self,response):
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
        if u'没有查询到该业务数据！'in response:
            return None
        records = []
        selector = etree.HTML(response.encode('utf-8'))
        call_form = selector.xpath('//table[@id="table6"]/tr')
        for item in call_form[1:-1]:
            data = {}
            data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data['call_cost'] = item.xpath('.//td[7]/text()')[0].replace(u'\xa0','').replace('\r\n','').replace('\t','').replace(' ','')
            data['call_time'] = item.xpath('.//td[1]/text()')[0].replace(u'\xa0','').replace('\r\n','').replace('\t','')
            data['call_method'] = item.xpath('.//td[3]/text()')[0].replace(u'\xa0','').replace('\r\n','').replace('\t','')
            data['call_type'] = item.xpath('.//td[6]/text()')[0].replace(u'\xa0','').replace('\r\n','').replace('\t','')
            data['call_from'] = item.xpath('.//td[2]/text()')[0].replace(u'\xa0','').replace('\r\n','').replace('\t','')
            data['call_to'] = ''
            data['call_tel'] = item.xpath('.//td[4]/text()')[0].replace(u'\xa0','').replace('\r\n','').replace('\t','')
            duration = item.xpath('.//td[5]/text()')[0]
            ret = re.findall('\d+',duration)
            if len(ret) == 3:
                data['call_duration'] = str(int(ret[0])*3600+int(ret[1])*60+int(ret[2]))
            elif len(ret) == 2:
                data['call_duration'] = str(int(ret[0])*60+int(ret[1]))
            else:
                data['call_duration'] = str(ret[0])
            records.append(data)
        return records

    def crawl_phone_bill(self, **kwargs):
        month_fee =[]
        today = date.today()
        month_bill_url = "http://www.hb.10086.cn/my/balance/showbillMixQuery.action?postion=outer"
        search_month = [x for x in range(0,-6,-1)]
        for each_month in search_month:
            month_fee_data = {}
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d"%(query_date.year, query_date.month)
            month_bill_data = {
                "qryMonthType":"current",
                "theMonth":query_month,
                "menuid":"myBill",
                "groupId":"tabs3"
            }
            try:
                month_bill_req = self.session.post(month_bill_url, data = month_bill_data)
            except:
                error = traceback.format_exc()
                return "request_error", 9, error, []
            if month_bill_req.status_code == 200:
                try:
                    month_fee_data['bill_month'] = query_month
                    selector = etree.HTML(month_bill_req.text)
                    fee_data = selector.xpath('//div[@class = "fyxx"]//tr[last()]/td[last()]/text()')[0].replace('\r\n','').replace('\t','')
                    if fee_data == "本人消费(元)":
                        fee_data = '0.00'
                    month_fee_data['bill_amount'] = fee_data
                except:
                    error = traceback.format_exc()
                    return "html_error", 9, "Xpath数据提取出错:%s"%error, {}
                month_fee.append(month_fee_data)
            else:
                return "unknown_error", 9, "爬取月度账单失败:code-%d,%s"%(month_bill_req.status_code, month_bill_req.text), []
        return "success", 0, u"爬取月度账单成功", month_fee

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "15072498067"
    USER_PASSWORD = "102907"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    print (c.crawl_phone_bill())
