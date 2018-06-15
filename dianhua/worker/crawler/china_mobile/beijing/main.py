# -*- coding: utf-8 -*-
import base64
import datetime
import random
import re
import sys
import time
import traceback
from lxml import etree
from dateutil.relativedelta import relativedelta

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA

reload(sys)
sys.setdefaultencoding("utf8")
if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from crawler.china_mobile.all_entry import all_entry_utils
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_mobile.all_entry import all_entry_utils

"""
        登录页面
        url = "https://login.10086.cn/sendRandomCodeAction.action"

"""


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.ssoSessionID = ""
        self.crawler_error = 0

    def get_login_verify_type(self, **kwargs):
        return 'SMS'

    def get_verify_type(self, **kwargs):
        return ''

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def send_login_verify_request(self, **kwargs):
        """
        Get validate image
        :param kwargs:
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        url = "https://login.10086.cn/sendRandomCodeAction.action"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {
            "userName": kwargs['tel'],
            "type": "POST",
            "channelID": "00100"
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key, ''
        self.log("crawler", "保存返回结果", resp)
        return all_entry_utils.parse_send_login_sms_code_response(self, resp)

    def get_encrypt(self, msg):
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

        serPwd = msg
        rsakey = RSA.importKey(publik_key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(serPwd.encode('utf-8')))
        return 0, cipher_text

    def login(self, **kwargs):
        """
        Login process
            1. Check Validate Code
            2. Check ID/PW
            3. Request Login
            4. Request Set Uid Cookie
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        try:
            code, sms_code = self.get_encrypt(kwargs['sms_code'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密短信失败{}   {}".format(kwargs['sms_code'], error), "")
            return 9, "website_busy_error"
        if code != 0:
            return code, sms_code

        url = "https://login.10086.cn/touchBjLogin.action"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {
            "rememberMe": "1",
            "accountType": "01",
            "pwdType": "02",
            "account": kwargs['tel'],
            "password": sms_code,
            "channelID": "00100",
            "protocol": "https:",
            "timestamp": str(time.time())
        }

        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key
        try:
            result = resp.json()
            result_code = result.get("code")
            if result_code != "0000" and result_code != "0":
                if result_code == "6002":
                    self.log("crawler", "短信验证码错误", resp)
                    return 9, "verify_error"
                else:
                    self.log("crawler", "未知原因错误", resp)
                    return 9, "login_param_error"
            artifact = result.get("artifact")
            self.ssoSessionID = result.get("uid")
            if not artifact or not self.ssoSessionID:
                self.log("crawler", "获取artifact或ssoSessionID为空", resp)
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析短信验证结果失败{}".format(error), resp)
            return 9, "json_error"

        url = "https://service.bj.10086.cn/ss/check/checklogin.do"
        params = {
            "backUrl": "https%3A%2F%2Fwww.bj.10086.cn%2Fservice%2Findex.html",
            "artifact": artifact
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key
        if not resp.text.strip():
            self.log("crawler", "返回为空", resp)
            return 9, "website_busy_error"
        if "详单查询" not in resp.text:
            self.log("crawler", "未知原因登录失败", resp)
            return 9, "unknown_error"
        # 验证服务密码
        url = "https://service.bj.10086.cn/poffice/package/xdcx/userYzmCheck.action"
        data = {
            "yzCheckCode": kwargs['pin_pwd'],
            "PACKAGECODE": "XD"
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://service.bj.10086.cn/poffice/package/xdcx/xdcxShow.action?PACKAGECODE=XD&PRODUCTSHOWCODE=TCJGDFXD&PRODUCTCODE=G_TCJGDFXD&PACKAGEID=289001&isAutonomous=1"
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key
        try:
            result = resp.json()
            message = result.get("message")
            if message != "Y":
                self.log("crawler", "服务密码错误", resp)
                return 9, "pin_pwd_error"
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析密码结果失败{}".format(error), resp)
        return 0, "success"

    def crawl_info(self, **kwargs):
        """
        Crawl user's personal info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        # Get Personal Info
        personal_info = {'full_name': '',
                         'id_card': '',
                         'is_realname_register': False,
                         'open_date': '',
                         'address': '',
                         }
        info_url = "https://service.bj.10086.cn/poffice/jsp/my/index_md.jsp"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        code, key, resp = self.get(info_url, headers=headers)
        if code != 0:
            return code, key, personal_info
        try:
            name = re.findall("hasRealName=(.*?),", resp.text)[0]
            idcard = re.findall("CredentialType=(.*?),", resp.text)[0]
            personal_info["full_name"] = name
            personal_info["id_card"] = idcard
            return 0, "success", personal_info
        except ValueError:
            error = traceback.format_exc()
            self.log("crawler", 'json_error: ' + error, resp)
            return 9, 'json_error', personal_info
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: " + error, resp)
            return 9, 'unknown_error', personal_info

    def get_search_list(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        search_list = []
        for month_offset in range(0, length):
            search_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return search_list

    def crawl_call_log(self, **kwargs):
        """
        Crawl user's detail bill info
            1. Get Current Month Detail Info
            2. Get Past Month Detail Info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        today = datetime.date.today()
        pos_miss_list = []
        miss_list = []

        # 暂时未做可能缺失
        search_month = [(i, self.max_retry) for i in self.get_search_list()]
        st_time = time.time()
        time_limit = 40
        retry_limit = -3
        break_time = st_time + time_limit
        rand_sleep = random.uniform(1.4, 3.2)
        retry_log = []
        data_list = []

        while search_month:
            search_str, retry_times = search_month.pop(0)
            code, key, data = self.get_page_data(search_str)
            if code == 0:
                if data:
                    data_list.extend(data)
                    continue
            now_time = time.time()

            if now_time > break_time or retry_times < retry_limit:
                miss_list.append(search_str)
            else:
                retry_times -= 1
                time.sleep(rand_sleep)
                retry_log.append((search_str, retry_times))
                search_month.append((search_str, retry_times))
        self.log("crawler", "记录重试内容{}".format(retry_log), "")
        self.log("crawler", "缺失列表记录{}".format(miss_list), "")
        if len(miss_list) == 6:
            if self.crawler_error > 0:
                return 9, "crawl_error", data_list, miss_list, pos_miss_list, []
            return 9, "website_busy_error", data_list, miss_list, pos_miss_list, []
        return 0, 'success', data_list, miss_list, pos_miss_list, []

    def get_page_data(self, search_month_str, **kwargs):
        data_list = []
        url = "https://service.bj.10086.cn/poffice/package/xdcx/xdcxShow.action"
        headers = {
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {
            "PACKAGECODE": "XD",
            "xdFlag": "GSM",
            "month": search_month_str
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key, data_list
        code, key, data = self.get_data(resp, search_month_str)
        if code != 0:
            self.log("crawler", "解析详单数据错误", resp)
            return code, key, data_list
        else:
            if data:
                data_list.extend(data)
            else:
                self.log("crawler", "未知原因数据为空", resp)
            return 0, "success", data_list

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        """
        call_time 格式化
        return
            call_time: str, 时间戳(秒)，eg：'1494577393'
        """
        time_str = time_str.encode(bm)
        if re.findall(r"(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})", time_str):
            time_str = reduce(lambda x, y: x + '-' + y, time_str.split(' ')[0].split('/')) + " " + time_str.split(" ")[
                1]
        if len(re.findall(r"(\d{2,4})", time_str)) == 5:
            today_month = datetime.date.today().month
            today_year = datetime.date.today().year
            str_month = int(time_str[:2])
            if str_month > today_month:
                str_year = today_year - 1
            else:
                str_year = today_year
            time_str = str(str_year) + "-" + time_str
        if len(re.findall(r"(\d{2,4})", time_str)) == 6:
            time_str_list = re.findall(r"(\d{2,4})", time_str)
            time_str = reduce(lambda x, y: x + '-' + y, time_str_list[0:3]) + " " + reduce(lambda x, y: x + ':' + y,
                                                                                           time_str_list[3:])
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

    def get_data(self, resp, month):
        try:
            data_list = []
            et = etree.HTML(resp.text)
            tbody = et.xpath("//*[@id='DETAIL']/tr")
            for li in tbody:
                data = {
                    "call_time": "",
                    "month": month,
                    "call_duration": "",
                    "call_type": "",
                    "call_method": "",
                    "call_tel": "",
                    "call_from": "",
                    "call_cost": "",
                    "call_to": ""
                }

                call_time = li.xpath("td[1]/text()")[0]
                data['call_time'] = self.time_transform(call_time)
                call_duration = li.xpath("td[6]/text()")[0]
                data['call_duration'] = self.time_format(call_duration)
                data['call_type'] = li.xpath("td[7]/text()")[0]
                data['call_method'] = li.xpath("td[3]/text()")[0]
                call_tel = li.xpath("td[5]/text()")[0]
                data['call_tel'] = call_tel.strip()
                raw_call_from = li.xpath("td[2]/text()")[0]
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data[u'call_from'] = call_from
                else:
                    data[u'call_from'] = raw_call_from
                data['call_cost'] = li.xpath("td[10]/text()")[0]
                data_list.append(data)
        except:
            self.crawler_error += 1
            error = traceback.format_exc()
            self.log("crawler", "解析详单出错{}".format(error), resp)
            return 9, "html_error", []
        return 0, "success", data_list

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
        # get cookies
        url = "https://cmodsvr1.bj.chinamobile.com/PortalCMOD/InnerInterFaceCiisHisBill"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "http://service.bj.10086.cn/bjyd/web/service/fee/zdcx/index.html"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return 9, 'website_busy_error', [], miss_list
        try:
            check_url = re.findall('action="(.*?)"', resp.text)[0]
            headers = {
                "Referer": url,
            }
            code, key, resp = self.get(check_url, headers=headers)
            if code != 0:
                return 9, 'website_busy_error', [], miss_list
            for his in resp.history:
                self.log("crawler", "记录账单跳转", his)
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取跳转URL失败{} ".format(error), resp)

        today = datetime.date.today()
        month_bill_url = "https://cmodsvr1.bj.chinamobile.com/PortalCMOD/bill/userbillall.do"
        headers = {
            "Accept": "text/html, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            # "Referer": "https://cmodsvr1.bj.chinamobile.com/PortalCMOD/bill/user_bill_all.jsp?ssoSessionID=02e06911c42147a0b14eba214e63243a&Month=2018.04&isReal=true",
            "X-Requested-With": "XMLHttpRequest"
        }

        search_month = [x for x in range(-1, -6, -1)]
        for each_month in search_month:
            # month_fee_data = {}
            query_date = today + relativedelta(months=each_month)
            month_str = "%d%02d" % (query_date.year, query_date.month)
            query_month = "%d.%02d" % (query_date.year, query_date.month)
            params = {
                "ssoSessionID": self.ssoSessionID,
                "Month": query_month,
                "livel": "ACCOUNT"
            }
            for i in range(self.max_retry):
                code, key, resp = self.get(month_bill_url, params=params, headers=headers)
                if code != 0:
                    msg = "network_request_error"
                    continue
                # print month_bill_req.text
                try:
                    month_bill_res = resp.json()
                    if month_bill_res.get("MESSAGE") != "OK":
                        self.log("crawler", "未知原因导致失败", resp)
                        return 9, 'website_busy_error', [], miss_list
                    bill_info = month_bill_res.get('userBillBMCCVo')
                    if not bill_info:
                        bill_info = month_bill_res.get("userBillCMCC4Vo")
                    call_bill_list = bill_info.get("feeGatherVo")
                    month_fee_data = {}
                    month_fee_data['bill_month'] = month_str
                    month_fee_data['bill_amount'] = call_bill_list.get('FEE_TOTAL', '')
                    month_fee_data['bill_package'] = call_bill_list.get('FEE_BASE', '')
                    month_fee_data['bill_ext_calls'] = call_bill_list.get('FEE_GSM', '')
                    month_fee_data['bill_ext_data'] = call_bill_list.get('FEE_GPRS', '')
                    month_fee_data['bill_ext_sms'] = call_bill_list.get('FEE_SMS_MMS', '')
                    month_fee_data['bill_zengzhifei'] = call_bill_list.get('FEE_ZENGZHI', '')
                    month_fee_data['bill_daishoufei'] = call_bill_list.get('FEE_DAISHOU', '')
                    month_fee_data['bill_qita'] = call_bill_list.get('FEE_OTHERS', '')
                    month_fee.append(month_fee_data)
                    break
                except:
                    error = traceback.format_exc()
                    msg = "json_error: " + error
                    continue
            else:
                if msg != "network_request_error":
                    self.log("crawler", msg, resp)
                miss_list.append(month_str)
                message_list.append(msg)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5:
            temp_list = map(
                lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0,
                message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], miss_list
        return 0, "success", month_fee, miss_list


if __name__ == '__main__':
    c = Crawler()
    USER_ID = "18301495516"
    USER_PASSWORD = "332266"
    # print(c.get_encrypt(pin_pwd=USER_PASSWORD))
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
