# -*- coding: utf-8 -*-
import base64
import datetime
import os
import random
import re
import time
import traceback
import urllib
from datetime import date

import lxml
import lxml.html
from dateutil.parser import *
from dateutil.relativedelta import relativedelta

import execjs
import response_data
from pprintpp import pprint as pp

if __name__ == '__main__':
    import sys

    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


def get_password(pwd):
    js_path = "%s/des_rsa.js" % "/".join(os.path.abspath(__file__).split("/")[:-1])
    with open(js_path, 'r') as f:
        js_content = f.read()
        ctx = execjs.compile(js_content)
        new_pwd = ctx.call("enString", pwd)
        return new_pwd
    return ''


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        # keep the time span > 30 sec between sending two sms verification
        self.sms_send_time = None
        self.web_busy_except_list = ["SSLError", "HTTPConnectionPool"]
        self.web_busy_err = lambda x: [True for i in self.web_busy_except_list if i in x]

    def need_parameters(self, **kwargs):
        return ['pin_pwd']

    def get_login_verify_type(self, **kwargs):
        return ''

    def send_login_verify_request(self, **kwargs):
        code, key, resp = self.get("https://he.ac.10086.cn/login")
        if code != 0:
            return code, key, ""
        headers = {"Referer": "https://he.ac.10086.cn/login"}
        for i in range(self.max_retry):
            r_num = random.randint(0, 99999999999)
            # self.r_num = r_num
            pic_url = 'https://he.ac.10086.cn/common/image.jsp?r_0.0%s' % r_num
            code, key, resp = self.get(pic_url, headers=headers)
            if code != 0:
                return code, key, ""
            # 云打码
            codetype = 3004
            key, result, cid = self._dama(resp.content, codetype)

            if key == "success" and result != "":
                captcha_code = str(result)
            else:
                self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                code, key = 9, "auto_captcha_code_error"
                continue
            # 验证图片
            url = "https://he.ac.10086.cn/validImageCode?r_{}&imageCode={}".format(random.random(), captcha_code)
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://he.ac.10086.cn/login"
            }
            code, key, resp = self.get(url, headers=headers)

            if code != 0:
                continue

            text = resp.text.strip()
            if text == '1':
                return 0, "success", captcha_code
            else:
                code, key = 9, "auto_captcha_code_error"
                self._dama_report(cid)
                self.log("crawler", "图片输入错误", resp)
                continue
        else:
            return code, key, ""

    def login(self, **kwargs):
        code, key, captcha_code = self.send_login_verify_request()
        if code != 0:
            return code, key

        try:
            # new_num = self.r_num + random.randint(0, 9999999)
            # image_validate_url_1 = "https://he.ac.10086.cn/validImageCode?r_0.3%s&imageCode=%s" % (new_num, kwargs['captcha_code'])
            # new_num = new_num + random.randint(0, 9999999)
            # code, key, resp = self.get(image_validate_url_1)
            # if code != 0:
            #     return code, key
            # if '0' in resp.text:
            #     self.log("user", u"图形验证码填写错误", resp)
            #     return 9, "verify_error"

            login_url = 'https://he.ac.10086.cn/Login'
            data = [
                ('displayPics', "mobile_sms_login:0===sendSMS:0===mobile_servicepasswd_login:0"),
                # ('displayPics', ""), 官网偶发异常时可请求
                ('displayPic', "1"),
                ('type', 'B'),
                ('formertype', 'B'),
                ('backurl', 'https://he.ac.10086.cn//hblogin/backPage.jsp'),
                ('warnurl', 'https://he.ac.10086.cn//hblogin/warnPage.jsp'),
                ('spid', '8af849a33630f66201363197d42b0006'),
                ('RelayState', 'type=B;backurl=http://www.he.10086.cn/my;nl=3;loginFrom=http://www.he.10086.cn/my'),
                ('mobileNum', kwargs['tel']),
                ('userIdTemp', kwargs['tel']),
                ('servicePassword', get_password(kwargs['pin_pwd'])),
                ('emailpwd', u'请输入密码'.encode('utf-8')),
                ('servicePassword', u'请输入6位数字的服务密码'.encode('utf-8')),
                ('smsValidCode', ''),
                ('login_pwd_type', ''),
                ('email', urllib.quote((u'输入Email邮箱地址'.encode('utf-8')))),
                ('validCode', captcha_code)
            ]
            code, key, resp = self.post(login_url, data=data)
            if code != 0:
                return code, key
            if resp.history:
                code = re.findall("code=(.*?)&", resp.url)[0]
                if code == "5001":
                    self.log("user", u"密码错误超上限", resp)
                    return 9, "over_query_limit"
                elif code == "5002":
                    self.log("user", u"手机号码或用户名不存在", resp)
                    return 9, "invalid_tel"
                elif code == "2003" or code == "2009":
                    # 2009 图片验证码已失效
                    self.log("user", u"验证码错误", resp)
                    return 9, "verify_error"
                elif code in ["3013"]:
                    self.log("user", u"简单服务密码", resp)
                    return 9, "sample_pwd"
                elif code in ["4001", "3013", '3006']:
                    # 3013 服务密码是简单密码
                    self.log("user", u"服务密码错误", resp)
                    return 9, "pin_pwd_error"
                elif code == "6000":
                    self.log("website", u"website_busy_error", resp)
                    return 9, "website_maintaining_error"
                else:
                    self.log("crawler", u"未知错误", resp)
                    return 9, "unknown_error"
            doc = lxml.html.document_fromstring(resp.text)
            # ----- backPage
            back_url = 'https://he.ac.10086.cn/hblogin/backPage.jsp'
            data = {}
            data['SAMLart'] = doc.xpath("//input[@name='SAMLart']/@value")[0]
            data['isEncodePassword'] = doc.xpath("//input[@name='isEncodePassword']/@value")[0]
            data['displayPic'] = doc.xpath("//input[@name='displayPic']/@value")[0]
            data['RelayState'] = doc.xpath("//input[@name='RelayState']/@value")[0]
            data['displayPics'] = ''
            code, key, resp = self.post(back_url, data=data)
            if code != 0:
                return code, key
            ## ----- my
            url = "http://www.he.10086.cn/my"
            doc = lxml.html.document_fromstring(resp.text)
            data = {}
            data['SAMLart'] = doc.xpath("//input[@name='SAMLart']/@value")[0]
            data['RelayState'] = doc.xpath("//input[@name='RelayState']/@value")[0]
            code, key, resp = self.post(url, data=data)
            if code != 0:
                return code, key
            ## ----- POST
            url = "http://he.ac.10086.cn/POST"
            doc = lxml.html.document_fromstring(resp.text)
            data = {}
            data['SAMLart'] = doc.xpath("//input[@name='SAMLRequest']/@value")[0]
            data['RelayState'] = doc.xpath("//input[@name='RelayState']/@value")[0]
            code, key, resp = self.post(url, data=data)
            if code != 0:
                return code, key
            ## ----- my
            url = "http://www.he.10086.cn/my/"
            doc = lxml.html.document_fromstring(resp.text)
            data = {}
            data['SAMLart'] = doc.xpath("//input[@name='SAMLart']/@value")[0]
            data['isEncodePassword'] = doc.xpath("//input[@name='isEncodePassword']/@value")[0]
            data['displayPic'] = doc.xpath("//input[@name='displayPic']/@value")[0]
            data['RelayState'] = doc.xpath("//input[@name='RelayState']/@value")[0]
            data['displayPics'] = ''
            code, key, resp = self.post(url, data=data)
            if code != 0:
                return code, key
            ## to bill page
            code, key, resp = self.get('http://www.he.10086.cn/service/fee/qryDetailBill.action')
            if code != 0:
                return code, key
            doc = lxml.html.document_fromstring(resp.text)
            data = {}
            data['SAMLart'] = doc.xpath("//input[@name='SAMLRequest']/@value")[0]
            data['RelayState'] = doc.xpath("//input[@name='RelayState']/@value")[0]
            url = "http://he.ac.10086.cn/POST"
            code, key, resp = self.post(url, data=data)
            if code != 0:
                return code, key
            doc = lxml.html.document_fromstring(resp.text)
            data = {}
            data['SAMLart'] = doc.xpath("//input[@name='SAMLart']/@value")[0]
            data['isEncodePassword'] = doc.xpath("//input[@name='isEncodePassword']/@value")[0]
            data['displayPic'] = doc.xpath("//input[@name='displayPic']/@value")[0]
            data['RelayState'] = doc.xpath("//input[@name='RelayState']/@value")[0]
            data['displayPics'] = ''
            url = "http://www.he.10086.cn/service/login!initLogin.action"
            code, key, resp = self.post(url, data=data)
            if code != 0:
                return code, key
            return 0, 'success'
        # 为什么有了异常时, 报验证码错误?
        except:
            error = traceback.format_exc()
            # 在封装中完成了对requests的错误处理, 所以直接调用r.text不会错误, 并且在会获取错误时的当前请求对象的响应实体
            self.log("crawler", "verify_error: {}".format(error), "")
            return 2, 'verify_error'

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def verify(self, **kwargs):
        r_num = random.randint(0, 99999999999)
        url = 'http://www.he.10086.cn/service/fee/qryDetailBill!checkSmsCode.action?r=0.%s' % r_num
        data = {'smsrandom': kwargs['sms_code']}
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key
        if u'证码不正确' in resp.text:
            status_key, level, message = 'verify_error', 9, u'sms验证码输入有误'
        elif u'outOfCount' in resp.text:
            status_key, level, message = 'over_max_sms_error', 9, u'您发送的短信次数不能超过30次/24小时'
        elif u'请重新获取' in resp.text:
            status_key, level, message = 'verify_error', 9, u'短信随机码已过期，请重新获取'
        else:
            status_key, level, message = 'success', 0, ''
        if level != 0:
            if level in [1, 2]:
                self.log("user", status_key, resp)
            else:
                self.log("crawler", status_key, resp)
        return level, status_key

    def send_verify_request(self, **kwargs):

        # keep the time span > 30 sec between sending two sms verification
        if self.sms_send_time != None:
            sleep_time = 30 - int(time.time() - self.sms_send_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

        r_num = random.randint(0, 99999999999)
        url = 'http://www.he.10086.cn/service/fee/fee/qryDetailBill!sendRandomCode.action?r=0.%s' % r_num
        code, key, resp = self.post(url)
        if code != 0:
            return code, key, ""
        if 'faild' in resp.text:
            self.log("crawler", "send_sms_error", resp)
            return 9, 'send_sms_error', ""
        # keep the lastet sending sms verification timestamp
        self.sms_send_time = time.time()
        return 0, 'success', ""

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        if re.search(r"\d{4} \d{2}-\d{2} \d{2}:\d{2}:\d{2}", time_str):
            time_s = time_str.split(" ")
            time_str = time_s[0] + '-' + time_s[1] + " " + time_s[2]
            # print time_str
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

    def crawl_call_log(self, **kwargs):
        pos_miss_list = []
        miss_list = []
        message_list = []

        def parse_call_record(query_date, r):
            records = []
            year = query_date.year
            year_month = "%d%02d" % (year, query_date.month)
            doc = lxml.html.document_fromstring(r.text)
            trs = doc.xpath("//table[@id='bill_page']//tr")
            call_from_set = set()
            for tr in trs[1:]:
                record = {}
                tds = tr.xpath('td')
                # 小于3 会怎样？ 根据网页结构, 小于3记录的不是数据信息
                if len(tds) < 3:
                    continue
                date_str = "%s %s %s" % (year, tds[0].text_content().strip(), tds[1].text_content().strip())
                record['call_time'] = self.time_transform(date_str)
                record['call_duration'] = self.time_format(tds[5].text_content().strip())
                record['call_tel'] = tds[4].text_content().strip()
                if not record['call_tel']:
                    self.log("crawler", "未知异常导致的无call_tel字段", r)
                    return 9, "html_error"
                record['call_cost'] = ''
                record['call_to'] = ''
                raw_call_from = tds[2].text_content().strip()
                call_from, error = self.formatarea(raw_call_from)
                if not call_from:
                    call_from = raw_call_from
                    call_from_set.add(raw_call_from)
                record['call_from'] = call_from
                record['call_method'] = tds[3].text_content().strip()
                record['call_type'] = tds[6].text_content().strip()
                record['call_to'] = ''
                record['month'] = year_month
                records.append(record)
            if call_from_set:
                self.log("crawler", "call_from_set: {}".format(call_from_set), resp)
            return 0, records

        today = date.today()
        records = []
        delta_months = [i for i in range(0, -6, -1)]
        page_and_retry = []
        # 时间为本月及之前6个月
        for delta_month in delta_months:
            query_date = today + relativedelta(months=delta_month)
            r_num = random.randint(0, 99999999999)
            url = 'http://www.he.10086.cn/service/fee/qryDetailBill!qryNewBill.action?smsrandom=&r=0.%s' % r_num
            data = {}
            data['menuid'] = ''
            data['fieldErrFlag'] = ''
            data['selectncode'] = ''
            data['ncodestatus'] = ''
            data['operatype'] = ''
            data['groupId'] = ''
            data['theMonth'] = "%d%02d" % (query_date.year, query_date.month)
            data['queryType'] = 'NGQryCallBill'
            data['qryscope'] = '0'
            data['selectTaken'] = ''
            data['regionstate'] = '1'
            data['onlinetime'] = ''
            data['qryType'] = '10'
            data['qryDate'] = '000'
            data['callPlace'] = '000'
            data['opTelnum'] = '000'
            data['callWay'] = '000'
            data['callType'] = '000'

            page_and_retry.append((data, url, query_date, self.max_retry))


        st_time = time.time()
        et_time = st_time + 30
        log_for_retry_request = []

        while page_and_retry:
            data, url, query_date, m_retry_times = page_and_retry.pop(0)
            now_month = "{}{}".format(query_date.year, '%02d' % query_date.month)
            log_for_retry_request.append((query_date, m_retry_times))
            m_retry_times -= 1
            code, key, resp = self.post(url, data=data)
            if code == 0:
                try:
                    code, one_records = parse_call_record(query_date, resp)
                    if code == 0:
                        if one_records:
                            records.extend(one_records)
                            continue
                        else:
                            key = "success"
                            level = 0
                            message = "no data"
                    else:
                        key = "html_error"
                        message = "获取的call_tel字段为空值"
                        level = 1
                except:
                    key = "html_error"
                    message = ": " + traceback.format_exc()
                    level = 1

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((data, url, query_date, m_retry_times))
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((data, url, query_date, m_retry_times))
                    time.sleep(rand_sleep)
                else:
                    if message != "network_request_error":
                        self.log("crawler", "crawler_failed" + message, '')
                    if message == 'no data':
                        pos_miss_list.append(now_month)
                    if now_month not in miss_list and level != 0:
                        message_list.append(key)
                        miss_list.append(now_month)
            else:
                if message != "network_request_error":
                    self.log("crawler", "crawler_failed" + message, '')
                if message == 'no data':
                    pos_miss_list.append(now_month)
                if now_month not in miss_list and level != 0:
                    message_list.append(key)
                    miss_list.append(now_month)

        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        if len(miss_list + pos_miss_list) == 6:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', records, miss_list, pos_miss_list
            else:
                return 9, 'crawl_error', records, miss_list, pos_miss_list
        return 0, 'success', records, miss_list, pos_miss_list

    def crawl_info(self, **kwargs):
        r_num = random.randint(0, 99999999999)
        url = "http://www.he.10086.cn/my/individualInfoServiceAction!init.action?menuid=individualInformation&pageId=0.%s" % (r_num)
        data = {}
        data['menuid'] = 'individualInformation'
        data['pageId'] = "0.%s" % r_num
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, {}
        try:
            doc = lxml.html.document_fromstring(resp.text)
            trs = doc.xpath("//div[@class='FramePerInfor_middle']//tr")
        except:
            error = traceback.format_exc()
            self.log("crawler", "unknown_error: " + error, resp)
            return 9, 'unknown_error', {}
        info = {}
        # TODO: 沒有全名跟身分證號
        try:
            info['full_name'] = trs[0].xpath('td')[2].text_content().strip()
            info['id_card'] = trs[6].xpath('td')[2].text_content().strip()
            info['open_date'] = self.time_transform(trs[3].xpath('td')[1].text_content().strip())
            info['address'] = trs[7].xpath('td')[2].text_content().strip()
            realname = trs[5].xpath('td')[2].text_content().strip()
            if u'已实名' == realname:
                info['is_realname_register'] = True
            return 0, 'success', info
        except:
            error = traceback.format_exc()
            self.log("crawler", 'crawl_error: ' + error, resp)
            return 9, 'crawl_error', {}

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        miss_list = []
        message_list = []
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            crawl_phone_bill_data = {
                'cycle': searchMonth
            }
            URL_PHONE_BILL = 'http://www.he.10086.cn/service/fee/qryMyBill!qryBillAllInfo.action'
            for i in range(self.max_retry):
                code, key, resp = self.get(URL_PHONE_BILL, params=crawl_phone_bill_data)
                if code != 0:
                    message = "network_request_error"
                    continue
                else:
                    level, key, message, result = response_data.phone_bill_data(resp.text, searchMonth)
                    # print result
                    if level != 0:
                        continue
                    phone_bill.append(result)
                    break
            else:
                if message != "network_request_error":
                    self.log("crawler", "html_error" + message, resp)
                message_list.append(key)
                miss_list.append(searchMonth)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', phone_bill, miss_list
            else:
                return 9, 'crawl_error', phone_bill, miss_list

        return 0, 'success', phone_bill, miss_list

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)


if __name__ == '__main__':
    import pprintpp
    """
    sizeof: 1452
    """
    c = Crawler()
    USER_ID = "15128668801"
    USER_PASSWORD = "345332"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
