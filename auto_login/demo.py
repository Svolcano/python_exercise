import requests
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import execjs


def get_ftblackbox():
    pass

def get_ttblackbox():
    pass


def get_blackbox():
    pass


def get_cookie():
    pass

def get_token():
    #work
    js_url = 'https://mpsnare.iesnare.com/snare.js'
    header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'mpsnare.iesnare.com',
        'Referer': 'http://sbc.ry00000.com/iovation/vindex.html?webProtocal=http&webDomain=www.hga025.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
    }
    desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
    for k, v in header.items():
        desired_capabilities['phantomjs.page.customHeaders.{}'.format(k)] = v
    hd = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
    hd.get(js_url)
    c = hd.get_cookies()
    print(c[0]['name'],c[0]['value'],)


def get_gid():
    #failed
    js_url = 'https://www.google-analytics.com/analytics.js'
    header = {
        ':authority': 'www.google-analytics.com',
        ':method': 'GET',
        ':path': '/analytics.js',
        ':scheme': 'https',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'Referer': 'http://www.hga025.com/app/member/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
    }
    desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
    for k, v in header.items():
        desired_capabilities['phantomjs.page.customHeaders.{}'.format(k)] = v
    hd = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
    r1 = requests.get(js_url)
    r2 = hd.get(js_url)
    c = hd.get_cookies()
    print(r1, r2, c, hd.page_source)


def login():
    url5 = 'http://www.hga025.com/app/member/new_login.php'
    rsp5 = requests.post(url5, data=data, headers=header, cookies=cookie)
    bs5 = BeautifulSoup(rsp5.text, 'html.parser')


def exejs():
    url = 'http://www.googletagmanager.com/gtm.js?id=GTM-WNMXQF'
    header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'www.googletagmanager.com',
        'Referer': 'http://www.hga025.com/app/member/',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
    }
    desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
    for k, v in header.items():
        desired_capabilities['phantomjs.page.customHeaders.{}'.format(k)] = v
    hd = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
    rp = hd.get(url)
    print(hd.get_cookies())


