# -*- coding: utf-8 -*-
import re
import traceback
import sys
import time
import datetime
import random
import response_data
# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")
from Queue import Queue
from threading import Thread
import threading
from datetime import date
from scrapy.selector import Selector
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
        self.pin_pwd_error_times = 0

    def need_parameters(self, **kwargs):
        return ['pin_pwd','sms_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        url = "http://login.189.cn/web/login/ajax"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://login.189.cn/web/login"
        }
        data = {
            "m": "checkphone",
            "phone": kwargs['tel']
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key, ""
        try:
            da = resp.json()
            self.areaCode = '0' + da['areaCode']
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取地区码失败{}".format(error), resp)
            return 9, "website_busy_error", ""

        ProvinceID = '17'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        """
        手动重定向至河南电信URL：
        """
        cookie_url = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10017&toStUrl=http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha"
        # headers = {"Referer": url}
        code, key, resp = self.get(cookie_url)
        if code != 0:
            return code, key
        if u'欢迎登录' not in resp.text:
            return 0, "success"
        # 跳转到登录界面，且没有错误代码，报官网繁忙。
        elif 'data-resultcode=""' in resp.text:
            self.log('website', 'website_busy_error', resp)
            return 9, 'website_busy_error'
        else:
            self.log('crawler', 'unknown_error', resp)
            return 9, "unknown_error"

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        send_sms_url = "http://ha.189.cn/service/bill/getRand.jsp"
        send_sms_data = {
            "PRODTYPE": "743065031822",
            "RAND_TYPE": "002",
            "BureauCode": "0374",
            "ACC_NBR": kwargs['tel'],
            "PROD_TYPE": "743065031822",
            "PROD_PWD": '',
            "REFRESH_FLAG": "1",
            "BEGIN_DATE": '',
            "END_DATE": '',
            "ACCT_DATE": "",
            "FIND_TYPE": "2",
            "SERV_NO": '',
            "QRY_FLAG": "1",
            "ValueType": "4",
            "MOBILE_NAME": kwargs['tel'],
            "OPER_TYPE": "CR1",
            "PASSWORD": ''
        }
        header = {'Referer': 'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha'}
        code, key, resp = self.post(send_sms_url, data=send_sms_data, headers=header)
        if code != 0:
            return code, key, ''
        if '<flag>0</flag>' in resp.text:
            return 0, "success", ""
        elif u'<flag>-196910</flag>' in resp.text:
            self.log('crawler', "send_sms_too_quick_error", resp)
            return 9, "send_sms_too_quick_error", ''
        else:
            self.log('crawler', "send_sms_error", resp)
            return 9, "send_sms_error", ''

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        check_sms_url = "http://ha.189.cn/service/iframe/bill/iframe_inxxall.jsp"
        check_sms_data ={
            "PRODTYPE": "743065031822",
            "RAND_TYPE": "002",
            "BureauCode": "0374",
            "ACC_NBR": kwargs['tel'],
            "PROD_TYPE": "743065031822",
            "PROD_PWD": '',
            "REFRESH_FLAG": "1",
            "BEGIN_DATE": '',
            "END_DATE": '',
            "ACCT_DATE": "201611",
            "FIND_TYPE": "2",
            "SERV_NO": '',
            "QRY_FLAG": "1",
            "ValueType": "4",
            "MOBILE_NAME": kwargs['tel'],
            "OPER_TYPE": "CR1",
            "PASSWORD": kwargs['sms_code']
        }
        code, key, resp = self.post(check_sms_url, data=check_sms_data)
        if code != 0:
            return code, key
        if u'您输入的查询验证码错误或过期' in resp.text:
            self.log('user', 'verify_error', resp)
            return 2, "verify_error"
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
        personal_info_url = "http://ha.189.cn/service/iframe/manage/my_selfinfo_iframe.jsp"
        personal_info_data = {
            "fastcode": "20000374",
            "cityCode": 'ha'
        }
        code, key, resp = self.get(personal_info_url, params=personal_info_data)
        if code != 0:
            return code, key, {}
        if "document.location.href" in resp.text:
            self.log("crawler", 'website_busy_error', resp)
            return 9, "website_busy_error", {}
        try:
            if u'以下资料为您在办理业务时留下的客户信息，请您仔细核对' in resp.text:
                # with open('info.py','w')as f:
                #     f.write(resp.text)
                user_info['full_name'] = re.search(u'客户名称：</td>[\s\S]*?<td>([\s\S]*?)</td>', resp.text).group(1)
                user_info['open_date'] = ''
                user_info['id_card'] = re.search(u'证件号码：</th>[\s\S]*?<td>([\s\S]*?)</td>',resp.text).group(1)
                user_info['is_realname_register'] = True if user_info['id_card'] else False #没有实名信息，使用是否有身份证进行判断
                address = re.findall(u'客户住址：</td>\s+<td><span class="text_content">(.*?)</span>',
                                                  resp.text.decode('utf8'))
                user_info['address'] = address[0] if address else ''
            else:
                self.log('crawler', 'unknown_error', resp)
                return 9, "unknown_error",{}
        except:
            error = traceback.format_exc()
            self.log('crawler', 'request_error %s' % error, resp)
            return 9, "request_error", {}
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

        tail_tel_num = ['1', '3', '5', '7']
        if kwargs['tel'][-1] in tail_tel_num:
            self.tel = kwargs['tel']
            return self.new_crawl_call_log()

        missing_list = []
        possibly_missing_list = []
        crawler_num = 0
        call_log = []
        page_and_retry = []
        call_log_url = "http://ha.189.cn/service/iframe/bill/iframe_inxxall.jsp"
        today = date.today()
        search_month = [x for x in range(0, -6, -1)]

        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = '{}{}'.format(query_date.year, str(query_date.month).zfill(2))
            call_log_data = {
                "ACC_NBR": kwargs['tel'],
                "PROD_TYPE": "743065031822",
                "BEGIN_DATE": '',
                "END_DATE": '',
                "ValueType": "4",
                "REFRESH_FLAG": "1",
                "FIND_TYPE": "1",
                "radioQryType": "on",
                "QRY_FLAG": "1",
                "ACCT_DATE": query_month,
                "ACCT_DATE_1": query_month
            }
            page_and_retry.append((call_log_data, query_month, self.max_retry))

        st_time = time.time()
        et_time = st_time + 15
        log_for_retry_request = []
        # missing_flag = False
        rand_time = random.randint(3, 5)
        while page_and_retry:
            call_log_data, m_query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            # for retry in range(self.max_retry):
            code, key, resp = self.post(call_log_url, data=call_log_data)
            if code != 0:
                now_time = time.time()
                if m_retry_times > 0:
                    page_and_retry.append((call_log_data, m_query_month, m_retry_times))
                elif now_time < et_time:
                    time.sleep(rand_time)
                else:
                    # missing_flag = True
                    self.log('website', u'未找到指定数据', resp)
                    if m_query_month not in missing_list:
                        missing_list.append(m_query_month)
                        # break
            elif u"未查询到您的详单信息" in resp.text:
                # missing_flag = False
                self.log("crawler", "未查询到您的详单信息", resp)
                if m_query_month not in possibly_missing_list:
                    possibly_missing_list.append(m_query_month)
                    # break
            else:
                tel = kwargs['tel']
                key, level, message, data = self.call_log_get(resp.text, "", m_query_month, tel)
                if level != 0:
                    if message != "no_data":
                        crawler_num += 1
                    self.log('crawler', message, resp)
                    if m_query_month not in missing_list:
                        missing_list.append(m_query_month)
                    continue
                call_log.extend(data)
        self.log("crawler", "重试记录：{}".format(log_for_retry_request), "")
        # print('missing_list:{}'.format(missing_list))
        # print('possibly_missing_list:{}'.format(possibly_missing_list))
        if len(missing_list + possibly_missing_list) == 6:
            if crawler_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def get_search_list(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        search_list = []
        for month_offset in range(0, length):
            search_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return search_list

    def new_crawl_call_log(self):
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        # 部分缺失月份
        part_missing_month_list = []

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

        searchMonth = self.get_search_list(6)
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

        # return 0
        while not self.last_month.empty():
            work_one = self.last_month.get()
            search_month_str = work_one[0]
            miss_set.add(search_month_str)
            again_queue_last.append(work_one)

        while not self.crawl_again_queue.empty():
            work_one = self.crawl_again_queue.get()
            search_month_str = work_one[0]
            miss_set.add(search_month_str)
            again_queue_last.append(work_one)

        again_list = []
        while not self.crawl_again_info_queue.empty():
            work_one = self.crawl_again_info_queue.get()
            # search_month_str = work_one[0]
            again_list.append({work_one[0]: work_one[1]})

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

    def get_page_data(self, year_month, retry_times):
        retry_times_limit = 5
        call_log_data = {
            "ACC_NBR": self.tel,
            "PROD_TYPE": "743065031822",
            "BEGIN_DATE": '',
            "END_DATE": '',
            "ValueType": "4",
            "REFRESH_FLAG": "1",
            "FIND_TYPE": "1",
            "radioQryType": "on",
            "QRY_FLAG": "1",
            "ACCT_DATE": year_month,
            "ACCT_DATE_1": year_month
        }

        retry_times += 1
        url = "http://ha.189.cn/service/iframe/bill/iframe_inxxall.jsp"

        code, key, resp = self.post(url, data=call_log_data)
        if code == 0:
            # code02, key02, result = self.call_log_get(resp.text, year_month)
            key, code02, message, result = self.call_log_get(resp.text, "", year_month, self.tel)
            if code02 == 0:
                if result:
                    [self.data_queue.put(x) for x in result]
                    return
                else:
                    self.log('crawler', u'详单为空', resp)
            else:
                self.log('crawler', result, resp)
                self.crawl_error += 1
        elif u"未查询到您的详单信息" in resp.text:
            self.log("crawler", "未查询到您的详单信息", resp)

        if retry_times <= retry_times_limit:
            self.crawl_again_queue.put((year_month, retry_times))
        else:
            self.last_month.put((year_month, retry_times))
        return

    def call_log_get(self, response, find_type_value, query_month, tel):
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
        try:
            records = []
            selector = Selector(text=response)
            call_form = selector.xpath('//div[@id="htmltitle"]/table/tbody/tr')
            for item in call_form:
                data = {}
                data['month'] = query_month
                call_cost = item.xpath('.//td[7]/text()').extract()
                if not call_cost:
                    continue
                data['call_cost'] = call_cost[0].strip()
                # data['call_cost'] = item.xpath('.//td[7]/text()').extract()[0].strip()
                data['call_time'] = item.xpath('.//td[3]/text()').extract()[0].strip()
                #以下几行 解决时间戳转换
                call_time = re.findall('\d{2}',item.xpath('.//td[3]/text()').extract()[0].strip().encode('utf8'))
                call_time_reverse = call_time[0]+call_time[1]+'-'+call_time[2]+'-'+call_time[3]+' '+call_time[4]+':'+call_time[5]+':'+call_time[6]
                timeArray = time.strptime(call_time_reverse, "%Y-%m-%d %H:%M:%S")
                call_time_timeStamp = str(int(time.mktime(timeArray)))
                data['call_time'] = call_time_timeStamp
                call_method = item.xpath('.//td[6]/text()').extract()[0].strip()
                data['call_method'] = call_method
                # 主叫
                call_tel_from = item.xpath('.//td[1]/text()').extract()[0].strip()
                # 被叫
                call_tel_to = item.xpath('.//td[2]/text()').extract()[0].strip()
                if call_tel_from != tel:
                    call_tel = call_tel_from
                elif call_tel_to != tel:
                    call_tel = call_tel_to
                else:
                    return "html_error", 9, "有数据, 但是数据有问题", []
                data['call_tel'] = call_tel
                data['call_type'] = find_type_value
                data['call_from'] = ''
                data['call_to'] = ''
                call_duration = item.xpath('.//td[5]/text()').extract()[0].strip()
                call_duration_H, call_duration_M, call_duration_S = map(int, call_duration.split(":"))
                call_duration = call_duration_H * 60 * 60 + call_duration_M * 60 + call_duration_S
                data['call_duration'] = str(call_duration)
                records.append(data)
        except:
            error = traceback.format_exc()
            return 'html_error', 9, 'html_error %s' % error, []
        if records:
            return 'success', 0, '', records
        else:
            return 'success', 9, 'no_data', records

    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        crawler_num = 0
        phone_bill = list()
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            crawl_phone_bill_data = {
                "ACC_NBR": kwargs['tel'],
                "DATE": searchMonth,
                "AreaCode": self.areaCode,
                "usertype": "1",
            }
            URL_PHONE_BILL = 'http://ha.189.cn/service/iframe/bill/iframe_zd.jsp'
            for retry in xrange(self.max_retry):
                code, key, resp = self.post(URL_PHONE_BILL, data=crawl_phone_bill_data)
                if code != 0:
                    pass
                elif u'数据库查询失败，请稍候再试。给您带来不便，敬请谅解' in resp.text or u'请登录后再访问该功能' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                else:
                    break
            else:
                missing_list.append(searchMonth)
                continue
            key, level, message, result = response_data.phone_bill_data(self, resp, searchMonth)
            if level != 0:
                missing_list.append(searchMonth)
                if key != "no_data":
                    crawler_num += 1
                self.log("crawler", "{}{}".format(key, message), resp)
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

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset+1)).strftime(strf)


if __name__ == '__main__':
    c = Crawler()
    USER_ID = "18937776301"
    USER_PASSWORD = "398498"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)

    # print c.aes_encrypt(USER_PASSWORD)
