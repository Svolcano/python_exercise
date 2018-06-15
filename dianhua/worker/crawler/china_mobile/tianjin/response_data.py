# -*- coding: utf-8 -*-
import traceback
import json
import lxml.html
from lxml import etree
import re,traceback,time

# 登录前_XPath
def before_login_data(html):
    before_login = {'error': False}
    try:
        root = etree.HTML(html)
        before_login['token'] = root.xpath('//*[@id="token"]/@value')[0]
        before_login['redirectUrl'] = root.xpath('//*[@id="redirectUrl"]/@value')[0]
        before_login['appKey'] = root.xpath('//*[@id="appKey"]/@value')[0]
    except :
        error = traceback.format_exc()
        msg = 'html_error:{}'.format(error)
        return {'error': True, 'msg': msg}
    return before_login


# 登录前_图片验证码
def before_login_captcha_data(self,resp):
    content_text = resp.text
    if not content_text or content_text == '0':
        self.log('crawler', 'unknown_error', resp)
        return 9, 'unknown_error', ""
    return 0, 'success', content_text.replace('data:image/png;base64,','')

# 登录
def login_data(self, resp):
    try:
        resp.encoding = 'utf-8'
        json_string = resp.text
        result = json.loads(json_string)
        if len(result) == 0:
            self.log('crawler', 'json_error', resp)
            return 9, 'json_error'

        if result['state'] == True:
            return 0, 'success'
        if u'验证码输入不正确' in resp.text:
            self.log('user', 'verify_error', resp)
            return 2, 'verify_error'
        elif u'服务密码不正确' in resp.text:
            self.log('user', 'pin_pwd_error', resp)
            return 2, 'pin_pwd_error'
        elif result['state'] == False and result['message']:
            self.log('user', 'login_param_error', resp)
            return 1, 'login_param_error'
        else:
            self.log('user', 'json_error', resp)
            return 9, 'json_error'
    except:
        error = traceback.format_exc()
        if u'<title>天津移动-网上营业厅</title>' in resp.text:
            self.log('website', 'website_busy_error', resp)
            return 9, 'website_busy_error'
        self.log('crawler', 'unknown_error:{}'.format(error), resp)
        return 9, 'unknown_error'


# 登录后_获取短信验证码
def before_call_log_get_sms_data(self, resp):
    try:
        xml_json = resp.text
        if '请您登陆后进行' in xml_json:
            self.log('crawler', 'website_busy_error', resp)
            return 9, 'website_busy_error', ''
        root = etree.fromstring(xml_json.encode('utf-8'))
        json_string = root.xpath('//*[@id="dataset"]')
        if len(json_string) == 0:
            self.log('crawler', 'xml_error', resp)
            return 9, 'xml_error', ''

        result = json.loads(json_string[0].text)[0]
        if len(result) == 0:
            self.log('crawler', 'xml_error', resp)
            return 9, 'xml_error', ''

        if result['FLAG'] == 'true':
            return 0, 'success', ''
        self.log('crawler', 'send_sms_error', resp)
        return 9, 'send_sms_error', ''
    except:
        error = traceback.format_exc()
        self.log('crawler', 'xml_error:{}'.format(error), resp)
        return 9, 'xml_error', ''


# 登录后_验证短信验证码
def before_call_log_verify_sms_data(self, resp):
    try:
        xml_json = resp.text
        root = etree.fromstring(xml_json.encode('utf-8'))
        json_string = root.xpath('//*[@id="dataset"]')
        if len(json_string) == 0:
            self.log('crawler', 'xml_error', resp)
            return 9, 'xml_error'

        result = json.loads(json_string[0].text)[0]
        if len(result) == 0:
            self.log('crawler', 'xml_error', resp)
            return 9, 'xml_error'
        
        if result['FLAG'] == 'true':
            self.einfo = result['ECHTOKENINFO']
            return 0, 'success'
        elif result['FLAG'] == 'false' and result['RESULTINFO']:
            self.log('user', 'verify_error', resp)
            return 2, 'verify_error'
        else:
            self.log('user', 'xml_error', resp)
            return 9, 'xml_error'
    except:
        error = traceback.format_exc()
        self.log('crawler', 'unknown_error:{}'.format(error), resp)
        return 9, 'unknown_error'


def time_transform(time_str,bm='utf-8',str_format="%Y-%m-%d %H:%M:%S"):
    time_type = time.strptime(time_str.encode(bm), str_format)
    return str(int(time.mktime(time_type)))


def time_format(time_str,**kwargs):
    exec_type=1
    time_str = time_str.encode('utf-8')
    if 'exec_type' in kwargs:
        exec_type = kwargs['exec_type']
    if (exec_type == 1):
        xx = re.match(r'(.*时)?(.*分)?(.*秒)?',time_str)
        h,m,s = 0,0,0
        if  xx.group(1):
            hh = re.findall('\d+', xx.group(1))[0]
            h = int(hh)
        if  xx.group(2):
            mm = re.findall('\d+', xx.group(2))[0]
            m = int(mm)
        if  xx.group(3):
            ss = re.findall('\d+', xx.group(3))[0]
            s = int(ss)
        real_time = h*60*60 + m*60 +s
    if (exec_type == 2):
        xx = re.findall(r'\d*', time_str)
        h, m, s = map(int,xx[::2])
        real_time = h*60*60 + m*60 +s
    return str(real_time)


