#!/user/bin/env python
# -*- coding:utf-8 -*-
import random
import re
import json
import traceback
import sys
import time
import calendar
import datetime
from datetime import date
# 这段代码是用于解决中文报错的问题
from dateutil.relativedelta import relativedelta

reload(sys)
sys.setdefaultencoding("utf8")

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler

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

    def need_parameters(self, **kwargs):
        return ['pin_pwd','sms_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        url = 'http://js.189.cn/nservice/listQuery/index'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key
        try:
            # uuid = re.findall("var dataR = queryUserLoginInfoByKey\('(.*)?'\);", resp.text)[0]
            uuid = re.findall("var dataR = queryUserLoginInfoByKey\('([a-zA-Z0-9\-]+)'\);", resp.text)[0]
        except:
            msg = traceback.format_exc()
            self.log('website', msg, resp)
            return 9, 'crawl_error'

        login_url = 'http://js.189.cn/nservice/login/doLogin?TargetURL=http://js.189.cn/nservice/listQuery/index&menuType=0'
        headers = {
            'Referer': 'http://js.189.cn/nservice/listQuery/index',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # 4位字母数字
        codetype = 2004
        for i in range(self.max_retry):
            url = 'http://js.189.cn/nservice/verication/getCodeImage'
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

            data = {
                'userType': '2000004',
                'logonPattern': '2',
                'newUamType': '-1',
                'productId': kwargs['tel'],
                'userPwd': kwargs['pin_pwd'],
                'validateCodeNumber': Captcha,
                # 'validateCodeNumber': 'ssss',
                }

            code, key, resp = self.post(login_url, data=data, headers=headers)
            if code != 0:
                return code, key

            if 'showTimeMsgPupup' in resp.text:
                if u'验证码错误，请重新输入' in resp.text:
                    self.log('user', 'verify_error', resp)
                    self._dama_report(cid)
                    continue
                if u'帐号或密码错误' in resp.text:
                    self.log('user', 'pin_pwd_error', resp)
                    return 1, 'pin_pwd_error'
                if u'帐号被锁定' in resp.text:
                    self.log('user', 'account_locked', resp)
                    return 9, 'account_locked'
                if u'系统繁忙，请稍后' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    return 9, 'website_busy_error'

                self.log('user', u'未知错误', resp)
                return 9, 'crawl_error'

            url = 'http://js.189.cn/nservice/login/queryUserLoginInfoByKey'
            data = {
                'uuid': uuid,
            }
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                return code, key
            if '"TSR_CODE":"0"' in resp.text:
                return 0, 'success'
            self.log('crawler', u'未知错误', resp)
            return 9, 'crawl_error'
        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error'

    def send_verify_request(self, **kwargs):
        url = 'http://js.189.cn/nservice/wec/sendMsg'
        data = {
            'accNbr':kwargs['tel'],
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, ''
        if 'yes' in resp.text:
            return 0, 'success', ''
        # if 'no' in resp.text:

        self.log('crawler', u'send_sms_error', resp)
        return 9, 'send_sms_error', ''

    def verify(self, **kwargs):
        url = 'http://js.189.cn/nservice/checkCode/checkVeiCode'
        data = {
            'accNbr': kwargs['tel'],
            'code':kwargs['sms_code'],
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key
        if 'yes' in resp.text:
            return 0, 'success'
        resp.encoding = 'utf-8'
        self.log('crawler', u'verify_error', resp)
        return 9, 'verify_error'

    def crawl_call_log(self, **kwargs):
        missing_list = []
        possibly_missing_list = []
        call_log = []
        crawl_num = 0
        call_log_url = 'http://js.189.cn/nservice/listQuery/queryList'
        today = date.today()

        page_and_retry = []
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            begDate = "%d-%02d-01" % (query_date.year, query_date.month)
            endDay = calendar.monthrange(query_date.year, query_date.month)[1]
            if each_month == 0:
                endDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            else:
                endDate = "%d-%02d-%s" % (query_date.year, query_date.month, endDay)
            call_log_data = {
                'listType': '1',
                'stTime': begDate,
                'endTime': endDate,
            }
            query_month = "%d%02d" % (query_date.year, query_date.month)
            page_and_retry.append((call_log_data, query_month, self.max_retry))

        st_time = time.time()
        et_time = st_time + 30
        log_for_retry_request = []
        while page_and_retry:
            call_log_data, m_query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            code, key, resp = self.post(call_log_url, data=call_log_data)
            result = []
            if code == 0:
                try:
                    if u'无记录' in resp.text:
                        self.log('website', u'无记录', resp)
                        possibly_missing_list.append(m_query_month)
                        continue
                    call_log_res = json.loads(resp.text)
                    if call_log_res['respCode'] == "0000":
                        result = self.call_log_get(call_log_res, m_query_month)
                        if result:
                            call_log.extend(result)
                            continue
                except:
                    crawl_num += 1
                    error = traceback.format_exc()
                    self.log('crawler', "json_error :%s" % error, resp)

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((call_log_data, m_query_month, m_retry_times))
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((call_log_data, m_query_month, m_retry_times))
                    time.sleep(rand_sleep)
                else:
                    if code == 0 and not result:
                        possibly_missing_list.append(m_query_month)
                    else:
                        missing_list.append(m_query_month)
                    self.log('website', u'未找到指定数据1', resp)
            else:
                if code == 0 and not result:
                    possibly_missing_list.append(m_query_month)
                else:
                    missing_list.append(m_query_month)
                self.log('website', u'未找到指定数据2', resp)

        # print('possibly_missing_list:', possibly_missing_list)
        # print('missing_list:', missing_list)
        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        if len(missing_list) + len(possibly_missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def call_log_get(self, response, month):
        records = []
        for item in response['respMsg']:
            item = item[0]
            data = {}
            data['month'] = month
            data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data['call_cost'] = item['ticketChargeCh']
            # data['call_time'] = item['startDateNew'] +" "+ item['startTimeNew']
            # 以下几行为了转换时间戳
            call_time = re.findall('\d{2}', item['startDateNew'] + " " + item['startTimeNew'])
            call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + call_time[
                4] + ':' + call_time[5] + ':' + call_time[6]
            timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
            call_time_timeStamp = str(int(time.mktime(timeArray)))

            data['call_time'] = call_time_timeStamp
            data['call_method'] = item['ticketTypeNew']
            data['call_type'] = item['durationType']
            # data['call_from'] = item['areaCode']

            raw_call_from = item['areaCode'].strip()
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                data['call_from'] = call_from
            else:
                data['call_from'] = raw_call_from

            data['call_to'] = ''
            data['call_tel'] = item['nbr']
            # 以下几行是为了把时间转换成秒
            duration = item['duartionCh']
            call_durations = duration.split(':')
            call_duration = int(call_durations[0]) * 3600 + int(call_durations[1]) * 60 + int(call_durations[2])
            data['call_duration'] = str(call_duration)
            records.append(data)
        return records

    def crawl_info(self, **kwargs):
        return 9, 'unknown_error', {}

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        missing_list = []
        crawl_num = 0
        data = {
            'zhangqi':'',
            'style':'0',
        }
        url = 'http://js.189.cn/nservice/billQuery/consumptionQuery'
        for searchMonth in self.__monthly_period(6, '%Y-%m'):
            data['zhangqi'] = searchMonth
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

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

    def get_phone_bill(self, resp, month):
            phone_bill = json.loads(resp.text)
            bill_list = phone_bill['consumptionList'][0]
            bill_data = {
                'bill_month': month.replace('-', ''),
                'bill_amount': '',
                'bill_package': '',
                'bill_ext_calls': '',
                'bill_ext_data': '',
                'bill_ext_sms': '',
                'bill_zengzhifei': '',
                'bill_daishoufei': '',
                'bill_qita': '',
            }
            bill_data['bill_amount'] = bill_list['dccBillFee']
            for item in bill_list['dccBillList'][0]['dccBillList']:
                # print(item)
                if item['dccBillItemName'] == u'语音通信费':
                    bill_data['bill_ext_calls'] = item['dccBillFee']
                if item['dccBillItemName'] == u'短信彩信费':
                    bill_data['bill_ext_sms'] = item['dccBillFee']
                if item['dccBillItemName'] == u'优惠费用':
                    bill_data['bill_package'] = item['dccBillFee']
            return bill_data

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17368357716"
    USER_PASSWORD = "488496"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)





