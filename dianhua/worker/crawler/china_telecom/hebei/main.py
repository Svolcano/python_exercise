# -*- coding: utf-8 -*-

import hashlib
import base64
import traceback
import datetime
import time
import calendar
import sys
import re
# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")

from Crypto.Cipher import AES
from datetime import date
from dateutil.relativedelta import relativedelta
from lxml import etree



if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from crawler.china_telecom_tool import login_error
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_error

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
        self.AREA_CODE = '183'

    def need_parameters(self, **kwargs):
        return ['pin_pwd','sms_verify',
         'full_name', 'id_card', 'captcha_verify'
         ]

    def get_login_verify_type(self, **kwargs):
        return "Captcha"

    def send_login_verify_request(self, **kwargs):
        url = "http://login.189.cn/web/captcha?undefined&source=login&width=100&height=37"
        headers = {"Referer": "http://login.189.cn/login"}

        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ""
        return 0, "success", base64.b64encode(resp.content)

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def aes_encrypt(self,n):
        # this is the porting from telecom javascript
        pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
        n = pad(n)
        e = hashlib.md5('login.189.cn')
        t = e.hexdigest()
        i = t.encode('utf-8')
        r = u'1234567812345678'.encode('utf-8')
        encryption_suite = AES.new(i, AES.MODE_CBC, r)
        cipher_text = encryption_suite.encrypt(n)
        base64.b64encode(cipher_text)
        return base64.b64encode(cipher_text)

    def login(self, **kwargs):
        login_url = "http://login.189.cn/web/login"
        try:
            pwd = self.aes_encrypt(kwargs['pin_pwd'])
        except:
            error = traceback.format_exc()
            message = 'login_param_error %s' % error
            self.log('crawler', message, '')
            return 9, 'login_param_error'
        login_data = {
            "Account": kwargs['tel'],
            "UType": '201',
            "ProvinceID": '05',
            "AreaCode": "",
            "CityNo":"",
            "RandomFlag": '0',
            "Password": pwd,
            "Captcha": kwargs['captcha_code'],
        }
        code, key, login_req = self.post(login_url, data=login_data)
        if code != 0:
            return code, key
        if not login_req.history:
            code, key = login_error(login_req, self)
            return code, key
        else:
            cookie_url = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10006&toStUrl=http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he"
            code, key, cookie_req = self.get(cookie_url)
            if code != 0:
                return code, key
            self.user_info = cookie_req.text

            for i in xrange(self.max_retry):
                city_code_url = "http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he"
                code, key, resp = self.get(city_code_url)
                if code != 0:
                    return code, key
                try:
                    rr = re.search(r'doQuery\(\'(.*?\')\)', resp.text)
                    strs = rr.group(1)
                    city_code_str = strs.split(',')[1]
                    rs = re.search(r'\'(\d*)\'', city_code_str)
                    city_code_int = rs.group(1)
                    self.AREA_CODE = str(city_code_int)
                    break
                except:
                    error = traceback.format_exc()
            else:
                self.log("website", 'param_error: 获取AREA_CODE失败{}'.format(error), resp)
                return 9, "param_error"

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
        send_sms_url = "http://he.189.cn/public/postValidCode.jsp"
        send_sms_data = {
            "NUM": kwargs["tel"],
            "AREA_CODE": self.AREA_CODE,
            "LOGIN_TYPE": "21",
            "OPER_TYPE": "CR0",
            "RAND_TYPE": "006",
        }
        header = {
            'Referer': 'http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he',
        }
        code, key, resp = self.post(send_sms_url, data=send_sms_data, headers=header)
        if code != 0:
            return code, key, ''
        return 0, "success",  ""


    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        check_sms_url = "http://he.189.cn/public/pwValid.jsp"
        check_sms_data = {
            "_FUNC_ID_":"WB_VALID_RANDPWD",
            "CustName":kwargs['full_name'],
            "IdentityCode": kwargs['sms_code'],
            "ACC_NBR": str(kwargs['id_card']),
            "AREA_CODE": self.AREA_CODE,
            "LOGIN_TYPE": "21",
            "MOBILE_FLAG":"",
            "MOBILE_LOGON_NAME":"",
            "MOBILE_CODE": kwargs['sms_code'],
            "FLAG_QUERYSTR": "12",
        }
        code, key, check_sms_req = self.post(check_sms_url, data=check_sms_data)
        if code != 0:
            return code, key
        if u"\u968f\u673a\u77ed\u4fe1\u9a8c\u8bc1\u7801\u8f93\u5165\u9519\u8bef" in check_sms_req.text:
            self.log('crawler', 'verify_error', check_sms_req)
            return 9, "verify_error"
        return 0, "success"


    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯个i他誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        user_info_dict = {}
        ehtml = etree.HTML(self.user_info)
        # with open('info.py','w')as f:
        #     f.write(self.user_info)
        try:
            user_info_dict['full_name'] = ehtml.xpath("//*[@id='frmModify']/div[2]/table/tr[1]/td/text()")[0]
            # isVerify = ehtml.xpath("//*[@id='frmModify']/div[2]/table/tr[5]/td/text()")
            # user_info_dict['is_realname_register'] = True if isVerify else False
            user_info_dict['id_card'] = ehtml.xpath("//td[@id='CUSTCARDNO']/text()")[0]
            user_info_dict['open_date'] = ""
            address = re.findall(u'id="span_RelaAddress" class="text_content">(.*?)</span>',self.user_info)
            user_info_dict['address'] = address[0] if address else ''
        except:
            error = traceback.format_exc()
            self.log('crawler', "html_error : %s" % error, '')
            return 9, 'html_error', {}

        return 0, "success",  user_info_dict

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        missing_list = []
        possibly_missing_list = []
        call_log = []
        today = date.today()
        cralwler_num = 0
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            BEGIN_DATE = "%d-%02d-" % (query_date.year, query_date.month) + '01 00:00:00'
            END_DATE = "%d-%02d-" % (query_date.year, query_date.month) + \
                       str(calendar.monthrange(query_date.year, query_date.month)[1]) + ' 23:59:59'
            call_log_url = 'http://he.189.cn/service/bill/action/ifr_bill_detailslist_em_new_iframe.jsp'
            call_log_data = {
                'ACC_NBR': kwargs["tel"],
                'CITY_CODE': self.AREA_CODE,
                'BEGIN_DATE': BEGIN_DATE,
                'END_DATE': END_DATE,
                'FEE_DATE': query_month,
                'SERVICE_KIND': '8',
                'retCode': '0000',
                'QUERY_TYPE_NAME': '移动语音详单',
                'QUERY_TYPE': '1',
                'radioQryType': 'on',
                'QUERY_FLAG': '1',
                'QRY_FLAG': '1',
                'ACCT_DATE': query_month,
                'ACCT_DATE_1': "%d%02d" % (today.year, today.month)
            }
            # print self.AREA_CODE
            header = {
                "Referer": "http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he",
                "Host": "he.189.cn",
                "Origin": "http://he.189.cn"
            }
            missing_flag = False
            for retry in xrange(self.max_retry):
                code, key, call_log_req = self.post(call_log_url, data=call_log_data,headers=header)
                if code != 0:
                    missing_flag = True
                elif u"没有相应的记录" in call_log_req.text:
                    missing_flag = False
                else:
                    break
            else:
                if missing_flag:
                    missing_list.append(query_month)
                else:
                    self.log('crawler', '没有查到您的清单数据', call_log_req)
                    possibly_missing_list.append(query_month)
                continue
            key, level, message, call_month_log = self.call_log_get(call_log_req.text.encode('utf8'), query_month)
            if level != 0:
                self.log('crawler', message, call_log_req)
                cralwler_num += 1
                missing_list.append(query_month)
                continue
            if call_month_log:
                call_log.extend(call_month_log)
            else:
                self.log("crawler", '没有数据', call_log_req)
                possibly_missing_list.append(query_month)
        if len(missing_list+possibly_missing_list) == 6:
            if cralwler_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list


    def call_log_get(self, response, query_month):
        """
        `call_tel` | string | 18202541892 | 电话号码 |
        | `call_cost` | string | 0.00 | 通话费用 |
        | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
        | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
        | `call_type` | string | 本地 | 通话类型（本地, 长途） |
        | `call_from` | string | 北京市 | 本机通话地 |
        | `call_to` | string | 长沙市 | 对方归属地 |
        | `call_duration` | integer | 300 | 通话时长(秒),
        """
        call_month_log = []
        try:
            selector = etree.HTML(response)
            call_form = selector.xpath("//*[@id='details_table']/tbody/tr")
            if not call_form:
                return 'html_error', 9, 'html_error', call_month_log
            for item in call_form:
                data = {}
                data['month'] = query_month
                data['call_duration'] = item.xpath('.//td[5]/text()')[0]
                call_tel = item.xpath('.//td[2]/text()')
                call_method = item.xpath('.//td[3]/text()')
                # 如果这条数据中没有对方号码或没有通话类型且通话时长为0，则属于垃圾数据
                # 18903377761	(无通话类型)	2017-07-21 11:24:26	0	0	50.0	0.0	0.0	0.0	OCS充值扣费业务	50.0
                if (not call_tel or not call_method) and data['call_duration']=='0':
                    continue
                data['call_tel'] = call_tel[0]
                data['call_method'] = item.xpath('.//td[3]/text()')[0]
                call_time = item.xpath('.//td[4]/text()')[0]
                data['call_time'] = self.time_format(call_time)
                data['call_type'] = ''
                data['call_from'] = ''
                data['call_to'] = ''
                try:
                    data['call_cost'] = item.xpath('.//td[8]/text()')[0]
                except:
                    data['call_cost'] = item.xpath('.//td[12]/text()')[0]

                call_month_log.append(data)
        except:
            error = traceback.format_exc()
            return 'html_error', 9, 'html_error : %s' % error, call_month_log
        return 'success', 0, 'success', call_month_log

    def time_format(self,timeoo):
        call_time = re.findall('\d{2}', timeoo)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[
            3] + ' ' + '00' + ':' + '00' + ':' + '00'
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        crawler_num = 0
        phone_bill = list()
        month_bill_url = 'http://he.189.cn/service/bill/action/bill_month_list_detail_iframe.jsp'
        for month in self.__monthly_period(6, '%Y%m'):
            post_data = {
                'ACC_NBR': kwargs['tel'],
                'feeDate': month,
                'SERVICE_KIND': '8',
                'retCode': '0000'
            }
            for retry in xrange(self.max_retry):
                code, key, resp = self.post(month_bill_url, data=post_data)
                if code != 0:
                    pass
                else:
                    break
            else:
                missing_list.append(month)
                continue
            try:
                selector = etree.HTML(resp.text, parser=etree.HTMLParser(encoding='utf-8'))
                bill_form = etree.tostring(selector.xpath('//div[@id="divFee"]')[0], encoding='UTF-8')
                month_bill = {
                    'bill_month': month,
                    'bill_amount': '',
                    'bill_package': '',
                    'bill_ext_calls': '',
                    'bill_ext_data': '',
                    'bill_ext_sms': '',
                    'bill_zengzhifei': '',
                    'bill_daishoufei': '',
                    'bill_qita': ''
                }
                bill_amounts = re.findall(u'<div>本期费用合计：([\d.]+)元', bill_form.decode('utf8'))
                if bill_amounts:
                    month_bill['bill_amount'] = bill_amounts[0]
                bill_package = re.findall(u'套餐月基本费</td>.*?<span id="parent_1_5_4">([\d.]+)</span>',
                                          bill_form.decode('utf8'), re.S)
                if bill_package:
                    month_bill['bill_package'] = bill_package[0]
                bill_ext_sms = re.findall(u'短信彩信费</td>.*?<span id="parent_1_5_4">([\d.]+)</span>'
                                          , bill_form.decode('utf8'), re.S)
                if bill_ext_sms:
                    month_bill['bill_ext_sms'] = bill_ext_sms[0]
                bill_ext_data = re.findall(u'上网及数据通信费.*?id="parent_1_5_4">(\d+\.\d+)</span>', bill_form.decode('utf8'), re.S)
                if bill_ext_data:
                    month_bill['bill_ext_data'] = bill_ext_data[0]
            except:
                error = traceback.format_exc()
                missing_list.append(month)
                crawler_num += 1
                self.log('crawler', 'html_error : %s' % error, resp)
                continue
            phone_bill.append(month_bill)
        if crawler_num > 0:
            return 9, 'crawl_error', phone_bill, missing_list
        if len(missing_list) == 6:
            return 9, 'website_busy_error', phone_bill, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, 'success', phone_bill, missing_list


    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset+1)).strftime(strf)

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "13323065781"
    USER_PASSWORD = "187560"
    full_name = "龙卉"
    id_card = "430103199003191021"


    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD, full_name=full_name, id_card=id_card)
