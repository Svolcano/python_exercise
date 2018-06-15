# -*- coding: utf-8 -*-
import re
import hashlib
import base64
import json
import traceback
import sys
import time
import datetime
import random
# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")

from datetime import date
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
        return ['pin_pwd','sms_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        ProvinceID = '23'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        """
        手动重定向至四川电信URL：
        """
        cookie_url = "http://www.189.cn/login/sso/ecs.do?method=linkTo&platNo=10023&toStUrl=http://sc.189.cn/service/accounthome/index.jsp?fastcode=20000511&cityCode=sc"
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
        today = date.today()
        send_sms_url = "http://sc.189.cn/service/billDetail/sendSMSAjax.jsp?"
        send_sms_data = {
            "dateTime1": "{}-{}-01".format(today.year,str(today.month).zfill(2)),
            "dateTime2": "{}-{}-{}".format(today.year,str(today.month).zfill(2),str(today.day).zfill(2)),
        }
        header = {'Referer': 'http://sc.189.cn/service/v6/xdcx?fastcode=20000326&cityCode=sc'}
        code, key, resp = self.get(send_sms_url, params=send_sms_data, headers=header)
        if code != 0:
            return code, key, ''
        try:
            resp_json_response = resp.json()
        except:
            error = traceback.format_exc()
            self.log('crawler', 'json_error : {}'.format(error), resp)
            return 9, 'json_error', ''
        if resp_json_response.get('retCode','') == 'S' or resp_json_response.get('retCode','') == '0':
            return 0, "success", ""
        elif resp_json_response.get('retCode','') == '21':
            self.log('crawler', 'send_sms_error', resp)
            return 9, "send_sms_error",  ""
        elif resp_json_response.get('retCode','') == '-2':
            self.log('website', 'website_busy_error', resp)
            return 9, "website_busy_error", ""
        else:
            self.log('crawler', 'send_sms_error', resp)
            return 9, "send_sms_error", ""

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        today = date.today()
        self.encrypt_sms = base64.b64encode(kwargs['sms_code'])
        check_sms_url = "http://sc.189.cn/service/billDetail/detailQuery.jsp"
        check_sms_data = {
            "startTime": "{}-{}-01".format(today.year,str(today.month).zfill(2)),
            "endTime": "{}-{}-{}".format(today.year,str(today.month).zfill(2),str(today.day).zfill(2)),
            'qryType':'21',
            'randomCode':self.encrypt_sms,
        }
        for retry in xrange(self.max_retry):
            code, key, resp = self.get(check_sms_url, params=check_sms_data)
            if code != 0:
                return code, key
            try:
                resp_josn_response = json.loads(resp.text)
            except:
                error = traceback.format_exc()
                self.log('crawler', 'json_error : %s' % error, resp)
                return 9, 'json_error'
            if 'sessNum' not in resp_josn_response.keys():
                continue
            else:
                break
        else:
            self.log('crawler', 'html_error', resp)
            return 9, "website_busy_error"
        if resp_josn_response['sessNum'] != "true":
            self.log('crawler', 'login_param_error', resp)
            return 9, "verify_error"
        return 0, "success"

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
        personal_info_url = "http://sc.189.cn/service/v6/wdzl"
        personal_info_data = {
            "fastcode": "20000547",
            "cityCode": 'sc'
        }
        code, key, resp = self.get(personal_info_url,params=personal_info_data)
        if code != 0:
            return code, key, {}
        try:
            user_info['full_name'] = re.search(u'用户名 :</p>[\s\S]*?<span>([\s\S]*?)</span>',resp.text).group(1)
        except:
            user_info['full_name'] = ""
        try:
            user_info['open_date'] = re.search(u'安装日期 :</p>[\s\S]*?<span>([\s\S]*?)</span>',resp.text).group(1)
        except:
            user_info['open_date'] = ""
        if user_info['open_date']:
            user_info['open_date'] = self.time_format(user_info['open_date'])
        user_info['id_card'] = ''
        address = re.findall(u'安装地址 :</p>\s+<span>(.*?)</span>',resp.text)
        user_info['address'] = address[0] if address else ''
        user_info['is_realname_register'] = True
        return 0, "success", user_info

    def time_format(self,timeoo):
        call_time = re.findall('\d{2}', timeoo)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[
            3] + ' ' + '00' + ':' + '00' + ':' + '00'
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp


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
        pos_missing = []
        crawl_num = 0
        call_log = []
        call_log_url = "http://sc.189.cn/service/billDetail/detailQuery.jsp"
        today = date.today()
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            if each_month == 0:
                query_date = today + relativedelta(months=each_month)
            else:
                query_date = today + relativedelta(months=each_month, day=31)
            query_month = "%d%02d" % (query_date.year,query_date.month)
            call_log_data = {
                "startTime": "{}-{}-01".format(query_date.year,str(query_date.month).zfill(2)),
                "endTime": "{}-{}-{}".format(query_date.year,str(query_date.month).zfill(2),str(query_date.day).zfill(2)),
                'qryType': '21',
                'randomCode': self.encrypt_sms
            }
            missing_flag = False

            st_time = time.time()
            et_time = st_time + 12

            retry_times = 5
            for retry in range(retry_times):
                retry_times -= 1
                code, key, resp = self.post(call_log_url, data=call_log_data)
                if code != 0:
                    now_time = time.time()
                    if retry_times >= 3:
                        continue
                    elif now_time < et_time:
                        time.sleep(random.randint(4,5))
                    missing_flag = True
                # did not 查询到相应记录
                elif '2024' in resp.text or '2025' in resp.text:
                    missing_flag = False
                else:
                    break
            else:
                if missing_flag:
                    missing_list.append(query_month)
                else:
                    self.log('crawler', '未查询到您的详单信息', resp)
                    pos_missing.append(query_month)
                continue
            if '证件号码输入有误' in resp.text:
                self.log('crawler', 'user_id_error', resp)
                missing_list.append(query_month)
                continue
            try:
                json_logs = json.loads(resp.text)
            except:
                error = traceback.format_exc()
                self.log('crawler', 'json_error : %s' % error, resp)
                missing_list.append(query_month)
                continue
            if json_logs.get('retCode', '') == '0':
                key, level, message, log_data = self.call_log_get(resp.text, query_month)
                if level != 0:
                    self.log('crawler', message, resp)
                    missing_list.append(query_month)
                    crawl_num += 1
                    continue
                else:
                    call_log.extend(log_data)
            # 2014 代表短信验证码失效
            elif json_logs.get('retCode', '') == '2014':
                self.log('website', 'param_timeout', resp)
                missing_list.append(query_month)
                continue
            # -1 调用第三方失败
            elif json_logs.get('retCode', '') == '-1':
                self.log("website", 'website_busy_error', resp)
                missing_list.append(query_month)
                continue
            else:
                self.log('crawler', 'html_error', resp)
                missing_list.append(query_month)
                crawl_num += 1
                continue
        if crawl_num > 0:
            return 9, 'crawl_error', call_log, missing_list, pos_missing
        if len(missing_list+pos_missing) == 6:
            return 9, 'website_busy_error', call_log, missing_list, pos_missing
        return 0, "success", call_log, missing_list, pos_missing

    def call_log_get(self, response, query_month):
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
        json_logs = json.loads(response)

        records = []
        for item in json_logs.get('json',{}).get('retInfo',[]):
            data = {}
            try:
                data['month'] = query_month
                data['call_cost'] = item.get('MONEY','')
                # 以下几行   转换成时间戳
                call_time = re.findall('\d{2}', item.get('START_TIME',''))
                call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + \
                                   call_time[4] + ':' + call_time[5] + ':' + call_time[6]
                timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
                call_time_timeStamp = str(int(time.mktime(timeArray)))
                data['call_time'] = call_time_timeStamp

                data['call_method'] = item.get('CALL_TYPE','')
                data['call_type'] = item.get('CALCUNIT','')
                # data['call_from'] = item.get('BILLING_AREA','')

                raw_call_from = item.get('BILLING_AREA','').strip()
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                    data['call_from'] = raw_call_from

                # data['call_to'] = item.get('CALLED_CITYCODE','')
                raw_call_to = item.get('BILLING_AREA', '').strip()
                call_to, error = self.formatarea(raw_call_to)
                if call_to:
                    data['call_to'] = call_to
                else:
                    self.log("crawler", "{}  {}".format(error, raw_call_to), "")
                    data['call_to'] = raw_call_to

                data['call_tel'] = item.get('OTHERPHONE','')
                data['call_duration'] = item.get('TIMELONG','')
                records.append(data)
            except:
                error = traceback.format_exc()
                return 'html_error', 9, 'html_error : %s' % error, []
        return 'success', 0, 'success', records

    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        crawl_num = 0
        phone_bill = list()
        month_bill_url = 'http://sc.189.cn/ajax/accbillajax.jsp'
        now_month = datetime.datetime.now().strftime("%Y%m")
        for month in self.__monthly_period(5, '%Y%m'):
            post_data = {
                'yyyyMM': month
            }
            for retry in xrange(self.max_retry):
                code, key, resp = self.post(month_bill_url, data=post_data)
                if code != 0:
                    pass
                else:
                    break
            else:
                missing_list.append(month)
                continue
            key, level, message, result = self.crawl_month_bill(month, resp)
            if level != 0:
                self.log('crawler', message, resp)
                crawl_num += 1
                missing_list.append(month)
                continue
            if result['bill_amount'] == '':
                if 'Web调用App超时' in message:
                    self.log('crawler', u'调用APP超时', resp)
                else:
                    self.log('crawler', u'账单记录为空', resp)
                missing_list.append(month)
                continue
            phone_bill.append(result)
        if now_month in missing_list:
            missing_list.remove(now_month)
        if crawl_num > 0:
            return 9, 'crawl_error', phone_bill, missing_list
        if len(missing_list) == 5:
            return 9, 'website_busy_error', phone_bill, missing_list
        return 0, 'success', phone_bill, missing_list


    def crawl_month_bill(self,month,response):
        month_bill = {
            'bill_month': month,
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
            bill = json.loads(response.text)
            if '0' != bill['retCode']:
                # return 'request_error', 9, response.status_code, dict()
                return 'success', 0, bill.get('retMsg', ''), month_bill
            for x in bill['list']:
                if ''!=x['FEE_TOTAL']:
                    month_bill['bill_amount'] = x['FEE_TOTAL']
                if '1'==x['LEVEL_ID'] and '套餐月基本费'==x['ACC_ITEM_TYPE'].strip() and ''!=x['FEE']:
                    month_bill['bill_package'] = '%.2f' % (float(x['FEE'])/100)
                if '1'==x['LEVEL_ID'] and '语音通信费'==x['ACC_ITEM_TYPE'].strip() and ''!=x['FEE']:
                    month_bill['bill_ext_calls'] = '%.2f' % (float(x['FEE'])/100)
                if '1' == x['LEVEL_ID'] and '短信彩信费'==x['ACC_ITEM_TYPE'].strip() and ''!=x['FEE']:
                    month_bill['bill_ext_sms'] = '%.2f' % (float(x['FEE'])/100)
        except:
            error = traceback.format_exc()
            return 'html_error', 9, 'html_error : %s' % error, []
        return 'success', 0, 'success', month_bill

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(-1, length):
            yield (current_time - relativedelta(months=month_offset+1)).strftime(strf)


if __name__ == '__main__':
    c = Crawler()
    USER_ID = "18180423849"
    # USER_ID = "18980888830345354"
    USER_PASSWORD = "443028"
    # USER_PASSWORD = "522588"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # print c.aes_encrypt(USER_PASSWORD)
