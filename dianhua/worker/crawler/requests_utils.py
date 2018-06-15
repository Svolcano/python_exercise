#-*- coding: utf-8 -*-

import requests
import random
import urllib2
import traceback

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests import Session
from requests.compat import OrderedDict
from requests.hooks import default_hooks, dispatch_hook
from requests.cookies import cookiejar_from_dict
from requests.models import Request, DEFAULT_REDIRECT_LIMIT
from requests.utils import default_headers
from requests.packages.urllib3._collections import RecentlyUsedContainer
from requests.adapters import HTTPAdapter
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from com.logger import logger

if __name__ == '__main__':
    import sys
    sys.path.append('../../')
from setting.proxy_config import *

from com.redis_que import redis_que

REDIRECT_CACHE_SIZE = 1000

"""
    初始化Request

" @func __init__
"""
def __init__(self):
    self.headers = default_headers()
    self.auth = None
    self.proxies = {}
    self.hooks = default_hooks()
    self.params = {}
    self.stream = False
    self.verify = True
    self.cert = None
    self.max_redirects = DEFAULT_REDIRECT_LIMIT
    self.trust_env = True
    self.cookies = cookiejar_from_dict({})
    self.adapters = OrderedDict()
    self.mount('https://', HTTPAdapter())
    self.mount('http://', HTTPAdapter())
    self.redirect_cache = RecentlyUsedContainer(REDIRECT_CACHE_SIZE)

    self._get_proxies()
"""
    重写实现Request方法

" @func request
"
" @param method
" @param url
" @param params
" @param data
" @param headers
" @param cookies
" @param files
" @param auth
" @param timeout
" @param allow_redirects
" @param proxies
" @param hooks
" @param stream
" @param verify
" @param cert
" @param json
"""
def request(self, method, url, params=None, data=None, headers=None,
                cookies=None, files=None, auth=None, timeout=None, allow_redirects=True,
                    proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None):

    req = Request(
        method = method.upper(),
        url = url,
        headers = headers,
        files = files,
        data = data or {},
        json = json,
        params = params or {},
        auth = auth,
        cookies = cookies,
        hooks = hooks,
    )

    proxies = proxies or {}
    send_kwargs = {
        'timeout': timeout,
        'allow_redirects': allow_redirects,
    }
    prep = self.prepare_request(req)
    settings = self.merge_environment_settings(
        prep.url, proxies , stream, verify, cert
    )
    for times in xrange(2):
        if CONFIG_IS_OPEN:
            # 联通代理
            if proxies:
                proxies = proxies
            else:
                self._get_proxies()
                proxies = self.proxies or {}

            send_kwargs = {
                'timeout': timeout if timeout else TIMEOUT,
                'allow_redirects': allow_redirects if allow_redirects else ALLOW_REDIRECTS,
            }
            settings = self.merge_environment_settings(
               prep.url, proxies , stream, verify if verify else VERIFY, cert
            )
        send_kwargs.update(settings)
        try:
            # print proxies
            return self.send(prep, **send_kwargs)
        except:
            message = traceback.format_exc()
            # print '/n',message,'/n'
            # print times, proxies, self.proxies
            data = {
                'proxies':proxies,
                'send_kwargs':send_kwargs,
            }
            logger('proxies_log', 'ERROR', message, **data)
            self.proxies = None
            proxies = None
            if times == 1:
                proxies = proxies or {}
                settings = self.merge_environment_settings(
                   prep.url, proxies , stream, verify if verify else VERIFY, cert
                )
                send_kwargs.update(settings)
                return self.send(prep, **send_kwargs)
            continue

"""
    定于Proxies模板

" @func random_proxies
"""
def random_proxies():
    proxies = {}
    try:
        IP = redis_que.pop_proxies()
    except:
        return proxies 
    
    proxies = {
        "http": "http://{ip}:{port}".format(ip=IP, port=PROXIES_PORT),
        "https": "http://{ip}:{port}".format(ip=IP, port=PROXIES_PORT)
    }
    return proxies


"""
    判断IP是否可用, 定义IP获取规则

" @func get_random_proxies
"
" @param url
" @param times
"""
def get_random_proxies(self, times = 0):
    if not self.proxies:
        self.proxies = random_proxies()
        try:
            proxy_handler = urllib2.ProxyHandler(self.proxies)
            opener = urllib2.build_opener(proxy_handler)
            opener.open(IS_IP_AVAILABLE_URL, timeout=TIMEOUT)
        except:
            times += 1
            self.proxies = None
            if times >= TRY_TIMES:
                return self.proxies
            self._get_proxies(times)
    # return self.proxies


"""
    初始化注册方法

" @clz RequestsUtils
"""
class RequestsUtils(object):

    def __init__(self):
        Session.request = request
        Session._get_proxies = get_random_proxies

if __name__ == '__main__':

    """
    via off
    forwarded_for off
    request_header_access From deny all
    request_header_access Server deny all
    request_header_access WWW-Authenticate deny all
    request_header_access Link deny all
    request_header_access Cache-Control deny all
    request_header_access Proxy-Connection deny all
    request_header_access X-Cache deny all
    request_header_access X-Cache-Lookup deny all
    request_header_access Via deny all
    request_header_access X-Forwarded-For deny all
    request_header_access Pragma deny all
    request_header_access Keep-Alive deny all
    """

    RequestsUtils()
    import requests
    r = requests.Session().get("http://httpbin.org/headers")
    # print r.request.headers
    print r.request.headers
    print r.headers
    print r.text
