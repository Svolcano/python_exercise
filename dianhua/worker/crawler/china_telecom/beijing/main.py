# -*- coding: utf-8 -*-

import random
import hashlib
import base64
import json
import urllib
import traceback
import sys
import time
import calendar
import re
# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")

from datetime import date
import datetime
from lxml import etree
from dateutil.relativedelta import relativedelta


if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
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
        # return ['pin_pwd', 'captcha_verify']
        return ['pin_pwd']

    def get_verify_type(self, **kwargs):
        return ''

    def login(self, **kwargs):
        ProvinceID = '01'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        """
        手动重定向至北京电信URL：
        """
        cookie_url = "http://www.189.cn/login/sso/ecs.do?method=linkTo&platNo=10001&toStUrl=http://bj.189.cn/iframe/feequery/detailBillIndex.action"
        code, key, resp = self.get(cookie_url)
        if code != 0:
            return code, key
        return 0, "success"


    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        send_sms_url = "http://bj.189.cn/iframe/feequery/smsRandCodeSend.action"
        send_sms_data = {
            'accNum': kwargs['tel']
        }
        header = {'Referer': 'http://bj.189.cn/iframe/feequery/detailBillIndex.action?fastcode=01390638&cityCode=bj'}
        code, key, resp = self.post(send_sms_url, data=send_sms_data, headers=header)
        if code != 0:
            return code, key, ''
        if 'SRandomCode' in resp.text:
            try:
                send_sms_res = json.loads(resp.text)
            except:
                error = traceback.format_exc()
                message = 'json_error :%s' % error
                self.log('crawler', message, resp)
                return 9, "json_error",  ""
            self.sms_code = send_sms_res['SRandomCode']
            # print self.sms_code
            if send_sms_res['tip'] == u'对不起，当日使用随机短信次数过多。无法继续发送。':
                self.log('crawler', 'over_max_sms_error', resp)
                return 9, "over_max_sms_error",  ""
            return 0, "success",  ""
        elif u'查询失败' in resp.text:
            self.log('crawler', 'request_error', resp)
            return 9, "request_error", ""
        else:
            self.log('crawler', 'unknown_error', resp)
            return 9, "unknown_error",  ""


    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        check_sms_url = "http://bj.189.cn/iframe/feequery/detailValidCode.action"
        check_sms_data = {
            "requestFlag": 'asynchronism',
            "accNum": kwargs['tel'],
            "sRandomCode": self.sms_code
        }
        code, key, resp = self.post(check_sms_url, data=check_sms_data)
        if code != 0:
            return code, key
        try:
            check_sms_res = json.loads(resp.text)
        except:
            error = traceback.format_exc()
            message = 'json_error : %s' % error
            self.log('crawler', message, resp)
            return 9, "json_error"
        if check_sms_res['ILoginType'] == 4 and check_sms_res['billDetailValidate'] == "true":
            return 0, "success"
        elif check_sms_res['tip'] == u"随机短信码错误":
            self.log('crawler', 'verify_error', resp)
            return 2, "verify_error"
        elif check_sms_res['billDetailValidate'] == -1:
            self.log('crawler', 'user_exit', resp)
            return 9, "user_exit"
        else:
            self.log('crawler', 'crawl_error', resp)
            return 9, "crawl_error"


    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        change_info_url = "http://bj.189.cn/iframe/custservice/modifyUserInfo.action?fastcode=10000181&cityCode=bj"
        headers = {
            "Referer": "http://www.189.cn/dqmh/my189/initMy189home.do",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }
        code, key, resp = self.get(change_info_url, headers=headers)
        if code != 0:
            return code, key, {}
        full_name = ""
        open_date = ""
        try:
            et = etree.HTML(resp.text)
            info_list = et.xpath("//td[@class='tl']/text()")
            full_name = info_list[0]
            open_date = info_list[-1]
            time_type = time.strptime(open_date, "%Y-%m-%d %H:%M:%S")
            open_date = str(int(time.mktime(time_type)))
        except:
            error = traceback.format_exc()
            self.log("crawler", 'html_error{}'.format(error), resp)
            return 9, 'html_error', {}
        user_info = {}
        info_url = 'http://www.189.cn/dqmh/userCenter/userInfo.do?method=editUserInfo_new&fastcode=&cityCode=bj'
        code, key, resp = self.get(info_url)
        if code != 0:
            return code, key, {}
        try:
            selector = etree.HTML(resp.text)
            user_info['full_name'] = full_name
            user_info['open_date'] = open_date
            if '<option selected="selected" value="1">身份证</option>' in resp.text.encode('utf8'):
                id_card = selector.xpath('//input[@name="certificateNumber"]/@value')
                user_info['id_card'] = id_card[0] if id_card else ''
            else:
                user_info['id_card'] = ''
            address = selector.xpath('//*[@id="address"]/text()')
            user_info['address'] = address[0] if address else ''
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error :%s' % error, resp)
            return 9, 'html_error', {}
        return 0, "success", user_info

    def time_stamp(self,old_time):
        temp_month = re.findall('-(\d)-', old_time)
        if temp_month:
            old_time = re.sub('-\d-', '0' + temp_month[0] + '-', old_time)
        temp_day = re.findall('-(\d)\s', old_time)
        if temp_day:
            old_time = re.sub('-\d\s', '0' + temp_day[0], old_time)
        call_time = re.findall('\d{2}', old_time)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + call_time[
            4] + ':' + call_time[5] + ':' + call_time[6]
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

    def random_sleep(self, tm, page=1, modulus=3):
        time.sleep(random.uniform(tm / page / modulus / 1.5, 1.5 * tm / page / modulus))

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
        part_missing_list = []
        crawler_list = 0
        call_log = []
        call_log_url = "http://bj.189.cn/iframe/feequery/billDetailQuery.action"
        today = date.today()
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            call_month = "%d%02d" % (query_date.year,query_date.month)
            query_month = '%d年%02d月'%(query_date.year,query_date.month)
            endDate = calendar.monthrange(query_date.year, query_date.month)[1]
            call_log_data ={
                "requestFlag": 'synchronization',
                "billDetailType": 1,
                "qryMonth": query_month,
                "startTime":'1',
                "accNum":kwargs['tel'],
                "endTime":str(endDate),
            }
            start_time = time.time()
            end_time = start_time + 12
            aid_time_dict = dict()
            retry_times = self.max_retry
            log_for_retry = []
            while 1:
                log_for_retry.append((1, retry_times))
                retry_times -= 1
                code, key, resp = self.post(call_log_url, data=call_log_data)
                if code:
                    missing_flag = True
                elif u'该号码资料不存在' in resp.text:
                    self.log('user', 'user_prohibited_error', resp)
                    return 9, 'user_prohibited_error', [], [], []
                elif u'尊敬的用户，您好，随机密码登录用户 无权限访问此功能' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
                elif u'用户设置了详单禁查!' in resp.text:
                    self.log('user', 'user_prohibited_error', resp)
                    return 9, 'user_prohibited_error', [], [], []
                elif u'抱歉！查询失败，请稍后重试' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    missing_flag = True
                elif u"未查询到该帐期详单!" in resp.text or u'未查询到您的详单信息' in resp.text:
                    missing_flag = False
                elif u"系统正忙" in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    missing_flag = True
                elif u'调用后台详单查询方法出错!' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    missing_flag = True
                else:
                    flag = True
                    break
                now_time = time.time()
                if retry_times >= 0:
                    aid_time_dict.update({retry_times: time.time()})
                elif now_time < end_time:
                    loop_time = aid_time_dict.get(0, time.time())
                    left_time = end_time - loop_time
                    self.random_sleep(left_time)
                else:
                    flag = False
                    if missing_flag:
                        missing_list.append(call_month)
                    else:
                        possibly_missing_list.append(call_month)
                    break
            if not flag:
                self.log('crawler', '{}重试记录{}'.format(call_month, log_for_retry), '')
                continue
            # for retry in xrange(self.max_retry):
            #     code, key, resp = self.post(call_log_url, data=call_log_data)
            #     if code != 0:
            #         missing_flag = True
            #     elif u"未查询到该帐期详单" in resp.text or u'未查询到您的详单信息' in resp.text:
            #         missing_flag = False
            #     elif u"系统正忙" in resp.text:
            #         missing_flag = True
            #     else:
            #         break
            # else:
            #     if missing_flag:
            #         missing_list.append(call_month)
            #     else:
            #         self.log('crawler', '未查询到您的详单信息', resp)
            #         possibly_missing_list.append(call_month)
            #     continue
            # if u'该号码资料不存在' in resp.text:
            #     self.log('user', 'user_prohibited_error', resp)
            #     return 9, 'user_prohibited_error', [], [], []
            # if u'尊敬的用户，您好，随机密码登录用户 无权限访问此功能' in resp.text:
            #     self.log('website', 'website_busy_error', resp)
            #     return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
            # if u'抱歉！查询失败，请稍后重试' in resp.text:
            #     self.log('website', 'website_busy_error', resp)
            #     missing_list.append(call_month)
            #     continue
            # if u'用户设置了详单禁查!' in resp.text:
            #     self.log('user', 'user_prohibited_error', resp)
            #     return 9, 'user_prohibited_error', [], [], []
            # # with open(call_month, 'w')as f:
            # #     f.write(resp.text)
            key, level, message, data, page_num = self.call_log_get(resp.text, call_month)
            if level != 0:
                self.log('crawler',  message, resp)
                if data:
                    part_missing_list.append(call_month)
                    call_log.extend(data)
                else:
                    missing_list.append(call_month)
                crawler_list += 1
                self.log('crawler', '{}重试记录{}'.format(call_month, log_for_retry), '')
                continue
            call_log.extend(data)
            if page_num <= 1:
                self.log('crawler', '{}重试记录{}'.format(call_month, log_for_retry), '')
                continue

            page_list = list(range(2, page_num + 1))
            page_and_retry = [(page, self.max_retry) for page in page_list]
            while page_and_retry:
                page, retry_times = page_and_retry.pop(0)
                log_for_retry.append((page, retry_times))
                retry_times -= 1
                call_log_data['billPage'] = page
                code, key, resp = self.post(call_log_url, data=call_log_data)
                if not code:
                    key, level, message, data, page = self.call_log_get(resp.text, call_month)
                    if not level:
                        call_log.extend(data)
                        continue
                    else:
                        crawler_list += 1
                        self.log('crawler', message, resp)
                        part_missing_list.append(call_month) if call_month not in part_missing_list else None
                        if data:
                            call_log.extend(data)
                        continue
                now_time = time.time()
                if retry_times >= 0:
                    page_and_retry.append((page, retry_times))
                    aid_time_dict.update({retry_times: time.time()})
                elif now_time < end_time:
                    page_and_retry.append((page, retry_times))
                    loop_time = aid_time_dict.get(0, time.time())
                    left_time = end_time - loop_time
                    self.random_sleep(left_time, len(page_and_retry))
                else:
                    part_missing_list.append(call_month) if call_month not in part_missing_list else None
            self.log('crawler', '{}重试记录{}'.format(call_month, log_for_retry), '')
        self.log("crawler", "缺失: {}, 可能缺失: {}, 部分缺失: {}".format(missing_list, possibly_missing_list, part_missing_list), "")

        if len(missing_list + possibly_missing_list) == 6:
            if crawler_list > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list, part_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list, part_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list, part_missing_list

    def call_log_get(self, resp, call_month):
        """
        | `update_time` | string | 更新时间戳 |
        | `call_cost` | string | 爬取费用 |
        | `call_time` | string | 通话起始时间 |
        | `call_method` | string | 呼叫类型（主叫, 被叫） |
        | `call_type` | string | 通话类型（本地, 长途）  |
        | `call_from` | string | 本机通话地 |
        | `call_to` | string | 对方归属地 |
        | `call_duration` | string | 通话时长 |
        """
        page_number = 0
        records = []
        try:
            selector = etree.HTML(resp.decode('utf-8'))
            call_form = selector.xpath('//table[@class="ued-table"]/tr')
            if not call_form:
                return 'html_error', 9, 'html_error', records, page_number
            for item in call_form[1:-2]:
                data = {}
                data['month'] = call_month
                data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                data['call_cost'] = item.xpath('.//td[10]/text()')[0]
                # 以下几行转换成时间戳
                call_time = re.findall('\d{2}', item.xpath('.//td[6]/text()')[0])
                call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + \
                                   call_time[4] + ':' + call_time[5] + ':' + call_time[6]
                timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
                call_time_timeStamp = str(int(time.mktime(timeArray)))

                data['call_time'] = call_time_timeStamp
                data['call_method'] = item.xpath('.//td[2]/text()')[0]
                data['call_type'] = item.xpath('.//td[3]/text()')[0]

                raw_call_from = item.xpath('.//td[4]/text()')[0].strip()
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    data['call_from'] = raw_call_from
                data['call_to'] = ''
                call_tel = item.xpath('.//td[5]/text()')
                #如果没有对方号码， 不要这条记录
                if not call_tel:
                    continue
                data['call_tel'] = call_tel[0]
                data['call_duration'] = item.xpath('.//td[9]/text()')[0]
                records.append(data)
            # 请求页数
            page = re.findall(u'<a href="javascript:page(.*?)">尾页</a>', resp)
            if len(page) > 0:
                page_number = int(page[0].replace('(', '').replace(')', ''))
        except:
            error = traceback.format_exc()
            return 'html_error', 9, 'html_error : %s' % error, records, page_number
        return 'success', 0, 'success', records, page_number


    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        month_bill_url = 'http://bj.189.cn/iframe/feequery/billInfoQuery.action'
        phone_bill = list()
        for month in self.__monthly_period(6, '%Y%m'):
            params = {
                'accNum': kwargs['tel'],
                'billCycle': month,
                'billReqType': '3'
            }
            for retry in range(self.max_retry):
                code, key, resp = self.get(month_bill_url, params=params)
                if code != 0:
                    pass
                else:
                    break
            else:
                missing_list.append(month)
                continue
            #子函数中用的是findall函数，  不用加异常处理
            code, key, result = self.phone_bill_get(resp, month)
            if result['bill_amount'] == '0.00':
                missing_list.append(month)
                continue
            phone_bill.append(result)
        if len(missing_list) == 6:
            return 9, 'website_busy_error', phone_bill, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, 'success', phone_bill, missing_list



    def phone_bill_get(self, resp, month):
        month_bill = {
            'bill_month': month,
            'bill_amount': '0.00',
            'bill_package': '',
            'bill_ext_calls': '',
            'bill_ext_data': '',
            'bill_ext_sms': '',
            'bill_zengzhifei': '',
            'bill_daishoufei': '',
            'bill_qita': ''
        }
        bill_amounts = re.findall(u'本期费用合计：([\d.]+)元',resp.text)
        if bill_amounts:
            month_bill['bill_amount'] = bill_amounts[0]
        bill_package = re.findall(u'主套餐基本费.*?([\d.]+)</td>', resp.text)
        if bill_package:
            month_bill['bill_package'] = bill_package[0]
        bill_ext_calls = re.findall(u'本地通话费.*?([\d.]+)</td>', resp.text)
        if bill_ext_calls:
            month_bill['bill_ext_calls'] = bill_ext_calls[0]
        bill_ext_data = re.findall(u'本地上网使用费.*?([\d.]+)</td>', resp.text)
        if bill_ext_data:
            month_bill['bill_ext_data'] = bill_ext_data[0]
        bill_ext_sms = re.findall(u'短信通信费.*?([\d.]+)</td>', resp.text)
        if bill_ext_sms:
            month_bill['bill_ext_sms'] = bill_ext_sms[0]

        return 0, 'success', month_bill

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset+1)).strftime(strf)

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17701020875"
    USER_PASSWORD = "578020"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
