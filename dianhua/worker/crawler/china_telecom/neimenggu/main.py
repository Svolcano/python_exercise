# -*- coding: utf-8 -*-
import re
import json
import traceback
import sys
import time
import datetime
import random

# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")

from datetime import date
from scrapy.selector import Selector
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from base_crawler import BaseCrawler
    from crawler.china_telecom_tool import login_unity
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_unity

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
        self.info_res = ''

    def need_parameters(self, **kwargs):
        return ['pin_pwd']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):

        ProvinceID = '07'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        cookie_url = 'http://nm.189.cn/selfservice/service/userLogin'
        cookie_data = {
            "number" : kwargs['tel'],
            "intLoginType":"4",
            "areaCode":"0471",
            "isBusinessCustType":"N",
            "identifyType":"B",
            "userLoginType":"4",
            "password":"",
            "randomPass":"",
            "noCheck":"N",
            "isSSOLogin":"Y",
            "sRand":"SSOLogin"
        }
        code, key, resp = self.post(cookie_url, data=json.dumps(cookie_data))
        if code != 0:
            return code, key
        personal_info_url = 'http://www.189.cn/dqmh/userCenter/userInfo.do?method=editUserInfo_new&fastcode=10000557&cityCode=nm'
        for retry in xrange(self.max_retry):
            code, key, tel_info_res = self.get(personal_info_url)
            if code != 0:
                return code, key
            if u'真实姓名' in tel_info_res.text:
                self.info_res = tel_info_res.text
                return 0, "success"
            else:
                pass
        else:
            self.log('crawler', "request_error", tel_info_res)
            return 9, "website_busy_error"


    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        send_sms_url = "http://nm.189.cn/selfservice/bill/xdQuerySMS"
        send_sms_data = {
            "phone": kwargs['tel']
        }
        code, key, resp = self.post(send_sms_url, data=json.dumps(send_sms_data))
        if code != 0:
            return code, key, ""
        if resp.text:
            try:
                resp_json_response = resp.json()
            except:
                error = traceback.format_exc()
                self.log('crawler', "Not json file : {}, resp:{}".format(error, resp.history), resp)
                return 9, 'website_busy_error', ''
            if resp_json_response.get('flag', '') == '0':
                return 0, "success", ""
            elif resp_json_response.get('flag', '') == '2':
                self.log('crawler', "send_sms_error", resp)
                return 9, "send_sms_error", ''
            else:
                self.log('crawler', "unknown_error", resp)
                return 9, "unknown_error", ''
        else:
            self.log('crawler', "send_sms_error", resp)
            return 9, "send_sms_error", ''

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        check_sms_url = "http://nm.189.cn/selfservice/bill/xdQuerySMSCheck"
        check_sms_data = {
            'code': kwargs['sms_code']
        }
        code, key, resp = self.post(check_sms_url, data=json.dumps(check_sms_data))
        if code != 0:
            return code, key
        try:
            resp_json_response = resp.json()
        except:
            error = traceback.format_exc()
            self.log('crawler', "json_error : %s" % error, resp)
            return 9, 'json_error'
        if resp_json_response.get('flag', '') == '0':
            self.log('crawler', "verify_error", resp)
            return 2, "verify_error"
        # 如果直接返回详单数据按成功处理。
        elif resp_json_response.get('flag', '') == '1' or 'resultNum' in resp.text or 'items' in resp.text:
            return 0, "success"
        else:
            self.log('crawler', "unknown_error", resp)
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
        selector = Selector(text=self.info_res)
        try:
            full_name = selector.xpath('//input[@name="realName"]/@value').extract()
            user_info['full_name'] = full_name[0] if full_name else ''
            id_card = selector.xpath('//input[@name="certificateNumber"]/@value').extract()
            user_info['id_card'] = id_card[0] if id_card else ''
            address = re.findall(u'id="address".*?;">(.*?)</textarea>', self.info_res)
            user_info['address'] = address[0] if address else ''
            user_info['open_date'] = ""
            user_info['is_realname_register'] = True
        except:
            error = traceback.format_exc()
            self.log('crawler', "html_error : %s" % error, '')
            return 9, "html_error", {}
        return 0, "success", user_info

    def random_sleep(self, tm, modulus=3):
        time.sleep(random.uniform(tm / modulus / 1.5, 1.5 * tm / modulus))

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        call_log = []
        crawl_num = 0
        call_log_url = "http://nm.189.cn/selfservice/bill/xdQuery"
        today = date.today()
        missing_list = []
        pos_missing = []
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            search_month = "%d%02d" % (query_date.year, query_date.month)
            call_log_data = {
                "billingCycle": "{}{}".format(query_date.year, str(query_date.month).zfill(2)),
                'accNbr': kwargs['tel'],
                'accNbrType': '4',
                'areaCode': '0478',
                'pageNo': -1,
                'pageRecords': -1,
                'prodSpecId': '378',
                'qtype': '0',
                'isYWlQuery': 'N',
            }
            header = {
                'Referer': 'http://nm.189.cn/selfservice/bill/xd',
                'Host': 'nm.189.cn',
                'Content-Type': 'application/json'
            }
            start_time = time.time()
            end_time = start_time + 10
            aid_time_dict = dict()
            retry_times = self.max_retry
            log_for_retry = []
            while 1:
                log_for_retry.append((1, retry_times))
                retry_times -= 1
                code, key, resp = self.post(call_log_url, data=json.dumps(call_log_data), headers=header)
                if code:
                    missing_flag = True
                elif 'POR-2102' in resp.text:
                    # 无查询结果，这个月没有数据
                    missing_flag = False
                else:
                    flag = True
                    break
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
                        missing_list.append(search_month)
                    else:
                        pos_missing.append(search_month)
                    break
            self.log('crawler', '{}重试记录{}'.format(search_month, log_for_retry), '')
            if not flag:
                continue
            # for retry in range(self.max_retry):
            #     code, key, resp = self.post(call_log_url, data=json.dumps(call_log_data), headers=header)
            #     if code != 0:
            #         missing_flag = True
            #     # 无查询结果 ， 这个月没有数据
            #     elif 'POR-2102' in resp.text:
            #         missing_flag = False
            #     else:
            #         break
            # else:
            #     if missing_flag:
            #         missing_list.append(search_month)
            #     else:
            #         self.log('crawler', '未查询到您的详单信息', resp)
            #         pos_missing.append(search_month)
            #     continue
            try:
                resp_json_response = resp.json()
            except:
                error = traceback.format_exc()
                self.log('crawler', 'html_error : %s' % error, resp)
                missing_list.append(search_month)
                continue
            if resp_json_response.get('resultCode', '') == 'POR-0000':
                status_key, status_level, message, log_data = self.call_log_get(resp.text, search_month)
                if status_level != 0:
                    crawl_num += 1
                    self.log('crawler', message, resp)
                    missing_list.append(search_month)
                    continue
                else:
                    call_log.extend(log_data)
            else:
                self.log('crawler', 'html_error', resp)
                missing_list.append(search_month)
        if crawl_num > 0:
            return 9, 'crawl_error', call_log, missing_list, pos_missing
        if len(missing_list+pos_missing) == 6:
            return 9, 'website_busy_error', call_log, missing_list, pos_missing
        return 0, "success", call_log, missing_list, pos_missing

    def call_log_get(self, response, search_month):
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
        try:
            json_logs = json.loads(response)
        except:
            error = traceback.format_exc()
            return 'json_error', 9, 'json_error %s' % error, []
        if json_logs.get('resultCode', '') == 'POR-0000':
            records = []
            for item in json_logs.get('items', []):
                data = {}
                try:
                    data['month'] = search_month
                    data['call_cost'] = item.get('fee', '')
                    # 以下几行   转换成时间戳
                    temp = '{} {}'.format(item.get('converseDate', ''), item.get('converseTime', ''))
                    call_time = re.findall('\d{2}', temp)
                    call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + \
                                       call_time[4] + ':' + call_time[5] + ':' + call_time[6]
                    timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
                    call_time_timeStamp = str(int(time.mktime(timeArray)))

                    data['call_time'] = call_time_timeStamp
                    data['call_method'] = item.get('callType', '')
                    data['call_type'] = item.get('converseType', '')
                    # data['call_from'] = item.get('converseAddr', '')

                    raw_call_from = item.get('converseAddr', '').strip()
                    call_from, error = self.formatarea(raw_call_from)
                    if call_from:
                        data['call_from'] = call_from
                    else:
                        # self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                        data['call_from'] = raw_call_from

                    data['call_to'] = item.get('callArea', '')
                    data['call_tel'] = item.get('callingNbr', '')
                    # 以下几行转换成秒
                    durations = item.get('converseDuration', '').split("'")
                    duration = int(durations[0]) * 3600 + int(durations[1]) * 60 + int(durations[2])

                    data['call_duration'] = str(duration)
                    records.append(data)
                except:
                    error = traceback.format_exc()
                    return 'html_error', 9, 'html_error %s' % error, []
            return 'success', 0, 'success', records
        else:
            return 'html_error', 9, 'html_error', []


    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        missing_list = []
        month_bill_url = 'http://nm.189.cn/selfservice/bill/khzdQuery'
        header = {
            'Referer': 'http://nm.189.cn/selfservice/bill/khzd-mini?fastcode=10000542&cityCode=nm',
            'Host': 'nm.189.cn',
            'Content-Type': 'application/json'
        }
        for month in self.__monthly_period(6, '%Y%m'):
            post_data = {
                'accNbr': kwargs['tel'],
                'accNbrType': '4',
                'areaCode': '0478',
                'billingCycle': month,
                'prodSpecId': '378',
                'prodSpecName': '',
                'smsCode': '',
            }
            for retry in xrange(self.max_retry):
                code, key, resp = self.post(month_bill_url, headers=header, data=json.dumps(post_data))
                if code != 0:
                    continue
                else:
                    break
            else:
                missing_list.append(month)
                continue
            key, level, message, result = self.phone_bill_get(month, resp)
            if level != 0 or result['bill_amount'] == '' or result['bill_amount'] == '0.00':
                missing_list.append(month)
                continue
            phone_bill.append(result)
        if len(missing_list) == 6:
            return 9, 'website_busy_error', phone_bill, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, 'success', phone_bill, missing_list


    def phone_bill_get(self, month, resp):
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
        try:
            bill = json.loads(resp.text)
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error'+error, resp)
            return 'html_error', 9, 'html_error'+error, {}
        if bill['resultSet'] == None:
            self.log('website', 'website_busy_error', resp)
            return 'website_busy_error', 9, 'website_busy_error', {}
        bill_amounts = re.findall(u'费用合计：([\d.]+)元', resp.text)
        if bill_amounts:
            month_bill['bill_amount'] = bill_amounts[0]
        bill_package = re.findall(u"套餐费</span><span class='pricebills'>([\d.]+)</span>", resp.text)
        if bill_package:
            month_bill['bill_package'] = bill_package[0]

        return 'success', 0, 'website_busy_error', month_bill

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset + 1)).strftime(strf)


if __name__ == '__main__':
    c = Crawler()
    USER_ID = "15335686893"
    # USER_ID = "15335686896"
    USER_PASSWORD = "135126"
    USER_FULL_NAME = "薛胜英"
    USER_ID_CARD = "152801198002090347"

    c.self_test(tel=USER_ID,pin_pwd=USER_PASSWORD)
