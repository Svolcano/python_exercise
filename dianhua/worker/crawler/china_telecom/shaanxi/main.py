# -*- coding: utf-8 -*-
import re
import hashlib
import base64
import traceback
import sys
import time
import datetime
import password
import random

# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")
from lxml import etree
from Crypto.Cipher import AES
from datetime import date
from scrapy.selector import Selector
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
        return ['full_name', 'id_card', 'pin_pwd',
                'sms_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        ProvinceID = '27'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        cookie_url = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10027&toStUrl=http://sn.189.cn/service/bill/fee.action?type=ticket&fastcode=10000202&cityCode=sn"
        for each in range(3):
            code, key, cookie_req = self.get(cookie_url)
            if code != 0:
                pass
            else:
                break
        else:
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
        send_sms_url = "http://sn.189.cn/service/bill/sendValidReq.action"
        send_sms_data = {
            "mobileNum": "{}".format(kwargs['tel']),
            'listType': '102',
        }

        header = {'Referer': 'http://sn.189.cn/service/bill/fee.action?type=bill&fastcode=10000199&cityCode=sn'}
        code, key, resp = self.post(send_sms_url, data=send_sms_data, headers=header)
        if code != 0:
            return code, key, ''
        try:
            resp_json_response = resp.json()
        except:
            error = traceback.format_exc()
            if u'欢迎登录' in resp.text or u'action="/kdts/toOrder.action"' in resp.text:
                self.log('website', "website_busy_error : %s" % error, resp)
                return 9, "website_busy_error", ''
            self.log('crawler', 'json_error : %s' % error, resp)
            return 9, 'json_error', ''

        if resp_json_response.get('success',''):
            return 0, "success", ""
        else:
            self.log('crawler', "send_sms_error", resp)
            return 9, "send_sms_error", ""

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        check_sms_url = "http://sn.189.cn/service/shopChange/checkAuthByLevel.action"
        try:
            check_sms_data ={
                "certiNbr": base64.b64encode(kwargs['id_card']).replace("+", " ").replace("CR", "C  R").replace("LF", "L   F"),
                "certiName": base64.b64encode(kwargs['full_name']).replace("+", " ").replace("CR", "C  R").replace("LF", "L   F"),
                'serviceNbr': password.pwd.call('strEnc',kwargs['tel'],'3','2','1'),
                'msgCode': password.pwd.call('strEnc',kwargs['sms_code'],'3','2','1'),
                'certiType': '1',
                'checkLevel':'1',
                'latnId':'290',
                'prodType':'4',
                'radomIdSessionId':'undefined',
            }
        except:
            error = traceback.format_exc()
            self.log('crawler', 'crawl_error : %s' % error, '')
            return 9, 'crawl_error'
        code, key, resp = self.post(check_sms_url, data=check_sms_data)
        if code != 0:
            return code, key
        try:
            resp_json_response = resp.json()
        except:
            error = traceback.format_exc()
            if u'欢迎登录' in resp.text:
                self.log('website', 'website_busy_error : %s' % error, resp)
                return 9, "website_busy_error"
            if u'起始时间' in resp.text or u'费用合计' in resp.text:
                return 0, "success"
            self.log('crawler', 'json_error : %s' % error, resp)
            return 9, 'json_error'
        if resp_json_response.get('returnCd', '') == '1':
            return 0, "success"
        elif u'请输入用户姓名' in resp_json_response.get('returnDesc', '') or u'姓名不一致' in resp_json_response.get('returnDesc', ''):
            self.log('user', 'user_name_error', resp)
            return 2, "user_name_error"
        elif u'请输入证件号码' in resp_json_response.get('returnDesc', '') or u'证件号码不一致' in resp_json_response.get('returnDesc', '') or u'证件类型不一致' in resp_json_response.get('returnDesc', ''):
            self.log('user', 'user_id_error', resp)
            return 2, "user_id_error"
        elif u'输入的随机码错误' in resp_json_response.get('returnDesc', ''):
            self.log('user', 'verify_error', resp)
            return 2, "verify_error"
        elif u'客户信息为空' in resp_json_response.get('returnDesc', ''):
            self.log('user', 'success', resp)
            return 0, "success"
        else:
            self.log('crawler', 'unknown_error', resp)
            return 9, "unknown_error"

    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        user_info = {}
        personal_info_url = "http://www.189.cn/dqmh/userCenter/userInfo.do?"
        personal_info_data = {
            'method': 'editUserInfo_new',
            'fastcode': '',
            'cityCode': 'sn'
        }
        code, key, resp = self.get(personal_info_url, params=personal_info_data)
        if code != 0:
            return code, key, user_info
        try:
            selector = Selector(text=resp.text)
            full_name = selector.xpath('//input[@name="realName"]/@value').extract()
            user_info['full_name'] = full_name[0] if full_name else ''
            user_info['open_date'] = ''
            id_card = selector.xpath('//input[@name="certificateNumber"]/@value').extract()
            user_info['id_card'] = id_card[0] if id_card else ''
            address = re.findall(u'id="address".*?>(.*?)</textarea>',resp.text)
            user_info['address'] = address[0] if address else ''
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error : %s' % error, resp)
            return 9, 'html_error', user_info
        return 0, "success", user_info

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
        crawl_num = 0
        pos_missing = []
        call_log = []
        call_log_url = 'http://sn.189.cn/service/bill/feeDetailrecordList.action'
        today = date.today()
        search_month = [x for x in range(0, -6, -1)]
        search_month_retry = [(x, self.max_retry) for x in search_month]
        st_time = time.time()
        rand_time = random.randint(23, 45) / 10.0
        full_time = 50.0
        time_fee = 0
        retrys_limit = -4
        log_for_retrys = []
        while search_month_retry:
            each_month, retrys = search_month_retry.pop(0)
            retrys -= 1

            if each_month == 0:
                query_date = today + relativedelta(months=each_month)
            else:
                query_date = today + relativedelta(months=each_month, day=31)
            call_log_data = {
                "effDate": "{}-{}-01".format(query_date.year,str(query_date.month).zfill(2)),
                "expDate": "{}-{}-{}".format(query_date.year,str(query_date.month).zfill(2),str(query_date.day).zfill(2)),
                'serviceNbr': kwargs['tel'],
                'operListID': '1',
                'isPrepay': '0',
                'pOffrType': '481',
                'pageSize': '9999',
                'currentPage': '1'
            }
            search_month = "%d%02d" % (query_date.year, query_date.month)
            if retrys < retrys_limit:
                self.log("crawler", "重试完毕{}".format(search_month), "")
                missing_list.append(search_month)
                continue
            log_for_retrys.append((search_month, retrys, time_fee))
            code, key, resp = self.post(call_log_url, data=call_log_data)
            if code != 0:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    search_month_retry.append((each_month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    search_month_retry.append((each_month, retrys))
                else:
                    self.log("crawler", "全部重试完毕", "")
                    missing_list.append(search_month)
                continue
            elif u'无话单记录' in resp.text:
                self.log('crawler', '未查询到您的详单信息', resp)
                pos_missing.append(search_month)
                continue
            # with open(search_month+'.py', 'w')as f:
            #     f.write(resp.text)
            try:
                selector = Selector(text=resp.text)
                if selector.xpath('//input[@id="totalRow"]/./@value'):
                    # total_row = int(selector.xpath('//input[@id="totalRow"]/./@value').extract()[0])
                    status_key, status_level, message, data = self.call_log_get(resp.text, search_month)
                    if status_level != 0:
                        if retrys >= 0:
                            time_fee = time.time() - st_time
                            search_month_retry.append((each_month, retrys))
                        elif time_fee < full_time:
                            time.sleep(rand_time)
                            time_fee = time.time() - st_time
                            search_month_retry.append((each_month, retrys))
                        else:
                            self.log("crawler", "全部重试完毕", "")
                            missing_list.append(search_month)
                        continue
                    else:
                        call_log.extend(data)
                        continue
                else:
                    self.log('crawler', 'html_error', resp)
                    pos_missing.append(search_month)
                    continue
                # if total_row > 10:
                #     for page in range(2,(total_row/10+2)):
                #         call_log_data['currentPage'] = page
                #         code, key, resp = self.post(call_log_url, data=call_log_data)
                #         if code != 0:
                #             missing_list.append(search_month)
                #             break
                #         if Selector(text=resp.text).xpath('//input[@id="totalRow"]/./@value'):
                #             status_key,status_level,message, data = self.call_log_get(resp.text, search_month)
                #             if status_level != 0:
                #                 self.log('crawler', message, resp)
                #                 missing_list.append(search_month)
                #                 crawl_num += 1
                #                 break
                #             else:
                #                 call_log.extend(data)
                #         else:
                #             continue
            except:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    search_month_retry.append((each_month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    search_month_retry.append((each_month, retrys))
                else:
                    error = traceback.format_exc()
                    self.log('crawler', 'html_error : %s' % error, resp)
                    missing_list.append(search_month)
                    crawl_num += 1
                continue
        missing_list.sort(reverse=True)
        pos_missing.sort(reverse=True)
        self.log("crawler", "重试记录; {}".format(log_for_retrys), "")
        if crawl_num > 0:
            return 9, 'crawl_error', call_log, missing_list, pos_missing
        if len(pos_missing+missing_list) == 6:
            return 9, 'website_busy_error', call_log, missing_list, pos_missing
        return 0, "success", call_log, missing_list, pos_missing


    def call_log_get(self, response, search_month):
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
        selector = etree.HTML(response)
        records = []
        for item in selector.xpath('//tr')[1:]:
            data = {}
            try:
                data['month'] = search_month
                data['call_cost'] = str(item.xpath('./td[8]/text()')[0]) if item.xpath('./td[8]/text()') else ""
                # 以下几行为了转换成秒
                call_time_raw = item.xpath('./td[2]/text()')
                if call_time_raw:
                    call_time = re.findall('\d{2}', item.xpath('./td[2]/text()')[0])
                    call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + \
                                       call_time[4] + ':' + call_time[5] + ':' + call_time[6]
                    timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
                    call_time_timeStamp = str(int(time.mktime(timeArray)))
                else:
                    call_time_timeStamp = ""
                data['call_time'] = call_time_timeStamp
                data['call_method'] = item.xpath('./td[4]/text()')[0] if item.xpath('./td[4]/text()') else ""
                data['call_type'] = item.xpath('./td[7]/text()')[0] if item.xpath('./td[7]/text()') else ""

                raw_call_from = item.xpath('./td[3]/text()')[0] if item.xpath('./td[3]/text()') else ""
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                    data['call_from'] = raw_call_from

                data['call_to'] = ''
                data['call_tel'] = str(item.xpath('./td[5]/text()')[0]) if item.xpath('./td[5]/text()') else ""
                call_duration_raw = item.xpath('./td[6]/text()')
                if call_duration_raw:
                    data['call_duration'] = self.time_format(str(item.xpath('./td[6]/text()')[0]))
                else:
                    data['call_duration'] = ""
                records.append(data)
            except:
                error = traceback.format_exc()
                return 'html_error', 9, 'html_error : %s' % error, []
        return 'success', 0, 'success get call_log', records

    def time_format(self, time_str):
        h, m, s = map(int, time_str.split(":"))
        ss = h * 3600 + m * 60 + s
        return str(ss)


    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        phone_bill = list()
        params = {
            'tel': kwargs['tel']
        }
        for month in self.__monthly_period(6, '%Y%m'):
            params['month'] = month
            for retry in xrange(self.max_retry):
                key, level, message, result = self.crawl_month_bill(**params)
                if level != 0 or result['bill_amount'] == '' or result['bill_amount'] == '0.00':
                    continue
                else:
                    break
            else:
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

    def crawl_month_bill(self,**kwargs):
        month_bill_url = 'http://sn.189.cn/service/bill/billDetail.action'
        params = {
            'accnbr': kwargs['tel'],
            'month': kwargs['month'],
            'billtype': '1',
            'productid': '41010300',
            'areacode': '290'
        }
        code, key, resp = self.get(month_bill_url, params=params)
        if code != 0:
            return key, code, u'请求失败', {}

        month_bill = {
            'bill_month': kwargs['month'],
            'bill_amount': '',
            'bill_package': '',
            'bill_ext_calls': '',
            'bill_ext_data': '',
            'bill_ext_sms': '',
            'bill_zengzhifei': '',
            'bill_daishoufei': '',
            'bill_qita': ''
        }
        try:
            et = etree.HTML(resp.text)
            er = et.xpath("//tr[@name='classfiy1']")
            for i in er:
                name = i.xpath("td[@align='left']/text()")[0].strip()
                fe = i.xpath("td[@align='right'][3]/text()")[0]
                if u'套餐' in name:
                    month_bill['bill_package'] = fe
                elif u'短信' in name:
                    month_bill['bill_ext_sms'] = fe
                elif u'通话' in name:
                    month_bill['bill_ext_calls'] = fe
        except:
            err_msg = traceback.format_exc()
            self.log('website', err_msg, resp)
            return 'website_busy_error', 9, 'website_busy_error', month_bill
        bill_amounts = re.findall(kwargs['tel'] + u'.*?合计:(\d*?\.\d{1})', resp.text, re.S)
        if bill_amounts:
            month_bill['bill_amount'] = bill_amounts[0]
        return 'success', 0, 'success', month_bill

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset+1)).strftime(strf)

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "18092805191"
    USER_PASSWORD = "191508"
    FULL_NAME = u'白兆鹏'
    ID_CARD = '610402197711040317'

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD,full_name=FULL_NAME,id_card=ID_CARD)

