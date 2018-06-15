# -*- coding: utf-8 -*-

import base64
import timeit
import requests
import traceback
import inspect
import time
import json
import socket
import sys
import datetime

from dateutil.relativedelta import relativedelta
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    sys.path.append('../../')

from requests_utils import RequestsUtils
from fake_useragent import UserAgent
from com.logger import logger
from com.yundama import yundama
from com.dama2 import dama2
from com.feifeidama import fateadm
from com.format_callfrom import formatArea
from com.redis_que import redis_que
from setting.status_code import STATUS_CODE
from setting.proxy_config import PROXIES_UNICOM_IP_POOLS, PROXIES_PORT
from setting.dama2 import DAMA2_CODE
from setting.yundama_config import YUNDAMA_CODE
from setting.feifeidama import fateadm_code
from setting.dama_type import DAMA_TYPE
from com.multiprocess_dama import multiprocess_dama

def print_message(message_name, key, code):
    print u'============{}============='.format(message_name)
    print u'KEY:', key
    print u'CODE:', code
    print u'============{}============='.format(message_name)

def is_string(value):
    if type(value) in [str, unicode]:
        return True
    if str in type(value).__bases__:
        return True
    if unicode in type(value).__bases__:
        return True
    return False

def is_dict(value):
    if type(value) == dict:
        return True
    return False

def is_list(value):
    if type(value) == list:
        return True
    return False

def is_bool(value):
    if type(value) == bool:
        return True
    return False

def check_string(data):
    if not is_string(data):
        assert 0, 'should be a string'

def check_list(data):
    if not is_list(data):
        assert 0, 'should be a list'

def check_dict(data):
    if not is_dict(data):
        assert 0, 'should be a dict'

def check_key_code(code, key):
    if key not in STATUS_CODE.keys():
        assert 0, 'key should be in STATUS_CODE'
    if code not in [0, 1, 2, 9]:
        assert 0, 'code should be in [0, 1, 2, 9]'

def get_start_end_time_stemp(month):
    str_format = "%Y-%m-%d %H:%M:%S"

    now_month = datetime.date(int(month[:4]), int(month[4:]), 1)
    next_month = now_month - relativedelta(months=-1)
    end_time_str = next_month.strftime("%Y-%m-%d") + " 00:00:00"
    end_time_type = time.strptime(end_time_str, str_format)
    end_timestemp = int(time.mktime(end_time_type))

    start_time_str = month[:4] + "-" + month[4:] + "-01 00:00:00"
    start_time_type = time.strptime(start_time_str, str_format)
    start_timestemp = int(time.mktime(start_time_type))

    return start_timestemp, end_timestemp

def get_search_list(length=6, strf='%Y%m'):
    current_time = datetime.datetime.now()
    search_list = []
    for month_offset in range(0, length):
        search_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
    return search_list

def check_month_call_time(data_list):
    month_list = get_search_list()
    timestemp_dict = {}
    error_list = []
    for i in month_list:
        timestemp_dict[i] = get_start_end_time_stemp(i)

    for i in data_list:
        start_timestemp, end_timestemp = timestemp_dict[i['month']]
        if start_timestemp <= int(i['call_time']) < end_timestemp:
            pass
        else:
            error_list.append(i)

    if error_list:
        assert 0, "call_time not in month {}".format(error_list)


INFO_TYPE = {'full_name': is_string,
             'id_card': is_string,
             'address': is_string,
             'open_date': is_string}
def check_info(data):
    if not is_dict(data):
        assert 0, 'Info should be a dictionary'
    for key in INFO_TYPE:
        if key not in data:
            assert 0, 'Cannot find {}'.format(key)
        type_func = INFO_TYPE[key]
        if not type_func(data[key]):
            assert 0, '{} should be {}'.format(key, type_func.__name__)
    print 'Pass Info Check'

CALL_LOG_TYPE = {'call_from': is_string,
                 'call_time': is_string,
                 'call_to': is_string,
                 'call_tel': is_string,
                 'call_method': is_string,
                 'call_type': is_string,
                 'call_cost': is_string,
                 'call_duration': is_string}