# 通话详单
def call_log_data(xml_json, searchMonth, self_obj=None):
    # print 'xml_json:', xml_json
    try:
        if "&#31995;&#32479;&#32321;&#24537;" in xml_json:
            return 9, "website_busy_error", "系统繁忙，请稍后再试", []
        if "号码状态异常" in xml_json:
            return 9, "websiter_prohibited_error", '手机号码异常', []
        root = etree.fromstring(xml_json.encode('utf-8'))
        json_string = root.xpath('//*[@id="dataset"]')
        if len(json_string) == 0:
            return 9, 'xml_error', 'xpath id="dataset"', []

        result = json.loads(json_string[0].text)[0]
        if len(result) == 0:
            return 9, 'xml_error', 'xml_json_string error', []
        # 查看没有当月详单情况
        data = list()
        if result.has_key('ERRORINFO'):
            # 当月通话详单为空时情况
            if u'由于您的号码状态异常，不能进行此业务办理' in result['ERRORINFO']:
                return 0, 'success', '', []
            return 9, 'request_error', result['ERRORINFO'], data

        if not result.has_key('detailInfos'):
            return 9, 'request_error', 'no result[detailInfos]', data

        for record in result['detailInfos']:
            #print  'type(record):', type(record)
            raw_call_from = record['AREA_CODE']

            call_from, error = self_obj.formatarea(raw_call_from)
            if not call_from:
                call_from = raw_call_from
                self_obj.log("crawler", "{}-{}".format(error, raw_call_from), "")
            _data = {
                'call_from': call_from,
                'call_time': time_transform(record['START_TIME']),
                'call_to': '',
                'call_tel': record['OTHER_PARTY'],
                'call_method': record['FORWARD_CAUSE'],
                'call_type': record['LONG_TYPE'],
                'call_cost': record['CFEE_LFEE'],
                'call_duration': time_format(record['DURATION']),
                'month': searchMonth,
            }
            data.append(_data)

        # print '\n', 'call_log_data:', data
        return 0, 'success', 'success', data
    except :
        error = traceback.format_exc()
        message = 'unknown_error:{}'.format(error)
        return 9, 'unknown_error', message, []

# 账单
def phone_bill_data(xml_json, searchMonth):
    try:
        root = etree.fromstring(xml_json.encode('utf-8'))

        json_string = root.xpath('//*[@id="dataset"]')
        if len(json_string) == 0:
            return 9, 'xml_error', 'xpath id="dataset" error', []

        result = json.loads(json_string[0].text)[0]

        if len(result) == 0:
            return 9, 'xml_error', 'xml_json_string error', []

        if result.has_key('ERRORINFO'):
            return 0, 'success', result['ERRORINFO'], []

        if not result.has_key('BILL'):
            return 0, 'success', 'no result[BILL]', []

        data = {
            'bill_month': searchMonth,
            'bill_amount': result['BILL']['ALL_FEE'],
            'bill_package': result['BILL']['DISCNT_GUDING_FEE'],
            'bill_ext_calls': result['BILL']['YUYIN_TONGXIN_FEE'],
            'bill_ext_data': result['BILL']['SHANGWANG_FEE'],
            'bill_ext_sms': result['BILL']['DUANXIN_FEE'],
            'bill_zengzhifei': result['BILL']['ZENGZHI_YEWU_FEE'],
            'bill_daishoufei': result['BILL']['DAISHOUFEI_YEWU_FEE'],
            'bill_qita': result['BILL']['OTHER_FEE'],
        }
        return 0, 'success', 'success', data
    except :
        error = traceback.format_exc()
        message = 'unknown_error:{}'.format(error)
        return 9, 'unknown_error', message, []


def personal_info_data(self,resp):
    try:
        xml_json = resp.text
        root = etree.fromstring(xml_json.encode('utf-8'))
        json_string = root.xpath('//*[@id="dataset"]')
        if len(json_string) == 0:
            self.log('crawler', 'xml_error', resp)
            return 9, 'xml_error',  {}

        result = json.loads(json_string[0].text)[0]
        if len(result) == 0:
            self.log('crawler', 'xml_error', resp)
            return 9, 'xml_error',  {}

        data = {
            'full_name': result['CUST_NAME'],
            'id_card': '',
            'is_realname_register': False,
            'open_date': time_transform(result['OPEN_DATE']),
            'address': '',
        }

        return 0, 'success', data
    except:
        error = traceback.format_exc()
        message = 'unknown_error:{}'.format(error)
        self.log('crawler', message, resp)
        return 9, 'unknown_error', {}
