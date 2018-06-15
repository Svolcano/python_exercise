# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import random
import traceback
import datetime
import time
import sys
import re

from Crypto.Cipher import AES
from datetime import date
from dateutil.relativedelta import relativedelta

# 这段代码是用于解决中文报错的问题
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

# from com.yundama import yundama
from setting.yundama_config import YUNDAMA_CODE

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
        return ['pin_pwd', 'full_name', 'id_card']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):

        ProvinceID = '16'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key


        url = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10016&toStUrl=http://sd.189.cn/selfservice/account/returnAuth?columnId=0211'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key

        return 0, "success"

    def send_verify_request(self, **kwargs):
        self.headers = {
            'Host': 'sd.189.cn',
            'Origin': 'http://sd.189.cn',
            'X-Requested-With': 'XMLHttpRequest',
        }
        today = date.today()
        self.today_month = "%d%02d" % (today.year, today.month)

        # 检查登录状态
        check_data = {"accNbr": kwargs['tel'], "billingCycle": self.today_month, "ticketType": "0"}
        check_url = 'http://sd.189.cn/selfservice/bill/queryBillDetailNum'
        code, key, resp = self.post(check_url, data=json.dumps(check_data), headers=self.headers)
        if code != 0:
            return code, key, ''

        image_url = 'http://sd.189.cn/selfservice/validatecode/codeimg.jpg'
        for i in xrange(self.max_retry):
            code, key, resp = self.get(image_url)
            if code != 0:
                return code, key, ''
            # f = open('./2tmp.png', 'wb')
            # f.write(resp.content)
            # f.close()
            codetype = 1004
            try:
                # cid, result = yundama.decode(resp.content, codetype)
                key, result, cid = self._dama(resp.content, codetype)
            except:
                error = traceback.format_exc()
                self.log("website", "website_busy_error: " + error, resp)
                if i == self.max_retry - 1:
                    return 9, 'website_busy_error', ''
                continue
            if key == "success" and result != "":
                self.captcha_code = str(result).lower()
                # 发送短信并验证图片
                url = 'http://sd.189.cn/selfservice/service/sendSms'
                data = {"orgInfo": kwargs['tel'], "valicode": self.captcha_code, "smsFlag": "real_2busi_validate"}
                code, key, resp = self.post(url, data=json.dumps(data))
                if code != 0:
                    return code, key, ''
                if resp.text != '0':
                    # 打码错误，上报，本次免费
                    # yundama.report(cid)
                    if i == self.max_retry-1:
                        self.log('user', '图像验证码出错cid:{},result{}'.format(cid, result), resp)
                        return 2, 'verify_error', ''
                    continue
                break
            else:
                # message = YUNDAMA_CODE.get(str(cid), '').decode('utf-8')
                message = u'打码失败'
                self.log("website", "website_busy_error:云打码异常{}。".format(message), '')
                if i == self.max_retry - 1:
                    return 9, 'website_busy_error', ''

        return 0, 'success', ''

    def verify(self, **kwargs):
        header ={
            'Referer': 'http://sd.189.cn/selfservice/service/toBusiVa?v=83&r=1',
        }
        url = 'http://sd.189.cn/selfservice/service/busiVa'
        data = {"username_2busi": kwargs['full_name'],
                "credentials_type_2busi": "1",
                "credentials_no_2busi": kwargs['id_card'],
                # "validatecode_2busi": self.captcha_code,
                "validatecode_2busi": '1325',
                "randomcode_2busi": kwargs['sms_code'],
                "randomcode_flag": "0"}
        code, key, resp = self.post(url, data=json.dumps(data), headers=header)
        if code != 0:
            return code, key

        try:
            verify_json = json.loads(resp.text)
            retn_code = verify_json['retnCode']
            if retn_code != 0:
                if retn_code == 5 or retn_code == 3:
                    status_key = 'verify_error'
                    msg = '短信验证出错'
                #  姓名错误，和身份证错误报错信息相同
                elif retn_code == 6:
                    status_key = 'user_name_error'
                    msg = '姓名错误或身份证错误'
                else:
                    status_key = 'unknown_error'
                    msg = '未知错误'
                self.log('user', msg, resp)
                return 9, status_key
        except:
            msg = traceback.format_exc()
            self.log('crawler', msg, resp)
            return 9, 'json_error'

        check_data = {"accNbr": kwargs['tel'], "billingCycle": self.today_month, "ticketType": "0"}
        check_url = 'http://sd.189.cn/selfservice/bill/queryBillDetailNum'
        code, key, resp = self.post(check_url, data=json.dumps(check_data), headers=self.headers)
        if code != 0:
            return code, key
        try:
            if u'您的用户号码尚未实名制' in resp.text:
                self.log('user', 'real_name_registration_error', resp)
                return 9, 'real_name_registration_error'
            check_json = json.loads(resp.text)
            if check_json['resultMsg'] == '成功':
                return 0, 'success'
            elif check_json['resultMsg'] == '身份信息校验未通过' :
                self.log('website', '身份信息校验未通过', resp)
                return 9, 'website_busy_error'
        except:
            msg = traceback.format_exc()
            self.log('crawler', msg, resp)
            return 9, 'json_error'
        return 0, 'success'

    def crawl_call_log(self, **kwargs):
        crawler_error_num = 0
        missing_list = []
        possibly_missing_list = []
        headers = {
            'Referer': 'http://sd.189.cn/selfservice/bill?tag=monthlyDetail',
            'Origin': 'http://sd.189.cn',
            'X-Requested-With': 'XMLHttpRequest',
        }
        call_log = []
        call_log_url = 'http://sd.189.cn/selfservice/bill/queryBillDetail'
        page_and_retry = []
        for call_month in self.__monthly_period(6, '%Y%m'):
            call_log_data = {"accNbr": kwargs['tel'],
                             "billingCycle": call_month,
                             "pageRecords": "9999",
                             "pageNo": "0",
                             "qtype": "0",
                             "totalPage": "50",
                             "queryType": "6"}
            page_and_retry.append((call_log_data, call_month, self.max_retry))
        st_time = time.time()
        et_time = st_time + 30
        log_for_retry_request = []
        while page_and_retry:
            call_log_data, m_query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            message = "init"
            code, key, resp = self.post(call_log_url, data=json.dumps(call_log_data), headers=headers)
            if code == 0:
                code_a, key, message, call_month_log = self.call_log_get(resp, m_query_month)
                if code_a == 0 and call_month_log:
                    call_log.extend(call_month_log)
                    continue
                if message != 'website_busy_error':
                    crawler_error_num += 1

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((call_log_data, m_query_month, m_retry_times))
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((call_log_data, m_query_month, m_retry_times))
                    time.sleep(rand_sleep)
                else:
                    self.log('website', u'未找到指定数据1{}'.format(message), resp)
                    if code == 0 and code_a == 0 and not call_month_log:
                        possibly_missing_list.append(m_query_month)
                    else:
                        missing_list.append(m_query_month)
            else:
                self.log('website', u'未找到指定数据2{}'.format(message), resp)
                if code == 0 and code_a == 0 and not call_month_log:
                    possibly_missing_list.append(m_query_month)
                else:
                    missing_list.append(m_query_month)

        # print('missing_list:', missing_list)
        # print('possibly_missing_list:', possibly_missing_list)
        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        if len(missing_list + possibly_missing_list) == 6:
            if crawler_error_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success",  call_log, missing_list, possibly_missing_list

    def call_log_get(self, response, call_month):
        """
        | 'month' | string |201708 | 通话月份
        | `call_tel` | string | 18202541892 | 电话号码 |
        | `call_cost` | string | 0.00 | 通话费用 |
        | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
        | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
        | `call_type` | string | 本地 | 通话类型（本地, 长途） |
        | `call_from` | string | 北京市 | 本机通话地 |
        | `call_to` | string | 长沙市 | 对方归属地 |
        | `call_duration` | integer | 300 | 通话时长(秒),
        """
        call_month_log = []
        try:
            if u'服务忙，请稍后再试' in response.text or u'运行异常' in response.text:
                return 9, 'website_busy_error', 'website_busy_error', []
            items = json.loads(response.text)['items']
            for item in items:
                data = {}
                data['month'] = call_month
                data['call_cost'] = item['charge']
                data['call_time'] = self.time_format(item['startTime'])
                data['call_method'] = item['callType']
                if '主叫' in data['call_method']:
                    data['call_tel'] = item['calledNbr']
                else:
                    data['call_tel'] = item['callingNbr']
                data['call_type'] = item['eventType']
                # data['call_from'] =

                raw_call_from = item['position'].strip()
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    data['call_from'] = raw_call_from

                data['call_to'] = ''
                data['call_duration'] = item['duration']
                call_month_log.append(data)
        except:
            error = traceback.format_exc()
            return 9, 'json_error', 'json_error : %s' % error, []
        return 0, 'success', 'success', call_month_log

    # 将通话起始时间转换为时间戳
    def time_format(self, timeoo):
        call_time = re.findall('\d{2}', timeoo)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[
            3] + ' ' + call_time[4] + ':' + call_time[5] + ':' + call_time[6]
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

    def crawl_info(self, **kwargs):
        headers = {
            'Host': 'sd.189.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://sd.189.cn/selfservice/cust/manage',
        }
        url = 'http://sd.189.cn/selfservice/cust/querymanage?100'
        code, key, resp = self.post(url, headers=headers)
        if code != 0:
            return '9', 'request_error', {}

        try:
            json_str = json.loads(resp.text)
            user_info = {}
            dd = json_str['result']['prodRecords']['prodRecord']['custInfo']
            user_info['full_name'] = dd['name']
            user_info['id_card'] = dd['indentNbr']
            user_info['address'] = dd['addr']
            user_info['is_realname_register'] = True
            user_info['open_date'] = ''
        except:
            err = traceback.format_exc()
            self.log('crawler', 'json err:{}'.format(err), resp)
            return 9, 'json_error', {}
        return 0, 'success', user_info

    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        crawler_num = 0
        phone_bill = list()
        headers = {
            'Host': 'sd.189.cn',
            'Origin': 'http://sd.189.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://sd.189.cn/selfservice/bill?tag=custBill',
        }

        month_bill_url = 'http://sd.189.cn/selfservice/bill/queryTwoBill'
        for month in self.__monthly_period(6, '%Y%m'):
            data = {"valueType": "1", "value": kwargs['tel'], "billingCycle": month, "areaCode": "0546",
                    "queryType": "5", "proType": "4"}
            message = 'crawler_error'
            for retry in range(self.max_retry):
                code, key, resp = self.post(url=month_bill_url, data=json.dumps(data), headers=headers)
                if code != 0:
                    continue
                try:
                    month_bill_json = json.loads(resp.text)
                    if not month_bill_json:
                        message = "no_data"
                        continue
                    month_bill = {
                        'bill_month': month,
                        'bill_amount': month_bill_json['total'],
                        'bill_package': '',
                        'bill_ext_calls': '',
                        'bill_ext_data': '',
                        'bill_ext_sms': '',
                        'bill_zengzhifei': '',
                        'bill_daishoufei': '',
                        'bill_qita': ''
                    }
                    bill_json = month_bill_json['items']
                    if len(bill_json) > 0:
                        for item in bill_json:
                            if '套餐费' in item['name']:
                                month_bill['bill_package'] = item['value']
                            elif '通话费' in item['name']:
                                month_bill['bill_ext_calls'] = item['value']
                            elif '短信通信费' in item['name']:
                                month_bill['bill_ext_sms'] = item['value']
                except:
                    message = traceback.format_exc()
                    continue
                phone_bill.append(month_bill)
                break
            else:
                if code == 0:
                    if message != 'no_data':
                        crawler_num += 1
                    self.log('crawler', message, resp)
                    missing_list.append(month)

        # print 'missing_list:', missing_list
        if self.today_month in missing_list:
            missing_list.remove(self.today_month)
        if len(missing_list) == 5:
            if crawler_num > 0:
                return 9, 'crawl_error', [], missing_list
            return 9, 'website_busy_error', [], missing_list
        return 0, 'success', phone_bill, missing_list

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)


if __name__ == '__main__':
    c = Crawler()

    USER_ID = "17763234151"
    # USER_ID = "17763234152"
    USER_PASSWORD = "155153"
    full_name = "孙太凤"
    id_card = "230822199509144679"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD, full_name=full_name, id_card=id_card)