def check_call_log(data):
    if not is_list(data):
        assert 0, 'Call log should be a list'
    for a_log in data:
        if not is_dict(a_log):
            assert 0, 'Each call log should be a dict'
        for key in CALL_LOG_TYPE:
            if key not in a_log:
                assert 0, 'Cannot find {}'.format(key)
            type_func = CALL_LOG_TYPE[key]
            if not type_func(a_log[key]):
                assert 0, '{} should be {}'.format(key, type_func.__name__)
    print 'Pass Call Log Check'

PHONE_BILL_TYPE = {'bill_month': is_string,
                   'bill_amount': is_string,
                   'bill_package': is_string,
                   'bill_ext_calls': is_string,
                   'bill_ext_data': is_string,
                   'bill_ext_sms': is_string,
                   'bill_zengzhifei': is_string,
                   'bill_daishoufei': is_string,
                   'bill_qita': is_string}
def check_phone_bill(data):
    if not is_list(data):
        assert 0, 'phone_bill should be a list'
    for a_bill in data:
        if not is_dict(a_bill):
            assert 0, 'Each call BILL should be a dict'
        for key in PHONE_BILL_TYPE:
            if key not in a_bill:
                assert 0, 'Cannot find {}'.format(key)
            type_func = PHONE_BILL_TYPE[key]
            if not type_func(a_bill[key]):
                assert 0, '{} should be {}'.format(key, type_func.__name__)
    print 'Pass Call Log Check'

