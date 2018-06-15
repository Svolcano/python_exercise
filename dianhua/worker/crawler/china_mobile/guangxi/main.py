# -*- coding: utf-8 -*-
import base64
import datetime
import time
import traceback
import re
from lxml import etree

from dateutil.relativedelta import relativedelta
import sys
import random
from Queue import Queue
from threading import Thread

reload(sys)
sys.setdefaultencoding("utf8")

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler
import request_headers
import request_params
import response_data

URL_XPATH_BEFORE_LOGIN = 'https://gx.ac.10086.cn/login'
URL_PHONE_NUM_CHECK = 'https://gx.ac.10086.cn/user/UserServlet?num={}&mobile={}'
URL_LOGIN = 'https://gx.ac.10086.cn/Login'
URL_AFTER_LOGIN = 'http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp'
URL_AFTER_LOGIN_TOKEN = 'http://www.gx.10086.cn/wodeyidong'
URL_LOGIN_CONFIRMATION = 'http://www.gx.10086.cn/wodeyidong/mymob/xiangdan.jsp'
URL_INIT_SECOND_VERIFICATION = 'http://www.gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/initBusi.menu'
URL_SMS_GET_BEFORE_CALL_LOG = 'http://www.gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/sendSecondPsw.menu'
URL_SMS_VERIFY_BEFORE_CALL_LOG = 'http://www.gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/checkSecondPsw.menu'
URL_CALL_LOG = 'http://www.gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/queryDetailDoPage.menu'


URL_INIT_PHONE_BILL = 'http://www.gx.10086.cn/wodeyidong/mymob/zdcx.jsp'
URL_DESTROY_MENU = 'http://www.gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/destroyBusi.menu'
URL_INIT_PHONE_BILL2 = 'http://www.gx.10086.cn/wodeyidong/ecrm/querymonthbill/QueryMonthBillAction/initBusi.menu'
URL_PRE_PHONE_BILL = 'http://www.gx.10086.cn/wodeyidong/ecrm/querymonthbill/QueryMonthBillAction/queryBusi.menu'
URL_PHONE_BILL = 'http://www.gx.10086.cn/wodeyidong/ecrm/querymonthbill/QueryMonthBillAction/feeinfonew.menu'


class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.spid = ''
        self.date_time_token = ''

# 登录时
    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']
    
# 登录时
    def get_login_verify_type(self, **kwargs):
        return 'SMS'

