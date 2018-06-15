#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import hashlib
import random
import time

import re
import traceback
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA


def parse_send_login_sms_code_response(self, response):
    if response.text == '0':  # server fail return 'error', success return '0'
        # the duration between two sms verification should be more than 60 sec
        self.send_time = time.time()  # keep the first sms verification time
        return 0, 'success', ''
    elif response.text == '1':
        message = u'对不起，短信随机码暂时不能发送，请一分钟以后再试'
        return 9, 'send_sms_too_quick_error', message
    elif response.text == '2':
        message = u'短信下发数已达上限，您可以使用服务密码方式登录！(也有可能是手机已停机)。'
        return 9, 'over_max_sms_error', message
    elif response.text == '3':
        message = u'对不起，短信发送次数过于频繁'
        return 9, 'send_sms_too_quick_error', message
    elif response.text == '4005':
        message = u'手机号码有误，请重新输入'
        return 1, 'invalid_tel', message
    else:
        message = u'发送验证码错误'
        return 9, 'send_sms_error', message


def get_encrypt(self, **kwargs):
    url = "https://login.10086.cn/platform/js/encrypt.js?resVer=20141125"
    headers = {
        "Accept": "*/*",
        "Referer": "https://login.10086.cn/html/login/login.html"
    }
    code, key, resp = self.get(url, headers=headers)
    if code != 0:
        return code, key
    try:
        public_key = re.findall("var key = \"(.*?)\";", resp.text, re.S)[0]
    except:
        error = traceback.format_exc()
        self.log("crawler", error, resp)
        return 9, "website_busy_error"
    publik_key = """-----BEGIN PUBLIC KEY-----
            {}
            -----END PUBLIC KEY-----""".format(public_key)

    serPwd = kwargs['pin_pwd']
    rsakey = RSA.importKey(publik_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(serPwd.encode('utf-8')))
    return 0, cipher_text


def get_login_params(**kwargs):
    if "result" in kwargs and "backUrl" in kwargs and "channelID" in kwargs:
        pass
    else:
        return 9, "输入参数不够!!"
    params = {
        'accountType': '01',
        'account': kwargs['tel'],
        'password': kwargs['result'],
        'pwdType': '01',
        'smsPwd': kwargs['sms_code'],
        'inputCode': '',
        'backUrl': kwargs['backUrl'],
        'rememberMe': '0',
        'channelID': kwargs['channelID'],
        'protocol': 'https:',
    }
    return 0, params


def parse_verify_login_sms_code_response(self, response):
    try:
        ret_data = response.json()
        error_msg = ret_data['desc']
        error_code = ret_data['code']
        ret_text = response.text
        if error_code != '0000':
            if error_code in ['6001', '6002']:
                status_key = 'verify_error'
                code = 9
            elif error_code in ['2036']:
                status_key = 'pin_pwd_error'
                code = 9
            elif error_code in ['8014'] or u'系统繁忙' in ret_text:
                status_key = 'website_busy_error'
                code = 9
            elif error_code in ['2046', '8009'] or u'密码输入超过次数账号已锁定' in ret_text:
                status_key = 'over_query_limit'
                code = 9
            else:
                status_key = 'login_param_error'
                code = 9
            return code, status_key, error_msg, ''
        return 0, 'success', '', ret_data
    except ValueError:
        error_msg = traceback.format_exc()
        return 9, 'json_error', 'json_error:{}'.format(error_msg), ''
    except:
        error_msg = traceback.format_exc()
        return 9, 'unknown_error', 'unknown_error:{}'.format(error_msg), ''


def get_timestamp():
    return str(int(time.time() * 1000))


def get_digest(timestamp):
    digest = base64.b64encode(hashlib.md5(timestamp + "CM_201606").hexdigest())
    return digest


def get_conversationId(timestamp):
    x = time.localtime(int(timestamp[:10]))
    time_str = time.strftime('%Y %m %d %H %M %S', x)
    fullYear, month, date, hours, minutes, seconds = time_str.split()
    milliseconds = timestamp[10:]
    if len(milliseconds) != 3:
        milliseconds = "{:0<3}".format(milliseconds)
    full_time_str = reduce(lambda x, y: x + y, [fullYear, month, date, hours, minutes, seconds, milliseconds])
    rand1 = str(random.randint(0, 999))
    if len(rand1) != 3:
        rand1 = "{:0<3}".format(rand1)
    rand2 = str(random.randint(0, 999))
    if len(rand2) != 3:
        rand1 = "{:0<3}".format(rand2)
    rand = rand1 + rand2
    conversationId = full_time_str + rand
    return conversationId


if __name__ == '__main__':
    kwargs = {"tel": "123", "sms_code": "asd"}
    result = "asd"
    kwargs.update({
        "backUrl": "http://service.sn.10086.cn/pch5/personal/html/mymobile.html",
        "result": result,
        "channelID": "12027",
    })
    code, params = get_login_params(**kwargs)
    print(code, params)


