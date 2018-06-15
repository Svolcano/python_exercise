# -*- coding: utf-8 -*-
import sys

if __name__ == '__main__':

    sys.path.append('../../../')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler
# import re
# import random
# import datetime
from dateutil.relativedelta import relativedelta
import calendar
# import traceback
from base_request_param import *
from base_sd_crawler import *
from base_security_js import *

# Const Login URL
START_URL = "https://sd.ac.10086.cn/login/"


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)

    def get_login_verify_type(self, **kwargs):
        return 'Captcha'

    def get_verify_type(self, **kwargs):
        return 'SMSCaptcha'

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'captcha_verify']

    def send_login_verify_request(self, **kwargs):
        """
        Get validate image
            1. To login page
            2. Set cookies for login
            3. Get Validate Code Image
        :param kwargs:
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """

        # To login page
        # self.session.get(START_URL, verify=False)
        code, key, resp = self.get(START_URL)
        if code != 0:
            return code, key, ''

        # Set cookies for login
        code, key = get_login_cookie(self)
        if code != 0:
            return code, key, ""

        # Get Validate Code Image
        return get_login_validate_image(self)

    def login(self, **kwargs):
        """
        Login process
            1. Get Login Result
            2. Set Prior Cookies
            3. Get Attribute ID
            4. Extract Attribute ID
            5. Set SSO Login
            6. Extract SSO Login Result
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        try:
            # Get Login Result
            code, key = get_login_result(self, kwargs['tel'], kwargs['pin_pwd'], kwargs['captcha_code'])
            if code != 0:
                return code, key

            # Set Prior Cookies
            code, key, resp = get_prior_cookie(self)
            if code != 0:
                return code, key

            # Get Attribute ID
            code, key, resp = get_attribute_id(self)
            if code != 0:
                return code, key

            # Extract Attribute ID
            code, key, message, result = extract_attribute_id_from_code(resp.text)
            if code != 0:
                self.log('crawler', message, resp)
                return code, key

            # Set SSO Login
            attribute_id = result
            code, key, result = get_sso_login_cookie(self, attribute_id)
            if code != 0:
                return code, key
        except:
            error = traceback.format_exc()
            self.log('crawler', 'unknown_error:{}'.format(error),resp)
            return '9', 'unknown_error'

        # Extract SSO Login Result

        return 0, "success"

    def send_verify_request(self, **kwargs):
        """
        Send SMS and captcha verify code
            1. Send Second Validate SMS
            2. Extract Send Second Validate SMS Result
            3. Get Second Validate Image
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """

        # Send Second Validate SMS
        code, key, resp = send_second_validate_sms(self)
        if code != 0:
            return code, key, ""

        # Extract Send Second Validate SMS Result
        code, key = extract_send_second_validate_sms_result_from_dict(self, resp)
        if code != 0:
            return code, key, ""

        # Get Second Validate Image
        return get_second_validate_image(self)

    def verify(self, **kwargs):
        """
        Check SMS  ans captcha validate code
            1. Get Second Validate Result
            2. Extract Second Validate Result
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """

        # Get Second Validate Result
        code, key, resp = get_second_validate_result(self, kwargs['captcha_code'], kwargs['sms_code'])
        if code != 0:
            return code, key

        # Extract Second Validate Result
        code, key = extract_second_validate_result_from_html(self, resp)
        if code != 0:
            return code, key

        return 0, "success",

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
        code, key, resp = get_personal_info(self)
        if code != 0:
            return code, key, {}

        # Extract Personal Info from get_personal_info
        return extract_personal_info_from_dict(self, resp)

    def get_year_month(self, number):
        month_list = []
        for each_month in xrange(-0, -number, -1):
            today = datetime.date.today()
            query_date = today + relativedelta(months=each_month)
            month_list.append("%d%02d" % (query_date.year, query_date.month))
        return month_list

    def crawl_call_log(self, **kwargs):
        """
        Crawl user's detail bill info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        # 缺失月份
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []

        current_time = datetime.datetime.now()
        detail_info_list = list()

        # try:
        for month_offset in range(0, 6):
            year_month = (current_time - relativedelta(months=month_offset))

            day_count = calendar.monthrange(year_month.year, year_month.month)[1]
            start_date = "%s01000000" % year_month.strftime('%Y%m')
            end_date = "%s%s235959" % (year_month.strftime('%Y%m'), day_count)
            missing_month = "%s" % year_month.strftime('%Y%m')
            year__month = "%d%02d" % (year_month.year, year_month.month)
            for item in xrange(self.max_retry):
                # Get detail Bill of Target Month
                code, key, resp = get_detail_bill_result(self, start_date, end_date)
                if code != 0:
                    if missing_month not in missing_month_list and item == self.max_retry - 1:
                        missing_month_list.append(missing_month)
                        break
                    continue

                # Extract Detail Info from get_detail_bill_result
                code, key, message, result = extract_detail_bill_from_dict(resp.text, year__month, self_obj=self)
                if code != 0:
                    if item == self.max_retry - 1:
                        if 'website_busy_error' == key:
                            self.log('website', 'website_busy_error', resp)
                        elif 'pin_pwd_error' == key:
                            self.log('user', 'pin_pwd_error', resp)
                        else:
                            self.log('crawler', message, resp)
                        if missing_month not in missing_month_list:
                            missing_month_list.append(missing_month)
                        break
                    continue
                    # return key, code, message, result
                if not result:
                    self.log('crawler', '没有详单记录', resp)
                    possibly_missing_list.append(missing_month)
                detail_info_list += result
                break
        return 0, "success",  detail_info_list, missing_month_list, possibly_missing_list

    def get_six_year_month(self):
        # "默认时间起点为当前时间 返回值[(年, 月), (年, 月)...]"
        today_year = datetime.date.today().year
        today_month = datetime.date.today().month
        today_day = datetime.date.today().day
        if today_day <= 26:
            date_list = range(7)
        else:
            date_list = range(-1, 6)
        time_list = []
        for n in date_list:
            if (today_month - n) > 0:
                mon = (today_month-n)
                yea = today_year
            else:
                mon = 12 + (today_month - n)
                yea = today_year - 1
            time_list.append((yea, mon))

        def add(*args):
            i = args[0][0]
            j = args[0][1]
            if j > 12:
                i += 1
                j -= 12
            return i, j 
        time_list = map(add, time_list)
        return time_list

    def get_data(self, subsid, acctid):
        temp = self.get_six_year_month()
        # 获取开始时间
        sta_time = []
        end_time = []
        for i, j in temp[1:]:
            sta_time.append(str(i)+str(j).rjust(2, '0')+'27')
        # 获取结束时间
        for i, j in temp[:-1]:
            end_time.append(str(i)+str(j).rjust(2, '0')+'26')
        data_list = []        
        for i, j in zip(sta_time, end_time):
            data_list.append({
                "contextPath": "/eMobile",
                "customInfo.brandName": "",
                "customInfo.custName": "",
                "customInfo.prodName": "",
                "customInfo.subsId": subsid,
                "cycleMap.acctId_{}".format(i): acctid,
                "cycleMap.cycle_{}".format(i): str(i),
                "cycleMap.endDate_{}".format(i): str(j),
                "cycleMap.startDate_{}".format(i): str(i),
                "cycleMap.unionacct_{}".format(i): '0',
                "cycleStartDate": str(i),
                "feeType": "",
                "fieldErrFlag": "",
                "menuid": "queryBill",
                "month": str(i[:-2]),
                "retMonth":	str(i[:-2])
            })
        return data_list

    def crawl_phone_bill(self, **kwargs):
        missing_month_list =[]
        month_list = self.get_six_year_month()
        today = reduce(lambda x, y: str(x) + '%02d' % y, month_list[1])
        data = {
            "contextPath": "/eMobile",
            "customInfo.brandName":	"",
            "customInfo.custName": "",
            "customInfo.prodName": "",
            "customInfo.subsId": "",
            "cycleStartDate": "",
            "feeType": "",
            "fieldErrFlag": "",
            "menuid": "queryBill",
            "month": today,
            "retMonth": ""
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.sd.10086.cn/eMobile/queryBill.action?menuid=queryBill&pageId=448200474"
        }
        url = "http://www.sd.10086.cn/eMobile/queryBill_custInfo.action?pageid={}".format(random.random())
        for item in xrange(self.max_retry):
            code, key, resp = self.post(url, data=data, headers=headers)
            if code == 0:
                break
        else:
            missing_month_list = self.get_year_month(6)
            return 0, 'success', [], missing_month_list

        try:
            s = re.search(r"name=\"customInfo.subsId\" value=\"(\d*?)\"", resp.text)
            ss = re.search(r'value=\"(\d*?)\" id=\"queryBill_cycleMap_acctId', resp.text)
            subsid = s.group(1)
            acctid = ss.group(1)
        except ValueError:
            error = traceback.format_exc()
            missing_month_list = self.get_year_month(6)
            self.log('crawler', 'json_error:{}'.format(error),resp)
            # return "json_error", 9, "json_error_fir{}{}".format(error, res.text), []
            return 0, 'success', [], missing_month_list
        except:
            error = traceback.format_exc()
            # return "unknown_error", 9, "phone_bill_unknow_error_fir{}{}".format(error, res.text), []
            missing_month_list = self.get_year_month(6)
            self.log('crawler', 'unknown_error:{}'.format(error), resp)
            return 0, 'success', [], missing_month_list

        data_list = self.get_data(subsid, acctid)
        phone_bill = []
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.sd.10086.cn/eMobile/queryBill_custInfo.action?pageid=0.958331888932823"
        }
        for data in data_list:
            url = "http://www.sd.10086.cn/eMobile/queryBill_scheduled.action?pageid={}".format(random.random())
            missing_month = data['month']

            for item in xrange(self.max_retry):
                code, key, resp = self.post(url, data=data, headers=headers)
                if code != 0:
                    error ="request__error"
                    continue
                try:
                    month_bill = {}
                    month_bill["bill_month"] = re.search(u"账期.*?(\d{6})", resp.text).group(1)
                    month_bill["bill_amount"] = re.search(u"本月费用合计.*?(\d+\.\d{2})", resp.text, re.S).group(1)
                    month_bill["bill_package"] = re.search(u"套餐及固定费@_@(\d+\.\d{2})", resp.text).group(1)
                    month_bill["bill_ext_calls"] = re.search(u"语音通信费@_@(\d+\.\d{2})", resp.text).group(1)
                    month_bill["bill_ext_data"] = re.search(u"上网费@_@(\d+\.\d{2})", resp.text).group(1)
                    month_bill["bill_ext_sms"] = re.search(u"短彩信费@_@(\d+\.\d{2})", resp.text).group(1)
                    month_bill["bill_zengzhifei"] = re.search(u"增值业务费@_@(\d+\.\d{2})", resp.text).group(1)
                    month_bill["bill_daishoufei"] = re.search(u"代收费@_@(\d+\.\d{2})", resp.text).group(1)
                    month_bill["bill_qita"] = ""
                    phone_bill.append(month_bill)
                    break
                except:
                    error = traceback.format_exc()
                    self.log('crawler', 'html_error:{}'.format(error), resp)
                    continue
            else:
                if missing_month not in missing_month_list and error != "request__error":
                    missing_month_list.append(missing_month)
                    self.log('crawler', 'unknown_error', resp)
                    continue
        return 0, 'success', phone_bill, missing_month_list


if __name__ == '__main__':
    # from worker.crawler.china_mobile.SD.main import *
    c = Crawler()
    USER_ID = "15762559079"
    USER_PASSWORD = "172509"
    # c.get_six_year_month()
    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)

    # unit test
    # pprint(c.send_login_verify_request())

    # validate_code = ""
    # pprint(c.login(tel=USER_ID, pin_pwd=USER_PASSWORD, captcha_code=validate_code))

    # pprint(c.send_verify_request(tel=USER_ID))

    # sms_code = ""
    # captcha_code = ""

    # pprint(c.verify(tel=USER_ID,captcha_code=captcha_code, sms_code=sms_code))

    # pprint(c.crawl_info())
    # pprint(c.crawl_call_log())
