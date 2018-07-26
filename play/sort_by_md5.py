import requests
import ujson
import csv
import threading
import time
import os
import asyncio
import aiohttp
import queue
import shutil

#file_root_path = '/home/data/'
file_root_path = 'D:/pro_test_data'
file_name1 = 'dwa_d_ia_s_user_prod_0716.txt'
file_name2 = 'dwa_d_ia_s_user_prod_transcoded.txt'
md5_tel_dict = 'md5_tel.txt'


async def get_tel(md5):
    url = "http://decrypt.dianhua.cn/decrypt/?apikey=yuloreInner&country=86&uid=yulore&app=decryptTel&ver=1.0&v=1&h=1&tel=%s" % md5
    retry = 10
    tel = ''
    loop = asyncio.get_event_loop()
    while retry:
        async with aiohttp.ClientSession(loop=loop) as session:
            async with session.get(url=url) as response:
                text = await response.read()
                res_obj =ujson.loads(text)
                tel = res_obj.get('telNum', '')
                if tel:
                    break 
        retry -= 1
    return tel

async def _get_all_tel():
    ms_l = []
    with open("md5.txt", 'r') as fh:
        for d in fh:
            ms_l.append(d.strip())
    ms_l_t = []   
    c = 0    
    for md in ms_l:
        tel = await get_tel(md)
        ms_l_t.append((md, tel))
        c += 1
        print(md, tel, c)
    with open('md5_tel.txt', 'w', encoding='utf8', newline='') as wh:
        csv_w = csv.writer(wh)
        csv_w.writerows(ms_l_t)


def get_all_tel():
    st = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_get_all_tel())
    loop.close()
    et = time.time()
    print("cost: %.3f" % (et-st))

################################################

g_queue_size = 50000
g_cache_len = 10000

def deal_with_line(data):
    ll = data.split(' ')
    ll = [t for t in ll if t]
    ll[0] = ll[0].lower()
    return ll

def save_md5(cache_path, md5, vs):
    with open(f'{cache_path}/{md5}.csv', 'a', encoding='utf8', newline='') as fh:
        cw = csv.writer(fh)
        cw.writerows(vs)
 

def save_cache(cache, cache_path):
    print('save_cache')
    fh_dict = {}
    for md5 in cache:
        v = cache[md5]
        save_md5(cache_path, md5, v)

def produce(src_file_path, q):
    with open(src_file_path, 'r', encoding='utf8') as src_fh:
        c = 0
        for l in src_fh:
            l = l.strip()
            if not l:
                continue
            q.put(l)
            c += 1
            print('put', c)
    q.put(None)


def consumer(dest_fh, cache_path, q, dd):
    cache = {}
    while 1:
        data = q.get(block=True)
        print('get')
        if data == None :
            break
        ret = deal_with_line(data)
        md5 = ret[0]
        ret.insert(1, dd[md5])
        if md5 in cache:
            cache[md5].append(ret)
        else:
            cache[md5] = []
        if len(cache) == g_cache_len:
            save_cache(cache, cache_path)
            cache.clear()
    if len(cache):
            save_cache(cache, cache_path)
            cache.clear()


def load_dict(f_path):
    dd = {}
    with open(f_path, 'r', encoding='utf8') as fh:
        cr = csv.reader(fh)
        for l in cr:
            dd[l[0]] = l[1]
    return dd


def deal_with_file1(f=file_name1):
    q = queue.Queue(maxsize=g_queue_size)
    src_file_path = f"{file_root_path}/{f}"
    dict_path = f"{file_root_path}/{md5_tel_dict}"
    cache_path = f"{file_root_path}/cache_{file_name1.split('.')[0][-5:]}"
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)
    os.makedirs(cache_path)
    dest_file_path = src_file_path + '.out'
    dd = load_dict(dict_path)
    pt = threading.Thread(target=produce, args=(src_file_path, q))
    pt.start()
    ct = threading.Thread(target=consumer, args=(dest_file_path, cache_path, q, dd))
    ct.start() 
    ct.join()


def ssort():
    st = time.time()
    deal_with_file1(file_name1)
    #merge1()
    et = time.time()
    print("merge done", et - st)

if __name__ == "__main__":
    ssort()

