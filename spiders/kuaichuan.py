# 快传号

import requests
import random
import hashlib
from pprint import pprint
from lxml import etree
import json
import re
import time
from urllib import parse
from dama.yundama import verify_captcha

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/601.1.10 (KHTML, like Gecko) Version/8.0.5 Safari/601.1.10",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; ; NCT50_AAP285C84A1328) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
]

UA = random.choice(_USER_AGENTS)

LOGIN_URL = 'https://login.360.cn/'
USER = '13633602987'
PWD = 'yu19920704'


class KuaiChuan(object):

    def __init__(self):
        pass

    @staticmethod
    def get_md5(pwd):
        md5 = hashlib.md5()
        b_pwd = pwd.encode('utf-8')
        md5.update(b_pwd)
        a = md5.hexdigest()
        print(a)
        return a

    @staticmethod
    def get_timestamp():
        return int(time.time() * 1000)

    @staticmethod
    def get_jquery_fun(t):
        return f'jQuery19108193473241252336_{t}'

    @staticmethod
    def get_token(s):
        t = KuaiChuan.get_timestamp()
        url = (f'https://login.360.cn/?func={KuaiChuan.get_jquery_fun(t)}'
               f'&src=pcw_so&from=pcw_so&charset=UTF-8&requestScema=https'
               f'&quc_sdk_version=6.7.0&quc_sdk_name=jssdk'
               f'&o=sso&m=getToken&userName={USER}&_={t}')
        resp = s.get(url, verify=False)
        resp_text = resp.text
        found = re.search('jQuery\d+_\d+\((.*)\)', resp_text)
        if found:
            ans_str = found.group(1)
            ans_obj = json.loads(ans_str)
            return ans_obj['token']
        return ''

    @staticmethod
    def get_jquery_result(t):
        found = re.search('jQuery.*?\((.*)\)', t)
        if found:
            ans_str = found.group(1)
            ans_obj = json.loads(ans_str)
            return ans_obj
        return None

    @staticmethod
    def get_capture(session):
        t = KuaiChuan.get_timestamp()
        capture_url = (f'http://i.360.cn/QuCapt/getQuCaptUrl?callback={KuaiChuan.get_jquery_fun(t)}'
                       f'&src=pcw_so&from=pcw_so&charset=UTF-8&requestScema=http&quc_sdk_version=6.7.0'
                       f'&quc_sdk_name=jssdk&captchaScene=login&captchaApp=i360&border=none&_={t}')

        resp = session.get(capture_url)
        resp_text = resp.text
        ans_obj = KuaiChuan.get_jquery_result(resp_text)
        if ans_obj:
            capture_pic_url = ans_obj['captchaUrl']
            pic_resp = session.get(capture_pic_url, verify=False)
            image_bin = pic_resp.content
            with open("a.jpeg", 'wb') as wh:
                wh.write(image_bin)
            cid, capture = verify_captcha(image_bin, 1005)
            return capture
        return 0, ''

    @staticmethod
    def get_login_errno(text):
        errno_re = r'&errno=(\d+?)&'
        found = re.search(errno_re, text)
        if found:
            return int(found.group(1))
        print("failed to get login errno ")
        return -1

    @staticmethod
    def get_login_errmsg(text):
        errno_re = r'&errmsg=(.*?)&'
        found = re.search(errno_re, text)
        if found:
            return parse.unquote(found.group(1))
        print("failed to get login errmsg ")
        return ''

    @staticmethod
    def logout(s):
        t = KuaiChuan.get_timestamp()
        logout_url = (f'https://login.360.cn/?func={KuaiChuan.get_jquery_fun(t)}'
                      f'&src=pcw_so&from=pcw_so&charset=UTF-8&requestScema=https'
                      f'&quc_sdk_version=6.7.0&quc_sdk_name=jssdk&o=sso&m=logout'
                      f'&_={t}')
        resp = s.get(logout_url, verify=False)
        ans_obj = KuaiChuan.get_jquery_result(resp.text)
        if ans_obj:
            errno = ans_obj['errno']
            if errno == 0:
                print('logout success')
                return True
            else:
                print('logout failed', ans_obj['errmsg'])
                return False
        print("logout failed")
        return False

    @staticmethod
    def init():
        s = requests.Session()
        s.headers.update({'User-Agent': UA})
        return s

    @staticmethod
    def close(s):
        try:
            s.close()
        except:
            pass

    @staticmethod
    def get_home_url(t):
        rp = re.compile('location.href=\'(.*?)\';')
        found = rp.search(t)
        if found:
            home_url = found.groups()[0]
            return home_url
        return ''

    @staticmethod
    def login(s):
        try:
            home_url = ''
            token = KuaiChuan.get_token(s)
            passwd = KuaiChuan.get_md5(PWD)
            login_param = {
                "src": "pcw_so",
                "from": "pcw_so",
                "charset": "UTF-8",
                "requestScema": "https",
                "quc_sdk_version": "6.7.0",
                "quc_sdk_name": "jssdk",
                "o": "sso",
                "m": "login",
                "lm": "0",
                "captFlag": "1",
                "rtype": "data",
                "validatelm": "0",
                "isKeepAlive": "1",
                "captchaApp": "i360",
                "userName": USER,
                "smDeviceId": "",
                "type": "normal",
                "account": USER,
                "password": passwd,
                "captcha": "",
                "token": token,
                "proxy": "http://kuaichuan.360.cn/psp_jump.html",
                "callback": "QiUserJsonp143798668",
                "func": "QiUserJsonp143798668",
            }
            login_resp = s.post(LOGIN_URL, data=login_param, verify=False)
            login_resp_text = login_resp.text
            error_no = KuaiChuan.get_login_errno(login_resp_text)
            error_msg = KuaiChuan.get_login_errmsg(login_resp_text)
            print(error_msg, error_no)
            if error_no == 0:
                print('success', login_resp_text)
                return KuaiChuan.get_home_url(login_resp_text)
            retry = 3
            while retry:
                captcha = KuaiChuan.get_capture(s)
                if not captcha:
                    print("failed to get captcha")
                    return home_url
                print(captcha)
                login_param['captcha'] = captcha
                login_resp = s.post(LOGIN_URL, data=login_param, verify=False)
                login_resp_text = login_resp.text
                error_no = KuaiChuan.get_login_errno(login_resp_text)
                error_msg = KuaiChuan.get_login_errmsg(login_resp_text)
                if error_no == 78000:
                    retry -= 1
                    continue
                elif error_no == 0:
                    print('login success', login_resp_text)
                    return KuaiChuan.get_home_url(login_resp_text)
                else:
                    print(error_no, error_msg)
                    return home_url
        except Exception as e:
            print(e, 'when login')
        return home_url

    @staticmethod
    def get_cookie(s, home_url):
        resp = s.get(home_url, verify=False)
        if resp.status_code == 200:
            return s.cookies.get_dict()
        else:
            return {}


