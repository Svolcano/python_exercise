#!/user/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/4/26 14:11
# @Author  : zhangjun
# Title    :
import calendar
import json
import traceback
import sys
import random
import datetime
from dateutil.relativedelta import relativedelta
reload(sys)
sys.setdefaultencoding("utf8")
from datetime import date
import time

if __name__ == '__main__':
    sys.path.append('../../..')
    sys.path.append('../../../..')
    sys.path.append('../../../../..')
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_unity
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

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify', 'full_name', 'id_card']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):

        # 页面跳转
        url = 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00710602'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key

        # 统一登录
        ProvinceID = '09'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        url = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10030&toStUrl=http://jl.189.cn/service/bill/toDetailBillFra.action?fastcode=00710602&cityCode=jl'
        headers = {
            'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00710602'}
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key
        Referer = resp.url

        form_data = {
            'ruleDetalId': '109',
            'certCode': kwargs['id_card'],
            'custName': kwargs['full_name'],
            'randCode': '',
        }

        # '3105': {"type": u"1-5位不定长数字英文混合"
        codetype = 3105
        for i in range(self.max_retry):
            url = "http://jl.189.cn/authImg?0.6104396236079717"
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
                form_data['randCode'] = str(result).lower()
            else:
                continue

            header = {
                'Origin': 'http://login.189.cn/login',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': Referer,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            }

            LOGIN_URL = 'http://jl.189.cn/realname/checkIdCardFra.action'
            code, key, resp = self.post(
                url=LOGIN_URL, data=form_data, headers=header)
            if code != 0:
                return code, key
            if '"result":"0"' in resp.text:
                return 0, 'success'
            elif u'"result":"1"' in resp.text:
                self.log('user', u'身份证错误或者姓名错误', resp)
                return 9, 'user_id_error'
            elif u'验证码错误' in resp.text:
                self.log('user', 'verify_error', resp)
                self._dama_report(cid)
                continue
            else:
                self.log('crawler', u'未知错误', resp)
                return 9, 'crawl_error'
        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error'

    # 请用本机发送CXXD至10001获取查询详单的验证码（发送免费）。
    def send_verify_request(self, **kwargs):
        return 0, 'success', ''

    def verify(self, **kwargs):
        # '3105': {"type": u"1-5位不定长数字英文混合"
        codetype = 3105
        for i in range(self.max_retry):
            url = "http://jl.189.cn/authImg?0.6104396236079717"
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
                randCode = str(result).lower()
            else:
                continue

            # 开始验证
            url = 'http://jl.189.cn/service/bill/doDetailBillFra.action'
            data = {
                'sRandomCode': kwargs['sms_code'],
                'randCode': randCode,
            }
            code, key, resp = self.post(url, data=data)
            if code != 0:
                return code, key
            if '"tip":""' in resp.text:
                return 0, 'success'
            if u'验证码有误' in resp.text:
                self.log('user', '验证码有误', resp)
                continue
            if u'短信随机码码错误' in resp.text:
                self.log('user', u'短信随机码码错误', resp)
                return 2, 'verify_error'
            self.log('crawler', u'未知错误', resp)
            return 9, 'crawl_error'
        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error'

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
        port_missting_list = []
        crawler_num = 0
        call_log = []
        log_for_retry_request = []

        url = 'http://jl.189.cn/service/bill/billDetailQueryFra.action'
        today = date.today()
        search_month = [x for x in range(0, -6, -1)]
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://jl.189.cn/service/bill/toDetailBillFra.action?cityCode=jl&fastcode=00710602',
        }
        month_and_retry = []
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            begDate = "%d-%02d-01" % (query_date.year, query_date.month)
            endDay = calendar.monthrange(query_date.year, query_date.month)[1]
            endDate = "%d-%02d-%s" % (query_date.year,
                                      query_date.month, endDay)
            query_month = "%d%02d" % (query_date.year, query_date.month)

            # totalPage = 0
            data = {
                'billDetailValidate': 'true',
                'billDetailType': '2',
                'startTime': begDate,
                'endTime': endDate,
                'pagingInfo.currentPage': '0',
                'contactID': '',
            }
            month_and_retry.append((data, query_month, 3))

        while month_and_retry:
            data, query_month, m_retry_times = month_and_retry.pop(0)
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                return code, key
            try:
                records, totalPage, contactID = self.call_log_get(resp)
                if records:
                    call_log.extend(records)
                else:
                    self.log('crawler', u'详单为空', resp)
                    possibly_missing_list.append(query_month)
                    continue
                if totalPage < 2:
                    continue
            except ValueError:
                msg = traceback.format_exc()
                if m_retry_times > 0:
                    time.sleep(2)
                    month_and_retry.append((data, query_month, m_retry_times))
                else:
                    self.log('website', msg, resp)
                    missing_list.append(query_month)
                continue
            except:
                msg = traceback.format_exc()
                if m_retry_times > 0 :
                    crawler_num += 1
                    time.sleep(2)
                    month_and_retry.append((data, query_month, m_retry_times))
                else:
                    self.log('website', msg, resp)
                    missing_list.append(query_month)
                continue

            page_list = list(range(2, totalPage + 1))
            page_and_retry = [(page, self.max_retry) for page in page_list]

            st_time = time.time()
            et_time = st_time + 5
            # log_for_retry_request = []

            while page_and_retry:
                msg = '---'
                page, retry_times = page_and_retry.pop(0)
                log_for_retry_request.append((query_month, page, retry_times))
                retry_times -= 1
                data['pagingInfo.currentPage'] = page
                data['contactID'] = contactID
                code, key, resp = self.post(url, data=data, headers=headers)
                if code == 0:
                    try:
                        records, totalPage, contactID = self.call_log_get(resp)
                        if records:
                            call_log.extend(records)
                            continue
                    except ValueError:
                        msg = traceback.format_exc()
                        self.log('website', msg, resp)
                        continue
                    except:
                        msg = traceback.format_exc()
                        self.log('crawler', msg, resp)
                        crawler_num += 1

                now_time = time.time()
                if retry_times > 0:
                    page_and_retry.append((page, retry_times))
                    continue
                elif now_time < et_time:
                    rand_sleep = random.randint(1, 2)
                    if retry_times > -5:
                        page_and_retry.append((page, retry_times))
                        time.sleep(rand_sleep)
                        continue
                port_missting_list.append(query_month)
                self.log('website', u'未找到指定数据:{}'.format(msg), resp)

        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        # print('missing_list:{}'.format(missing_list))
        # print('possibly_missing_list:{}'.format(possibly_missing_list))
        if len(missing_list) + len(possibly_missing_list) == 6:
            if crawler_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list, port_missting_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list, port_missting_list
        return 0, "success", call_log, missing_list, possibly_missing_list, port_missting_list

    def crawl_info(self, **kwargs):
        return 9, "unknown_error", {}

    def call_log_get(self, response):
        records = []
        json_data = json.loads(response.text)
        items = json_data['items']
        for item in items:
            data = {}
            data['update_time'] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime())
            data['month'] = item['beginTime'].replace('-', '')[:6]
            data['call_cost'] = str(item['fee'] / 100)
            timeArray = time.strptime(
                item['beginTime'].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
            call_time_timeStamp = str(int(time.mktime(timeArray)))
            data['call_time'] = call_time_timeStamp
            data['call_tel'] = item['calledAccNbr']
            data['call_method'] = item['callType']
            # data['call_method'] = item['callType'].decode('utf-8')
            data['call_type'] = item['netType']

            raw_call_from = item['visitArea'].strip()
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                data['call_from'] = call_from
            else:
                data['call_from'] = raw_call_from
            raw_call_to = item['callingArea'].strip()
            call_to, error = self.formatarea(raw_call_to)
            if call_to:
                data['call_to'] = call_to
            else:
                data['call_to'] = raw_call_to
            data['call_duration'] = str(item['duration'])
            records.append(data)

        if records == []:
            return [], 0, ''

        totalPage = 0
        if 'pagingInfo' in json_data:
            totalPage = int(json_data['pagingInfo']['totalPage'])
        if 'contactID' in json_data:
            contactID = json_data['contactID']
        return records, totalPage, contactID

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        missing_list = []
        crawl_num = 0
        url = 'http://jl.189.cn/service/bill/queryBillInfoFra.action'
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            data = {
                'billingCycle': searchMonth,
            }
            code, key, resp = self.post(url, data=data)
            if code != 0:
                return code, key, [], []
            if u'一致性账单查询查询' in resp.text:
                self.log('user', u'账单为空', resp)
                missing_list.append(searchMonth)
                continue
            try:
                bill_data = self.get_phone_bill(resp=resp,month=searchMonth)
            except:
                msg = traceback.format_exc()
                self.log('crawler', u'解析出错:\n{}'.format(msg), resp)
                crawl_num += 1
                continue
            phone_bill.append(bill_data)
        if len(missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', phone_bill, missing_list
            return 9, 'website_busy_error', phone_bill, missing_list

        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        # print('missing_list:{}'.format(missing_list))
        return 0, 'success', phone_bill, missing_list

    def get_phone_bill(self, resp, month):
        da_json = json.loads(resp.text)
        items = da_json['billItemList'][0]['acctItems']
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
            if u'月基本费' == item['acctItemName']:
                bill_data['bill_package'] = item['acctItemFee']
            if u'语音通信费' == item['acctItemName']:
                bill_data['bill_ext_calls'] = item['acctItemFee']
                # print(item)
        bill_amount = da_json['billItemList'][0]['billFee']

        bill_data['bill_amount'] = str(int(bill_amount) / 100)
        return bill_data

if __name__ == '__main__':
    c = Crawler()

    USER_ID = "17386803185"
    # USER_ID = "17386803187"
    USER_PASSWORD = "675145"
    full_name = "薛胜光"
    id_card = "152801197510160319"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD,
                full_name=full_name, id_card=id_card)
