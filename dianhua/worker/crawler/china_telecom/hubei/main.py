# -*- coding: utf-8 -*-

import base64
import traceback
import sys
import time
import re
import hashlib
# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")

from Crypto.Cipher import AES
from datetime import date
from lxml import etree
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from crawler.china_telecom_tool import login_error
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_error

"""
    注意会限制短信发送频率,三次一禁
"""

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
        self.citycode = ''

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        return
            list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        return ['pin_pwd', 'sms_code', 'captcha_verify']

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

    def aes_encrypt(self,n):
        # this is the porting from telecom javascript
        BS = 16
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        n = pad(n)
        e = hashlib.md5('login.189.cn')
        t = e.hexdigest()
        i = t.encode('utf-8')
        r  = u'1234567812345678'.encode('utf-8')
        encryption_suite = AES.new(i, AES.MODE_CBC, r)
        cipher_text = encryption_suite.encrypt(n)
        base64.b64encode(cipher_text)
        return base64.b64encode(cipher_text)

    def login(self, **kwargs):

        url = 'http://hb.189.cn/pages/selfservice/feesquery/detailListQuery.jsp'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key

        try:
            tologin_url = 'http://hb.189.cn' + re.findall('top.location="(.*?)"', resp.text)[0]
        except:
            err_msg = traceback.format_exc()
            self.log('crawler', 'html_error', err_msg)
            return 9, 'html_error'

        headers = {
            'Referer': 'http://hb.189.cn/pages/selfservice/feesquery/detailListQuery.jsp'
        }
        code, key, resp = self.get(tologin_url, headers=headers)
        if code != 0:
            return code, key

        login_url = "http://login.189.cn/web/login"
        try:
            pwd = self.aes_encrypt(kwargs['pin_pwd'])
        except:
            error = traceback.format_exc()
            self.log('crawler', 'login_param_error : %s' % error, '')
            return 9, 'login_param_error'
        login_data = {
            "Account": kwargs['tel'],
            "UType": '201',
            "ProvinceID": '18',
            "AreaCode": "",
            "CityNo": "",
            "RandomFlag": '0',
            "Password": pwd,
            "Captcha": kwargs['captcha_code'].lower(),
        }
        header = {'Referer': 'http://login.189.cn/web/login'}
        code, key, login_req = self.post(login_url, data=login_data, headers=header)
        if code != 0:
            return code, key
        if not login_req.history:
            code, key = login_error(login_req, self)
            return code, key
        else:
            is_login_url = 'http://hb.189.cn/ajaxServlet/getCityCodeAndIsLogin'
            is_login_data = {
                'method':'getCityCodeAndIsLogin',
            }
            header = {'Referer':'http://hb.189.cn/pages/selfservice/feesquery/detailListQuery.jsp'}
            code, key, is_login_req = self.post(is_login_url, data=is_login_data, headers=header)
            if code != 0:
                return code, key
            if 'true' in is_login_req.text:
                self.citycode = re.search(r'"CITYCODE":"(\d{4})"',is_login_req.text).group(1)
                #如果citycode返回为空代表出错
                if not str(self.citycode):
                    self.log('crawler', "html_error", is_login_req)
                    return 9, 'website_busy_error'
                return 0, "success"
            else:
                self.log('crawler', "param_error", is_login_req)
                return 9, "param_error"

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        send_sms_url = "http://hb.189.cn/feesquery_PhoneIsDX.action"
        send_sms_data = {
            'productNumber': kwargs['tel'],
            'cityCode': str(self.citycode),
            'sentType': 'C',
            'ip': '0'
        }
        header = {'Referer': 'http://hb.189.cn/pages/selfservice/feesquery/detailListQuery.jsp'}
        code, key, resp = self.post(send_sms_url, data=send_sms_data, headers=header)
        if code != 0:
            return code, key, ''
        if '随机验证码已经发送' in resp.text or '随机码已经发到您的手机' in resp.text:
            return 0, "success", ""
        elif '获取随机码操作过于频繁' in resp.text:
            self.log('crawler', 'send_sms_too_quick_error', resp)
            return 9, "send_sms_too_quick_error", ""
        elif u'接口失敗' in resp.text:
            self.log('website', 'website_busy_error', resp)
            return 9, 'website_busy_error', ''
        elif u'网络故障' in resp.text:
            self.log('website', 'website_busy_error', resp)
            return 9, 'website_busy_error', ''
        else:
            self.log('crawler', 'unknown_error', resp)
            return 9, "unknown_error", ''

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        check_sms_url = "http://hb.189.cn/feesquery_checkCDMAFindWeb.action"
        check_sms_data = {
            "random": kwargs['sms_code'],
            "sentType": 'C',
        }
        code, key, resp = self.post(check_sms_url, data=check_sms_data)
        if code != 0:
            return code, key
        if '1' in resp.text:
            today = date.today()
            today_month = "%d%02d0000" % (today.year, today.month)
            call_log_url = "http://hb.189.cn/feesquery_querylist.action"
            header = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'http://hb.189.cn/pages/selfservice/feesquery/detailListQuery.jsp',
            }
            call_log_data = {
                'startMonth': today_month,
                'type': '5',
                'random': kwargs['sms_code'],
            }
            code, key, resp = self.post(call_log_url, data=call_log_data, headers=header)
            if code != 0:
                return code, key
            return 0, "success"
        elif '0' in resp.text:
            self.log('crawler', 'verify_error', resp)
            return 9, "verify_error"
        else:
            self.log('crawler', 'unknown_error', resp)
            return 9, "unknown_error"

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
        realname_register_url = "http://hb.189.cn/pages/selfservice/custinfo/userinfo/userInfo.action"
        code, key, resp = self.get(realname_register_url)
        if code != 0:
            return code, key, {}
        # with open('1.html','w') as file:
        #     file.write(resp.text)
        try:
            selector = etree.HTML(resp.text)
            full_name = selector.xpath('//*[@id="showTable02"]/tr[1]/td[2]/text()')
            user_info['full_name'] = full_name[0] if full_name else ''
            id_card = selector.xpath('//*[@id="zjhmli1"]/text()')
            user_info['id_card'] = id_card[0].replace('\r\n','').replace('\t','').replace(' ','') if id_card else ''
            open_date = selector.xpath('//*[@id="cjrqli1"]/text()')
            open_date = open_date[0] if open_date else ''
            user_info['open_date'] = self.time_stamp(open_date) if open_date else ''
            address = selector.xpath('//*[@id="telAddress"]/@value')
            user_info['address'] = address[0] if address else ''
        except:
            error = traceback.format_exc()
            self.log('crawler', "html_error : %s" % error, resp)
            return 9, 'html_error', {}
        return 0, "success", user_info

    def time_stamp(self,old_time):
        temp = re.findall('-(\d)-', old_time)
        if temp:
            old_time = re.sub('-\d-', '0' + temp[0], old_time)
        call_time = re.findall('\d{2}', old_time)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + call_time[
            4] + ':' + call_time[5] + ':' + call_time[6]
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

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
        crawler_num = 0
        possibly_missing_list = []
        call_log = []
        call_log_url = "http://hb.189.cn/feesquery_querylist.action"
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer':'http://hb.189.cn/pages/selfservice/feesquery/detailListQuery.jsp',
        }
        today = date.today()
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            startMonth = "%d%02d0000" % (query_date.year, query_date.month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            call_log_data = {
                'startMonth': startMonth,
                'type':'5',
                # 'random': kwargs['sms_code'],
                }
            missing_flag = False
            for retry in xrange(self.max_retry):
                code, key, resp = self.post(call_log_url, data=call_log_data, headers=header)
                if code != 0:
                    missing_flag = True
                elif '系统没有查到' in resp.text:
                    missing_flag = False
                else:
                    break
            else:
                if missing_flag:
                    missing_list.append(query_month)
                else:
                    self.log('crawler', '未查询到您的详单信息', resp)
                    possibly_missing_list.append(query_month)
                continue
            try:
                page_num = re.search(u"共(\d+)页",resp.text).group(1)
            except:
                error = traceback.format_exc()
                self.log('crawler', 'html_error : %s' % error, resp)
                possibly_missing_list.append(query_month)
                continue
            call_page_url = 'http://hb.189.cn/feesquery_pageQuery.action'
            missing_flag = False
            for each in range(int(page_num)):
                call_page_data = {
                    'page': each+1,
                    'showCount': '20'
                }
                code, key, call_page_req = self.post(call_page_url, data=call_page_data)
                if code != 0:
                    missing_flag = True
                    break
                status_key, level, message, data = self.call_log_get(call_page_req.text, query_month)
                if level != 0:
                    missing_flag = True
                    crawler_num += 1
                    self.log('crawler', message, call_page_req)
                    missing_list.append(query_month)
                    break
                call_log.extend(data)
            if missing_flag:
                missing_list.append(query_month)
                continue
        if len(missing_list) + len(possibly_missing_list) == 6:
            if crawler_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

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
        records = []
        try:
            selector = etree.HTML(response)
            page_data = selector.xpath('//ul/table/tr')[1:-2]
            # with open('call_log.py','w')as f:
            #     f.write(response)
            for item in page_data:
                data = {}
                data['month'] = query_month
                data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                data['call_cost'] = item.xpath('.//td[10]/text()')[0]
                # data['call_time'] = item.xpath('.//td[1]/text()')[0]
                #以下几行为了转换时间戳
                call_time = re.findall('\d{2}',item.xpath('.//td[1]/text()')[0])
                call_time_change = call_time[0]+call_time[1]+'-'+call_time[2]+'-'+call_time[3]+' '+call_time[4]+':'+call_time[5]+':'+call_time[6]
                timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
                call_time_timeStamp = str(int(time.mktime(timeArray)))
                data['call_time'] = call_time_timeStamp
                data['call_method'] = item.xpath('.//td[4]/text()')[0]
                data['call_type'] = item.xpath('.//td[5]/text()')[0]
                raw_call_from = item.xpath('.//td[7]/text()')[0].strip()

                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                    data['call_from'] = raw_call_from

                # data['call_from'] = call_from[0] if call_from else ''
                data['call_to'] = ''
                data['call_tel'] = item.xpath('.//td[2]/text()')[0]
                data['call_duration'] = item.xpath('.//td[3]/text()')[0]
                records.append(data)
        except:
            error = traceback.format_exc()
            return 'html_error', 9, 'html_error :%s' % error, []
        return 'success', 0, 'success', records

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
        """
        missing_list = []
        today = date.today()
        search_month = [x for x in range(0, -6, -1)]
        month_fee = []
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            month_bill_url = "http://hb.189.cn/pages/selfservice/feesquery/newBOSSQueryCustBill.action"
            month_bill_data = {
                'billbeanos.citycode': self.citycode,
                'billbeanos.btime': query_month,
                'billbeanos.accnbr': kwargs['tel'],
                'billbeanos.paymode': '1'
            }
            for retry in xrange(self.max_retry):
                code, key, month_bill_req = self.post(month_bill_url, data=month_bill_data)
                if u"客户账单" not in month_bill_req.text:
                    self.log('crawler', key, month_bill_req)
                else:
                    break
            else:
                missing_list.append(query_month)
                continue
                # with open('1.html','w') as file:
                #     file.write(month_bill_req.text)
            month_fee_data = {}
            month_fee_data['bill_month'] = query_month
            month_fee_data['bill_package'] = ''
            month_fee_data['bill_ext_calls'] = ''
            month_fee_data['bill_ext_data'] = ''
            month_fee_data['bill_ext_sms'] = ''
            month_fee_data['bill_zengzhifei'] = ''
            month_fee_data['bill_daishoufei'] = ''
            month_fee_data['bill_qita'] = ''
            bill_amount = re.findall(r'本项小计.*?(\d\.\d{2})元',month_bill_req.text.encode('utf-8'))
            if bill_amount:
                month_fee_data['bill_amount'] = bill_amount[0]
            else:
                missing_list.append(query_month)
                continue
            bill_package = re.findall(r'套餐月基本费.*?(\d\.\d{2})元',month_bill_req.text.encode('utf-8'))
            if bill_package:
                month_fee_data['bill_package'] = bill_package[0]
            bill_ext_calls = re.findall(r'.*漫游通话.*?(\d\.\d{2})元',month_bill_req.text.encode('utf-8'))
            if bill_ext_calls:
                month_fee_data['bill_ext_calls'] = bill_ext_calls[0]
            bill_ext_data = re.findall(r'.*上网使用费.*?(\d\.\d{2})元',month_bill_req.text.encode('utf-8'))
            if bill_ext_data:
                month_fee_data['bill_ext_data'] = bill_ext_data[0]
            bill_ext_sms = re.findall(r'.*短信费.*?(\d\.\d{2})元',month_bill_req.text.encode('utf-8'))
            if bill_ext_sms:
                month_fee_data['bill_ext_sms'] = bill_ext_sms[0]
            bill_zengzhifei = re.findall(r'来电显示.*?(\d\.\d{2})元',month_bill_req.text.encode('utf-8'))
            if bill_zengzhifei:
                month_fee_data['bill_zengzhifei'] = bill_zengzhifei[0]
            month_fee.append(month_fee_data)
        if len(missing_list) == 6:
            return 9, 'website_busy_error', month_fee, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, "success",  month_fee, missing_list


if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17371178631"
    USER_PASSWORD = "43661574"

    # self_test

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # print c.crawl_phone_bill(tel=USER_ID)
    # print c.crawl_call_log()
    # print c.crawl_phone_bill()
    # print c.send_login_verify_request()
    # print c.aes_encrypt('578020')
    # print c.bill_log()