def format_post_params(s=''):
    s = '''
    src=pcw_so&from=pcw_so&charset=UTF-8&requestScema=https&quc_sdk_version=6.7.0&quc_sdk_name=jssdk&o=sso&m=login&lm=0&captFlag=1&rtype=data&validatelm=0&isKeepAlive=1&captchaApp=i360&userName=13633602987&smDeviceId=&type=normal&account=13633602987&password=0528acfff590c7e6ec935501daac04ed&captcha=&token=820f20b7d9bfc4e8&proxy=http%3A%2F%2Fkuaichuan.360.cn%2Fpsp_jump.html&callback=QiUserJsonp115700314&func=QiUserJsonp115700314
    '''
    ret = {}
    s = s.strip()
    sl = s.split('&')
    for k in sl:
        kk, v = k.split('=')
        ret[kk] = v
    pprint(ret)
    return ret


def format_header(s=''):
    s = '''
    Accept: application/json, text/plain, */*
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: quCapStyle=2; quCryptCode=D6TqMQxFspm09vZHFMpamzOTlfkI4qi1gODXB2r1mHfHBQ0TJhs6n%252F8%252BUMVW1IDG; Q=u%3D%25O0%25P1%25PN%25Q3%25O7%25R5%26n%3D%26le%3DZGR4AmxlAmDyAQOkpF5wo20%3D%26m%3DZGZ2WGWOWGWOWGWOWGWOWGWOBGt3%26qid%3D328784150%26im%3D1_t01386b81c31e58d8dd%26src%3Dpcw_so%26t%3D1; T=s%3D4b1494578cc44a45bb024cb5a1b07085%26t%3D1550149305%26lm%3D%26lf%3D2%26sk%3D07497f5df9395745e71d2c39b4db50d3%26mt%3D1550149305%26rc%3D%26v%3D2.0%26a%3D1; __guid=65234612.1205336357213016600.1550149305682.5251; test_cookie_enable=null
Host: kuaichuan.360.cn
Proxy-Connection: keep-alive
Referer: http://kuaichuan.360.cn/
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36

    '''
    s = s.strip()
    ret = {}
    sl = s.split('\n')
    for one in sl:
        one = one.strip()
        k, v = one.split(': ')
        ret[k] = v
    pprint(ret)
    return ret


if __name__ == "__main__":
    # s = KuaiChuan.init()
    # try:
    #     home_url = KuaiChuan.login(s)
    #     if home_url:
    #         ck = KuaiChuan.get_cookie(s, home_url)
    #         print(ck)
    #         KuaiChuan.logout(s)
    # except Exception as e:
    #     print('fff', e)
    #     KuaiChuan.close(s)
    format_header()
