import requests
import hashlib
import time


def get_time():
    return int(time.time())

def get_sha1(a, b=''):
    if isinstance(a, str):
        a = a.encode()
    sha = hashlib.sha1()
    sha.update(a)
    ret = sha.hexdigest()
    if b:
        assert ret == b
    return ret


def sort(t, secret):
    a = [t, secret]
    a.sort()
    return a

url = 'https://pns-dev.dianhua.cn:8094/active/search'
param = {
    'client_key':'',
    'tels':'',
    'signature':'',
    'timestamp':'',
}

resp = requests.post(url, data=param)
if resp.status_code == 200:
    print(resp.text)