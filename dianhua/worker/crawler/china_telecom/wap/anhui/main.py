#!/user/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/7 14:57

import calendar
import json
import random
import traceback
import sys
from lxml import etree
reload(sys)
sys.setdefaultencoding("utf8")

from fake_useragent import UserAgent
from datetime import date, datetime
import time
from dateutil.relativedelta import relativedelta

from des_js import des_encode

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
        super(Crawler, self).__init__(**kwargs)
        self.session.headers.update({'User-Agent': UserAgent().safari})

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_verify_type(self, **kwargs):
        # return 'SMS'
        # 官网需要短信
        pass

    def login(self, **kwargs):
        url = 'http://wapah.189.cn/detail/detailQueryInit.shtml'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key

        try:
            htmltree = etree.HTML(resp.text)
            empoent = htmltree.xpath('//*[@id="empoent"]/@value')[0]
            module = htmltree.xpath('//*[@id="module"]/@value')[0]
            userphone = des_encode(empoent, module, kwargs['tel'])
            khmm = des_encode(empoent, module, kwargs['pin_pwd'])

        except:
            msg = traceback.format_exc()
            self.log('crawler', msg, resp)
            return 9, 'crawl_error'

        # "1-5位不定长数字英文混合"
        codetype = 3105
        for i in range(self.max_retry):
            url = "http://wapah.189.cn/Kaptcha.code?482"
            code, key, resp = self.get(url)
            if code != 0:
                return code, key
            try:
                key, result, cid = self._dama(resp.content, codetype)
            except:
                msg = traceback.format_exc()
                self.log('crawler', u'打码失败:{}'.format(msg), '')
                continue
            if key == "success" and result != "":
                Captcha = str(result).lower()
            else:
                continue
            url = 'http://wapah.189.cn/ua/login.shtml?tt='

            formData = {
                'userphone':userphone,
                'check_userphone':kwargs['tel'],
                'logintype':'1',
                'khmm': khmm,
                'sjmm': '',
                'randomCode':Captcha,
            }
            data = {
                'formData': json.dumps(formData),
            }
            headers = {
                'Referer': 'http://wapah.189.cn/ua/toLogin.shtml',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
            }
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                return code, key
            if '"retMsg":"登录成功","retCode":"0"' in resp.text or 'flowUseList' in resp.text or 'fmList' in resp.text:
                return 0, 'success'
            if u'验证码错误' in resp.text:
                self.log('user', u'打码错误', '')
                self._dama_report(cid)
                continue
            if u'密码错误' in resp.text:
                self.log('user', u'密码错误', resp)
                return 1, 'pin_pwd_error'
            if u'密码过于简单' in resp.text:
                self.log('user', u'服务密码过于简单', resp)
                return 1, 'sample_pwd'
            if u'您的账号验证错误次数过多' in resp.text:
                self.log('user', u'账号已被运营商锁定', resp)
                return 9, 'account_locked'
            if u'帐号不存在' in resp.text:
                self.log('user', u'帐号不存在', resp)
                return 9, 'invalid_tel'
            self.log('website', u'登录未知出错', resp)
            return 9, 'crawl_error'
        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error'

    def send_verify_request(self, **kwargs):
        url = 'http://wapah.189.cn/ua/sendSms.shtml'
        data = {
            'smsPhone': kwargs['tel'],
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, ''
        if '{"retCode":"0"}' in resp.text:
            return 0, 'success', ''
        if u'每分钟只能发送一次短信' in resp.text:
            self.log('user', u'发送短信过快', resp)
            return 9, 'send_sms_too_quick_error', ''
        self.log('website', u'发送短信未知出错', resp)
        return 9, 'send_sms_error', ''

    def verify(self, **kwargs):
        url = 'http://wapah.189.cn/detailSingleQuery.shtml'

        startDate = str(time.strftime('%Y-%m-01', time.localtime(time.time())))
        endDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        data = {
            'sendcheck': kwargs['sms_code'],
            'endDate': endDate,
            'startDate': startDate,
            'serviceNbr': kwargs['tel'],
            'type': '1',
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key
        if '"mesg":0' in resp.text:
            return 0, 'success'
        if '"mesg":-5,' in resp.text:
            self.log('user', u'短信输入错误', resp)
            return 2, 'verify_error'
        self.log('website', u'验证短信未知出错', resp)
        return 9, 'crawl_error'

    def crawl_info(self, **kwargs):
        return 9, "unknown_error", {}

    def crawl_call_log(self, **kwargs):
        # return 0, 'success',[],[],[]
        missing_list = []
        possibly_missing_list = []
        call_log = []
        crawl_num = 0
        today = date.today()
        page_and_retry = []

        url = 'http://wapah.189.cn/detailQueryAfter.shtml'
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            begDate = "%d-%02d-01" % (query_date.year, query_date.month)
            endDay = calendar.monthrange(query_date.year, query_date.month)[1]
            if each_month == 0:
                endDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            else:
                endDate = "%d-%02d-%s" % (query_date.year, query_date.month, endDay)
            data = {
                # 'sendcheck':kwargs['sms_code'],
                'sendcheck':'0',
                'endDate':endDate,
                'startDate':begDate,
                'type':'2',
                'serviceNbr':kwargs['tel'],
                'pageNum':3000,
            }
            page_and_retry.append((data, begDate.replace('-','')[:6], self.max_retry))

        st_time = time.time()
        et_time = st_time + 20
        log_for_retry_request = []

        while page_and_retry:
            call_log_data, m_query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            result = []
            msg = ''
            code, key, resp = self.post(url, data=call_log_data)
            if code == 0:
                try:
                    result = self.call_log_get(resp.text)
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
            if crawl_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def call_log_get(self, response):
        records = []
        if '"totalLantProId":null' in response:
            return []
        resp_json = json.loads(response)
        items = resp_json['flowUseList']['fmList']
        for item in items:
            data = {}
            data['call_tel'] = item['qryFifthLine']
            if data['call_tel'] == "--------":
                continue
            data['month'] = item['qryEighthLine'].replace('-', '')[:6]
            data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data['call_cost'] = item['qryEleventhLine']
            timeArray = time.strptime(item['qryEighthLine'], "%Y-%m-%d %H:%M:%S")
            call_time_timeStamp = str(int(time.mktime(timeArray)))
            data['call_time'] = call_time_timeStamp
            data['call_method'] = item['qrySecondLine']
            data['call_type'] = item['qryThirdLine']
            # data['call_from'] = item['qrySixthLine']
            raw_call_from = item['qrySixthLine'].strip()
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                data['call_from'] = call_from
            else:
                data['call_from'] = raw_call_from

            raw_call_to = item['qryForthLine'].strip()
            call_to, error = self.formatarea(raw_call_to)
            if call_to:
                data['call_to'] = call_to
            else:
                data['call_to'] = raw_call_to
            call_durations = item['qryTenthLine'].split(':')
            call_duration = int(call_durations[0]) * 3600 + int(call_durations[1]) * 60 + int(call_durations[2])
            data['call_duration'] = str(call_duration)
            records.append(data)
        return records

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        missing_list = []
        crawl_num = 0
        url = 'http://wapah.189.cn/bill/easyAjax.shtml'
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            data = {
                'month': searchMonth,
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
        resultMessage = eval(resp_json['resultMessage'])
        items = resultMessage['ContractRoot']['SvcCont']['SOO'][1]['INVOICE_ITEM_INFO']
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
        if type(items) == dict:
            bill_data['bill_qita'] = items['CHARGE_S']
            bill_data['bill_amount'] = items['CHARGE_S']
            return bill_data

        bill_amount = 0
        for item in items:
            if item['INVOICE_NAME'] == u'语音通信费':
                bill_data['bill_ext_calls'] = item['CHARGE_S']
            if item['INVOICE_NAME'] == u'短信彩信费':
                bill_data['bill_ext_sms'] = item['CHARGE_S']
            if item['INVOICE_NAME'] == u'上网及数据通信费':
                bill_data['bill_ext_data'] = item['CHARGE_S']
            if item['INVOICE_NAME'] == u'综合信息服务费':
                bill_data['bill_qita'] = item['CHARGE_S']
            bill_amount += float(item['CHARGE_S'])
        bill_data['bill_amount'] = str(round(bill_amount, 2))

        return bill_data


if __name__ == '__main__':
    c = Crawler()

    USER_ID = "13399565307"
    USER_PASSWORD = "786742"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)





