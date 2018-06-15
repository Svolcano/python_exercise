# -*- coding: utf-8 -*-

referer_url = ''
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'

def login_cookies_refer():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent': user_agent,
        'Referer': referer_url
    }

def before_login_headers():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Host': 'tj.ac.10086.cn',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent,
    }

def before_login_captcha_headers():
    return {
        'Accept': '*/*',
        'Host': 'tj.ac.10086.cn',
        'Pragma': 'no-cache',
        'Referer': referer_url,
        'User-Agent': user_agent,
        'X-Requested-With': 'XMLHttpRequest',
    }

def login_headers():
    return {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'tj.ac.10086.cn',
        'Origin': 'https://tj.ac.10086.cn',
        'Pragma': 'no-cache',
        'User-Agent': user_agent,
        'Referer': referer_url,
        'X-Requested-With': 'XMLHttpRequest',
    }

def before_call_log_get_sms_headers():
    return {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Host': 'service.tj.10086.cn',
        'Pragma': 'no-cache',
        'Referer': 'http://service.tj.10086.cn/ics/myMobile/myDetailRecords.html',
        'User-Agent': user_agent,
        'X-Requested-With': 'XMLHttpRequest',
    }

def before_call_log_verify_sms_headers():
    return before_call_log_get_sms_headers()

def call_log_headers():
    return before_call_log_get_sms_headers()

def phone_bill_headers():
    params = before_call_log_get_sms_headers()
    params['Referer'] = 'http://service.tj.10086.cn/ics/myMobile/myBillQuery.html'
    return params

def personal_info_headers():
    params = before_call_log_get_sms_headers()
    params['Referer'] = 'http://service.tj.10086.cn/ics/myMobile/myInfo.html'
    return params
