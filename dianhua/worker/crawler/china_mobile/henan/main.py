# -*- coding: utf-8 -*-
import base64
import random

from lxml import etree
import re
import time
import datetime
import traceback
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
import sys
reload(sys)
sys.setdefaultencoding("utf8")

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
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

    def get_login_verify_type(self, **kwargs):
        return 'SMS'

    def get_verify_type(self, **kwargs):
        return 'SMS'


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
        sms_url = 'https://login.10086.cn/sendRandomCodeAction.action'
        sms_data = {
            'userName': kwargs['tel'],
            'type': '01',
            'channelID': '10371',
                }
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://login.10086.cn/login.html?channelID=10371&backUrl=http://service.ha.10086.cn/service/index.action"
        }
        code, key, resp = self.post(sms_url, data=sms_data, headers=headers)
        if code != 0:
            return code, key, ""

        if u"系统繁忙" in resp.text:
            code, key = 9, "website_busy_error"
        elif 'error' == resp.text:
            # 请检查您输入的手机号码, 如确认号码无误, 请稍等几分钟再试
            code, key = 9, "website_busy_error"
        elif resp.text == '0':
            code, key = 0, 'success'
        elif resp.text == '1':
            # 对不起，短信随机码暂时不能发送，请一分钟以后再试
            code, key = 9, 'send_sms_too_quick_error'
        elif resp.text == '2':
            # 短信下发数已达上限，您可以使用服务密码方式登录
            code, key = 9, 'over_max_sms_error'
        elif resp.text == '3':
            # 对不起，短信发送次数过于频繁
            code, key = 9, 'send_sms_too_quick_error'
        elif resp.text == '4':
            # 对不起，渠道编码不能为空
            code, key = 9, 'send_sms_error'
        elif resp.text == '5':
            # 对不起，渠道编码异常
            code, key = 9, 'send_sms_error'
        else:
            # 发送登录验证失败
            code, key = 9, 'unknown_error'

        if code != 0:
            self.log("crawler", key, resp)
        return code, key, ""

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
            code, pwd = self.get_encrypt(**kwargs)
            if code != 0:
                return 9, "website_busy_error"
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密失败{}".format(error), "")
            return 9, "website_busy_error"
        login_url = "https://login.10086.cn/login.htm"
        login_params = {
            'accountType': '01',
            'account': kwargs['tel'],
            'password': pwd,
            'pwdType': '01',
            'smsPwd': kwargs['sms_code'],
            'inputCode': '',
            'backUrl': 'http://service.ha.10086.cn/service/index.action',
            'rememberMe': '0',
            'channelID': '10371',
            'protocol': 'https:',
            'timestamp': '{}'.format(time.time())
                }
        # self.headers['Referer'] = 'https://login.10086.cn/login.html?channelID=10371&backUrl=http://service.ha.10086.cn/service/mobile/my-consume.action'
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://login.10086.cn/login.html?channelID=10371&backUrl=http://service.ha.10086.cn/service/index.action"
        }
        code, key, resp = self.get(login_url, params=login_params, headers=headers)
        if code != 0:
            return code, key

        try:
            json_response = resp.json()
            result_code = json_response.get('result', '')
            code_code = json_response.get('code', '')
            if json_response.get('artifact', ''):
                artifact = json_response.get('artifact', '')
                key, code, msg = "", 0, ""
            elif code_code == '8014':
                key, code, msg = 'website_busy_error', 9, ""
            elif code_code == '5002':
                key, code, msg = "pin_pwd_error", 9, ""
            elif code_code == '6002' or result_code == u'8':
                # u'短信随机码不正确或已过期，请重新获取'
                key, code, msg = 'verify_error', 9, ""
            elif code_code == '2036' or result_code == u'2':
                # u'您的账户名与密码不匹配，请重新输入'
                key, code, msg = 'login_param_error', 9, ""
            elif result_code == u'4':
                # u'手机号码不正确，请您重新输入'
                key, code, msg = 'login_param_error', 1, ""
            # 系统繁忙
            elif result_code == u'5':
                key, code, msg = "website_busy_error", 9, ""
            else:
                # 登录验证json_error
                key, code, msg = 'unknown_error', 9, ""
        except:
            error = traceback.format_exc()
            self.log("crawler", "json_error: "+error, resp)
            return 9, 'json_error'

        if code != 0:
            if code in [1, 2]:
                self.log("user", key, resp)
            elif key == "website_busy_error":
                self.log("website", key, resp)
            else:
                self.log("crawler", key, resp)
            return code, key
        temp_params = {
            'artifact': artifact,
            'backUrl': 'http://service.ha.10086.cn/service/mobile/my-consume.action',
        }
        code, key, resp = self.get('http://service.ha.10086.cn/sso/getartifact.jsp', params=temp_params)
        if code != 0:
            return code, key
        return 0, "success"

    def send_verify_request(self, **kwargs):
        """
        Send SMS verify code
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        headers = {
            "Accept": "application/json, text/javascript, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://service.ha.10086.cn/service/self/tel-bill!detail.action?menuCode=1026"
        }
        send_verify_request_url = "http://service.ha.10086.cn/verify!xdSendSmsCode.action"
        code, key, resp = self.post(send_verify_request_url, headers=headers)
        if code != 0:
            return code, key, ""
        try:
            if u"系统繁忙" in resp.text or u"重新登录" in resp.text or u'系统异常' in resp.text:
                self.log("crawler", "website_busy_error", resp)
                return 9, "website_busy_error", ''
            json_response = resp.json()
            if json_response.get('returnCode', '') == '0':
                return 0, 'success', ''
            elif json_response.get('returnCode', '') == '1':
                self.log("crawler", "send_sms_too_quick_error", resp)
                return 9, 'send_sms_too_quick_error', ''
            elif json_response.get('returnMessage', '') == u'您在24小时内获取二次鉴权码次数已达到10次,不要频繁获取!':
                self.log("user", "over_query_limit", resp)
                return 9, 'over_query_limit', ""
            elif u'达到最大重试次数' in resp.text:
                self.log("website", '接口达到最大重试次数', resp)
                return 9, 'over_query_limit', ""
            else:
                self.log("crawler", "unknown_error", resp)
                return 9, 'unknown_error', ''

        except:

            error = traceback.format_exc()
            self.log("crawler", 'json_error: '+error, resp)
            return 9, 'json_error', ''


    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        verify_url = "http://service.ha.10086.cn/verify!xdcodeAuth.action"
        today = datetime.datetime.now().strftime('%Y%m%d')
        verify_data = {
                'startDate': today[:-2]+'01',
                'endDate': today,
                'verifyCode': kwargs['sms_code'],
        }
        headers = {
            "Accept": "application/json, text/javascript, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://service.ha.10086.cn/service/self/tel-bill!detail.action?menuCode=1026"
        }
        code, key, resp = self.post(verify_url, data=verify_data, headers=headers)
        if code != 0:
            return code, key
        try:
            json_response = resp.json()
            if json_response.get('returnCode', '') == '0':
                return 0, 'success'
            else:
                self.log("user", "verify_error", resp)
                return 9, 'verify_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", "json_error: "+error, resp)
            return 9, 'json_error'

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
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.ha.10086.cn/service/self/tel-bill.action"
        }
        info_url = "http://service.ha.10086.cn/service/self/customer-info-uphold.action?menuCode=1140"
        code, key, resp = self.get(info_url, headers=headers)
        if code != 0:
            return code, key, {}
        if self.get_info(resp.text)[0]:
            return 0, 'success', self.get_info(resp.text)[1]
        else:
            self.log("crawler", "html_error: "+self.get_info(resp.text)[1], resp)
            return 9, 'html_error', {}

    def get_info(self, response_text):
        try:
            full_name = re.search(u'机主姓名：</span><span class="f14px">([\s\S]*?)<a', response_text).group(1)
            id_card = re.search(u'入网身份证号：</span><span class="f14px o_num">([\s\S]*?)</span></li>', response_text).group(1)
            is_realname_register = re.search(u'实名制信息：([\s\S]*?)</a></span></li>', response_text).group(1)
            open_date = self.time_transform(re.search(u'入网时间：</span><span class="f14px o_num">([\s\S]*?)</span></li>', response_text).group(1), str_format="%Y-%m-%d")

            # info_file = codecs.open('info.py','w+','utf-8')
            # info_file.write(response_text)
            full_name = ''.join(full_name)
            full_name = full_name.replace('&nbsp;', '')
            realname_info = ''.join(is_realname_register)
            address = ''
            return True, {'full_name': full_name,
                          'id_card': id_card,
                          'is_realname_register': u'已实名' in realname_info or u'客户信息真实' in realname_info,
                          'open_date': ''.join(open_date),
                          'address': address
                          }
        except:
            error = traceback.format_exc()
            return False, error

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

        # Get Current Month Detail Info
        record_list = []
        message_list = []
        today = datetime.date.today()
        level, key, message, result, response = self.request_single_month(today)
        if u'您未登录，请先登录' in response.text:
            self.log('website', u'登录失败异常', response)
            return 9, 'website_busy_error', [], [], []
        missing_list, possibly_missing_list = [], []
        year_month = "%d%02d" % (today.year, today.month)
        if level == 0:
            if result:
                record_list.extend(result)
                # print("{}:详单个数{}".format(year_month, len(result)))
            else:
                self.log("crawler", key, response)
                possibly_missing_list.append(year_month)
        if level != 0:
            self.log("crawler", key, response)
            missing_list.append(year_month)
        page_and_retry = []
        for month_end in list(
            rrule(MONTHLY,
                  count=5,
                  bymonthday=-1,
                  dtstart=today + relativedelta(months=-5))):
            year_month = str(month_end.year) + '%02d' % month_end.month
            page_and_retry.append((month_end, year_month, self.max_retry))

        st_time = time.time()
        et_time = st_time + 30
        log_for_retry_request = []

        while page_and_retry:
            month_end, m_query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            level, key, message, result, response = self.request_single_month(month_end)
            if level == 0 and result:
                record_list.extend(result)
                # print("{}:详单个数{}".format(m_query_month, len(result)))
                continue
            elif not result:
                self.log("crawler", u"详单为空：{}{}".format(key, message), response)
            if level != 0:
                if message != "network_request_error":
                        self.log("crawler", "{}{}".format(key, message), response)
                message_list.append(key)

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((month_end, m_query_month, m_retry_times))
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((month_end, m_query_month, m_retry_times))
                    time.sleep(rand_sleep)
                else:
                    if not result and level == 0:
                        possibly_missing_list.append(m_query_month)
                    else:
                        missing_list.append(m_query_month)
            else:
                if not result and level == 0:
                    possibly_missing_list.append(m_query_month)
                else:
                    missing_list.append(m_query_month)
        # print(len(record_list))
        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        if len(missing_list+possibly_missing_list) == 6:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or x.count('network_request_error') or 0, message_list)
            if temp_list.count(0) ==0:
                return 9, 'website_busy_error', [], missing_list, possibly_missing_list
            else:
                return 9, 'crawl_error', [], missing_list, possibly_missing_list
        return 0, 'success', record_list, missing_list, possibly_missing_list

    def request_single_month(self, month_end, check_flag=False):

        call_params = {
                'type': 'call',
                'FilteredMobileNo': '',
                'StartDate': '{0}{1}01'.format(month_end.year, str(month_end.month).zfill(2)),
                'EndDate': '{0}{1}{2}'.format(month_end.year, str(month_end.month).zfill(2), str(month_end.day).zfill(2)),
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.ha.10086.cn/service/self/tel-bill-detail.action?menuCode=1032"
        }
        call_url = "http://service.ha.10086.cn/service/self/tel-bill-detail!call.action"
        code, key, resp = self.get(call_url, params=call_params, headers=headers)
        if code != 0:
            return code, key, "network_request_error", [], resp
        year_month = "%d%02d" % (month_end.year, month_end.month)
        try:
            if u'业务受限' in resp.text:
                return 9, "websiter_prohibited_error", u"由于用户申请受限（业务受限），无法进行查询", [], resp
            err_code, err_desc, err_msg, data = self.get_call(resp.text, year_month)
            if err_desc != "success":
                return err_code, err_desc, err_msg, [], resp
            if not data:
                key, level, message, result, response = 'success', 0, '查询成功, 但是数据为空', [], resp
                if not check_flag:
                    level, key, message, result, response = self.request_single_month(month_end, check_flag=True)
                return level, key, message, result, response
        except:
            error = traceback.format_exc()
            # print "转换时间格式失败%s"%error
            return 9, "unknown_error", u"unknown_error:{}".format(error), [], resp
        return 0, 'success', '成功', data, resp

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        # 2017-03-17/10:35:07
        if time_str == "":
            return ""
        if str_format == "%Y-%m-%d":
            ymd = re.findall(r"(\d{4}).*?(\d{1,2}).*?(\d{1,2})", time_str.encode("utf-8"))[0]
            time_str = reduce(lambda x, y: x+'-'+y, ymd)
            time_str += " 12:00:00"
        str_format = "%Y-%m-%d %H:%M:%S"
        time_type = time.strptime(time_str.encode(bm), str_format)
        return str(int(time.mktime(time_type)))

    def time_format(self, time_str, **kwargs):
        exec_type = 1
        if time_str == "":
            return ""
        time_str = time_str.encode('utf-8')
        if (exec_type == 1):
            xx = re.match(r'(.*时)?(.*分)?(.*秒)?', time_str)
            h, m, s = 0, 0, 0
            if xx.group(1):
                hh = re.findall(r'\d+', xx.group(1))[0]
                h = int(hh)
            if xx.group(2):
                mm = re.findall(r'\d+', xx.group(2))[0]
                m = int(mm)
            if xx.group(3):
                ss = re.findall(r'\d+', xx.group(3))[0]
                s = int(ss)
            real_time = h*60*60 + m*60 + s
        return str(real_time)

    def get_call(self, response_text, year_month):
        try:
            et = etree.HTML(response_text)
            if u'对不起,查询信息不存在!' in et.xpath('//tbody[@id="tbody_call"]//text()'):
                return 0, "success", "no data", []
            else:
                let = et.xpath("//*[@id='tbody_call']")[0]
                cc = let.xpath("./tr[@class='table_bg_bottom']")
                data_list = []
            for i in cc:
                record = {}
                li = i.xpath("./td")
                if len(li) <= 2:
                    return 0, "success", "解析失败, 数据区域为空", []
                # print li
                # 获取当前节点同级的节点 并且class属性为指定值的节点列表
                date_list = i.xpath('./preceding-sibling::tr[@class="table_bg_bottom pinp-tdb font-co"]/td/text()')
                # 获取上述列表的最后一个值, 即为当前日期值
                call_date = date_list[-1]
                record['month'] = year_month
                record['call_duration'] = self.time_format(''.join(li[4].xpath('./text()') and li[4].xpath('./text()')[0]))
                record['call_type'] = ''.join(li[5].xpath('./text()') and li[5].xpath('./text()')[0])
                record['call_method'] = ''.join(li[2].xpath('./text()') and li[2].xpath('./text()')[0])
                record['call_tel'] = ''.join(li[3].xpath('./text()') and li[3].xpath('./text()')[0])
                raw_call_from = ''.join(li[1].xpath('./text()') and li[1].xpath('./text()')[0])
                call_from, error = self.formatarea(raw_call_from)
                if not call_from:
                    call_from = raw_call_from
                    # self.log("crawler", "{}-{}".format(error, raw_call_from), "")
                record['call_from'] = call_from
                record['call_cost'] = ''.join(li[8].xpath('./text()') and li[8].xpath('./text()')[0])
                record['call_to'] = ''
                record['call_time'] = self.time_transform(call_date + ' ' + ''.join(li[0].xpath('./text()') and li[0].xpath('./text()')[0]))
                data_list.append(record)
            return 0, "success", "OK", data_list
        except:
            error = traceback.format_exc()
            return 9, "xml_error", "解析xml失败{}原始文本:{}".format(error, response_text), []

    def crawl_phone_bill(self, **kwargs):

        phone_bill = list()
        message_list = []
        params = {'tel': kwargs['tel']}
        missing_list = []
        for month in self.__monthly_period(6, '%Y%m'):
            params['month'] = month
            level, key, message, result, response = self.crawl_month_bill(**params)
            if level != 0:
                if message != "network_request_error":
                    self.log("crawler", "{}{}".format(key, message), response)
                message_list.append(key)
                missing_list.append(month)
            if result:
                phone_bill.append(result)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in missing_list and missing_list.remove(now_month)
        if len(missing_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], missing_list
        return 0, 'success', phone_bill, missing_list

    def crawl_month_bill(self, **kwargs):
        month_bill_url = 'http://service.ha.10086.cn/service/self/tel-bill.action?menuCode=1026'
        data = {'QMonth': kwargs['month']}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://service.ha.10086.cn/service/self/tel-bill.action"
        }
        for i in range(self.max_retry):
            code, key, resp = self.post(month_bill_url, data=data, headers=headers)
            if code != 0:
                is_err, err_msg, err_code, err_desc, response = True, key, code, "network_request_error", resp
                continue
            resp.encoding = 'utf=8'
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
                fee = re.findall(u'合计费用</td>\s*<td><b[\s\S]*?>([\d.]+)</b></td>', resp.text)
                if fee:
                    month_bill['bill_amount'] = fee[0]
                else:
                    is_err, err_msg, err_code, err_desc, response = True, "success", 9, "no_data", resp
                    continue
                fee = re.findall(u'套餐及固定费</td>\s*<td><b[\s\S]*?>([\d.]+)</b></td>', resp.text)
                if fee:
                    month_bill['bill_package'] = fee[0]
                fee = re.findall(u'话音通信费</td>\s*<td><b[\s\S]*?>([\d.]+)</b></td>', resp.text)
                if fee:
                    month_bill['bill_ext_calls'] = fee[0]
                fee = re.findall(u'上网费</td>\s*<td><b[\s\S]*?>([\d.]+)</b></td>', resp.text)
                if fee:
                    month_bill['bill_ext_data'] = fee[0]
                fee = re.findall(u'短彩信费</td>\s*<td><b[\s\S]*?>([\d.]+)</b></td>', resp.text)
                if fee:
                    month_bill['bill_ext_sms'] = fee[0]
                fee = re.findall(u'自有增值业务费</td>\s*<td><b[\s\S]*?>([\d.]+)</b></td>', resp.text)
                if fee:
                    month_bill['bill_zengzhifei'] = fee[0]
                fee = re.findall(u'代收费业务费</td>\s*<td><b[\s\S]*?>([\d.]+)</b></td>', resp.text)
                if fee:
                    month_bill['bill_daishoufei'] = fee[0]
                fee = re.findall(u'其他费用</td>\s*<td><b[\s\S]*?>([\d.]+)</b></td>', resp.text)
                if fee:
                    month_bill['bill_qita'] = fee[0]
                return 0, 'success', 'success', month_bill, resp
                # return 'success', 0, 'success', month_bill, resp
            except:
                error = traceback.format_exc()
                is_err, err_msg, err_code, err_desc, response = True, "unknown_error", 9, error, resp
                continue

        if is_err:
            return err_code, err_msg, err_desc, {}, resp

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)


if __name__ == '__main__':
    # from worker.crawler.main import *
    c = Crawler()
    USER_ID = "15939599335"
    USER_PASSWORD = "199935"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    """

        num:1058

        4:9
        3:17
        2:1
        1:2
        12:695
        11:334

    """