if __name__ == "__main__":
    header = {
        'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'''
    }
    data = '''username=lt885509&passwd=aabb8899&langx=zh-cn&auto=EFBHCF&blackbox=0400AKHeWb1CT4UHcCiyOFFxUOgYeCMpnjNhUzPtu#hsUXx8PrL/sgEx7mZ7#EnMfC4LgId6dDaNkNU3koT6Hdqn9fi8fptuT4V#57LnmsP38HaJ#KmAMZ21YUzZey/rZNEc4037zRqlee5yFcSkqakryzwj6OrTK/Zzi7pxCD5kB99#UiRMTdA2wF4mvFKAFzE#ex1TLARybUr4X35U0eVzPZLWOlxpt0YU9cmKrLQxcxA5OE2KkOZe/0jXzk77ILZ/eUsQ7RNrLro1kTKIs1496YkpIh3A707lm2e25SQbo1N9hSupCh0nrdvl2zl01373HKNCV/CVusXmY1XpDGBtye8mR20/oWqfE9LST5p23mXKf2hhwqstJ#rhYKIcxurYOW/647wT3aapeLTsE#XfZEsys#sxW8mW8sTzEDL#2GfZsbSyl9kH53ErNjRzWcwCIVu##nmS2BfegODK6ANpJkBHbtl2L6#On6hGq2RYwiqS1jpcabdGFCw#Jld00Kp8oBvPA6u04i1McDaVptovbQl2Y1Y/iacvjAucj41K34TIB9QxnksoWmbZIYRwZnYim9ceHDKRCiK4xI1RTIYC8ouD71qCKcmZqa#c5UMfdLNXqLz#1vlqUAr9dE2jcfl0wgroQBfpyuIcH#e41nTPEq/GsepjzbdjVTw2C4oQ2p6vWc20/w4QKST/riUqiozfAOitx40UDzaLaxNWMM2S8UTjbKzZpUNBRBMCEOrXqvjkTEmWwQPJZ0dJgNEI2eLrsC2ODMcwYCTnx/Hf5FzDPQjgcQmcY6YbS8Sher9jz8ZeEEHPc6ASbxv#PpDzuoNj2bgmK84#JhEE17xPvsMMFVmX90phXFvaXbY#Ny6EWFSWyWZ9R/10NvcWvRjQFbq8XMYkf0ShP/3saErTg5#rRdhejcFMJfaGlo2fO/6U2rfQOTaZmbqh/pCxcRLd9jcNIKh8cj1oeYpV8Lsfk4HM8hLwVQQVe5gdQVL2duy/r6AaSu2CWE7xND/KhUgGeNqKwHaf9f8MJCfm/HSHTxG/ZJvXHhwykQoiwoG4Fz5os4x5VpgkQXTQzbLmsQMABG0XzWYTHlPicx47ke4gho#vc6h8ziXiREbEDPWCyXC02/rcPlZPhNwqdAj#k93Kn7p/PqrIKVOONpnVc9dV/kxCbF1HrEuE2uSOAzRk4BEEa#l0Q4A/TKlI1kJI4/wX97IA0ADaJWS7nwj2SgUfyd91CMe8mnFiPj0iHraRrhCMqdRGs/rx2nWC76wkYGoaEmVFxA9x3qRKbjPnLlQ8#sHRpJb/jSkzy7mZIDPqkpCE0sN6f7k2KJ2ENQ==;0400bpNfiPCR/AUNf94lis1ztpUkBF3gMqJVUvQPAuo2LgKAC3SfR7deSLSUZpybFcXA9SHJSmUeiL2574HgzbCSorEfVk9EjAzqJqKR0TY3#IFLuAeH2h6vGuixLXGBICA18sQyiQagYnGrecmfaqukfc6mhllQ7/XHYDvethm0ixXKgDzSlcJpdqYR9FtpPsLf0LVQmADUFBlDgm50c6V/UsE25KpZgUeTfmJPV146JuMtAB9loDuNKLAcesNbcdJjGc#x7ZkkKyrh7d/W78RPOnlWmCRBdNDNnZsKRSTH#INXmndwxC1qdooOq2/rQwMyfTKQFDeDVWVUgBbu4NCNc/UJiL5MGqvebjzZg2dKb7GN#C/99KOKmSBk5ooFeBhZhCASX#GDOzCQpDzW48ilKJHhbENIDDJO3BLJhsUTViU85h7zmVcUJNpNdLlhvHt3SqNpBOnsVOHd6Wf1rrmlEKIGit1Q7ozZo2Ji61Ck5rdiHsRUrA6QS4uoKmLN7sWcyP/U1#EY5mcwZ8YN8wmMvR62ka4QjKnURrP68dp1gu9XM7bPcd/7vrmZnC9N#MV7hZEdr7sAeq0s1XJ1i2WxjESGZaTVu1fFDX8icOWPZcy4Xo6JR#o8uNh2BeaMmRyXBWs8HpCjwMaETb/DddSD#NYP3/gOZ8g3uFbUdAika0AB84#POrI4MvGQ6XvQZB3u6LuRi#5UtR#6/vHLXw14vAHzj486sjgyHfk2EOMYpr6l2pKAmu1wluCISazs9PD83/seKcOlvXrGxhKauwqEWLxUN0sYF8r08f8uCcC0xODcb#CqMKE6vfSnjAI#dNjqC4S1xrCX3HdMyPpjzYuuV#VhT2JQxvTdC24eZzo97tw16kQoiglK7BJDLfM/X8TvaSyxlUFCiGEdsE8OdwolivehTqT3rw1rR9l0dEJHzndNg#95/NceoRDAstLN4US59PE4fRZTRwzCQai4/k8/K5lhazmeAdS6uwLLNTE9qpx0SycwUaGowrwwxLEPmOlCNL0IkkwWQDkNCt4dbWG12CkicvSlZ60t4slfC5U8v3RtDejX3Y9Ewm1AfntOdBWf1TjX#G7rPnMFCE1XRfN#HZ21ET4rhaHYN4YbjEiJxk0sBAAQcH4loNwTidneZ5Wedvp3EOKiSx6OC0ceqoTbyG/m3Zqxt3w1Bn6LxoWOnZu64rr07LwRGXZpyc7oQIV63xadNE2jqb6o3IAEdbB#xCVNS65m83pQ#qMTRH6GRVfg7HAcS5fnS33EPopga4/Zy2vyIvB4Wzvugm1PCON3QfZ9psE08sbHbfwiCeLtkwTjK9GFecOQizvulKce2GXNanuG3yN14fd2bO2#D0lWhXNZLD097iGQgmfSM07NWhH7TJ2/klrEPMrKB#CSvojDYogWOE58#ALRokCz#wGdb#VoLbLteYSCBbncVWWlL2ICQTpkxNErnTq3GT5/OotW4splW3UJXUw='''
    cookie = {
        'protocolstr': 'http',
        '_ga': 'GA1.2.1535290052.1521300572',
        '_gid': 'GA1.2.970677319.1521300572',
    }
    iovationURL = 'http://sbc.ry00000.com/iovation/vindex.html?webProtocal=http&webDomain=www.hga025.com'
    iovation_Proxy = 'http://sbc.ry00000.com'
    exejs()



