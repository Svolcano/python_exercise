# -*- coding: utf-8 -*-
import base64
import random

import requests
import urllib
import time
import calendar
import re
import sys
import traceback
import json
reload(sys)
sys.setdefaultencoding("utf8")

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from crawler.china_telecom_tool import login_unity
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_unity

from common import aes_encrypt, parse_call_record
from datetime import date
from dateutil.relativedelta import relativedelta

class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'captcha_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        ProvinceID = '08'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key
        COOKIE_URL = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10005&toStUrl=http://ln.189.cn/group/bill/bill_detail.do?fastcode=01650722&cityCode=ln"
        code, key, cookie_req = self.get(COOKIE_URL)
        if code != 0:
            return code, key
        # print cookie_req.history,cookie_req.url
        if '本机短信验证码' in cookie_req.text:
            return 0, "success"
        elif u'欢迎登录' in cookie_req.text or cookie_req.url == LOGIN_URL:
            self.log('crawler', 'request_error', cookie_req)
            return 9, 'request_error'
        else:
            self.log('crawler', 'unknown_error', cookie_req)
            return 9, "unknown_error"


    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片
        return
        status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
        level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
        message: unicode, 詳細的錯誤信息
        image_str: str, Captcha圖片, SMS則回空
        """
        SMS_POST_URL = "http://ln.189.cn/sendCheckSecondPwdAction.action"
        sms_post_data = {
            "inventoryVo.accNbr": kwargs['tel'],
            "inventoryVo.productId": '8'
        }
        code, key, resp = self.post(SMS_POST_URL, data=sms_post_data)
        if code != 0:
            return code, key, ''
        if '请您注意查收' in resp.text:
            return 0, 'success', ''
        else:
            self.log('crawler', 'unknown_error', resp)
            return 9, "unknown_error", ''

    def verify(self, **kwargs):
        CHECK_SMS_URL = "http://ln.189.cn/group/secondCheckIdNumber/checkIdNumber.action"
        check_sms_data = {
            "idType":'',
            "realNameType":'realNameType4',
            "ramdoCode":kwargs['sms_code'],
            "userType":'2000004'
        }
        code, key, resp = self.post(CHECK_SMS_URL, data=check_sms_data)
        if code != 0:
            return code, key
        try:
            check_sms_res = resp.json()
        except:
            error = traceback.format_exc()
            self.log('crawler', 'Not json file: {}, resp:{}'.format(error, resp.history), resp)
            return 9, "website_busy_error"
        if check_sms_res.get('flag') == '0' or '"TSR_CODE":"0"' in resp.text or 'items' in resp.text:
            return 0, 'success'
        elif check_sms_res.get('flag') == '1':
            self.log('crawler', 'verify_error', resp)
            return 2, "verify_error"
        self.log('crawler', 'unknown_error', resp)
        return 9, "unknown_error"

    def crawl_call_log(self, **kwargs):
        missing_list = []
        pos_missing = []
        today = date.today()
        crawl_num = 0
        records = []
        delta_months = [i for i in range(0, -6,  -1)]

        BILL_DETAIL_URL = "http://ln.189.cn/queryVoiceMsgAction.action"
        page_and_retry = []

        for delta_month in delta_months:
            query_date = today + relativedelta(months=delta_month)
            start_date = "%d-%02d-01"%(query_date.year, query_date.month)
            end_day = calendar.monthrange(query_date.year, query_date.month)[1]
            end_date = "%d-%02d-%02d"%(query_date.year, query_date.month, end_day)
            search_month = "%d%02d" % (query_date.year, query_date.month)
            bill_detail_data = {
                'inventoryVo.accNbr':kwargs['tel'],
                'inventoryVo.getFlag':'3',
                'inventoryVo.begDate': start_date,
                'inventoryVo.endDate': end_date,
                'inventoryVo.family':'8',
                'inventoryVo.accNbr97':'',
                'inventoryVo.productId':'8',
                'inventoryVo.acctName': kwargs['tel'],
                'inventoryVo.feeDate': search_month,
            }
            query_month = "%d%02d" % (query_date.year, query_date.month)
            page_and_retry.append((bill_detail_data, query_month, self.max_retry))


        st_time = time.time()
        et_time = st_time + 30
        log_for_retry_request = []

        while page_and_retry:
            bill_detail_data, query_month, m_retry_times = page_and_retry.pop(0)
            m_retry_times -= 1
            log_for_retry_request.append((query_month, m_retry_times))
            log_result = []
            error_message = u'爬虫出错'
            code, key, resp = self.post(BILL_DETAIL_URL, data=bill_detail_data)
            if code == 0:
                try:
                    bill_detail_res = resp.json()
                    if bill_detail_res.get('Count') != "0":
                        log_result = parse_call_record(self, bill_detail_res, query_month)
                        if log_result:
                            records.extend(log_result)
                            continue
                except:
                    error_message = traceback.format_exc()
                    crawl_num += 1

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((bill_detail_data, query_month, m_retry_times))
                continue
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((bill_detail_data, query_month, m_retry_times))
                    time.sleep(rand_sleep)
                    continue

            if code == 0 and not log_result:
                self.log('website', u'详单为空: %s'% error_message, resp)
                pos_missing.append(query_month)
            else:
                self.log('crawler', 'html_error : %s' % error_message, resp)
                missing_list.append(query_month)

        # print('missing_list:',missing_list)
        # print('pos_missing:',pos_missing)
        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        if len(missing_list) == 6 or len(pos_missing) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', records, missing_list, pos_missing
            return 9, 'website_busy_error', records, missing_list, pos_missing
        return 0, 'success', records, missing_list, pos_missing

    def crawl_info(self, **kwargs):
        result = {}
        USER_INFO_URL = "http://ln.189.cn/getSessionInfo.action"
        code, key, resp = self.post(USER_INFO_URL)
        if code != 0:
            return code, key, {}
        try:
            user_info_res = resp.json()
        except:
            error = traceback.format_exc()
            self.log('crawler', 'json_error : %s' % error, resp)
            return 9, "json_error", {}
        try:
            if user_info_res.get('isRealName') == "0":
                result['is_realname_register'] = True
            else:
                result['is_realname_register'] = False
            result['full_name'] = user_info_res.get('userName')
            result['id_card'] = user_info_res.get('indentCode')
            result['address'] = user_info_res.get('userAddress')
            result['open_date'] = self.time_stamp(user_info_res.get('acceptDate'))
        except:
            error = traceback.format_exc()
            self.log('crawler', "html_error : %s" % error, resp)
            return 9, "html_error", {}
        return 0, "success", result


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


    def crawl_phone_bill(self, **kwargs):
        month_fee =[]
        MONTH_BILL_URL = "http://ln.189.cn/chargeQuery/chargeQuery_queryBillForSixMonth.action?queryKind=1"
        missing_list = []
        for retry in xrange(self.max_retry):
            code, key, resp = self.post(MONTH_BILL_URL)
            if code != 0:
                pass
            else:
                break
        else:
            return 9, 'website_busy_error', [], missing_list
        if '"TSR_CODE":"CT_66666"' in resp.text:
            self.log('website', 'website_busy_error', resp)
            return 9, 'website_busy_error', [], missing_list
        try:
            month_bill_res = resp.json()
        except:
            error = traceback.format_exc()
            self.log('crawler', 'json_error %s' % error, resp)
            return 9, 'website_busy_error', [], missing_list
        try:
            month_data = month_bill_res.get('monthAccountStr')
            each_month = re.findall(u'(\d{4})年(\d{2})月[\s\S]+?(\d+\.\d{2})',month_data)
            for item in each_month:
                month_fee_data = {
                    'bill_month': '',
                    'bill_amount': '',
                    'bill_package': '',
                    'bill_ext_calls': '',
                    'bill_ext_data': '',
                    'bill_ext_sms': '',
                    'bill_zengzhifei': '',
                    'bill_daishoufei': '',
                    'bill_qita': ''
                }
                month_fee_data['bill_month'] = item[0]+item[1]
                month_fee_data['bill_amount'] = item[2]
                if month_fee_data['bill_amount'] == '0.00':
                    missing_month = str(item[0]+item[1])
                    missing_list.append(missing_month)
                    continue
                month_fee.append(month_fee_data)
        except:
            error = traceback.format_exc()
            self.log('crawler', "html_error : %s" % error, resp)
            return 9, 'crawl_error', [],  missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, "success", month_fee, missing_list



if __name__ == '__main__':
    c = Crawler()
    USER_ID = "13358845391"
    USER_PASSWORD = "193548"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # print (c.crawl_phone_bill())
