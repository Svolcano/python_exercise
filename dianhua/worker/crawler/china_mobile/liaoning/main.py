# -*- coding: utf-8 -*-
import datetime
import re
import random
import sys
import time
import traceback
import base64
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, rrule
# from lxml.html import soupparser
from lxml import etree

import response_data

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
reload(sys)
sys.setdefaultencoding("utf-8")

'''TODO:
    * pass the normal flow
    * logging the import step and info to the file for debugging
    * test session funciton
    * handle normal error case as possible as you can
    * handle any unexpected exception case
'''

if __name__ == '__main__':
    sys.path.append('../../..')
    sys.path.append('../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.headers = {}
        self.record_list = []

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_code']

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
            level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """

        url = 'https://login.10086.cn/sendRandomCodeAction.action?'
        form_data = {
            'type': '01',
            'userName': kwargs['tel'],
            'channelID': '00240',
        }
        headers = {"X-Requested-With": "XMLHttpRequest"}
        code, key, resp = self.post(url, data=form_data, headers=headers)
        if code != 0:
            return code, key, ""
        if resp.text == u'0':
            key, level, message, result = 'success', 0, '', ''
        elif resp.text == '1':
            key, level, message, result = 'send_sms_too_quick_error', 9, '对不起，短信随机码暂时不能发送，请一分钟以后再试！response:{}'.format(resp.text), ''
        elif resp.text == '2':
            key, level, message, result = 'over_max_sms_error', 9, '短信下发数已达上限，您可以使用服务密码方式登录！response:{}'.format(resp.text), ''
        elif resp.text == '3':
            key, level, message, result = 'send_sms_too_quick_error', 9, '对不起，短信发送次数过于频繁！response:{}'.format(resp.text), ''
        elif resp.text == '4':
            key, level, message, result = 'send_sms_error', 9, '对不起，渠道编码不能为空！response:{}'.format(resp.text), ''
        elif resp.text == '5':
            key, level, message, result = 'send_sms_error', 9, '对不起，渠道编码异常！response:{}'.format(resp.text), ''
        else:
            if resp.text == 'error':
                key, level, message, result = "send_sms_error", 9, '请求发送短信时, 官网返回error{}'.format(resp.text), ''
            key, level, message, result = 'send_sms_error', 9, 'slvr_response:{}'.format(resp.text), ''
        if level != 0:
            self.log("crawler", "{}: {}".format(key, message), resp)
        return level, key, result

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """

        headers = {"X-Requested-With": "XMLHttpRequest"}
        url = "http://www.ln.10086.cn/busicenter/detailquery/DetailQueryMenuAction/initBusi.menu?_menuId=40399&_menuId=40399"
        # url = 'http://www.ln.10086.cn/busicenter/myinfo/MyInfoMenuAction/initBusi.menu?_menuId=1040101&_menuId=1040101'
        send_verify_data = {'divId': 'main'}
        code, key, resp = self.post(url, data=send_verify_data, headers=headers)
        if code != 0:
            return code, key, ""
        if u'对不起，今日您输入错误次数过多，请明天再试' in resp.text:
            self.log("user", 'over_max_sms_error', resp)
            return 9, 'over_max_sms_error', ''
        if u'系统已经以短消息的形式将随机短信密码发送到手机上，请在下面的输入框中输入该密码。' not in resp.text:
            self.log("crawler", 'send_sms_error', resp)
            return 9, 'send_sms_error', ''
        return 0, 'success', ''

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
            level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
        """
        try:
            code, pwd = self.get_encrypt(**kwargs)
            if code != 0:
                return 9, "website_busy_error"
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密失败{}".format(error), "")
            return 9, "website_busy_error"
        url = 'https://login.10086.cn/login.htm'
        params = {
            'accountType': '01',
            'account': kwargs['tel'],
            'password': pwd,
            'pwdType': '01',
            'smsPwd': kwargs['sms_code'],
            'inputCode': '',
            'backUrl': 'www.ln.10086.cn/my/account/index.xhtml',
            'rememberMe': '0',
            'channelID': '00240',
            'protocol': 'https:',
            'timestamp': '{}'.format(int(time.time()))
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://login.10086.cn/login.html?channelID=00240&backUrl=www.ln.10086.cn%2Fmy%2Faccount%2Findex.xhtml"
        }
        code, key, resp = self.get(url, params=params, headers=headers)
        if code != 0:
            return code, key
        if u'您输入的短信验证码错误' in resp.text:
            self.log("user", 'verify_error', resp)
            return 9, 'verify_error'
        try:
            json_response = resp.json()
            if json_response.get('artifact', ''):
                artifact = json_response.get('artifact', '')
                key, level, message = "success", 0, ""
            elif json_response.get('code', '') == '6002':
                key, level, message = 'verify_error', 9, ""
            elif json_response.get('code') == '2036' or json_response.get('code') == '5002':
                # 您的账户名与密码不匹配，请重新输入
                # 不确定是否可重试, 使用商城验证码, 暂假定为无法重试
                key, level, message = 'pin_pwd_error', 9, ""
            elif json_response.get('code') == '8014':
                # code:"8014","desc":"系统繁忙，请您稍后再试"
                key, level, message = "website_busy_error", 9, ""
            elif json_response.get('result', '') == u'2' or json_response.get('result', '') == u'8':
                key, level, message = 'verify_error', 9, ""
            else:
                key, level, message = 'unknown_error', 9, ""
        except:
            error = traceback.format_exc()
            key, level, message = 'json_error', 9, ": " + error
        if level != 0:
            if level in [1, 2]:
                self.log("user", key + message, resp)
            else:
                self.log("crawler", key + message, resp)
            return level, key
        temp_params = {
            'artifact': artifact,
            'backUrl': 'www.ln.10086.cn/sso/iLoginFrameCas.jsp',
        }
        code, key, resp = self.get('http://www.ln.10086.cn/SSOLogin', params=temp_params)
        if code != 0:
            if isinstance(resp, str):
                pass
            else:
                if str(resp.status_code) == '404':
                    return 9, 'website_busy_error'
            return code, key
        return 0, 'success'

    def verify(self, **kwargs):
        """
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
        """
        url = "http://www.ln.10086.cn/busicenter/detailquery/DetailQueryMenuAction/checkSmsPassWd.menu"
        verify_data = {'_menuId': '40399', 'commonSmsPwd': kwargs['sms_code']}
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.ln.10086.cn/my/account/detailquery.xhtml"
        }
        code, key, resp = self.post(url, data=verify_data, headers=headers)
        if code != 0:
            return code, key
        try:
            json_response = resp.json()
            if json_response.get('checkResult', '') == 'success':
                key, level, message = 'success', 0, ''
            elif json_response.get('errorCode', '') == u'20007':
                key, level, message = 'verify_error', 9, ""
            elif json_response.get('errorCode', '') == u'20202':
                key, level, message = 'over_max_sms_error', 9, ""
            elif json_response.get('errorCode', '') == u'10017':
                key, level, message = 'send_sms_too_quick_error', 2, ""
            elif json_response.get('type', '') == u'3':
                key, level, message = 'website_busy_error', 9, ""
            else:
                key, level, message = 'unknown_error', 9, ""
        except:
            error = traceback.format_exc()
            key, level, message = 'unknown_error', 9, ": " + error
        if level != 0:
            self.log("crawler", key + message, resp)
        return level, key

    def crawl_info(self, **kwargs):
        """
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        url = 'http://www.ln.10086.cn/busicenter/myinfo/MyInfoMenuAction/initBusi.menu?_menuId=1040101&_menuId=1040101'
        crawl_info_data = {'divId': 'main'}
        code, key, resp = self.post(url, data=crawl_info_data)
        if code != 0:
            return code, key, {}
        is_ok, result = self.get_info(resp.text)
        if is_ok:
            return 0, 'success', result
        else:
            self.log("crawler", result, resp)
            return 9, 'html_error', {}

    def get_info(self, response_text):
        try:
            full_name = re.search(u'客户姓名：([\s\S]*?)</li>', response_text).group(1)
            id_card = re.search(u'证件号码：([\s\S]*?)</li>', response_text).group(1)
            is_realname_register = True
            open_date = self.time_transform(re.search(u'入网时间：([\s\S]*?)</li>', response_text).group(1), str_format="%Y-%m-%d")
            address = re.search(u'客户地址：([\s\S]*?)</li>', response_text).group(1)

            return True, {
                'full_name': ''.join(full_name),
                'id_card': id_card,
                'is_realname_register': is_realname_register,
                'open_date': open_date,
                'address': address
            }
        except:
            error = traceback.format_exc()
            return False, "html_error: {}".format(error)

    def crawl_call_log(self, **kwargs):
        """
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        pos_miss_list = []
        miss_list = []
        message_list = []
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        url = 'http://www.ln.10086.cn/busicenter/detailquery/DetailQueryMenuAction/initBusi.menu?_menuId=40399&_menuId=40399'
        detailquery_data = {'divId': 'main'}
        # 获取cookies
        for i in range(self.max_retry):
            code, key, resp = self.post(url, data=detailquery_data, headers=headers)
            if code != 0:
                continue
            else:
                if u'请选择您要查询的月份' not in resp.text:
                    key, level, message = "unknown_error", 9, "获取详单未知异常{}".format(resp.text)
                    continue
                break
        else:
            self.log("crawler", "{}网络错误, 或者未知错误导致数据全空".format(key), resp)
            miss_list = list(self.__monthly_period(offset=0))
            if key == "unknown_error":
                return 9, 'crawl_error', self.record_list, miss_list, pos_miss_list
            else:
                return 9, 'website_busy_error', self.record_list, miss_list, pos_miss_list
        # 因为在get_call 中处理所有的异常情况, 在request_single_month中, self.record_list可以保证不会重复填充
        today = datetime.date.today()
        level, status_key, message, response = self.request_single_month(today, miss_list, pos_miss_list)
        if level != 0:
            self.log('crawler', status_key + message, response)
        for month_end in list(
                rrule(MONTHLY,
                      count=5,
                      bymonthday=-1,
                      dtstart=today + relativedelta(months=-5))):

            level, status_key, message, response = self.request_single_month(month_end, miss_list, pos_miss_list)
            if level != 0 and message != "network_request_error":
                self.log("crawler", status_key + message, resp)
                message_list.append(status_key)
        self.log('crawler', '缺失：{}, 可能缺失：{}'.format(miss_list, pos_miss_list), '')
        if len(miss_list + pos_miss_list) == 6:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or x.count('no_call_log') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], miss_list, pos_miss_list
            else:
                return 9, 'crawl_error', [], miss_list, pos_miss_list
        return 0, 'success', self.record_list, miss_list, pos_miss_list

    def request_single_month(self, month_end, miss_list, pos_miss_list):
        call_params = {
            '_menuId': '40399',
            'beginDate': '{0}{1}01'.format(month_end.year, str(month_end.month).zfill(2)),
            'endDate': '{0}{1}{2}'.format(month_end.year, str(month_end.month).zfill(2), str(month_end.day).zfill(2)),
            'select': '{0}{1}'.format(month_end.year, str(month_end.month).zfill(2)),
            '_': '{0}'.format(int(float(time.time()) * 1000)),
            'detailType': '202'
        }
        year_month = "%d%02d" % (month_end.year, month_end.month)
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        call_url = "http://www.ln.10086.cn/busicenter/detailquery/DetailQueryMenuAction/queryResult.menu"
        start_time = time.time()
        end_time = start_time + 11
        aid_time_dict = dict()
        retry_times = self.max_retry
        log_for_retry = []
        while 1:
            log_for_retry.append((1, retry_times))
            retry_times -= 1
            code, key, resp = self.get(call_url, params=call_params, headers=headers)
            if not code:
                code, key, message, result = self.get_call(resp.text, year_month)
                if not code:
                    flag = True
                    self.record_list.extend(result)
                    break
                elif code and key == 'no_call_log':
                    missing_flag = False
                else:
                    missing_flag = True
            else:
                missing_flag = True
                message = "network_request_error"
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
                    miss_list.append(year_month)
                else:
                    pos_miss_list.append(year_month)
                break
        self.log('crawler', '{}重试记录{}'.format(year_month, log_for_retry), '')
        if flag:
            return 0, 'success', '', ''
        return code, key, message, resp

        # for i in range(self.max_retry):
        #     message = ""
        #     level, key, resp = self.get(call_url, params=call_params, headers=headers)
        #     if level != 0:
        #         message = "network_request_error"
        #         continue
        #     # print resp.text
        #     level, key, message, result = self.get_call(resp.text, year_month)
        #     if level == 0:
        #         self.record_list.extend(result)
        #         break
        #     else:
        #         continue
        # else:
        #     if level != 0 and key == 'no_call_log':
        #         pos_miss_list.append("%d%02d" % (month_end.year, month_end.month))
        #     elif level != 0:
        #         miss_list.append("%d%02d" % (month_end.year, month_end.month))
        #     return level, key, message, resp
        # return 0, 'success', '', ""

    @staticmethod
    def random_sleep(tm, modulus=3):
        time.sleep(random.uniform(tm / modulus / 1.5, 1.5 * tm / modulus))

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        if str_format == "%Y-%m-%d":
            time_str += " 12:00:00"
        str_format = "%Y-%m-%d %H:%M:%S"
        time_type = time.strptime(time_str.encode(bm), str_format)
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

    def get_call(self, response_text, year_month):
        call_log = []
        try:
            et = etree.HTML(response_text)
            ee = et.xpath("//table[@class='w950_detailtable'][2]/tr")[1:]
            if len(ee) == 0:
                return 9, "no_call_log", "没有数据", []
            now_data = ""
            for i in ee:
                if len(i) == 1:
                    now_data = i.xpath('th/text()')[0]
                else:
                    if now_data == "":
                        return 9, "crawl_error", "不应该出现这种情况, 除非官网数据不对", []
                    record = {}
                    xx = i.xpath("td")
                    """
                    0 <td>03:39:57</td>
                    1 <td>北京</td>
                    2 <td>主叫</td>
                    3 <td>2G</td>
                    4 <td>10086</td>
                    5 <td>非本地移动号码</td>
                    6 <td></td>
                    7 <td>1分钟58秒</td>
                    8 <td>国内异地主叫</td>
                    9 <td></td>
                    10 <td>0.00</td>
                    """
                    call_time, record['call_method'], record['call_tel'], record['call_duration'], \
                    record['call_type'], record['call_cost'] = (xx[x].xpath("text()")[0] for x in
                                                                (0, 2, 4, 7, 8, 10))
                    raw_call_from = xx[1].xpath("text()")[0]
                    call_from, error = self.formatarea(raw_call_from)
                    if not call_from:
                        call_from = raw_call_from
                        # self.log("crawler", "{}-{}".format(error, raw_call_from), "")
                    record['call_from'] = call_from
                    record['call_to'] = ''
                    call_time = now_data + ' ' + call_time
                    record['call_duration'] = self.time_format(record['call_duration'])
                    record['call_time'] = self.time_transform(call_time)
                    record['month'] = year_month
                    call_log.append(record)
        except:
            error = traceback.format_exc()
            key, level, message, result = "html_error", 9, ": {}".format(error), []
            return level, key, message, result
        key, level, message, result = "success", 0, "", call_log
        return level, key, message, result

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        miss_list = []
        message_list = []
        # 官网无当前月账单, 返回 该月未出账单
        # miss_list.append(datetime.datetime.now().strftime("%Y%m"))
        for searchMonth in self.__monthly_period(5, '%Y%m'):
            crawl_phone_bill_data = {
                'flag': '999',
                'billMonth': searchMonth,
                '_menuId': '1050344'
            }
            URL_PHONE_BILL = 'http://www.ln.10086.cn/busicenter/fee/monthbill/MonthBillMenuAction/initBusi.menu'
            for i in range(self.max_retry):
                code, key, resp = self.get(URL_PHONE_BILL, params=crawl_phone_bill_data)
                if code != 0:
                    message = 'network_request_error'
                    continue
                level, key, message, result = response_data.phone_bill_data(resp.text, searchMonth)
                if level != 0:
                    continue
                if result:
                    phone_bill.append(result)
                    break
                elif i == self.max_retry - 1:
                    message = "no_data"
                    continue
            else:
                if message != "network_request_error":
                    self.log("crawler", key + message, resp)
                message_list.append(key)
                miss_list.append(searchMonth)
        if len(miss_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], miss_list
        return 0, 'success', phone_bill, miss_list

    def __monthly_period(self, length=6, strf='%Y%m', offset=1):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset + offset)).strftime(strf)


if __name__ == '__main__':
    tel = '18242941749'
    pin_pwd = '717889'
    c = Crawler()
    c.self_test(tel=tel, pin_pwd=pin_pwd)