# 二次验证
    def get_verify_type(self, **kwargs):
        return 'SMS'

    def send_login_verify_request(self, **kwargs):
        # 登录spid cookies
        code, key, resp = self.get(URL_XPATH_BEFORE_LOGIN)
        if code != 0:
            return code, key, ''

        has_location = re.findall(r"location.replace\('(.*)'\)", resp.text)
        if has_location:
            try:
                url = has_location[0]
            except:
                error = traceback.format_exc()
                self.log("crawler", "获取跳转信息失败{}".format(error), resp)
                pass
            headers = {"Referer": "https://gx.ac.10086.cn/login"}
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key, ''
        # 获取SPID
        try:
            self.spid = re.search('id="spid" value="([\s\S]*?)"', resp.content).group(1)
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取spid失败{}".format(error), resp)
            return 9, "html_error", ""
        """
        before_login = response_data.before_login_data(resp)
        if before_login['error']:
            self.log('crawler', before_login['msg'], resp)
            return 9, before_login['key'], ''
        before_login.pop('error')
        self.spid = before_login['spid']
        """

        # 验证手机号码  cookies
        headers = request_headers.phone_num_check_header()
        code, key, resp = self.post(URL_PHONE_NUM_CHECK.format(random.random(), kwargs['tel']), headers=headers)
        if code != 0:
            return code, key, ""
        if 'Y' in resp.content:
            pass
        elif 'N' in resp.content:
            self.log('user', 'invalid_tel', resp)
            return 1, 'invalid_tel', ""
        else:
            self.log('crawler', u'验证手机号，unknown_error', resp)
            return 9, 'unknown_error', ""

        # 发送短信
        headers = request_headers.before_login_captcha_headers()
        url = "https://gx.ac.10086.cn/SMSCodeSend?mobileNum={}&errorurl=https://gx.ac.10086.cn/4logingx/errorPage.jsp&name=menhu&spid={}".format(kwargs['tel'], self.spid)
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ''
        if u'验证码已发送' in resp.text:
            return 0, 'success', ""
        elif u'操作频繁，暂时无法下发短信' in resp.text:
            self.log("crawler", u"请求过于频繁", resp)
            return 9, "send_sms_too_quick_error", ""
        elif u'BOSS未知错误，请您稍后重试' in resp.text:
            self.log("crawler", u"BOSS系统错误", resp)
            return 9, "website_busy_error", ""
        else:
            self.log("crawler", 'send_sms_error', resp)
            return 9, "send_sms_error", ""

    def login(self, **kwargs):
        # login
        pin_pwd = kwargs['pin_pwd']
        if len(pin_pwd) != 6:
            return 1, "pin_pwd_error"

        params = request_params.login_params(self.spid, **kwargs)
        for i in xrange(self.max_retry):
            code, key, resp = self.post(URL_LOGIN, data=params)
            if code != 0:
                return code, key
            if resp.text.strip() == '':
                continue
            break
        else:
            self.log('website', 'website_busy_error', resp)
            return 9, 'website_busy_error'
        # 当发生302跳转, 则有错误(验证码错或其他)
        if resp.history:
            # code = ""
            # cc = re.findall("code=(.*?)&", resp.url)
            # if cc:
            #     code = cc[0]
            # if code == "9008":
            #     # 尊敬的用户，登录签名验证错误，请您稍后再试
            #     self.log("crawler", u"登录签名验证错误", resp)
            #     return 9, "website_busy_error"
            # if code == "6002" or code =="2004":
            #     # code == "6002" 短信验证码不存在
            #     # code == "2004" 请您输入正确的短信验证码
            #     self.log("crawler", u"短信验证码错误", resp)
            #     return 9, 'verify_error'
            # 有两种错误提示方式, 统一使用下面的, 上面的和下面的不兼容
            if u'验证码已失效' in resp.text or u'请您输入正确的短信验证码' in resp.text:
                self.log("user", 'verify_error', resp)
                return 9, 'verify_error'
            if re.findall(u'验证码(.*?)错误', resp.text):
                self.log("user", 'verify_error', resp)
                return 9, 'verify_error'
            if u'短信验证码不存在' in resp.text:
                self.log("crawler", u"短信已失效", resp)
                return 9, 'verify_error'
            if u'BOSS未知错误' in resp.text or u'登录签名验证错误' in resp.text:
                self.log("website", u"系统异常", resp)
                return 9, "website_busy_error"
            self.log("crawler", u"未知异常", resp)
            return 9, "unknown_error"
        # 构造请求data
        has_location = re.findall(r"location.replace\('(.*)'\)", resp.text)
        if has_location:
            try:
                url = has_location[0]
            except:
                error = traceback.format_exc()
                if 'postartifact.submit()' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    return 9, 'website_busy_error'
                self.log("crawler", '获取跳转url失败{}'.format(error), resp)
                return 9, "html_error"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "https://gx.ac.10086.cn/Login"
            }
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key
        else:
            try:
                resp.encoding = "gb2312"
                et = etree.HTML(resp.text)
                url = et.xpath("//form/@action")[0]
                if url == "https://gx.ac.10086.cn/4logingx/backPage.jsp":
                    pass
                else:
                    self.log("crawler", url, resp)
                    url = "https://gx.ac.10086.cn/4logingx/backPage.jsp"
                SAM = re.findall(r'name="SAMLart" value="(.*?)"', resp.text)[0]
                data = {
                    "SAMLart": SAM,
                    "isEncodePassword": "1",
                    "displayPic": "0",
                    "RelayState": "type=A;backurl=http%3A%2F%2Fwww.gx.10086.cn%2Fwodeyidong%2FindexMyMob.jsp;nl=3;loginFrom=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp",
                    "isEncodeMobile": "1",
                    "displayPics": "mobile_sms_login:998===sendSMS:999===mobile_servicepasswd_login:0"
                }
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Referer": "https://gx.ac.10086.cn/Login"
                }
                # code, key, resp = self.get(url, headers=headers)
                code, key, resp = self.post(url, headers=headers, data=data)
                if code != 0:
                    return code, key
            except:
                error = traceback.format_exc()
                self.log("crawler", "记录错误{}".format(error), resp)
                return 9, "html_error"

        if not resp.text.strip():
            self.log("website", u"官网下发数据为空", resp)
            return 9, "website_busy_error"
        try:
            SAMLart = re.findall(r"Login.callAssert\('(.*?)'\)", resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error{}".format(error), resp)
            return 9, "html_error"
        # params = request_params.after_login_params(data['SAMLart'])
        params = {
            "SAMLart": SAMLart,
            "RelayState": "type=A;backurl=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp;nl=3;loginFrom=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp",
            "myaction": "http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp",
            "netaction": "http://www.gx.10086.cn/padhallclient/netclient/customer/businessDealing"
        }
        code, key, resp = self.post(URL_AFTER_LOGIN, params=params)
        if code != 0:
            return code, key
        # Get _dateTimeToken
        code, key, resp = self.post(URL_AFTER_LOGIN_TOKEN)
        if code != 0:
            return code, key
        after_login_token_data = response_data.after_login_token_data(resp)
        if after_login_token_data['error']:
            if "java" in resp.text and 'Exception' in resp.text \
                    or 'postartifact.submit()' in resp.text:
                # java.net.SocketException: Connection reset
                self.log("crawler", u"官网异常", resp)
                return 9, "website_busy_error"
            self.log('crawler', after_login_token_data['msg'], resp)
            return 9, 'html_error'
        after_login_token_data.pop('error')
        self.date_time_token = after_login_token_data['dateTimeToken']
        # Login confirm post
        code, key, resp = self.get(URL_LOGIN_CONFIRMATION)
        if code != 0:
            return code, key
        return response_data.login_confirm_data(self, resp, kwargs['tel'])

    def send_verify_request(self, **kwargs):
        params = request_params.before_send_sms_init_params(self.date_time_token)
        headers = request_headers.before_send_sms_init_headers()
        code, key, resp = self.get(URL_INIT_SECOND_VERIFICATION, params=params,headers=headers)
        if code != 0:
            return code, key, ''

        headers = request_headers.before_call_log_get_sms_headers()
        code, key, resp = self.get(URL_SMS_GET_BEFORE_CALL_LOG, params=params, headers=headers)
        if code != 0:
            return code, key, ''
        return response_data.before_call_log_get_sms_data(self, resp)

    def verify(self, **kwargs):
        url = "http://www.gx.10086.cn/wodeyidong/"
        code, key, resp = self.get(url)
        if code != 0:
            return code, key
        try:
            _dateTimeToken = re.findall(r"var _dateTimeToken = \'(.*?)\';", resp.text, re.S)[1]
        except:
            if "SAMLRequest" in resp.text:
                self.log("crawler", u"官网异常跳转", resp)
                return 9, "website_busy_error"
            if resp.text == "":
                self.log("website", "官网偶发异常返回为空", resp)
                return 9, "website_busy_error"
            error = traceback.format_exc()
            self.log("crawler", 'html_error: {}'.format(error), resp)
            return 9, "html_error"
        headers = request_headers.before_call_log_verify_sms_headers()
        data = {
            "input_random_code": kwargs['sms_code'],
            "input_svr_pass": kwargs['pin_pwd'],
            "queryRegOkVal": "",
            "is_first_render": "true",
            "_zoneId": "_sign_errzone",
            "_tmpDate":	time.time(),
            "_menuId":	"410900003558",
            "_buttonId": "other_sign_btn",
            "_dateTimeToken": _dateTimeToken
        }
        code, key, resp = self.post(URL_SMS_VERIFY_BEFORE_CALL_LOG, data=data, headers=headers)
        if code != 0:
            return code, key
        if '系统服务异常,请稍后再重试' in resp.content:
            self.log("crawler", "系统异常", resp)
            if len(kwargs['pin_pwd']) != 6:
                return 1, 'pin_pwd_error'
            else:
                return 9, "website_busy_error"
        if '输入服务密码为空' in resp.content:
            self.log("crawler", "服务密码少于6为数", resp)
            return 1, 'pin_pwd_error'
        return response_data.before_call_log_verify_sms_data(self, resp)

    def get_page_data(self, month, page):
        # month "201804"
        # print "***************get_page_data****************"
        headers = request_headers.call_log_headers()

        params = self.get_call_log_params
        params['queryMonth'] = month.strip()
        params['queryMonthList'] = month.strip()
        searchMonth = month.replace('-', '')
        params['iPage'] = str(page)

        code, key, resp = self.get(URL_CALL_LOG, params=params, headers=headers)
        # print month, page, time.time()
        if code != 0:
            self.crawl_again_queue.put((month, page))
            return code, key, "network_error"
        code, key, message, result = response_data.call_log_data(resp, searchMonth, self_obj=self)
        if code != 0:
            if key == "unknown_error":
                self.crawl_error += 1
            self.log("crawler", "获取详单失败", resp)
            self.crawl_again_queue.put((month, page))
            return code, key, message
        if str(page) == '1':
            code, key, message, total_page = response_data.get_total_page_num(resp)
            if total_page != '':
                [self.work_queue.put((month, str(page_info))) for page_info in range(2, int(total_page)+1)]
        if result:
            [self.data_queue.put(result_data) for result_data in result]
            return 0, "success", ""
        else:
            self.crawl_again_queue.put((month, page))
            return 0, "success", "no_data"
        #     [self.data_queue.put(result_data) for result_data in result]
        # print month, page, time.time()
        # print "END_END_END_END  get_page_data   END_END_END_END"

    def control_possibly_missing_queue(self):
        pass

    def control_again_queue(self):
        time_limit = 50
        empty_time_limit = 20
        st_time = time.time()
        break_time = st_time + time_limit
        empty_break_time = st_time + empty_time_limit
        while True:
            # print "检查错误列表"
            if not self.crawl_again_queue.empty():
                get_page_data_params = self.crawl_again_queue.get()
                self.crawl_again_info_queue.put(get_page_data_params)
                code, key, message = self.get_page_data(*get_page_data_params)
                # 增加切换到work_queue的概率
                time.sleep(0)

            # 调整再次重试的间隔
            time.sleep(0.5)

            now_time = time.time()
            if now_time > break_time and self.work_queue.empty():
                break
            if self.work_queue.empty() and self.crawl_again_queue.empty() and now_time > empty_break_time:
                break

    def control_work_queue(self):
        time_limit = 50
        empty_time_limit = 20
        st_time = time.time()
        break_time = st_time + time_limit
        empty_break_time = st_time + empty_time_limit
        while True:
            if not self.work_queue.empty():
                get_page_data_params = self.work_queue.get()
                self.work_queue_info.put((get_page_data_params, time.time()))
                code, key, message = self.get_page_data(*get_page_data_params)
                if code == 9:
                    if key == "websiter_prohibited_error":
                        break
            # 将控制权移交出去
            time.sleep(0)
            now_time = time.time()
            if now_time > break_time and self.work_queue.empty():
                break
            if self.work_queue.empty() and self.crawl_again_queue.empty() and now_time > empty_break_time:
                break

    def get_crawl_call_log(self, **kwargs):
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        params = request_params.call_log_params(self.date_time_token)

        self.crawl_error = 0
        self.get_call_log_params = params

        self.work_queue = Queue()
        self.crawl_again_queue = Queue()
        self.work_queue_info = Queue()
        self.crawl_again_info_queue = Queue()
        self.data_queue = Queue()

        searchMonth = self.monthly_period(6, strf='%Y-%m')
        [self.work_queue.put((x, '1')) for x in searchMonth]

        control_work_queue = Thread(target=self.control_work_queue)
        control_again_queue = Thread(target=self.control_again_queue)
        control_work_queue.start()
        control_again_queue.start()

        control_work_queue.join()
        control_again_queue.join()

        # print self.work_queue, "work_queue ***---***"*2
        # print self.crawl_again_queue, "crawl_again_queue ***---***" * 2
        # print self.crawl_again_info_queue, "crawl_again_info_quque ***---***" * 2

        again_queue_last = []
        full_retry_list = []
        full_request_list = []
        part_miss_set = set()
        miss_set = set()
        while not self.crawl_again_queue.empty():
            work_one = self.crawl_again_queue.get()
            search_month_str = work_one[0].replace("-", "")
            if work_one[1] == '1':
                miss_set.add(search_month_str)
            else:
                part_miss_set.add(search_month_str)
            again_queue_last.append(work_one)

        while not self.crawl_again_info_queue.empty():
            again_info_one = self.crawl_again_info_queue.get()
            full_retry_list.append(again_info_one)

        while not self.work_queue_info.empty():
            work_info_one = self.work_queue_info.get()
            full_request_list.append(work_info_one)

        # self.log("crawler", "全部请求: {}".format(full_request_list), "")
        self.log("crawler", "重试剩余: {}".format(again_queue_last), "")
        self.log("crawler", "全部重试: {}".format(full_retry_list), "")

        missing_month_list = [miss_x for miss_x in miss_set]
        missing_month_list.sort(reverse=True)
        part_missing_list = [x for x in part_miss_set]
        part_missing_list.sort(reverse=True)
        data_list = []
        while not self.data_queue.empty():
            data_list.append(self.data_queue.get())

        if len(missing_month_list) == 6:
            if self.crawl_error > 0:
                return 9, "crawl_error", [], missing_month_list, possibly_missing_list, part_missing_list
            else:
                return 9, "website_busy_error", [], missing_month_list, possibly_missing_list, part_missing_list
        return 0, "success", data_list, missing_month_list, possibly_missing_list, part_missing_list

    def crawl_call_log(self, **kwargs):
        tel = kwargs.get('tel')
        if tel[-1] in ['1', '2', '3']:
            code, key, data_list, missing_month_list, possibly_missing_list, part_missing_list = self.get_crawl_call_log(**kwargs)
            return code, key, data_list, missing_month_list, possibly_missing_list, part_missing_list

        # 缺失月份
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        part_missing_list = []
        params = request_params.call_log_params(self.date_time_token)
        headers = request_headers.call_log_headers()
        call_log = list()
        crawl_error = 0
        log_for_first_page_retry = []
        for searchMonth in self.__monthly_period(6, strf='%Y-%m'):
            full_time = 4.0
            st_time = time.time()
            time_fee = 0
            rand_time = random.randint(20, 40)/10.0

            params['queryMonth'] = searchMonth.strip()
            params['queryMonthList'] = searchMonth.strip()
            searchMonth = searchMonth.replace('-','')
            params['iPage'] = '1'
            # 查第一页并确定页数
            total_page = ''
            first_page_retry = self.max_retry
            while True:
                first_page_retry -= 1
                if first_page_retry < -4:
                    self.log("crawler", "重试次数超上限: {}".format(searchMonth), "")
                    missing_month_list.append(searchMonth)
                    break

                log_for_first_page_retry.append((searchMonth, first_page_retry, time_fee))
                code, key, resp = self.get(URL_CALL_LOG, params=params, headers=headers)
                # print resp.content
                if code != 0:
                    if first_page_retry >= 0:
                        time_fee = time.time() - st_time
                    elif time_fee < full_time:
                        time.sleep(rand_time)
                        time_fee = time.time() - st_time
                    else:
                        missing_month_list.append(searchMonth)
                        break
                    continue
                if u'请勿非法操作' in resp.text:
                    self.log("crawler", "请勿非法操作", resp)
                    missing_month_list.append(searchMonth)
                    break
                code, key, message, result = response_data.call_log_data(resp, searchMonth, self_obj=self)
                if code != 0:
                    if key not in ["websiter_prohibited_error", "website_busy_error"]:
                        crawl_error += 1
                    if first_page_retry >= 0:
                        time_fee = time.time() - st_time
                    elif time_fee < full_time:
                        time.sleep(rand_time)
                        time_fee = time.time() - st_time
                    else:
                        if key == 'unknown_error':
                            self.log('crawler', message, resp)
                        else:
                            self.log('crawler', key, resp)
                        missing_month_list.append(searchMonth)
                        break
                    continue
                if result:
                    call_log.extend(result)
                else:
                    if first_page_retry >= 0:
                        time_fee = time.time() - st_time
                    elif time_fee < full_time:
                        time.sleep(rand_time)
                        time_fee = time.time() - st_time
                    else:
                        if searchMonth not in possibly_missing_list and searchMonth not in missing_month_list:
                            self.log('crawler', '没有详单单记录', resp)
                            possibly_missing_list.append(searchMonth)
                        break
                    continue

                code, key, message, total_page = response_data.get_total_page_num(resp)
                break

            # 查剩下那些页
            if total_page == '':
                total_page = '1'

            log_for_retry_page = []
            page_st_time = time.time()
            page_ful_time = 6.0
            page_time_fee = 0
            page_list = [(x, self.max_retry) for x in range(2, int(total_page) + 1)]
            while page_list:
                page_num, retry_times = page_list.pop(0)
                # 将该操作放在所有操作前, 在判断重试次数是否耗尽时代码更清晰
                retry_times -= 1
                log_for_retry_page.append((page_num, retry_times, page_time_fee))
                params['iPage'] = str(page_num)

                code, key, resp = self.get(URL_CALL_LOG, params=params, headers=headers)
                if code != 0:
                    if searchMonth not in part_missing_list:
                        part_missing_list.append(searchMonth)
                    continue

                code, key, message, result = response_data.call_log_data(resp, searchMonth, self_obj=self)
                if code != 0:
                    if retry_times >= 0:
                        page_time_fee = time.time() - page_st_time
                        page_list.append((page_num, retry_times))
                    elif page_time_fee < page_ful_time:
                        time.sleep(rand_time)
                        page_time_fee = time.time() - page_st_time
                        page_list.append((page_num, retry_times))
                    else:
                        if searchMonth not in part_missing_list:
                            if key == 'unknown_error':
                                self.log('crawler', message, resp)
                            else:
                                self.log('crawler', key, resp)
                            part_missing_list.append(searchMonth)
                        if key not in ["websiter_prohibited_error", "website_busy_error"]:
                            crawl_error += 1
                    continue
                if result:
                    call_log.extend(result)
                    if searchMonth in missing_month_list:
                        missing_month_list.remove(searchMonth)
                        if searchMonth not in part_missing_list:
                            part_missing_list.append(searchMonth)
                else:
                    if searchMonth not in possibly_missing_list + missing_month_list + part_missing_list:
                        self.log('crawler', '没有详单单记录', resp)
                        part_missing_list.append(searchMonth)
            self.log("crawler", "记录{}的分页请求情况: {}".format(searchMonth, log_for_retry_page), resp)
        self.log("crawler", "缺失: {} 可能缺失: {} 部分缺失{}".format(missing_month_list, possibly_missing_list, part_missing_list), "")
        self.log("crawler", "记录首页重试的情况: {}".format(log_for_first_page_retry), "")
        if len(missing_month_list+possibly_missing_list) == 6:
            if crawl_error > 0:
                return 9, "crawl_error", call_log, missing_month_list, possibly_missing_list, part_missing_list
            else:
                return 9, "website_busy_error", call_log, missing_month_list, possibly_missing_list, part_missing_list
        return 0, 'success', call_log, missing_month_list, possibly_missing_list, part_missing_list

    def crawl_phone_bill(self, **kwargs):
        # visit zdcx.jsp
        headers = request_headers.init_phone_bill_headers()
        code, key, resp = self.get(URL_INIT_PHONE_BILL, headers=headers)
        if code != 0:
            return code, key, [], []
        # visit destroyBusi.menu
        headers = request_headers.destory_destroyBusi_headers()
        params = request_params.destory_destroyBusi_params(self.date_time_token)
        code, key, resp = self.post(URL_DESTROY_MENU, headers=headers, params=params)
        if code != 0:
            return code, key, [], []
        # visit initBusi.menu
        params = request_params.init_phone_bill2_params(self.date_time_token)
        headers = request_headers.init_phone_bill2_headers()
        code, key, resp = self.get(URL_INIT_PHONE_BILL2, headers=headers, params=params)
        if code != 0:
            return code, key, [], []
        missing_month_list = list()
        phone_bill = list()
        # current_month_skipped = False
        flag = True
        crawl_error = 0
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            if flag:
                # 当前月份
                current_month = searchMonth
                flag = False

            for item in xrange(self.max_retry):
                params = request_params.phone_bill_querybusi_params(self.date_time_token)
                headers = request_headers.phone_bill_headers()
                params['month_type_value'] = searchMonth
                params['month_selected_type'] = searchMonth
                # visit QueryMonthBillAction/queryBusi.menu
                code, key, resp = self.post(URL_PRE_PHONE_BILL, params=params, headers=headers)
                if code != 0 and item == self.max_retry - 1:
                    if searchMonth not in missing_month_list:
                        self.log('crawler', '账单记录出错', resp)
                        missing_month_list.append(searchMonth)
                    continue
                if '没有查询到' in resp.content:
                    if searchMonth not in missing_month_list:
                        self.log('crawler', '没有账单记录', resp)
                        missing_month_list.append(searchMonth)
                    break
                headers = request_headers.phone_bill_curtnessnew_headers()
                params = request_params.phone_bill_curtnessnew_params(self.date_time_token)
                code, key, resp = self.post(URL_PHONE_BILL, params=params, headers=headers)
                if code != 0 and item == self.max_retry - 1:
                    self.log('crawler', '账单记录出错2', resp)
                    missing_month_list.append(searchMonth)
                    continue
                code, key, message, result = response_data.phone_bill_data(resp,searchMonth)
                if code != 0 and item == self.max_retry - 1:
                    self.log('crawler', message, resp)
                    crawl_error += 1
                if result:
                    phone_bill.append(result)
                    break
                else:
                    self.log('crawler', '没有账单记录', resp)
                    if searchMonth not in missing_month_list:
                        missing_month_list.append(searchMonth)

        if current_month in missing_month_list:
            missing_month_list.remove(current_month)
        if len(missing_month_list) == 5:
            if crawl_error == 0:
                return 9, "website_busy_error", phone_bill, missing_month_list
        # print phone_bill
        # print missing_month_list
        return 0, 'success', phone_bill, missing_month_list
    
    def crawl_info(self, **kwargs):
        return 9, 'unknown_error', {}

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)
    def monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        xx = []
        for month_offset in range(0, length):
            xx.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return xx

if __name__ == '__main__':
    # from worker.crawler.main import *
    c = Crawler()

    USER_ID = "18277398591"
    # USER_PASSWORD = "447470"
    # USER_PASSWORD = "890602"
    USER_PASSWORD = "472982"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # print(c.get_crawl_call_log())
