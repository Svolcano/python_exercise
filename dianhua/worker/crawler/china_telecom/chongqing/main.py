# -*- coding: utf-8 -*-
import base64
import json
import traceback
import datetime
import time
import sys
import re
import random
# 这段代码是用于解决中文报错的问题
import request_params
from datetime import date


reload(sys)
sys.setdefaultencoding("utf8")

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from crawler.china_telecom_tool import login_unity
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_unity

CALL_BACK_URL = "http://222.180.175.36:8182/statistics/gather"

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

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'full_name', 'id_card']

    # 验证名称和身份证
    def verify_name_id(self, **kwargs):
        verify_url = 'http://cq.189.cn/new-bill/bill_SMZ'
        name_data = {
            'tname': kwargs['full_name'].decode('utf-8')[1:],
        }
        code, key, name_response = self.post(url=verify_url, data=name_data)
        if code != 0:
            return code, key
        if '{"sm":"1","xm":"1"}' in name_response.text:
            self.log('crawler', 'user_name_error', name_response)
            return 1, 'user_name_error'
        id_data = {
            'idcard': kwargs['id_card'][-6:],
        }
        code, key, id_card_res = self.post(url=verify_url, data=id_data)
        if code != 0:
            return code, key
        if '{"sm":"2","sfz":"2"}' in id_card_res.text:
            self.log('crawler', 'login_param_error', id_card_res)
            return 9, 'login_param_error'
        return 0, 'success'

    def login(self, **kwargs):

        ProvinceID = '04'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        url = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10004&toStUrl=http://cq.189.cn/new-bill/bill_xd?fastcode=02031273&cityCode=cq'
        code, key, response = self.get(url)
        if code != 0:
            if not isinstance(response, str):
                if response.status_code == 404:
                    key = 'website_busy_error'
            return code, key
        return 0, "success"

    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯个i他誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        user_info_dict = {}
        # 开始请求登记信息
        url = 'http://cq.189.cn/new-account/userInfo?fastcode=02021269&cityCode=cq'
        code, key, response = self.get(url)
        if code != 0:
            return code, key, {}
        try:
            address = re.findall(u'<th>客户地址：</th><td><b>(.*?)</b></td></tr>', response.text)
            name = re.findall(u'<tr><th>客户名称：</th><td><b>(.*?)</b></td>', response.text)
            id_card = re.findall(u'</td><th>证件号码：</th><td><b>(.*?)</b></td></tr>', response.text)
            if address:
                user_info_dict['address'] = address[0]
            else:
                user_info_dict['address'] = ""
            if name:
                user_info_dict['full_name'] = name[0]
            else:
                user_info_dict['full_name'] = ""
            if id_card:
                user_info_dict['id_card'] = id_card[0]
                user_info_dict['is_realname_register'] = True
            else:
                user_info_dict['id_card'] = ""
                user_info_dict['is_realname_register'] = False

            user_info_dict['open_date'] = ""
        except:
            error = traceback.format_exc()
            self.log('crawler', 'request_error : %s' % error, response)
            return 9, "request_error", {}
        return 0, "success", user_info_dict

    def crawl_call_log(self, **kwargs):
        crawler_error_num = 0
        missing_list = []
        possibly_missing_list = []
        code, key = self.verify_name_id(**kwargs)
        if code != 0:
            return 9, 'website_busy_error', [], missing_list, possibly_missing_list

        call_log = []
        header = {
            "Referer": "http://cq.189.cn/new-bill/bill_xd?fastcode=02031273&cityCode=cq",
        }
        search_month = [x for x in range(-0, -6, -1)]
        call_log_url = 'http://cq.189.cn/new-bill/bill_XDCXNR'
        today = date.today()

        page_and_retry = []
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            call_month = "%d%02d" % (query_date.year, query_date.month)
            call_log_data = request_params.call_log_data(each_month, **kwargs)

            page_and_retry.append((call_log_data, call_month, self.max_retry))

        wrong_flag = False

        log_for_retry_request = []
        st_time = time.time()
        et_time = st_time + 20

        while page_and_retry:
            call_log_data, m_call_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_call_month, m_retry_times))
            m_retry_times -= 1

            for retry in xrange(5):
                # 提交表单
                code, key, call_log_req = self.post(call_log_url, data=call_log_data, headers=header)
                if code != 0:
                    wrong_flag = True
                elif u'没有查到您的清单数据' in call_log_req.text or 'http://cq.189.cn/fw/error_404' in call_log_req.text:
                    wrong_flag = False
                else:
                    break
            else:
                if wrong_flag:
                    missing_list.append(m_call_month)
                    continue
                else:
                    self.log('crawler', '未查询到您的详单信息', call_log_req)
                    possibly_missing_list.append(m_call_month)
                    continue
            # 开始查询
            url = 'http://cq.189.cn/new-bill/bill_XDCX_Page'
            data = {
                'page': '1',
                'rows': '9999'
            }
            code, key, call_log_response = self.post(url, data=data)
            if code != 0:
                now_time = time.time()
                if m_retry_times > 0:
                    page_and_retry.append((call_log_data, m_call_month, m_retry_times))
                elif now_time < et_time:
                    page_and_retry.append((call_log_data, m_call_month, m_retry_times))
                    time.sleep(random.randint(3, 5))
                else:
                    missing_list.append(m_call_month)
                    # continue
            # 开始解析详单
            if "cq.189.cn/fw/error_404" in call_log_response.text:
                self.log("website", u"官网异常, 404", call_log_response)
                missing_list.append(m_call_month)
                continue
            key, level, message, call_month_log = self.call_log_get(call_log_response.text, m_call_month)
            if level != 0:
                self.log('crawler', message, call_log_response)
                missing_list.append(m_call_month)
                crawler_error_num += 1
                continue
            call_log.extend(call_month_log)
        self.log("crawler", "重试详情：{}".format(log_for_retry_request), "")
        # print len(call_log), missing_list, possibly_missing_list
        if crawler_error_num > 0:
            return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
        if len(missing_list + possibly_missing_list) == 6:
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def call_log_get(self, response, call_month):
        """
        `call_tel` | string | 18202541892 | 电话号码 |
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
            json_html = json.loads(response)
            if not json_html.has_key('rows'):
                return 'html_error', 9, 'html_error when parse call log', []
            for item in json_html['rows']:
                data = {}
                if u'合计' in item[u'对方号码']:
                    continue
                data['month'] = call_month
                data['call_tel'] = item[u'对方号码']
                data['call_method'] = item[u'呼叫类型']
                call_time = item[u'起始时间']
                data['call_time'] = self.time_format(call_time)
                data['call_duration'] = item[u'通话时长（秒）']
                data['call_type'] = item[u'通话类型']

                raw_call_from = item[u'使用地点'].strip()
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    # self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                    data['call_from'] = raw_call_from
                #
                # data['call_from'] = item[u'使用地点']
                data['call_to'] = ''
                data['call_cost'] = item[u'费用（元）']
                call_month_log.append(data)
        except:
            error = traceback.format_exc()
            return 'json_error', 9, 'json_error : %s' % error, []
        return 'success', 0, 'success', call_month_log

    def time_format(self, timeoo):
        call_time = re.findall('\d{2}', timeoo)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[
            3] + ' ' + call_time[4] + ':' + call_time[5] + ':' + call_time[6]
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        crawler_num = 0
        phone_bill = list()
        month_bill_url = 'http://cq.189.cn/new-bill/bill_ZZDCX'
        for month in self.__monthly_period(6, '%Y-%m'):
            post_data = request_params.month_bill_data(month, **kwargs)
            for retry in range(self.max_retry):
                code, key, response = self.post(month_bill_url, data=post_data)
                if code != 0:
                    pass
                else:
                    break
            else:
                missing_list.append(month.replace('-', ''))
                continue
            level, key, result = self.phone_bill_get(month)
            if level != 0:
                missing_list.append(month.replace('-', ''))
                crawler_num += 1
                continue
            if not result['bill_amount']:
                missing_list.append(month.replace('-', ''))
                continue
            phone_bill.append(result)
        if crawler_num > 0:
            return 9, 'crawl_error', phone_bill, missing_list
        if len(missing_list) == 6:
            return 9, 'website_busy_error', phone_bill, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, 'success', phone_bill, missing_list

    def phone_bill_get(self, month):
        url = "http://cq.189.cn/new-bill/bill_ZDCX"
        data = {
            'page': '1',
            'rows': '20'
        }
        code, key, response = self.post(url, data=data)
        if code != 0:
            return key, code, {}
        try:
            json_html = json.loads(response.text)
            # 套餐外语音通信费分为两部份，  移动国内拨打国内通话 和 手机国内漫游费
            bill_ext_calls1 = bill_ext_calls2 = 0
            bill_ext_data = ''
            bill_ext_sms = ''
            bill_package = ''

            if json_html['total'] != 0:
                for item in json_html['rows']:
                    if item['billItem'] == u'合计':
                        bill_amount = item['billAmount']
                    elif item['billItem'] == u'乐享套餐费':
                        bill_package = item['billAmount']
                    elif item['billItem'] == u'短信通信费':
                        bill_ext_sms = item['billAmount']
                    elif item['billItem'] == u'移动国内拨打国内通话':
                        bill_ext_calls1 = item['billAmount']
                    elif item['billItem'] == u'手机国内漫游费':
                        bill_ext_calls2 = item['billAmount']
                    elif item['billItem'] == u'手机数据费':
                        bill_ext_data = item['billAmount']
            else:
                bill_amount = ''
                bill_package = ''

            month_bill = {
                'bill_month': month.replace('-', ''),
                'bill_amount': bill_amount,
                'bill_package': bill_package,
                'bill_ext_calls': str(float(bill_ext_calls1)+float(bill_ext_calls2)),
                'bill_ext_data': bill_ext_data,
                'bill_ext_sms': bill_ext_sms,
                'bill_zengzhifei': '',
                'bill_daishoufei': '',
                'bill_qita': ''
            }

        except:
            error = traceback.format_exc()
            self.log('crawler', 'unknown_error :%s' % error, response)
            return 9, 'unknown_error', {}
        return 0, 'success', month_bill

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)


if __name__ == '__main__':
    c = Crawler()

    USER_ID = "17318495610"
    USER_PASSWORD = "909128"
    full_name = "王梦思"
    id_card = "411081199102158009"
    #  158009
    #  梦思

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD, full_name=full_name, id_card=id_card)
