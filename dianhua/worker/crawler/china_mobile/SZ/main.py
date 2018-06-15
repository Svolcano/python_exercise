# -*- coding: utf-8 -*-
import traceback
import urllib
import requests
import base64
from fake_useragent import UserAgent
import time
import json
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar
import lxml
import execjs
import random
import lxml.html
from pprintpp import pprint as pp
from dateutil.parser import *
from tool import ras
import time

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        self.s = requests.Session()
        self.s.verify = False

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'captcha_verify']

    def get_login_verify_type(self, **kwargs):
        return 'Captcha'

    def send_login_verify_request(self, **kwargs):
        headers = {}
        r = ''
        url = 'https://gd.ac.10086.cn/ucs/login/signup.jsps'
        try:
            r = self.s.get(url)
        except Exception as e:
            return 'request_error', 9, 'login error', ""

        self.rsa_n = r.text.split('maxdigits":67,"n":"')[1].split('"')[0]
        dt = int(time.time()*1000)
        captcha_url = "https://gd.ac.10086.cn/ucs/captcha/image/reade.jsps?sds=%s" % dt
        headers['Referer'] = "https://gd.ac.10086.cn/ucs/login/signup.jsps"
        try:
            r = self.s.post(url=captcha_url, headers=headers)
            return  'success', 0, '', base64.b64encode(r.content)
        except Exception as e:
            msg = traceback.format_exc()
        return 'request_error', 9, 'login error', ""

    def login(self, **kwargs):
        login_url = "https://gd.ac.10086.cn/ucs/login/register.jsps"
        headers = {}

        data = {
            'loginType': '2',
            'mobile': kwargs['tel'],
            'password':  ras(kwargs['pin_pwd'], self.rsa_n),
            'imagCaptcha': kwargs['captcha_code'],
            'cookieMobile':  'on',
            'bizagreeable':  'brue',
            'exp': '',
            'cid': '',
            'area': '',
            'resource': '',
            'channel': '0',
            'reqType': '0',
            'backURL': ''
        }
        r = self.s.post(url=login_url, headers=headers, data=data)
        if u'密码错误，请重新输入' in r.text:
            return 'pin_pwd_error', 2, ''

        url = 'http://gd.10086.cn/commodity/servicio/myService/queryBaseInfo.jsps'
        r = self.s.get(url=url, headers=headers)
        doc = lxml.html.document_fromstring(r.text)

        url = "https://gd.ac.10086.cn/ucs/login/signup.jsps"
        data = {
            'backURL': doc.xpath('//input[@name="backURL"]')[0].xpath('@value')[0],
            'reqType':  doc.xpath('//input[@name="reqType"]')[0].xpath('@value')[0],
            'channel': doc.xpath('//input[@name="channel"]')[0].xpath('@value')[0],
            'cid': doc.xpath('//input[@name="cid"]')[0].xpath('@value')[0],
            'area': doc.xpath('//input[@name="area"]')[0].xpath('@value')[0],
            'resource': doc.xpath('//input[@name="resource"]')[0].xpath('@value')[0],
            'loginType': doc.xpath('//input[@name="loginType"]')[0].xpath('@value')[0],
            'optional': doc.xpath('//input[@name="optional"]')[0].xpath('@value')[0],
            'exp': doc.xpath('//input[@name="exp"]')[0].xpath('@value')[0]
        }
        r = self.s.post(url=url, data=data, headers=headers)
        r.encoding = 'utf-8'
        if u'错误' in r.text or u'不能为空' in r.text:
            return 'verify_error', 2, ''
        return 'success', 0, 'Login Process Complete'

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def send_verify_request(self, **kwargs):
        headers = {}
        url = 'http://gd.10086.cn/commodity/servicio/servicioForwarding/queryData.jsps'
        today = date.today()
        data = {
            'servCode': 'REALTIME_LIST_SEARCH',
            'operaType': 'QUERY',
            'Payment_startDate': '%d%02d%2d000000' % (today.year, today.month, today.day),
            'Payment_endDate' : '%d%02d%2d235959' % (today.year, today.month, today.day)
        }
        self.s.post(url=url, data=data, headers=headers)

        url = "https://gd.ac.10086.cn/ucs/second/index.jsps"
        data = {
            'cid': '10003',
            'channel': '0',
            'reqType': '1',
            'backURL': '',
            'type': '2'
        }
        r = self.s.post(url=url, data=data, headers=headers)
        #self.rsa_n = r.text.split('maxdigits":67,"n":"')[1].split('"')[0]

        url = "https://gd.ac.10086.cn/ucs/captcha/dpwd/send.jsps"
        data = {'mobile': kwargs['tel'],'dt':'84'}
        headers['Referer'] = "https://gd.ac.10086.cn/ucs/second/loading.jsps"
        r = self.s.post(url=url, data=data, headers=headers)

        if u'只能发送3次' in r.text:
            return 'request_error', 9, r.status_code, u"动态密码发送失败！动态密码在10分钟内只能发送3次"
        elif u'失败' in r.text:
            return 'request_error', 9, r.status_code, u"动态密码发送失败。"
        return  'success', 0, '',  ''

    def verify(self, **kwargs):
        url = 'https://gd.ac.10086.cn/ucs/second/authen.jsps'
        headers = {}
        data = {
            'dpwd': ras(kwargs['sms_code'], self.rsa_n),
            'type': '2',
            'cid': '10003',
            'channel': '0',
            'reqType': '0',
            'backURL': ''
        }
        r = self.s.post(url=url, data=data, headers=headers)
        # if ok: {"content":"http://gd.10086.cn","type":"ucs.server.location.url"}
        if u'错误' in r.text:
            status_key, level, message = 'verify_error', 2, u'密码错误'
        else:
            status_key, level, message = 'success', 0, ''
        return status_key, level, message


    def crawl_call_log(self, **kwargs):
        def parse_call_record(json_str):
            """
            {
                u'becall': u'被叫',
                u'chargefee': u'0.00',
                u'contnum': u'18210637050',
                u'conttype': u'本地',
                u'giftfee': u'-',
                u'period': u'11秒',
                u'place': u'北京',
                u'taocantype': u'8元4G飞享套餐（省内）',
                u'time': u'12-08 10:24:03',
            }
            """
            records = []
            try:
                obj = json.loads(json_str)
            except Exception as e:
                return []
            objs = obj['content']["realtimeListSearchRspBean"]['calldetail']["calldetaillist"]
            for _obj in objs:
                record = {}
                record['call_time'] =  _obj['time']
                record['call_duration'] = _obj['period']
                record['call_tel'] = _obj['contnum']
                record['call_cost'] = _obj['chargefee']
                record['call_from'] = _obj['place']
                record['call_to'] = ''
                record['call_method'] = _obj['becall']
                record['call_type'] = _obj['conttype']
                records.append(record)
            return records

        today = date.today()
        records = []
        headers = {}
        url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/query.jsps'
        data = {
            'month' : '%d%02d' % (today.year, today.month)
            #ex 'month':'201612'
        }
        r = self.s.post(url=url, data=data, headers=headers)
        obj = json.loads(r.text)
        rand = obj['attachment'][0]['value']
        count_down_month = -6
        delta_months = [ i for i in range(0, count_down_month,  -1)]
        for delta_month in delta_months:
            query_date = today + relativedelta(months=delta_month)

            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/ajaxRealQuery.jsps'
            data = {
                'startTimeReal':'%d%02d01000000' % (query_date.year, query_date.month),
                'endTimeReal':'%d%02d%2d235959' % (query_date.year, query_date.month,
                                                   calendar.monthrange(query_date.year, query_date.month)[1]),
                'uniqueTag': rand,
                'month':'%d%2d' % (query_date.year, query_date.month),
                'monthListType':'',
                'isChange':''
            }
            resp = self.s.post(url=url, data=data, headers=headers)
            # fail: ServiceFailException in r.text
            # success: json

            # 此月无通话记录
            if u"realtimelistsearch.timevalite.error" in resp.text:
                continue

            # 网站繁忙
            if u'由于网络繁忙导致办理该业务未成功' in resp.text:
                continue
            
            # 每天只能查6次
            if u"请明天再来查询" in resp.text:
                return 'crawl_error', 9, u'您当天查询详单已达6次不可再查询详单，请明天再来查询', records

            content = ''
            if 'ServiceFailException' in r.text:
                with open('call_log_sample.json', 'r') as f:
                    content = f.read().decode('utf-8')
                return 'crawl_error', 9, 'crawl user info fails', records
            else:
                content = resp.text
            records.extend(parse_call_record(content))
        return 0, 0 , '', records


    def crawl_info(self, **kwargs):
        headers = {}

        url = 'http://gd.10086.cn/commodity/servicio/myService/queryservicecustomizationLeft.jsps'
        self.s.post(url)

        url  = 'http://gd.10086.cn/commodity/servicio/myService/queryBaseInfo.jsps'
        r = self.s.post(url, headers=headers)
        if u'生产环境' in r.text:
            with open('/tmp/fuck.html', 'w') as f:
                f.write(r.text.encode('utf-8'))
            time.sleep(10)

        self.s.get('http://gd.10086.cn/my/myService/myBasicInfo.shtml', headers=headers)

        today = date.today()
        url = 'http://gd.10086.cn/commodity/servicio/servicioForwarding/queryData.jsps'
        data = {
            'operaType': 'QUERY',
            'servCode': 'MY_BASICINFO'
        }
        r = self.s.post(url=url, data=data, headers=headers)
        doc = lxml.html.document_fromstring(r.text)
        trs = doc.xpath("//table[@class='tb_b']//tr")
        info = {}
        try:
            info['full_name'] = trs[0].xpath('td')[1].text_content().strip()
            info['id_card'] = trs[2].xpath('td')[1].text_content().strip()
            info['open_date'] = trs[5].xpath('td')[1].text_content().strip()
            info['is_realname_register'] = False
            realname = trs[2].xpath('td')[3].text_content().strip()
            if u'已登记' == realname:
                info['is_realname_register'] = True
                status_key, level, message, info = 'success', 0, '' , info
                return status_key, level, message, info
        except Exception as e:
            return 'crawl_error', 9, 'crawl user info fails', {}
        status_key, level, message, info = 'success', 0, '' , info

        return status_key, level, message, info

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "18823834164"
    USER_PASSWORD = "18331414"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)