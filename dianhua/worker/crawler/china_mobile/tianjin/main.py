# -*- coding: utf-8 -*-
import datetime
import random
import time
import base64
from dateutil.relativedelta import relativedelta
import sys
reload(sys)
sys.setdefaultencoding("utf8")
if __name__ == '__main__':
    sys.path.append('../../../..')

from worker.crawler.base_crawler import BaseCrawler

import request_headers
import request_params
import response_data

URL_XPATH_BEFORE_LOGIN = 'https://tj.ac.10086.cn/'
URL_CAPTCHA_BEFORE_LOGIN = 'https://tj.ac.10086.cn/captcha.htm'
URL_LOGIN = 'https://tj.ac.10086.cn/login.json'
URL_GET_LOGIN_COOKIE = "http://service.tj.10086.cn/ics/artifactServletRev?RelayState=MyHome"
URL_SMS_GET_BEFORE_CALL_LOG = 'http://service.tj.10086.cn/ics/ics'
URL_SMS_VERIFY_BEFORE_CALL_LOG = 'http://service.tj.10086.cn/ics/ics'
URL_CALL_LOG = 'http://service.tj.10086.cn/ics/ics'
URL_PERSONAL_INFO = 'http://service.tj.10086.cn/ics/ics'
URL_PHONE_BILL = 'http://service.tj.10086.cn/ics/ics'


