# -*- coding: utf-8 -*-
import json
import re
import sys
import time
import traceback

import data
import random
import math
reload(sys)
sys.setdefaultencoding("utf8")

from date import generate_dates
from dateutil.relativedelta import relativedelta
from datetime import date
import datetime
if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler

LOGIN_URL = u'https://uac.10010.com/portal/Service/MallLogin'

CHECK_LOGIN_URL = u'http://iservice.10010.com/e3/static/check/checklogin/?_={}'

INFO_URL = u'http://iservice.10010.com/e3/static/query/searchPerInfo/?_={}&accessURL=http%3A//iservice.10010.com/e4/query/basic/personal_xx.html%3FmenuId%3D'

CALL_URL = u'http://iservice.10010.com/e3/static/query/callDetail?_={}&accessURL=http%3A//iservice.10010.com/e4/query/bill/call_dan-iframe.html%3FmenuCode%3D000100030001%26%26menuId%3D000100030001&menuid=000100030001'

MONTH_BILL_URL = u"http://iservice.10010.com/e3/static/query/queryHistoryBill?_={}&accessURL=http://iservice.10010.com/e4/skip.html?menuCode=000100020001&menuCode=000100020001&menuid=000100020001"

class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.uvc = ''
        self.part_miss_list = []

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_login_verify_type(self, **kwargs):
        # return 'Captcha'
        return 'SMS'

    def send_login_verify_request(self, **kwargs):
        # 图片验证方式
        # for retry in xrange(self.max_retry):
        #     url = 'https://uac.10010.com/portal/Service/CreateImage?t={}'.format(int(time.time()))
        #     code, key, resp = self.get(url)
        #     if code != 0:
        #         return code, key, ''
        #
        #     # 登录参数
        #     self.uvc = self.session.cookies.get('uacverifykey')
        #     try:
        #         if self.uvc:
        #             return 0, 'success', base64.b64encode(resp.content)
        #     except:
        #         error = traceback.format_exc()
        #         if retry == self.max_retry-1:
        #             self.log('crawler', 'crawl_error{}'.format(error), resp)
        #             return 9, 'crawl_error', ''
        # else:
        #     self.log('crawler', u'图片未下载或没有uvc值', resp)
        #     return 9, 'crawl_error', ''


        # 验证手机
        random_num = int(time.time() * 1000)
        url = 'https://uac.10010.com/portal/Service/CheckNeedVerify'
        params = {
            'callback': 'jQuery17202818369394051403_{}'.format(random_num),
            'userName': kwargs['tel'],
            'pwdType': '01',
            '_': random_num,
        }
        headers = {
            'Referer': 'https://uac.10010.com/portal/homeLogin',
            'X-Requested-With': 'XMLHttpRequest',
        }
        code, key, resp = self.get(url, params=params, headers=headers)
        if code != 0:
            return code, key, ''
        if '"resultCode":"false' not in resp.text:
            if '"ckCode":"2"' in resp.text:
                self.log('user', 'over_query_limit', resp)
                return 9, 'over_query_limit', ''
            self.log('crawler', 'before_send_sms_error', resp)
            return 9, 'send_sms_error', ''

        # 短信验证
        url = 'https://uac.10010.com/portal/Service/SendCkMSG'
        params = {
            'callback': 'jQuery17202818369394051403_{}'.format(random_num),
            'req_time': random_num,
            'mobile': kwargs['tel'],
            '_': random_num,
        }
        code, key, resp = self.get(url, params=params, headers=headers)
        if code != 0:
            return code, key, ''
        if 'resultCode:"0000",' in resp.text:
            return 0, 'success', ''
        else:
            # 验证短信发送过快
            if 'resultCode:"7096"' in resp.text:
                self.log('crawler', 'send_sms_too_quick_error', resp)
                return 2, 'send_sms_too_quick_error', ''
            if 'resultCode:"7097"' in resp.text:
                self.log('crawler', 'invalid_tel', resp)
                return 1, 'invalid_tel', ''
            if 'resultCode:"7098"' in resp.text:
                self.log('user', u'当日随机码 发送次数已达上限，请明日再试！', resp)
                return 9, 'over_query_limit', ''
            self.log('crawler', 'send_sms_error', resp)
            return 9, 'send_sms_error', ''

    def login(self, **kwargs):

        # 爬虫错： crawler
        # 用户错： user
        # 官网错： website
        # 网络错： network
        # 系统错： system

        headers = {
            'Host': 'uac.10010.com',
            'Referer':'https://uac.10010.com/portal/homeLogin',
        }
        random_num = int(time.time() * 1000)
        login_data = {
            'callback': 'jQuery17209078111864265808_{}'.format(random_num),
            'req_time': random_num,
            'redirectURL': 'http://www.10010.com',
            'userName': kwargs['tel'],
            'password': kwargs['pin_pwd'],
            'pwdType': '01',
            'productType': '01',
            # 'verifyCode': kwargs['captcha_code'],
            # 'uvc': self.uvc,
            'redirectType': '01',
            'rememberMe': '1',
            'verifyCKCode':  kwargs['sms_code'],
            '_': random_num,
        }

        # 登录
        code, key, resp = self.get(LOGIN_URL, params=login_data, headers=headers)
        if code != 0:
            return code, key

        if u'系统忙，请稍后再试' in resp.text:
            self.log('website', 'website_busy_error', resp)
            return 9, 'website_busy_error'

        # 解析
        try:
            code, msg = self.parse_login_resp(resp)
        except Exception as e:
            msg = u'json_error: {}'.format(e)
            self.log('crawler', msg, resp)
            return 9, 'json_error'
        """
        疑问状态码: 描述
        7008: 您的账号登录受限，请联系客服
        7207: 由于本月您将升级成4G，请您在账期后（4日8:00）再使用系统
        7209: 账号登录异常，请稍后再试
        """
        try:
            if code != '0000':
                if code in ['7007', '8888', '7206', '7072'] or \
                   u'用户名或密码不正确' in msg or '服务密码（手机号码）为6位数字' in msg:
                    if u'登录密码出错已达上限' in resp.text:
                        status_key = 'over_query_limit'
                    else:
                        status_key = 'pin_pwd_error'
                    self.log('user', status_key, resp)
                    code = 1
                elif code in ['7009', '7217', '7209', '9999', '7215', '7218']:
                    # '7209' 2017-07-25 7209 是因为官网异常
                    code = 9
                    status_key = 'website_busy_error'
                    self.log('website', status_key, resp)
                elif code in ['7005']:
                    # 7005 您的号码所属省份系统正在升级，请稍后再试
                    code = 9
                    status_key = 'website_maintaining_error'
                    self.log('website', status_key, resp)
                # 服务密码输错3次会出现图形验证码。
                elif code == '7001' or u'验证码错误' in msg or code == '7231':
                    code = 2
                    status_key = 'verify_error'
                    self.log('user', status_key, resp)
                elif code in ['7002', '7003'] or u'简单密码' in msg:
                    status_key = 'sample_pwd'
                    code = 1
                    self.log('user', status_key, resp)
                elif code in ['7004', '7208']:
                    # 7004 登录密码错误达上限
                    status_key = 'over_query_limit'
                    code = 1
                    self.log('user', status_key, resp)
                elif code in ['7099']:
                    status_key = 'website_maintaining_error'
                    code = 9
                    self.log('website', status_key, resp)
                elif code in ['0300']:
                    # 登录前需要进行验证手机密令
                    status_key = 'user_prohibited_error'
                    code = 9
                    self.log('user', status_key, resp)
                else:
                    status_key = 'request_error'
                    code = 9
                    self.log('crawler', 'request_error', resp)
                return code, status_key
        except:
            error_msg = traceback.format_exc()
            message = u'expected_key_error:{}'.format(error_msg)
            self.log('crawler', message, resp)
            return 9, 'expected_key_error'
        return 0, 'success'

    # 解析登录参数，登录跳转使用
    def parse_login_resp(self,resp):
        CODE_RE = re.compile(u'resultCode:"(.*?)"')
        MSG_RE = re.compile(u'msg:\'(.*?)\',')
        text = resp.text
        try:
            code = CODE_RE.findall(text)[0]
        except:
            try:
                code = re.findall(r'resultCode":"(.*?)"', text)[0]
            except:
                code = ''
        if code == '0000':
            msg = ''
        else:
            try:
                msg = MSG_RE.search(text).group(1)
            except:
                msg = ''
        return code, msg

    def check_login(self):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Host': 'iservice.10010.com',
            'Referer':'http://iservice.10010.com/e4/query/bill/call_dan-iframe.html?menuCode=000100030001'
        }
        run_url = CHECK_LOGIN_URL.format(int(time.time()*1000))
        code, key, resp = self.post(run_url, headers=headers)
        if code != 0:
            return code, key, '', resp
        try:
            result_obj = json.loads(resp.text)
        except:
            error_msg = traceback.format_exc()
            message = u'json_error:{}'.format(error_msg)
            return 9, 'json_error', message, resp
        try:
            if not result_obj['isLogin']:
                return 9, 'crawl_error', u'crawl_error:登录验证出错', resp
        except:
            error_msg = traceback.format_exc()
            message = u'expected_key_error:{}'.format(error_msg)
            return 9, 'expected_key_error', message, resp
        return 0, 'success', '', resp

    def crawl_info(self, **kwargs):

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Host': 'iservice.10010.com',
            'Referer': 'http://iservice.10010.com/e4/query/basic/personal_xx.html?menuId=',
        }
        run_url = INFO_URL.format(int(time.time()*1000))
        code, key, resp = self.post(run_url, headers=headers)
        if code != 0:
            return code, key, {}

        resp.encoding = 'utf-8'
        if resp.text == '':
            result = {}
            result['full_name'] = ''
            result['id_card'] = ''
            result['address'] = ''
            result['open_date'] = ''
            result['is_realname_register'] = False
            self.log('website', '个人信息返回空', resp)
            return 0, 'success', result
        try:
            result_obj = json.loads(resp.text)
        except:
            error_msg = traceback.format_exc()
            message = u'json_error:{}'.format(error_msg)
            self.log('crawler', message, resp)
            return 9, 'json_error', {}

        status, result = data.info(result_obj)
        if not status:
            if 'website_busy_error' in result:
                self.log('website', 'website_busy_error', resp)
                return 9, 'website_busy_error', {}
            self.log('crawler', 'param_error:{}'.format(result), resp)
            return 9, 'crawl_error', {}
        return 0, 'success', result

    def call_log_analyze(self, result_obj, raw_resp):
        has_next = False
        try:
            if result_obj.get('limited', '') == '00' or 'limit' in raw_resp:
                return 'website_busy_error', u'官网繁忙', False, []
            flag = False
            if result_obj.has_key('isSuccess'):
                flag = result_obj.get('isSuccess', '')
            elif result_obj.has_key('success'):
                flag = result_obj.get('success', '')

            if not flag:
                message = '解析出错'
                err_code = ""
                if result_obj.has_key('errorMessage'):
                    message = result_obj['errorMessage']['respDesc']
                    err_code = result_obj['errorMessage'].get('respCode')
                # 湖北、海南联通 errormessage
                elif result_obj.has_key('errormessage'):
                    message = result_obj['errormessage']['errmessage']
                    err_code = result_obj['errormessage'].get('respCode')
                if u'查询无记录' in message or u'无详单记录' in message or u'没有查询到您的相关信息' in message or u'您选择时间段没有详单记录哦' in message:
                    status_key = 'no_query_data'
                elif u'访问过于频繁' in message:
                    status_key = 'over_query_limit'
                elif u'尊敬的客户' in message or u'业..务..连..接..超....时' in message or u'业务连接超时' in message \
                        or u'暂时无法为您提供服务' in message:
                    status_key = 'website_busy_error'
                elif err_code == '2107000040' or u'将暂停办理服务' in message:
                    status_key = 'website_maintaining_error'
                elif u'您输入的日期有误' in message:
                    status_key = 'crawl_error'
                else:
                    status_key = 'expected_key_error'
                return status_key, message, False, []
            if result_obj.has_key('pageMap'):
                page_info = result_obj['pageMap']
                page_info = page_info['result']
            #  湖北
            elif result_obj.has_key('result'):
                page_info = result_obj['result']['cdrinfo'][0]['cdrdetailinfo']
            else:
                return 'crawl_error', u'没有获取到页码信息', False, []
            return 'success', '', has_next, page_info
        except:
            error_msg = traceback.format_exc()
            message = u'crawl_error:{}'.format(error_msg)
            return 'crawl_error', message, False, []

    def get_a_page(self, date_start, date_end, page_num=1):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Host': 'iservice.10010.com',
            'Referer': 'http://iservice.10010.com/e4/query/bill/call_dan-iframe.html?menuCode=000100030001',
        }
        call_logs = []
        all_page = None
        page_size = 100
        # 湖北联通解析页面方式不同
        data = {'pageNo': page_num,
                'pageSize': page_size,
                'beginDate': date_start,
                'endDate': date_end}
        run_url = CALL_URL.format(int(time.time() * 1000))

        code, key, resp = self.post(run_url, data=data, headers=headers)
        if code != 0:
            return code, key, 'request_error', call_logs, resp

        resp.encoding = 'utf-8'
        try:
            result_obj = json.loads(resp.text)
        except:
            # 爬虫错误
            error = traceback.format_exc()
            message = u'json_error:{}'.format(error)
            return 9, 'json_error', message, call_logs, resp
        status_key, message, has_next, tmp_call_logs = self.call_log_analyze(result_obj, resp.text)
        # 成功返回
        if status_key == 'success':
            call_logs.extend(tmp_call_logs)
            if page_num == 1:
                total = re.findall(r'"total[r|R]ecord":"*(\d*)', resp.text)
                if total:
                    all_page = int(math.ceil(int(total[0])/100.0))
        elif status_key == 'website_busy_error':
            return 9, status_key, '', call_logs, resp
        elif status_key == 'no_query_data':
            return 0, 'success', 'no_data', call_logs, resp
        # 爬虫错误，直接返回
        else:
            return 9, status_key, message, call_logs, resp
        return 0, 'success', all_page, call_logs, resp

    def crawl_a_call_log(self, date_start, date_end):
        call_logs = []
        # 获取首页
        time_full = 5.0
        retrys_limit = -4
        time_fee = 0
        retrys = self.max_retry
        log_for_retrys = []
        all_page = None
        st_time = time.time()
        rand_time = random.randint(10, 20) / 10.0
        while True:
            retrys -= 1
            log_for_retrys.append((date_start, retrys, time_fee))
            code, key, msg, data_list, resp = self.get_a_page(date_start, date_end)

            if code == 0:
                if msg != 'no_data':
                    all_page = msg
                    call_logs.extend(data_list)
                    break
            if retrys >= 0:
                time_fee = time.time() - st_time
            elif time_fee < time_full:
                time.sleep(rand_time)
                time_fee = time.time() - st_time
                if retrys <= retrys_limit:
                    self.log("crawler", "获取首页失败; {}".format((code, key, msg)), resp)
                    self.log("crawler", "首页重试情况: {}".format(log_for_retrys), "")
                    return code, key, msg, data_list, resp
            else:
                self.log("crawler", "获取首页失败; {}".format((code, key, msg)), resp)
                self.log("crawler", "首页重试情况: {}".format(log_for_retrys), "")
                return code, key, msg, data_list, resp

        is_part_miss = False
        if all_page:
            search_month_str = date_start.replace('-', '')[:6]
            page_list = [(x, self.max_retry) for x in range(2, all_page+1)]
            local_st_time = time.time()
            local_time_fee = 0
            locat_time_full = 8.0
            log_for_part_retrys = []
            while page_list:
                page_num, retrys = page_list.pop(0)
                retrys -= 1
                if retrys < -4:
                    is_part_miss = True
                    self.log("crawler", "单页重试完毕: 页码 {}".format(page_num), "")
                    continue
                log_for_part_retrys.append((page_num, retrys, local_time_fee))
                code, key, msg, data_list, resp = self.get_a_page(date_start, date_end, page_num=page_num)
                if code == 0:
                    if msg != 'no_data':
                        call_logs.extend(data_list)
                        continue
                if retrys >= 0:
                    local_time_fee = time.time() - local_st_time
                    page_list.append((page_num, retrys))
                elif local_time_fee < locat_time_full:
                    time.sleep(rand_time)
                    local_time_fee = time.time() - local_st_time
                    page_list.append((page_num, retrys))
                else:
                    is_part_miss = True
                    self.log("crawler", "获取分页{}失败; {}".format(page_num, (code, key, msg)), resp)
            if is_part_miss:
                self.part_miss_list.append(search_month_str)
            self.log("crawler", "{}分页重试情况: {}".format(search_month_str, log_for_part_retrys), "")
        return 0, 'success', '', call_logs, resp

    def get_year_month(self, number):
        month_list = []
        for each_month in xrange(-0, -number, -1):
            today = datetime.date.today()
            query_date = today + relativedelta(months=each_month)
            month_list.append("%d%02d" % (query_date.year, query_date.month))
        return month_list

    def crawl_call_log(self, **kwargs):

        # 缺失月份
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        # 部分缺失
        part_missing_list = []

        # 检查登录状态，并设置cookie。
        for _ in xrange(self.max_retry):
            code, key, message, resp = self.check_login()
            if code == 0:
                break
        else:
            self.log('crawler', message, resp)
            missing_month_list = self.get_year_month(6)
            if key in ['json_error', 'param_error', 'expected_key_error']:
                return 9, 'crawl_error', [], missing_month_list, possibly_missing_list
            return 9, 'website_busy_error', [], missing_month_list, possibly_missing_list

        # 错误记录列表
        err_dict = {'crawl_error': 0, 'website_busy_error': 0}
        dates = generate_dates()
        final_call_logs = []
        dates_retrys = [(x, self.max_retry) for x in dates]
        log_for_retrys = []
        full_time = 60.0
        more_retry = 4
        time_fee = 0
        st_time = time.time()
        et_time = st_time + full_time
        max_retry_stop_time = 0
        while dates_retrys:
            # search_date ('2017-07-01', '2017-07-14')
            search_date, retry_times = dates_retrys.pop(0)

            retry_times -= 1
            local_st_time = time.time()

            year_month = search_date[0][:4] + search_date[0][5:7]

            log_for_retrys.append((year_month, retry_times, time_fee))

            code, key, message, call_log, resp = self.crawl_a_call_log(search_date[0], search_date[1])
            # 只用于单元测试, 当正常请求时间过长, 仍会重试指定的次数
            # time.sleep(4)
            if code != 0:
                if key == 'website_busy_error':
                    err_dict['website_busy_error'] += 1
                    self.log('website', 'website_busy_error', resp)
                elif key == 'request_error':
                    err_dict['website_busy_error'] += 1
                #  访问过于频繁,请明天再试。直接返回。
                elif key == 'over_query_limit':
                    self.log('user', 'over_query_limit', resp)
                    return 9, 'over_query_limit', [], [], []
                else:
                    err_dict['crawl_error'] += 1
                    missing_month_list.append(year_month)
                    self.log('crawler', message, resp)
                continue
            # 详单为空
            if not call_log:
                self.log('crawler', u'详单为空', resp)
                possibly_missing_list.append(year_month)
                continue
            status, result = data.call_log(self, call_log, year_month)
            if not status:
                self.log('crawler', 'param_error:{}'.format(result), resp)
                if year_month not in missing_month_list:
                    missing_month_list.append(year_month)
                continue
            if result:
                final_call_logs.extend(result)
            else:
                possibly_missing_list.append(year_month)
        missing_month_list.sort(reverse=True)
        possibly_missing_list.sort(reverse=True)
        part_missing_list = self.part_miss_list
        part_missing_list.sort(reverse=True)
        self.log("crawler", "记录月份重试情况: {}".format(log_for_retrys), "")
        self.log('crawler', '记录缺失列表:\n,缺失：{}\n可能缺失{}，\n部分缺失{}'.format(missing_month_list, possibly_missing_list, part_missing_list),'')
        if len(missing_month_list) + len(possibly_missing_list) == 6:
            if err_dict['crawl_error'] > 0:
                return 9, 'crawl_error', [], missing_month_list, possibly_missing_list, part_missing_list
            return 9, 'website_busy_error', [], missing_month_list, possibly_missing_list, part_missing_list

        return 0, 'success', final_call_logs, missing_month_list, possibly_missing_list, part_missing_list

    def crawl_phone_bill(self, **kwargs):
        """
        bill_month	    string	201612	账单月份
        bill_amount     string	10.00	账单总额
        bill_package	string	10.00	套餐及固定费
        bill_ext_calls	string	10.00	套餐外语音通信费
        bill_ext_data	string	10.00	套餐外上网费
        bill_ext_sms	string	10.00	套餐外短信费
        bill_zengzhifei	string	10.00	增值业务费
        bill_daishoufei	string	10.00	代收业务费
        bill_qita       string	10.00	其他费用
        """
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Host': 'iservice.10010.com',
            'Referer': 'http://iservice.10010.com/e4/query/basic/history_list.html?menuId=000100020001',
        }
        # 缺失月份
        missing_month_list = []
        # 错误记录列表
        crawl_error_num = 0
        month_fee =[]
        today = date.today()
        # 不能获取当月账单
        search_month = [x for x in range(-1, -6, -1)]
        for each_month in search_month:
            # month_fee_data = {}
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d"%(query_date.year, query_date.month)
            month_bill_data = {
                "querytype":"0001",
                "querycode":"0001",
                "billdate":query_month,
                "flag":"1"
            }

            for item in xrange(self.max_retry):
                MONTH_BILL_URL.format(str(int(time.time() * 1000)))
                code, key, resp = self.post(MONTH_BILL_URL, data=month_bill_data, headers=headers)
                if code == 0:
                    key = 'crawler'
                    message = 'crawler_failed'
                    #  为空则忽略
                    if "errormessage" not in resp.text or "errorMessage" not in resp.text:
                        try:
                            call_bill_list = data.parse_call_bill(resp.text, query_month)
                        except:
                            error = traceback.format_exc()
                            crawl_error_num += 1
                            message = 'param_error:{}'.format(error)
                            continue
                        if call_bill_list:
                            month_fee.append(call_bill_list)
                            break
                        else:
                            message = u'账单记录为空'
                    if u'业务连接超时' in resp.text or u'暂时无法为您提供服务' in resp.text or \
                            u'尊敬的客户，出了一点点问题' in resp.text or 'limit' in resp.text :
                        key = 'website'
                        message = u'官网繁忙'
                    if u'暂无账单记录' in resp.text:
                        key = 'website'
                        message = u'无账单记录'
                    if u'号码不支持该业务' in resp.text:
                        key = "website"
                        message = u"号码不支持该业务"
            else:
                # 重试2次为空或异常，记录日志，并添加到缺失月份
                # 访问出错不再记日志。
                if code == 0:
                    self.log(key, message, resp)
                missing_month_list.append(query_month)

        # print '账单 missing_month_list: ', missing_month_list
        #  5个月份全部为空
        if len(missing_month_list) == 5:
            if crawl_error_num > 0:
                return 9, 'crawl_error', [], missing_month_list
            return 9, 'website_busy_error', [], missing_month_list
        return 0, "success", month_fee, missing_month_list

