import requests
import json
import csv
import time
import aiohttp
import asyncio
import threading
import queue
import uuid
import urllib.request

test_num = 100

url = 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baiduadv&wd=05782212292&rqlang=cn&rsv_enter=1&rsv_sug3=2'
query_header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.baidu.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
}
query_cookie = {
            "BAIDUID": "",
            "BD_CK_SAM": "1",
            "PSTM": '',
            "PSINO": "1",
        }

def test():
    resp = requests.get(url, headers=query_header, cookies=query_cookie)
    print(resp.status_code)
    print(resp.text)

def do_test():
    st  = time.time()
    for i in range(test_num):
        test()
    et = time.time()
    inv = et - st
    print(inv, test_num/float(inv))

def _gen_cookie_guid():
    u_str = uuid.uuid4()
    u_str = str(u_str)
    return u_str.replace('-', '')

def thread_test(q):
    while True:
        url = q.get()
        if not url:
            break
        query_cookie['BAIDUID'] = "%s:FG=1" % _gen_cookie_guid().upper()
        query_cookie['PSTM'] = str(int(time.time()))
        resp = requests.get(url, headers=query_header, cookies=query_cookie)
        print(resp.status_code)

def do_thread_test():
    thread_pool_size = 8
    q_list = [queue.Queue() for i in range(thread_pool_size)]
    t_list = [threading.Thread(target=thread_test, args=(q,)) for q in q_list]
    for t in t_list:
        t.start()
    
    for i in range(test_num):
        q_list[i % thread_pool_size].put(url)
        for t in t_list:
            if not t.is_alive:
                index = t_list.index(t)
                tt = threading.Thread(target=test, args=(q_list[index],))
                tt.start()
                t_list[index] = tt

    for q in q_list:
        q.put(None)
    for t in t_list:
        t.join()
    print('test done')


def do_frame(fun):
    st = time.time()
    fun()
    et = time.time()
    cost = et -st
    print(f"cost:{cost}, ratio:{test_num/cost}")


def do_async_test():
    async def get(url):
        query_cookie['BAIDUID'] = "%s:FG=1" % _gen_cookie_guid().upper()
        query_cookie['PSTM'] = str(int(time.time()))
        async with aiohttp.ClientSession(cookies=query_cookie) as session:
            async with session.get(url, headers= query_header) as resp:
                k = await resp.text()
                return k

    st = time.time()
    loop = asyncio.get_event_loop()
    tasks = []
    for i in range(test_num):
        tasks.append(get(url))
    done = loop.run_until_complete(asyncio.gather(*tasks))
    for i in done:
        print(i)
    loop.close()
    et = time.time()
    cost = et -st
    print(f"cost:{cost}, ratio:{test_num/cost}")

def do_single():
    for i in range(test_num):
        resp = urllib.request.urlopen(url)
        #print(resp.status_code)

do_frame(do_single)