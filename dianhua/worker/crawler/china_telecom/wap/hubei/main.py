#!/user/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/8 17:28
# @Author  : zhangjun
# Title    :


import json
import random
import traceback
import sys
reload(sys)
sys.setdefaultencoding("utf8")

from random import choice
from datetime import date, datetime
import time
from dateutil.relativedelta import relativedelta
import base64

if __name__ == '__main__':
    sys.path.append('../../..')
    sys.path.append('../../../..')
    sys.path.append('../../../../..')
    from worker.crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        """
        初始化
        """
        user_agent = [
            'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1']

        super(Crawler, self).__init__(**kwargs)
        self.session.headers.update({'User-Agent': choice(user_agent)})

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_login_verify_type(self, **kwargs):
        return 'SMS'

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def send_login_verify_request(self, **kwargs):

        url = 'http://wap.hb.189.cn/login/login.jsp'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, ''

        url = 'http://wap.hb.189.cn/login/getSmsCode.htm?phoneNumber={}&randomType=loginRan'.format(kwargs['tel'])
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, ''
        if '"flag":"1"' in resp.text:
            return 0, 'success', ''
        if '"flag":"0"' in resp.text:
            self.log('crawler', u'短信发送过快', resp)
            return 9, 'send_sms_too_quick_error', ''
        self.log('crawler', u'登录前短信发送失败', resp)
        return 9, 'send_sms_error', ''

    def login(self, **kwargs):
        try:
            random_sms = base64.b64encode(kwargs['sms_code'])
            accountID_tel = base64.b64encode(kwargs['tel'])
        except:
            msg = traceback.format_exc()
            self.log('crawler', u'加密错误\n\n{}'.format(msg), '')
            return 9, 'crawl_error'

        data = {
            'random': random_sms,
            'accountID': accountID_tel,
            'loginType': '2',
        }
        url = 'http://wap.hb.189.cn/login/doLogin.htm'
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key
        if u'随机码错误' in resp.text:
            self.log('user', u'短信验证错误', resp)
            return 2, 'verify_error'

        url = 'http://wap.hb.189.cn/self/selfIndex.jsp'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key

        return 0, 'success'
        # return 9, 'crawl_error'

    def send_verify_request(self, **kwargs):
        time.sleep(30)
        headers = {
            'Referer': 'http://wap.hb.189.cn/service/custBillDetail.jsp',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'wap.hb.189.cn',
        }

        url = 'http://wap.hb.189.cn/login/getSmsCode.htm?phoneNumber={}&randomType=billQuery'.format(kwargs['tel'])
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ''
        if '"flag":"1"' in resp.text:
            return 0, 'success', ''
        self.log('crawler', u'发送短信失败', resp)
        return 9, 'send_sms_error', ''

    def verify(self, **kwargs):
        url = 'http://wap.hb.189.cn/billQuery/checkRan.htm'
        try:
            random_sms = base64.b64encode(kwargs['sms_code'])
            accountID_tel = base64.b64encode(kwargs['tel'])
        except:
            msg = traceback.format_exc()
            self.log('crawler', u'加密错误\n\n{}'.format(msg), '')
            return 9, 'crawl_error'

        data = {
            'random': random_sms,
            'accountID': accountID_tel,
        }

        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key

        if '"flag":"1"' in resp.text:
            return 0, 'success'
        if u'随机码错误' in resp.text:
            self.log('user', u'二次验证出错', resp)
            return 2, 'verify_error'
        self.log('user', u'二次验证未知错误', resp)
        return 9, 'verify_error'

    def crawl_call_log(self, **kwargs):
        missing_list = []
        possibly_missing_list = []
        call_log = []
        crawl_num = 0
        today = date.today()
        page_and_retry = []
        url = 'http://wap.hb.189.cn/billQuery/custBillDetail.htm'
        search_month = [x for x in range(0, -6, -1)]
        self.latnId = ''
        self.paymentMode = ''
        # self.billCycle = ''
        self.servId = ''
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            begDate = "%d%02d" % (query_date.year, query_date.month)
            data = {
                'billCycle': '',
                'latnId': '',
                'paymentMode': '',
                'queryType': '14',
                'servId': '',
            }
            page_and_retry.append((data, begDate, self.max_retry))

        st_time = time.time()
        et_time = st_time + 20
        log_for_retry_request = []

        while page_and_retry:
            call_log_data, m_query_month, m_retry_times = page_and_retry.pop(0)
            if self.servId:
                call_log_data['billCycle'] = m_query_month
                call_log_data['latnId'] = self.latnId
                call_log_data['paymentMode'] = self.paymentMode
                call_log_data['servId'] = self.servId

            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            result = []
            msg = ''
            code, key, resp = self.post(url, data=call_log_data)
            if code == 0:
                try:
                    result = self.call_log_get(resp.text, m_query_month)
                    if result:
                        call_log.extend(result)
                        continue
                except:
                    msg = traceback.format_exc()
                    crawl_num += 1

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((call_log_data, m_query_month, m_retry_times))
                continue
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((call_log_data, m_query_month, m_retry_times))
                    time.sleep(rand_sleep)
                    continue
            if code == 0 and not result:
                possibly_missing_list.append(m_query_month)
            else:
                missing_list.append(m_query_month)
            self.log('website', u'未找到指定数据:{}'.format(msg), resp)

        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        # print('missing_list:{}'.format(missing_list))
        # print('possibly_missing_list:{}'.format(possibly_missing_list))

        if len(missing_list) + len(possibly_missing_list) == 6:
            # 查询账单,判断是否为新卡
            searchMonth = "%d%02d" % (today.year, today.month)
            url = 'http://wap.hb.189.cn/billQuery/billQueryList.htm'
            data = {
                'billCycle': searchMonth,
                'task_remark': 'null',
            }
            code, key, resp = self.post(url, data=data)
            # 新卡
            if code == 0 and u'查询账期早于用户入网日期' in resp.text:
                return 9, 'websiter_prohibited_error', call_log, missing_list, possibly_missing_list
            if crawl_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def call_log_get(self, response, month):
        records = []
        resp_json = json.loads(response)
        self.latnId = resp_json['valueMap']['latnId']
        self.paymentMode = resp_json['valueMap']['paymentMode']
        self.servId = resp_json['valueMap']['servId']

        for item in resp_json['billDetail']['result']:
            data = {}
            item = item.split(',')
            data['month'] = month
            data['call_tel'] = item[0]
            data['call_cost'] = item[10]
            timeArray = time.strptime(item[2], "%Y/%m/%d %H:%M:%S")
            call_time_timeStamp = str(int(time.mktime(timeArray)))
            data['call_time'] = call_time_timeStamp
            data['call_method'] = item[5]
            data['call_type'] = item[9]

            raw_call_from = item[7].strip()
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                data['call_from'] = call_from
            else:
                data['call_from'] = raw_call_from
            raw_call_to = item[1].strip()
            call_to, error = self.formatarea(raw_call_to)
            if call_to:
                data['call_to'] = call_to
            else:
                data['call_to'] = raw_call_to
            data['call_duration'] = item[3]
            records.append(data)
        return records

    def crawl_info(self, **kwargs):
        """
        | `tel` | stirng | 用户电话号码  |
        | `update_time` | stirng | 更新时间戳 |
        | `full_name` | stirng | 机主用户姓名  |
        | `id_card` | stirng | 機主用戶身分證號(部分)  |
        | `is_realname_register` | string | 是否实名制 |
        | `open_date` | stirng | 入网時間 |
        """
        url = 'http://wap.hb.189.cn/info/queryUserInfo.htm'
        code, key, resp = self.post(url)
        if code != 0:
            return code, key
        user_info_dict = {
            'tel': '',
            'full_name': '',
            'id_card': '',
            'is_realname_register': '',
            'open_date': '',
            'address': '',
        }

        try:
            resp_json = json.loads(resp.text)
            user_info_dict['tel'] = resp_json['data']['serv']['aCCNBR']
            user_info_dict['full_name'] = resp_json['data']['serv']['uSERNAME']
            user_info_dict['open_date'] = resp_json['data']['serv']['cOMPLETEDATE']\
                .replace('年', '').replace('月','').replace('日', '')
            user_info_dict['id_card'] = resp_json['data']['serv']['cERTIFICATENO']
            user_info_dict['address'] = resp_json['data']['serv']['aDDRESSDETAIL']
            user_info_dict['is_realname_register'] = True
        except:
            msg = traceback.format_exc()
            self.log('crawler', msg, resp)
        return 0, 'success', user_info_dict

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

    def crawl_phone_bill(self, **kwargs):
        # phone_bill = list()
        phone_bill = []
        missing_list = []
        crawl_num = 0
        url = 'http://wap.hb.189.cn/billQuery/billQueryList.htm'
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            data = {
                'billCycle': searchMonth,
                'task_remark': 'null',
            }
            code, key, resp = self.post(url, data=data)
            if code != 0:
                missing_list.append(searchMonth)
                continue
            try:
                result = self.get_phone_bill(resp, searchMonth)
                phone_bill.append(result)
            except:
                msg = traceback.format_exc()
                self.log('crawler', msg, resp)
                missing_list.append(searchMonth)
                continue

        if len(missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', phone_bill, missing_list
            return 9, 'website_busy_error', phone_bill, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, 'success', phone_bill, missing_list


    def get_phone_bill(self, resp, month):
        resp_json = json.loads(resp.text)
        items = resp_json['csbR']['serviceInformationUniform']['billInforForUniform']['itemInforList']
        bill_data = {
            'bill_month': month,
            'bill_amount': '',
            'bill_package': '',
            'bill_ext_calls': '',
            'bill_ext_data': '',
            'bill_ext_sms': '',
            'bill_zengzhifei': '',
            'bill_daishoufei': '',
            'bill_qita': '',
        }

        for item in items:
            # print(item)
            if u'本项小计' in item['charge_type_Name']:
                bill_data['bill_amount'] = str(round(item['charge'] / 100.0, 2))
            if u'国内短信费' in item['charge_type_Name']:
                bill_data['bill_ext_sms'] = str(round(item['charge'] / 100.0, 2))
            if u'来电显示' in item['charge_type_Name']:
                bill_data['bill_package'] = str(round(item['charge'] / 100.0 , 2))
        return bill_data

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17371178631"
    USER_PASSWORD = "79416317"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)



