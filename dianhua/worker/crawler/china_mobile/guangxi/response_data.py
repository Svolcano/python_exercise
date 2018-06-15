# -*- coding: utf-8 -*-
import traceback
import json
import re
import datetime
from lxml import etree

import execjs
import os
import login_error_code


def convert_to_timestamp(strttime):
    try:
        month = int(strttime.split('-')[0])
        now_month = datetime.datetime.now().month
        now_year = datetime.datetime.now().year
        if month > now_month:
            year = str(now_year - 1)
        else:
            year = datetime.datetime.now().year
        strttime = str(year)+'-'+strttime
        actual_time = datetime.datetime.strptime(strttime,'%Y-%m-%d %H:%M:%S')
    except:
        error = traceback.format_exc()
        return 9, error
    return 0, actual_time.strftime('%s')


def convert_to_second(strtime):
    hours = 0
    mins = 0
    secs = 0
    if '小时' in strtime:
        hours = int(strtime[0:strtime.index('小时')])
        strtime = strtime[strtime.index('小时')+6:]
    if '分钟' in strtime:
        mins = int(strtime[0:strtime.index('分钟')])
        strtime = strtime[strtime.index('分钟')+6:]
    if '秒' in strtime:
        secs = int(strtime[0:strtime.index('秒')])
    return str(hours*60*60+mins*60+secs)


def encodePass(p):
    js_path = "%s/WT_FPC.js" % "/".join(os.path.abspath(__file__).split("/")[:-1])
    with open(js_path, 'r') as f:
        js_content = f.read()
        ctx = execjs.compile(js_content)
        new_pwd = ctx.call("encodePwd",p)
        return new_pwd


def get_WT_FPC():
    js_path = "%s/WT_FPC.js" % "/".join(os.path.abspath(__file__).split("/")[:-1])
    with open(js_path, 'r') as f:
        js_content = f.read()
        ctx = execjs.compile(js_content)
        new_pwd = ctx.call("getWT_FPC")
        return new_pwd

#登录前数据
def before_login_data(resp):
    before_login = {'error': False}
    try:
        # if 'location.replace' in resp.text:
        #     return {'error': True, 'msg': '偶发登录页面获取失败, 需要重新获取', 'key': 'website_busy_error'}
        spid = re.search('name="spid" value="([\s\S]*?)"', resp.content).group(1)
    except :
        error = traceback.format_exc()
        msg = 'html_error:{}'.format(error)
        return {'error': True, 'msg': msg, 'key': 'html_error'}
    # cookie = resp.cookies
    # cookie.set('WT_FPC', get_WT_FPC(), domain='.10086.cn', path='/')
    # before_login['cookie'] = cookie
    before_login['spid'] = spid
    return before_login


def after_login_data(self, resp):
    after_login = {}
    try:
        error_code = re.search('code=(\d{4})', resp.url)
        if error_code:
            error_code = error_code.group(1)
            error = login_error_code.error_code[error_code]
            web_msg = login_error_code.log_msg[error_code]
            if error['code'] == 1 or error['code'] == 2:
                self.log('user', web_msg, resp)
            elif error['code'] == 9:
                self.log('website', web_msg, resp)
            return error['code'], error['key'], {}
            # https://gx.ac.10086.cn/4logingx/errorPage.jsp?code=2006
            # 错误时有302跳转，以上是错误提示页面，信息在跳出提示窗口内
        # after_login['SAMLart'] = re.search('name="SAMLart" value="([\s\S]*?)"',
        #                                    resp.content).group(1)
        # after_login['RelayState'] = re.search(
        #     'name="RelayState" value="([\s\S]*?)"', resp.content).group(1)
        after_login['SAMLart'] = re.findall("<body onLoad=\"parent.Login.callAssert\('(.*?)'\);\">", resp.text)[0]

    except :
        error = traceback.format_exc()
        msg = 'html_error:{}'.format(error)
        self.log('crawler', msg, resp)
        return 9, 'html_error', {}
    return 0, 'success', after_login


def after_login_token_data(resp):
    after_login_token = {'error': False}
    try:
        after_login_token['dateTimeToken'] = re.search('var _dateTimeToken = \'([\S]+?)\'',
                                  resp.content).group(1)
    except :
        error = traceback.format_exc()
        msg = 'html_error:{}'.format(error)
        return {'error': True, 'msg': msg}
    return after_login_token


def login_confirm_data(self, resp, tel):
    try:
        if tel in resp.text:
            return 0, 'success'
        else:
            self.log('user', 'login_param_error', resp)
            return 1, 'login_param_error'
    except:
        error = traceback.format_exc()
        self.log('crawler', 'unknown_error:{}'.format(error), resp)
        return 9, 'unknown_error'


def before_call_log_get_sms_data(self, resp):
    # {"code":"0","msg":"随机短信验证码已发送成功,请注意查收!"}
    try:
        json_string = resp.text
        result = json.loads(json_string)

        if result['code'] == '0':
            return 0, 'success', ''
        else:
            self.log('user', 'verify_error', resp)
            return 1, 'login_param_error', ''
    except:
        if '刷新到首页' in resp.text:
            self.log("crawler", "官网异常情况", resp)
            return 9, 'website_busy_error', ''
        error = traceback.format_exc()
        self.log('crawler', 'json_error:{}'.format(error), resp)
        return 9, 'json_error', ''


