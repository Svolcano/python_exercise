# -*- coding: utf-8 -*-


def before_login_captcha_headers():
    return {
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Host': 'gx.ac.10086.cn',
        'Pragma': 'no-cache',
        'Referer': 'http://gx.ac.10086.cn/login',
        'X-Requested-With': 'XMLHttpRequest',
    }


def phone_num_check_header():
    return {
        'Accept': '*/*',
        'DNT': '1',
        'Host': 'gx.ac.10086.cn',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://gx.ac.10086.cn/login',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://gx.ac.10086.cn',
    }


def before_send_sms_init_headers():
    return {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'DNT': '1',
        'Host': 'www.gx.10086.cn',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.gx.10086.cn/wodeyidong/mymob/xiangdan.jsp',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://www.gx.10086.cn',
    }


def before_call_log_get_sms_headers():
    return {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'DNT': '1',
        'Host': 'www.gx.10086.cn',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.gx.10086.cn/wodeyidong/mymob/xiangdan.jsp',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin':'http://www.gx.10086.cn'
    }


def before_call_log_verify_sms_headers():
    return before_call_log_get_sms_headers()


def call_log_headers():
    return before_call_log_get_sms_headers()


def init_phone_bill_headers():
    return {
        'Host': 'www.gx.10086.cn',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'DNT': '1',
        'Referer': 'http://www.gx.10086.cn/wodeyidong/mymob/xiangdan.jsp',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    }

def destory_destroyBusi_headers():
    return {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'DNT': '1',
        'Host': 'www.gx.10086.cn',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.gx.10086.cn/wodeyidong/mymob/xiangdan.jsp',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://www.gx.10086.cn',
    }

def init_phone_bill2_headers():
    return {
        'Accept': 'text/html, */*; q=0.01',
        'DNT': '1',
        'Host': 'www.gx.10086.cn',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.gx.10086.cn/wodeyidong/mymob/zdcx.jsp',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://www.gx.10086.cn',
    }

def phone_bill_headers():
    return init_phone_bill2_headers()

def phone_bill_curtnessnew_headers():
    return init_phone_bill2_headers()