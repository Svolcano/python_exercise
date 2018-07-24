import requests
import hashlib
import time
import json


def get_time():
    return str(int(time.time()))

def get_sha1(a):
    if isinstance(a, str):
        a = a.encode()
    sha = hashlib.sha1()
    sha.update(a)
    return sha.hexdigest()


def dict_sort(t, secret):
    a = [t, secret]
    a.sort()
    return ''.join(a)


def query(tel, secret='wdakfkadfa2ds', client_key='test1'):
    url = 'https://pns-dev.dianhua.cn:8094/active/search'
    now_time_s = get_time()
    #print(now_time_s)
    ss = dict_sort(now_time_s, secret)
    #print(ss)
    signature = get_sha1(ss)
    #print(signature)
    param = {
        'client_key':client_key,
        'tels':tel,
        'signature':signature,
        'timestamp':now_time_s,
    }

    resp = requests.post(url, data=param)
    if resp.status_code == 200:
        obj = json.loads(resp.text)
        return obj
    return None

if __name__ == "__main__":
    tel = '18910153210'
    ret = query(tel)
    print(ret)