def before_call_log_verify_sms_data(self, resp):
    if resp.status_code == 200:
        if '短信验证码错误' in resp.content:
            self.log('user', 'verify_error', resp)
            return 9, 'verify_error'

        # 服务密码错误？
        if '密码输错' in resp.content:
            self.log('user', 'pin_pwd_error', resp)
            return 1, 'pin_pwd_error'
        return 0, 'success'
    else:
        self.log('crawler', 'unknown_error', resp)
        return 9, 'unknown_error'


def get_total_page_num(resp):
    try:
        page_num = re.search('\'ui-paging-bold\'>([\s\S]*?)<',resp.content).group(1)
        return 0, 'success', 'success', page_num.split('/')[1]
    except:
        return 0, 'success', 'success', '1'


def call_log_data(resp,searchMonth, self_obj=None):
    data_list = list()
    try:
        if u'不允许办理' in resp.text or u'不能进行该业务操作' in resp.text or u'补换卡' in resp.text:
            # 提示: 检查不通过，办理了补换卡业务72小时内不允许办理
            # 业务错误:用户在72小时内有做过异地补换卡操作,不能进行该业务操作
            return 9, 'websiter_prohibited_error', 'msg:success', []
        if u'系统异常' in resp.text or u'调用接口失败' in resp.text:
            # 调用接口失败hint：应用繁忙，请稍后
            return 9, 'website_busy_error', 'msg:success', []
        if u'系统提示' in resp.text and u'刷新到首页' in resp.text:
            return 9, 'website_busy_error', 'msg:success', []
        table = re.search('通话详单明细[\s\S]*?<tbody>([\s\S]*?)</tbody>',resp.content).group(1)
        entries = re.findall('<tr>([\s\S]*?)</tr>',table)
        if not entries:
            return 0, "success", "没有详单记录", []
        temp_record = re.findall('<td>([\s\S]*?)</td>', entries[0])
        call_time = temp_record[0].strip()
        if len(call_time) == 14:
            for entry in entries:
                record = re.findall('<td>([\s\S]*?)</td>',entry)
                call_time = record[0].strip()
                raw_call_from = record[1].strip()
                call_from, error = self_obj.formatarea(raw_call_from)
                if not call_from:
                    call_from = raw_call_from
                    # self_obj.log("crawler", "{}-{}".format(error, raw_call_from), "")
                code, call_time_result = convert_to_timestamp(call_time)
                if code != 0:
                    return 9, "unknown_error", call_time, []
                _data = {
                    'call_from': call_from,
                    'call_time': call_time_result,
                    'call_to': '',
                    'call_tel': record[3].strip(),
                    'call_method': record[2].strip(),
                    'call_type': record[5].strip(),
                    'call_cost': record[7].strip(),
                    'call_duration': convert_to_second(record[4].strip()),
                    'month': searchMonth,
                }
                data_list.append(_data)
        else:
            et = etree.HTML(resp.text)
            entries = et.xpath("//table[@id='payTable']/tbody/tr")
            for item in entries:
                data = {}
                item_td = item.xpath("td")
                """
                0 0	
                1 09-04 10:22:01	
                2 北京	
                3 主叫	
                4 10086
                5 2秒	
                6 国内异地主叫	
                7 全球通零听资费	
                8 0.00	
                9 1095	
                10 EF36|1100
                """
                data["call_from"], data['call_tel'], data['call_method'], data['call_type'], data[
                    'call_cost'], call_len, call_time = [
                    item_td[x].xpath("text()")[0].strip() for x in (2, 4, 3, 6, 8, 5, 1)]
                code, call_time = convert_to_timestamp(call_time)
                if code == 0:
                    data["call_time"] = call_time
                else:
                    return 9, "unknown_error", call_time, []
                data["call_duration"] = convert_to_second(call_len)
                data["month"] = searchMonth
                data["call_to"] = ""
                data_list.append(data)
        return 0, 'success', 'success', data_list
    except:
        error = traceback.format_exc()
        message = 'unknown_error:{}'.format(error)
        return 9, 'unknown_error', message, []


def phone_bill_data(resp, searchMonth):
    try:
        data = {
            'bill_month': searchMonth,
            'bill_amount': re.search('合计[\s\S]*?￥([\s\S]*?)<',resp.content).group(1).strip(),
            'bill_package': re.search('套餐及固定费[\s\S]*?￥([\s\S]*?)<',resp.content).group(1).strip(),
            'bill_ext_calls': re.search('语音通信费[\s\S]*?￥([\s\S]*?)<',resp.content).group(1).strip(),
            'bill_ext_data': re.search('上网费[\s\S]*?￥([\s\S]*?)<',resp.content).group(1).strip(),
            'bill_ext_sms': re.search('短彩信费[\s\S]*?￥([\s\S]*?)<',resp.content).group(1).strip(),
            'bill_zengzhifei': re.search('增值业务[\s\S]*?￥([\s\S]*?)<',resp.content).group(1).strip(),
            'bill_daishoufei': re.search('代收费业务[\s\S]*?￥([\s\S]*?)<',resp.content).group(1).strip(),
            'bill_qita': re.search('其它费用[\s\S]*?￥([\s\S]*?)<',resp.content).group(1).strip(),
        }
        return 0, 'success', 'success', data
    except:
        error = traceback.format_exc()
        message = 'unknown_error:{}'.format(error)
        return 9, 'unknown_error', message, []






