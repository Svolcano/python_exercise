import requests
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
import re


def get_blackbox(driver):
    driver.switch_to.frame('SI2_func')
    text = driver.page_source
    bb = re.search(r'<input.*id=.blackbox.*value=.(.*)[\'|"]', text)
    return bb.group(1)


def get_analysis(driver):
    t = {}
    for d in driver.get_cookies():
        if 'name' in d:
            t[d['name']] = d['value']
    return t


def get_iovationKey(driver):
    src = driver.page_source
    r =re.search(r"top.iovationKey.*'(.*)';", src)
    ms = r.group(1)
    return ms



def get_loginstr(username, pwd, iovationkey, blackbox):
    '''
    '''
    return ('username=%s&'
            'passwd=%s&'
            'langx=zh-cn&'
            'auto=%s&'
            'blackbox=%s&'
            ) % (username, pwd, iovationkey, blackbox)


def login():
    url = 'http://www.hga025.com/'
    header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '2896',
        'Content-type': 'application/x-www-form-urlencoded',
        'Host': 'www.hga025.com',
        'Origin': 'http://www.hga025.com',
        'Referer': 'http://www.hga025.com/app/member/',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
    }
    desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
    for k, v in header.items():
        desired_capabilities['phantomjs.page.customHeaders.{}'.format(k)] = v
    session = requests.session()
    c = {}
    hd = webdriver.PhantomJS()
    #hd.delete_all_cookies()
    hd.get(url)
    iovationKey = get_iovationKey(hd)
    print(iovationKey)
    analy = get_analysis(hd)
    print(analy)
    requests.utils.add_dict_to_cookiejar(session.cookies, analy)
    bb = get_blackbox(hd)
    #hd.switch_to.default_content
    print(bb)
    login_url = 'http://www.hga025.com/app/member/new_login.php'
    data_str = get_loginstr('lt885509', 'aabb8899', iovationKey, bb)
    header['Content-Length'] = str(len(data_str))
    resp = session.post(login_url, data=data_str, headers=header)
    print(resp.text, resp.headers)


if __name__ == "__main__":
    login()



