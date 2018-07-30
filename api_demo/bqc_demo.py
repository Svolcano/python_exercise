import requests
import hashlib
import time
import json
import random


def get_time():
    return str(int(time.time()))

def get_sha1(a):
    if isinstance(a, str):
        a = a.encode()
    sha = hashlib.sha1()
    sha.update(a)
    return sha.hexdigest()

def get_nonce():
    return str(random.randint(1000, 9999))

def dict_sort(t, secret, apikey, nonce):
    a = [t, secret, apikey, nonce]
    a.sort()
    return ''.join(a)

# test1/wdakfkadfa2ds
def query(tel, name, apikey='test1', apisecret='wdakfkadfa2ds'):
    url = f'https://bqc.dianhua.cn/bang/index?apikey={apikey}'
    nonce = get_nonce()
    t = get_time()
    params = {
        'nonce':nonce,
        'timestamp':t,
        'signature':get_sha1(dict_sort(t, apisecret, apikey, nonce)),
        'tel':tel,
        'name':name
    }
    resp = requests.post(url, data=params)
    if resp.status_code == 200:
        obj = json.loads(resp.text)
        return obj
    return None

if __name__ == "__main__":
    tel = '18910153210'
    name = '这是一个公司的名称'
    ret = query(tel, name)
    print(ret)