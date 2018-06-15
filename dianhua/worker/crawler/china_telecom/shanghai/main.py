# -*- coding: utf-8 -*-
import re
import json
import urllib
import time
import traceback
import calendar
import sys
import datetime
import random
# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")

from Queue import Queue
from threading import Thread
import threading
from datetime import date
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from base_crawler import BaseCrawler
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
        # 记录详单页面，分析字段不能对应问题
        self.flag = False

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):

        ProvinceID = '02'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key
        cookie_url ="http://www.189.cn/login/skip/ecs.do?method=skip&platNo=93507&toStUrl=http://service.sh.189.cn/service/query/detail"
        code, key, cookie_req = self.get(cookie_url)
        return code, key

    def send_verify_request(self, **kwargs):

        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # 设置cookie
        get_detail_url = "http://service.sh.189.cn/service/mobileLogin"
        code, key, resp = self.get(get_detail_url)
        if code != 0:
            return code, key, ''
        send_verify_data = {}
        send_verify_data['flag'] = 1
        send_verify_data['devNo'] = kwargs['tel']
        send_verify_data['dateType'] = ''
        send_verify_data['startDate'] = ''
        send_verify_data['endDate'] = ''
        send_verify_data = urllib.urlencode(send_verify_data)
        send_sms_url = "http://service.sh.189.cn/service/service/authority/query/billdetail/sendCode.do?" + send_verify_data
        code, key, resp = self.get(send_sms_url)
        if code != 0:
            return code, key, ''
        if 'service/error500' in resp.text:
            self.log('crawler', 'send_sms_error', resp)
            return 9, 'send_sms_error', ''
        try:
            send_sms_res = json.loads(resp.text)
            send_sms_code = send_sms_res['CODE']
        except:
            error = traceback.format_exc()
            self.log('crawler', "json_error : %s" % error, resp)
            return 9, "json_error", ""
        if send_sms_code == '0':
            return 0, "success", ""
        else:
            self.log('crawler', 'request_error', resp)
            return 9, "request_error", ""

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        verify_data = {}
        verify_data['input_code'] = kwargs['sms_code']
        verify_data['selDevid'] = kwargs['tel']
        verify_data['flag'] = 'nocw'
        verify_data = urllib.urlencode(verify_data)
        check_sms_url = "http://service.sh.189.cn/service/service/authority/query/billdetail/validate.do?" + verify_data
        code, key, resp = self.get(check_sms_url)
        if code != 0:
            return code, key
        try:
            check_sms_res = json.loads(resp.text)
        except:
            error = traceback.format_exc()
            self.log('crawler', "json_error : %s" % error, resp)
            return 9, "json_error"
        if check_sms_res['CODE'] == "0":
            return 0, "success"
        elif check_sms_res['CODE'] == "ME10001":
            self.log('network', "website_error", resp)
            return 2, "verify_error"
        else:
            self.log('crawler', "crawl_error", resp)
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
        user_info_url = "http://service.sh.189.cn/service/my/basicinfo.do"
        code, key, resp = self.post(user_info_url)
        if code != 0:
            return code, key, {}
        try:
            user_info_res = json.loads(resp.text)
        except:
            error = traceback.format_exc()
            self.log('crawler', "json_error : %s" % error, resp)
            return 9, "json_error", {}
        if user_info_res['CODE'] == "0":
            try:
                info_dict = self.user_info(user_info_res)
            except:
                error = traceback.format_exc()
                self.log('crawler', "html_error : %s" % error, resp)
                return 9, 'html_error', {}
            return 0, "success", info_dict

        # 官网不能查询个人信息，先返回空值。
        user_info_data = {
            'full_name': '',
            'id_card': '',
            'is_realname_register': False,
            'open_date': '',
            'address': ''
        }
        return 0, "success", user_info_data
        # elif user_info_res['CODE'] == "ME10001":
        #     return "website_busy_error", 5, "website problem", {}
        # else:
        #     return "param_error", 9, '返回参数未知:%s'%resp.text, {}

    def user_info(self,response):
        result = response['RESULT']
        full_name = result['CustNAME']
        id_card = result['MainIdenNumber']
        address = result['PrAddrName']
        open_date = ''
        if id_card != "":
            is_realname_register = True
        else:
            is_realname_register = False
        return {
            'full_name': full_name,
            'id_card': id_card,
            'is_realname_register': is_realname_register,
            'open_date': open_date ,
            'address' : address
        }

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """

        tail_tel_num = ['2', '4', '6', '8']
        if kwargs['tel'][-1] in tail_tel_num:
            self.tel = kwargs['tel']
            return self.new_crawl_call_log()

        missing_list = []
        pos_missing = []
        crawl_num = 0
        call_log = []
        today = date.today()
        search_month = [x for x in range(0,-6,-1)]

        dates_retrys = [(x, self.max_retry) for x in search_month]
        log_for_retrys = []
        full_time = 50.0
        time_fee = 0
        rand_sleep = random.randint(30, 55) / 10.0
        while dates_retrys:
            each_month, retrys = dates_retrys.pop(0)
            retrys -= 1
            local_st = time.time()

            query_date = today + relativedelta(months=each_month)
            search_month = "%d%02d"%(query_date.year, query_date.month)
            begDate = "%d-%02d-01"%(query_date.year,query_date.month)
            end_day = calendar.monthrange(query_date.year, query_date.month)[1]
            endDate = "%d-%02d-%d"%(query_date.year,query_date.month,end_day)

            log_for_retrys.append((search_month, retrys, time_fee))

            crawl_call_data = {}
            crawl_call_data['begin'] = 0
            crawl_call_data['end'] = 9999
            crawl_call_data['flag'] = 1
            crawl_call_data['devNo'] = kwargs['tel']
            crawl_call_data['dateType'] = 'now'
            crawl_call_data['bill_type'] = 'SCP'
            # 历史账单查询
            # crawl_call_data['queryDate'] = monthDate
            # 实时账单查询
            crawl_call_data['startDate'] = begDate
            crawl_call_data['endDate'] = endDate
            crawl_call_data = urllib.urlencode(crawl_call_data)
            # print crawl_call_data
            call_log_url = "http://service.sh.189.cn/service/service/authority/query/billdetailQuery.do?" + crawl_call_data

            code, key, resp = self.get(call_log_url)
            if code != 0:
                if retrys > 0:
                    local_fee = time.time() - local_st
                    time_fee += local_fee
                    dates_retrys.append((each_month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_sleep)
                    local_fee = time.time() - local_st
                    time_fee += local_fee
                    dates_retrys.append((each_month, retrys))
                else:
                    self.log("crawler", "重试失败{}".format(search_month), '')
                    missing_list.append(search_month)
                continue
            elif "ME10001" in resp.text:
                missing_flag = False
                #无通话记录，  这个月
                self.log('crawler', '未查询到您的详单信息', resp)
                pos_missing.append(search_month)
                continue
            try:
                call_log_res = json.loads(resp.text)
            except:
                error = traceback.format_exc()
                self.log('crawler', "json_error : %s" % error, resp)
                missing_list.append(search_month)
                continue
            if call_log_res['CODE'] == "0":
                key, level, message, month_log = self.call_log_get(call_log_res, search_month)
                if level != 0:
                    if retrys > 0:
                        local_fee = time.time() - local_st
                        time_fee += local_fee
                        dates_retrys.append((each_month, retrys))
                    elif time_fee < full_time:
                        time.sleep(rand_sleep)
                        local_fee = time.time() - local_st
                        time_fee += local_fee
                        dates_retrys.append((each_month, retrys))
                    else:
                        self.log('crawler', message, resp)
                        crawl_num += 1
                        missing_list.append(search_month)
                    continue
                if self.flag:
                    self.log('crawler', u'详单字段不对应问题', resp)
                    self.flag = False
                call_log.extend(month_log)
            else:
                if retrys > 0:
                    local_fee = time.time() - local_st
                    time_fee += local_fee
                    dates_retrys.append((each_month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_sleep)
                    local_fee = time.time() - local_st
                    time_fee += local_fee
                    dates_retrys.append((each_month, retrys))
                else:
                    self.log('crawler', 'html_error', resp)
                    missing_list.append(search_month)
                    crawl_num += 1
                continue
        self.log("crawler", "重试列表{}".format(log_for_retrys), "")
        missing_list.sort(reverse=True)
        if crawl_num > 0:
            return 9, 'crawl_error', call_log, missing_list, pos_missing
        if len(pos_missing) == 6 or len(missing_list) == 6:
            return 9, 'website_busy_error', call_log, missing_list, pos_missing
        return 0, "success", call_log, missing_list, pos_missing

    def get_search_list(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        search_list = []
        for month_offset in range(0, length):
            search_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return search_list

    def new_crawl_call_log(self):
        possibly_missing_list = []
        # 部分缺失月份
        self.crawl_error = 0
        # 爬虫队列
        self.work_queue = Queue()
        self.work_queue_info = Queue()
        # 重试队列
        self.crawl_again_queue = Queue()
        self.crawl_again_info_queue = Queue()
        # 详单数据
        self.data_queue = Queue()
        self._runing = threading.Event()
        self._runing.set()
        self.last_month = Queue()

        searchMonth = [x for x in range(0, -6, -1)]
        [self.work_queue.put((x, 0)) for x in searchMonth]

        control_work_queue = Thread(target=self.control_work_queue, args=(self.work_queue, 'main', 0.2))
        control_work_queue.start()

        control_again_queue = Thread(target=self.control_work_queue,
                                     args=(self.crawl_again_queue, "crawl_again", random.uniform(2, 3.5)))
        control_again_queue.start()

        self.work_control()

        control_work_queue.join()
        control_again_queue.join()

        again_queue_last = []
        part_miss_set = set()
        miss_set = set()

        today = date.today()

        while not self.last_month.empty():
            work_one = self.last_month.get()
            query_date = today + relativedelta(months=work_one[0])
            search_month_str = "%d%02d"%(query_date.year, query_date.month)
            miss_set.add(search_month_str)
            again_queue_last.append({search_month_str: work_one[1]})

        while not self.crawl_again_queue.empty():
            work_one = self.crawl_again_queue.get()
            query_date = today + relativedelta(months=work_one[0])
            search_month_str = "%d%02d"%(query_date.year, query_date.month)
            miss_set.add(search_month_str)
            again_queue_last.append({search_month_str: work_one[1]})

        again_list = []
        while not self.crawl_again_info_queue.empty():
            work_one = self.crawl_again_info_queue.get()
            # search_month_str = work_one[0]
            query_date = today + relativedelta(months=work_one[0])
            search_month_str = "%d%02d"%(query_date.year, query_date.month)
            again_list.append({search_month_str: work_one[1]})

        self.log("crawler", "重试队列: {}".format(again_list), "")
        self.log("crawler", "重试剩余: {}".format(again_queue_last), "")
        missing_month_list = [miss_x for miss_x in miss_set]
        missing_month_list.sort(reverse=True)
        part_missing_list = [x for x in part_miss_set]
        part_missing_list.sort(reverse=True)

        self.log("crawler", "缺失记录: {} 部分缺失: {}".format(missing_month_list, part_missing_list), "")
        data_list = []
        while not self.data_queue.empty():
            data_list.append(self.data_queue.get())

        if len(missing_month_list) == 6:
            if self.crawl_error > 0:
                return 9, "crawl_error", [], missing_month_list, possibly_missing_list, part_missing_list
            else:
                return 9, "website_busy_error", [], missing_month_list, possibly_missing_list, part_missing_list
        return 0, "success", data_list, missing_month_list, possibly_missing_list, part_missing_list

    def control_work_queue(self, work_queue, work_name="main", sleep_time=0):
        while self._runing.is_set():
            if not work_queue.empty():
                get_page_data_params = work_queue.get()
                self.get_page_data(*get_page_data_params)
                if work_name != 'main':
                    self.crawl_again_info_queue.put(get_page_data_params)

                if work_name != "main":
                    time.sleep(0)
            # 将控制权移交出去
            time.sleep(sleep_time)


    def work_control(self):
        must_stop_time = 40
        time_limit = 30
        empty_time_limit = 20

        st_time = time.time()
        break_time = st_time + time_limit
        empty_break_time = st_time + empty_time_limit
        must_break_time = st_time + must_stop_time

        while True:
            now_time = time.time()
            time.sleep(0)
            if self.work_queue.empty() and self.crawl_again_queue.empty() and now_time > empty_break_time:
                self.log("crawler", "break 1 {} {}".format(st_time, now_time), "")
                break
            if now_time > break_time and self.work_queue.empty():
                self.log("crawler", "break 2 {} {}".format(st_time, now_time), "")
                break
            if now_time > must_break_time:
                self.log("crawler", "break 3 {} {}".format(st_time, now_time), "")
                break
            time.sleep(0)
        self._runing.clear()

    def get_page_data(self, each_month, retry_times):
        retry_times_limit = 5
        retry_times += 1
        today = date.today()
        query_date = today + relativedelta(months=each_month)
        search_month = "%d%02d" % (query_date.year, query_date.month)
        begDate = "%d-%02d-01" % (query_date.year, query_date.month)
        end_day = calendar.monthrange(query_date.year, query_date.month)[1]
        endDate = "%d-%02d-%d" % (query_date.year, query_date.month, end_day)

        crawl_call_data = {}
        crawl_call_data['begin'] = 0
        crawl_call_data['end'] = 9999
        crawl_call_data['flag'] = 1
        crawl_call_data['devNo'] = self.tel
        crawl_call_data['dateType'] = 'now'
        crawl_call_data['bill_type'] = 'SCP'
        # 历史账单查询
        # crawl_call_data['queryDate'] = monthDate
        # 实时账单查询
        crawl_call_data['startDate'] = begDate
        crawl_call_data['endDate'] = endDate
        crawl_call_data = urllib.urlencode(crawl_call_data)
        call_log_url = "http://service.sh.189.cn/service/service/authority/query/billdetailQuery.do?" + crawl_call_data
        code, key, resp = self.get(call_log_url)
        if code == 0:
            try:
                call_log_res = json.loads(resp.text)
                if call_log_res['CODE'] == "0":
                    key, code02, message, result = self.call_log_get(call_log_res, search_month)
                    if code02 == 0:
                        if result:
                            if self.flag:
                                self.log('crawler', u'详单字段不对应问题', resp)
                                self.flag = False
                            [self.data_queue.put(x) for x in result]
                            return
                        else:
                            self.log('crawler', u'详单为空', resp)
                else:
                    self.log('crawler', u'未拿到数据', resp)
            except:
                error = traceback.format_exc()
                self.log('crawler', u"详单解析出错 : %s" % error, resp)
                self.crawl_error += 1

        if retry_times <= retry_times_limit:
            self.crawl_again_queue.put((each_month, retry_times))
        else:
            self.last_month.put((each_month, retry_times))
        return

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
        records = []
        try:
            items = response['RESULT']['pagedResult']
            call_total = len(items)
            for i in range(1,call_total):
                item = items[i]
                data = {}
                data['month'] = search_month
                data['update_time'] = item['beginTime']
                data['call_cost'] = item['totalFee']
                # 以下几行为了转换时间戳
                call_time = re.findall('\d{2}', item['beginTime'])
                call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + \
                                   call_time[4] + ':' + call_time[5] + ':' + call_time[6]
                timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
                call_time_timeStamp = str(int(time.mktime(timeArray)))

                data['call_time'] = call_time_timeStamp
                data['call_method'] = item['callType']
                data['call_type'] = item['longDistanceType']
                # data['call_from'] = item['callingPartyVisitedCity']

                raw_call_from = item['callingPartyVisitedCity'].strip()
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    # self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                    data['call_from'] = raw_call_from

                # data['call_to'] = item['calledPartyVisitedCity']

                raw_call_to = item['calledPartyVisitedCity'].strip()
                call_to, error = self.formatarea(raw_call_to)
                if call_to:
                    data['call_to'] = call_to
                else:
                    # self.log("crawler", "{}  {}".format(error, raw_call_to), "")
                    if u'国内长途' in raw_call_to and not self.flag:
                        self.flag = True
                    data['call_to'] = raw_call_to

                data['call_tel'] = item['targetParty']
                data['call_duration'] = self.time_format(item['callDuriation'])
                records.append(data)
        except:
            error = traceback.format_exc()
            return 'html_error', 9, 'html_error %s' % error, records
        return 'success', 0, 'success', records

    def time_format(self,time_str):
        xx = re.match(u'(.*时)?(.*分)?(.*秒)?', time_str)
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
        return str(real_time)

    # def month_bill(self, **kwargs):
    #     today = date.today()
    #     data = {}
    #     data['billingCycleld'] = "%d%02d"%(today.year,today.month)
    #     data['queryFlag'] = 0
    #     data['productld'] = 2
    #     data['accNbr'] = kwargs['tel']
    #     data = urllib.urlencode(data)
    #     month_bill_url = "http://js.189.cn/chargeQuery/chargeQuery_queryCustBill.action?" + data
    #     try:
    #         month_bill_req = self.session.post(month_bill_url)
    #     except:
    #         error = traceback.format_exc()
    #         return "request_error", 9, error
    #     if month_bill_req.status_code == 200:
    #         return "success", 0, "get info", self.bill_log(month_bill_req.text)
    #     else:
    #         return "request_error", 9, "月单爬取失败：%d"%month_bill_req.status_code
    #
    # def bill_log(self, response):
    #     # 目前返回一个列表，元素为一个字典，键暂定费用及月份
    #     month_bill_res = json.loads(response)
    #     items = month_bill_res['statisticalList']
    #     bill_list = []
    #     for i in range(0,6):
    #         data = {}
    #         data['date'] = items[i]['itemName']
    #         data['bill'] = items[i]['itemCharge']
    #         bill_list.append(data)
    #     return bill_list


    def crawl_phone_bill(self, **kwargs):
        def get_missing_list():
            missing_list = []
            today = date.today()
            search_month = [x for x in range(0, -6, -1)]
            for each_month in search_month:
                query_date = today + relativedelta(months=each_month)
                search_month = "%d%02d" % (query_date.year, query_date.month)
                missing_list.append(search_month)
            return missing_list
        # url = 'http://service.sh.189.cn/service/query/bill'
        # code, key, resp = self.get(url)
        # if code != 0:
        #     missing_list = get_missing_list()
        #     return 0, 'success', [], missing_list

        # if u'抱歉，预付费手机暂不支持账单查询，请选择其他设备查看账单' in resp.text:
        self.log('website', 'website_busy_error', '')
        missing_list = get_missing_list()
        return 0, 'success', [], missing_list

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17321021422"
    USER_PASSWORD = "368372"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)