class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.einfo = ""

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'captcha_verify']

    def get_login_verify_type(self, **kwargs):
        return ''

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def send_login_verify_request(self, **kwargs):
        if request_params.before_login['token'] == '':
            headers = request_headers.before_login_headers()
            code, key, resp = self.get(URL_XPATH_BEFORE_LOGIN, headers=headers)
            if code != 0:
                return code, key, '', ''
            request_headers.referer_url = resp.url
            before_login = response_data.before_login_data(resp.text)
            if before_login['error']:
                resp.encoding = 'utf-8'
                if u'<span class="mr_5">您现在所在的位置：</span>' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    return 9, 'website_busy_error', '', ''
                self.log('crawler', before_login['msg'], resp)
                return 9, 'html_error', '', ''
            before_login.pop('error')
            request_params.before_login = before_login

        params = request_params.before_login_captcha_params()
        headers = request_headers.before_login_captcha_headers()
        code, key, resp = self.get(URL_CAPTCHA_BEFORE_LOGIN, headers=headers, params=params)
        if code != 0:
            return code, key, '', ''

        code, key, image_str = response_data.before_login_captcha_data(self, resp)
        if code != 0:
            return code, key, "", ''
        codetype = '3004'
        key, result, cid = self._dama(base64.b64decode(image_str), codetype)
        if key == "success" and result != "":
            captcha_code = str(result).lower()
            return 0, cid, captcha_code, cid
        else:
            self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
            return code, key, "", ''


    def login(self, **kwargs):
        for i in range(self.max_retry):
            code, key, captcha_code, cid = self.send_login_verify_request()
            if code != 0:
                return code, key
            kwargs['captcha_code'] = captcha_code
            params = request_params.login_params(**kwargs)
            headers = request_headers.login_headers()

            code, key, resp = self.post(URL_LOGIN, params=params, headers=headers)
            if code != 0:
                return code, key
            code, key = response_data.login_data(self, resp)
            if code != 0:
                if key == 'verify_error':
                    self.log("crawler", "云打码失败", resp)
                    self._dama_report(cid)
                    continue
                return code, key
            break
        else:
            self.log("crawler", "图片打码失败", "")
            return 9, "auto_captcha_code_error"

        headers = request_headers.login_cookies_refer()
        code, key, resp = self.get(URL_GET_LOGIN_COOKIE, headers=headers)
        if code != 0:
            return code, key
        return 0, 'success'

    def send_verify_request(self, **kwargs):
        params = request_params.before_call_log_get_sms_params()
        headers = request_headers.before_call_log_get_sms_headers()
        code, key, resp = self.get(URL_SMS_GET_BEFORE_CALL_LOG, params=params, headers=headers)
        if code != 0:
            return code, key, ''

        return response_data.before_call_log_get_sms_data(self, resp)

    def verify(self, **kwargs):
        params = request_params.before_call_log_verify_sms_params(kwargs['sms_code'])
        headers = request_headers.before_call_log_verify_sms_headers()

        code, key, resp = self.get(URL_SMS_VERIFY_BEFORE_CALL_LOG, params=params, headers=headers)
        if code != 0:
            return code, key

        return response_data.before_call_log_verify_sms_data(self, resp)

    def crawl_call_log(self, **kwargs):
        # 缺失月份
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        err_dict = {'crawl_error': 0, 'website_busy_error': 0}
        params = request_params.call_log_params(self.einfo)
        headers = request_headers.call_log_headers()
        call_log = list()
        page_and_retry = []
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            page_and_retry.append((searchMonth, self.max_retry))

        st_time = time.time()
        et_time = st_time + 30
        log_for_retry_request = []

        while page_and_retry:
            query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((query_month, m_retry_times))
            m_retry_times -= 1
            params['searchMonth'] = query_month
            code_a, key, resp = self.get(URL_CALL_LOG, params=params, headers=headers)
            if code_a == 0:
                code, key, message, result = response_data.call_log_data(resp.text, query_month, self_obj=self)
                if code == 0 and result:
                    call_log.extend(result)
                    continue

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((query_month, m_retry_times))
                continue
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((query_month, m_retry_times))
                    time.sleep(rand_sleep)
                    continue

            if code_a == 0:
                if code == 0 and not result:
                    possibly_missing_list.append(query_month)
                else:
                    missing_month_list.append(query_month)
                if key == 'unknown_error':
                    self.log('crawler', message, resp)
                    err_dict['crawl_error'] += 1
                elif key == "website_busy_error":
                    self.log("website", "website_busy_error", resp)
                else:
                    self.log('crawler', key, resp)
                    err_dict['crawl_error'] += 1
            else:
                err_dict['website_busy_error'] += 1
                if query_month not in missing_month_list:
                    missing_month_list.append(query_month)

        # print(len(call_log))
        # print('missing_month_list:', missing_month_list)
        # print('possibly_missing_list:', possibly_missing_list)
        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        if len(missing_month_list + possibly_missing_list) == 6:
            if err_dict['crawl_error'] > 0:
                return 9, 'crawl_error', [], missing_month_list, []
            return 9, 'website_busy_error', [], missing_month_list, []
        return 0, 'success', call_log, missing_month_list, possibly_missing_list

    def crawl_phone_bill(self, **kwargs):
        # 缺失月份
        missing_month_list = []
        params = request_params.phone_bill_params()
        headers = request_headers.phone_bill_headers()

        crawl_error_num = 0
        phone_bill = list()
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            params['MONTH'] = searchMonth
            for item in xrange(self.max_retry):
                code_a, key, resp = self.get(URL_PHONE_BILL, params=params, headers=headers)
                if code_a != 0:
                    continue
                code, key, message, result = response_data.phone_bill_data(resp.text, searchMonth)
                if code != 0:
                    continue
                if result:
                    phone_bill.append(result)
                    break
                else:
                    message = u'没有账单记录'
                    continue
            else:
                if code_a == 0:
                    self.log('crawler', message, resp)
                    crawl_error_num += 1
                missing_month_list.append(searchMonth)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in missing_month_list and missing_month_list.remove(now_month)
        if len(missing_month_list) == 5:
            if crawl_error_num > 0:
                return 9, 'crawl_error', [], missing_month_list
            return 9, 'website_busy_error', [], missing_month_list
        return 0, 'success', phone_bill, missing_month_list

    def crawl_info(self, **kwargs):
        params = request_params.personal_info_params()
        headers = request_headers.personal_info_headers()

        code, key, resp = self.get(URL_PERSONAL_INFO, params=params, headers=headers)
        if code != 0:
            return code, key, {}

        return response_data.personal_info_data(self, resp)

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

if __name__ == '__main__':
    # from worker.crawler.main import *
    c = Crawler()
    """
        858
    """

    USER_ID = "18202541892"
    USER_PASSWORD = "039718"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