if __name__ == '__main__':
    c = Crawler()
    # c.self_test(tel='13193448531', pin_pwd='135844') # henan 21
    # c.self_test(tel='18511071359', pin_pwd='488496') #beijing
    # c.self_test(tel='13148832315', pin_pwd='513238') #guangdong_sz 051
    # c.self_test(tel='15586845785', pin_pwd='587548') #hubei 071
    # c.self_test(tel='13167167401', pin_pwd='135126') #shanghai 031
    # c.self_test(tel='13037282679', pin_pwd='976282') #jiangxi 075
    # c.self_test(tel='15680637591', pin_pwd='195736') #sichuan  081
    # c.self_test(tel='13195563907', pin_pwd='709365') #anhui
    # c.self_test(tel='15585157919', pin_pwd='919751') #guizhou
    # c.self_test(tel='13103263770', pin_pwd='077362') #hebei
    # c.self_test(tel='13045413078', pin_pwd='870314') #heilongjiang
    # c.self_test(tel='13217483953', pin_pwd='359384') #hunan
    # c.self_test(tel='13294396470', pin_pwd='074693') #jilin
    # c.self_test(tel='18605103601', pin_pwd='106301') #jiangsu
    c.self_test(tel='15541860723', pin_pwd='327068') #liaoning
    # c.self_test(tel='15547821633', pin_pwd='336128') #neimenggu
    # c.self_test(tel='18660698301', pin_pwd='103896') #shandong
    # c.self_test(tel='18629259008', pin_pwd='800952') #shaanxi
    # c.self_test(tel='15620062189', pin_pwd='981260') #tianjin
    # c.self_test(tel='13108570427', pin_pwd='724075') #yunnan
    # c.self_test(tel='13173690206', pin_pwd='602069') #zhejiang 19
    # c.self_test(tel='18620292830', pin_pwd='038292') #guangdong 17
    # c.self_test(tel='13212458896', pin_pwd='698854') #chongqing 17
    # c.self_test(tel='18636101640', pin_pwd='046101') #shanxi 17
    # c.self_test(tel='18506903527', pin_pwd='379509')   #fujian 1
    # c.self_test(tel='18677355246', pin_pwd='258368')   #guangxi 1
    # c.self_test(tel=sys.argv[1], pin_pwd=sys.argv[2])