class BaseCrawler(object):
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

    RequestsUtils()

    def __init__(self, **kwargs):
        """
        初始化基类, 子类务必继承父类__init__方法：
            super(Crawler, self).__init__(**kwargs)
        """
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': UserAgent().chrome})
        self.kwargs = kwargs
        self.max_retry = 2
        self.sleep_time = 0.2
        self.proxies = self._init_proxies()
        self.dama_flag = True
        self.call_from_set = set()
        # 代理标示
        self.pro_flag = 0

    def _init_proxies(self):
        """
        初始化联通代理
        """
        crawler = self.kwargs.get('crawler','')
        proxies = None
        if 'unicom' in crawler:
            try:
                UNICOM_IP = redis_que.pop_proxies('bmp_crawl_proxies_cucc')
                proxies  = {
                    "http": "http://{ip}:{port}".format(ip=UNICOM_IP, port=PROXIES_PORT),
                    "https": "http://{ip}:{port}".format(ip=UNICOM_IP, port=PROXIES_PORT)
                }
            except:
                return proxies 
        return proxies

    def _dama(self, img_data, code_type):
        dama_dict = DAMA_TYPE.get(str(code_type), {})
        # print dama_dict
        sid=self.kwargs.get('sid','xxxxxxxooooooo')
        if not dama_dict:
            return 'crawl_error', "打码类型错误:{}".format(code_type), ""
        status, code, cid,dama_flag=multiprocess_dama(sid,img_data, code_type)
        # print sid,img_data, code_type
        self.dama_flag =dama_flag
        return status, code, cid

    def _dama_report(self, cid):
        if self.dama_flag=='__fateadm':
            fateadm.Justice(cid)
            # yundama.report(cid)
        elif self.dama_flag=='__yundama':
            yundama.report(cid)
        elif self.dama_flag=='__dama2':
            dama2.reportError(cid)


    def formatarea(self, raw_call_from):
        call_from, error = formatArea(raw_call_from)
        if not call_from:
            self.call_from_set.add(raw_call_from)
        return call_from, error

    def save_call_from_set(self):
        self.log("crawler", "call_from 转换失败: {}".format(self.call_from_set), "")

    def log(self, code, msg, resp):
        """
        crawler爬虫日志调用：
        code:
            爬虫错： crawler
            用户错： user
            官网错： website
            *网络错： network
            *系统错： system
        msg:
            status_key: 'crawl_error'
            try...except: 'crawl_error:{}'.format(msg)
        usage：
            self.log('crawler', 'crawl_error:{}'.format(msg), resp)
        """
        sid = self.kwargs.get('sid','')
        crawler = self.kwargs.get('crawler','').replace('worker.crawler.','').replace('.main','')
        log_name = 'crawler_log'
        crawler_log = {}
        if isinstance(resp, requests.models.Response):
            crawler_log = {
                'func_name' : inspect.stack()[1][3],
                'req_url': str(resp.request.url),
                'req_params': str(resp.request.body),
                'req_header': str(resp.request.headers),
                'res_status_code': str(resp.status_code),
                'res_header': str(resp.headers),
                'res_body': str(resp.text)
            }
        data = {
            'sid':sid,
            'crawler':crawler,
            'crawler_log':crawler_log,
        }
        if socket.gethostname() == 'w219':
            import pprint
            print '\n'
            print msg
            print str({k: v.encode('utf-8') for k, v in crawler_log.items()}).decode('string-escape')
            print 'line: '
            print inspect.stack()[1][2]
            print '\n'

        logger(log_name, code, msg, **data)

    def deal_request(self, method, url, headers=None, data=None, params=None, cookies=None):
        if self.pro_flag == 0 and (self.proxies or self.session.proxies):
            self.pro_flag = 1
            self.log('crawler', u'联通代理ip:{}'.format(self.proxies), '')
            self.log('crawler', u'全局代理ip:{}'.format(self.session.proxies), '')

        # 测试使用
        # self.proxies = {'http': 'http://squidbj03.yulore.com:8080', 'https': 'http://squidbj03.yulore.com:8080'}
        # print(u'代理ip:{}'.format(self.proxies))
        # print(u'全局代理ip:{}'.format(self.session.proxies))
        # self.log('crawler', u'代理ip:{}'.format(self.proxies), '')
        # self.log('crawler', u'全局代理ip:{}'.format(self.session.proxies), '')

        """
        request请求预处理：
        return：
            code: int, 错误等级
            status_key: str, 状态码键值, 参考setting/status_code.py
            resp: object/str, request请求的返回对象
        """
        for _ in xrange(self.max_retry):
            try:
                if method == "post":
                    resp = self.session.post(url, headers=headers, data=data, params=params, proxies=self.proxies, cookies=cookies)
                elif method == "get":
                    resp = self.session.get(url, headers=headers, params=params, proxies=self.proxies, cookies=cookies)
                # time.sleep(self.sleep_time)
                # print resp.url, resp.request.headers
                if str(resp.status_code)[0] == "5":
                    self.log('website', 'website_busy_error', resp)
                    return 9, 'website_busy_error', resp
                if resp.status_code != 200:
                    if resp.status_code == 403:
                        self.log('crawler', u'403\n 代理 :{}'.format(self.session.proxies), resp)
                        return 9, 'request_error', resp
                    self.log('crawler', 'request_error', resp)
                    return 9, 'request_error', resp
                return  0, 'success', resp
            except (requests.ConnectionError, requests.Timeout):
                error = traceback.format_exc()
                msg = u"运营商官网错误,请求失败:{}".format(error)
                continue
            except:
                error = traceback.format_exc()
                msg = u"遇到未知错误,请求失败:{}".format(error)
                msg_dict = {
                    'msg':msg,
                    'method':method,
                    'url': url,
                    'headers': headers,
                    'data': data,
                    'params': params,
                    'proxies': self.proxies
                }
                self.log('crawler', 'unknown_error:{}'.format(json.dumps(msg_dict)), '')
                return 9, 'unknown_error', ''
        else:
            msg_dict = {
                'msg':msg,
                'method':method,
                'url': url,
                'headers': headers,
                'data': data,
                'params': params,
                'proxies': self.proxies
            }
            self.log('website', 'website_busy_error:{}'.format(json.dumps(msg_dict)), '')
            return 9, 'website_busy_error', ''

    def post(self, url, headers=None, data=None, params=None, cookies=None):
        """
        post 请求
        return：
            deal_request, func, 请求预处理
        """
        return self.deal_request('post', url, headers=headers, data=data, params=params, cookies=cookies)

    def get(self, url, headers=None, params=None, cookies=None):
        """
        get 请求
        return：
            deal_request, func, 请求预处理
        """
        return self.deal_request('get', url, headers=headers, params=params, cookies=cookies)

    def self_test(self, **kwargs):
        parameters = {'tel': kwargs.get('tel', ''),
                      'pin_pwd': kwargs.get('pin_pwd', ''),
                      'id_card': kwargs.get('id_card', ''),
                      'full_name': kwargs.get('full_name', '')}

        # set verify_code
        login_verify_type = self.get_login_verify_type(**parameters)
        if login_verify_type:
            start = timeit.default_timer()
            code, key, b64_str = \
                self.send_login_verify_request(**parameters)
            print 'Send Login Verify Request:', timeit.default_timer() - start
            check_key_code(code, key)
            check_string(b64_str)
            if code != 0:
                print_message('Login Verify Request', key, code)
                return
            elif login_verify_type == 'Captcha':
                f = open('./tmp.png', 'wb')
                f.write(base64.b64decode(b64_str))
                f.close()
                captcha_code = raw_input('input fucking captcha_code ===> ')
                parameters['captcha_code'] = captcha_code
            elif login_verify_type == 'SMS':
                sms_code = raw_input('input fucking sms_code ===> ')
                parameters['sms_code'] = sms_code
            elif login_verify_type == 'SMSCaptcha':
                f = open('./tmp.png', 'wb')
                f.write(base64.b64decode(b64_str))
                f.close()
                captcha_code = raw_input('input fucking captcha_code ===> ')
                parameters['captcha_code'] = captcha_code
                sms_code = raw_input('input fucking sms_code ===> ')
                parameters['sms_code'] = sms_code

        # login
        start = timeit.default_timer()
        code, key = self.login(**parameters)
        print 'Login:', timeit.default_timer() - start
        check_key_code(code, key)
        if code != 0:
            print_message('Login', key, code)
            return

        # set verify code
        verify_type = self.get_verify_type(**parameters)
        if verify_type:
            start = timeit.default_timer()
            code, key, b64_str = \
                self.send_verify_request(**parameters)
            print 'Send Verify Request:', timeit.default_timer() - start
            check_key_code(code, key)
            check_string(b64_str)
            if code != 0:
                print_message('Verify Request', key, code)
                return
            elif verify_type == 'Captcha':
                f = open('./tmp.png', 'wb')
                f.write(base64.b64decode(b64_str))
                f.close()
                captcha_code = raw_input('input fucking captcha_code ===> ')
                parameters['captcha_code'] = captcha_code
            elif verify_type == 'SMS':
                sms_code = raw_input('input fucking sms_code ===> ')
                parameters['sms_code'] = sms_code
            elif verify_type == 'SMSCaptcha':
                f = open('./tmp.png', 'wb')
                f.write(base64.b64decode(b64_str))
                f.close()
                captcha_code = raw_input('input fucking captcha_code ===> ')
                parameters['captcha_code'] = captcha_code
                sms_code = raw_input('input fucking sms_code ===> ')
                parameters['sms_code'] = sms_code

            # verify
            start = timeit.default_timer()
            code, key = self.verify(**parameters)
            print 'Verify:', timeit.default_timer() - start
            check_key_code(code, key)
            if code != 0:
                print_message('Verify', key, code)
                return

        # start crawl

        start = timeit.default_timer()
        results = self.crawl_call_log(**parameters)
        if len(results) == 5:
            code, key, call_log, missing_list, possibly_missing_list = results
            part_missing_list = []
        if len(results) == 6:
            code, key, call_log, missing_list, possibly_missing_list, part_missing_list = results
        # code, key, call_log, missing_list, possibly_missing_list = self.crawl_call_log(**parameters)
        print 'Crawl Call Log:', timeit.default_timer() - start
        check_key_code(code, key)
        check_list(call_log)
        check_month_call_time(call_log)
        check_list(missing_list)
        check_list(possibly_missing_list)
        check_list(part_missing_list)

        self.save_call_from_set()

        # 保证 missing_list、possibly_missing_list, part_missing_list 不重复
        if set.intersection(set(missing_list),set(possibly_missing_list), set(part_missing_list)):
            assert 0, 'missing_list and possibly_missing_list cannot have same values'

        if code != 0:
            print_message('Crawl Call Log', key, code)
        if code <= 1:
            print call_log, '\nsizeof:', len(call_log)
            check_call_log(call_log)

        print "call_from_set: {}".format(self.call_from_set)

        start = timeit.default_timer()
        code, key, info = self.crawl_info(**parameters)
        print 'Crawl Info:', timeit.default_timer() - start
        check_key_code(code, key)
        check_dict(info)
        if code != 0:
            print_message('Crawl Info', key, code)
        if code <= 1:
            print info
            check_info(info)

        start = timeit.default_timer()
        code, key, phone_bill, missing_list = self.crawl_phone_bill(**parameters)
        print 'Crawl Phone Bill:', timeit.default_timer() - start
        check_key_code(code, key)
        check_list(phone_bill)
        check_list(missing_list)
        if code != 0:
            print_message('Crawl Phone Bill', key, code)
        if code <= 1:
            print phone_bill
            check_phone_bill(phone_bill)

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        return
            list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        return ['full_name', 'id_card', 'pin_pwd',
                'sms_verify', 'captcha_verify']

    def get_login_verify_type(self, **kwargs):
        """
        告訴我登入的時候用什麼驗證
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        return ''

    def get_verify_type(self, **kwargs):
        """
        告訴我二次驗證用什麼驗證
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        return ''

    def send_login_verify_request(self, **kwargs):
        """
        登入時，請求發送短信，或是下載圖片，或是同時發送請求
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        pass

    def send_login_sms_request(self, **kwargs):
        """
        根據get_login_verify_type選擇實作的function
        SMS: send_login_sms_request
        Captcha: send_login_captcha_request
        SMSCaptcha: 兩個都要實作
        直接return send_login_verify_request是為了相容舊的爬蟲
        登入時，請求發送短信
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            image_str: str, 回空即可
        """
        return self.send_login_verify_request(**kwargs)

    def send_login_captcha_request(self, **kwargs):
        """
        根據get_login_verify_type選擇實作的function
        SMS: send_login_sms_request
        Captcha: send_login_captcha_request
        SMSCaptcha: 兩個都要實作
        直接return send_login_verify_request是為了相容舊的爬蟲
        登入時，請求下載圖片
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        return self.send_login_verify_request(**kwargs)

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        pass

    def send_sms_request(self, **kwargs):
        """
        根據get_verify_type選擇實作的function
        SMS: send_sms_request
        Captcha: send_captcha_request
        SMSCaptcha: 兩個都要實作
        直接return send_verify_request是為了相容舊的爬蟲
        登入時，請求發送短信
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            image_str: str, 回空即可
        """
        return self.send_verify_request(**kwargs)

    def send_captcha_request(self, **kwargs):
        """
        根據get_verify_type選擇實作的function
        SMS: send_sms_request
        Captcha: send_captcha_request
        SMSCaptcha: 兩個都要實作
        直接return send_verify_request是為了相容舊的爬蟲
        登入時，請求下載圖片
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        return self.send_verify_request(**kwargs)

    def login(self, **kwargs):
        """
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
        """
        pass

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
        """
        pass

    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        pass

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            call_log: list, 通信詳單，參考詳單格式
            missing_list: list, 详单缺失月份，"201707"
            possibly_missing_list: list, 详单可能缺失月份，"201707"
        """
        pass

    def crawl_phone_bill(self, **kwargs):
        """
        爬取账单
        return
            code: int, 錯誤等級
            key: str, 狀態碼金鑰，參考status_code
            phone_bill: list, 月度账单
            missing_list: list, 账单缺失月份，"201707"
        """
        pass

if __name__ == '__main__':
    kwargs = {
        'crawler': "api.crawler.dianxin.beijing.main",
    }
    base = BaseCrawler(**kwargs)
    import base64
    with open('../../test/img.txt', 'r') as fp:
        imgdata = base64.b64decode(fp.read())
    codetype = '3006'
    start = time.time()
    status, resp, cid  = base._dama(imgdata, codetype) #上传打码
    print time.time() - start
    print base._dama_report(cid)
    print status, resp, cid
