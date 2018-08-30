from utils.search import  BaiduEngine
from utils.constant import we_load_dict, load_ap
import csv
import multiprocessing
import time
import redis
import ujson

key_set, company_suffix = we_load_dict()
ap = load_ap()
redis_host = '172.18.18.173'
redis_db = 2
pool = redis.ConnectionPool(host=redis_host, port=6379,
                                decode_responses=True, db=redis_db)

def get_redis_hander():
    r = redis.Redis(connection_pool=pool)
    return r

def load_data():
    fn = "aa.csv"
    res = []
    i = 0
    count = 2
    tel_set = set()
    with open(fn, "r", encoding='utf8') as fh:
        cr = csv.reader(fh)
        for line in cr:
            tel = line[0].strip()
            tel_set.add(tel)
            res.append(tel)
            i+=1
            if i >= count:
                break
    return res


def parse_one(iq):
    global key_set, company_suffix, ap
    r = get_redis_hander()
    while True:
        try:
            tel = iq.get()
            if tel is None:
                break
            bd = BaiduEngine(tel, key_set=key_set, company_suffix=company_suffix, ap=ap)
            bd.parse()
            r.set(tel, ujson.dumps(bd.ret_res))
        except Exception as e:
            print(e)


def run(data):
    st = time.time()
    r = get_redis_hander()
    r.flushdb()
    thread_size = 8
    q_list = [multiprocessing.Queue() for i in range(thread_size)]
    t_list = [multiprocessing.Process(target=parse_one, args=(q,)) for q in q_list]
    for t in t_list:
        t.start()
    i = 0
    c = 0
    for tel in data:
        q_list[0].put(tel)
        c += 1
        i = (i+1) % thread_size
    print("put done")
    for q in q_list:
        q.put(None)
    print("terminate done")
    for t in t_list:
        t.join()
    print("join done")
    deal_ret = []
    all_key = r.keys('*')
    for k in all_key:
        v = r.get(k)
        ko = ujson.loads(v)
        tel = ko.get('i_tel')
        all_name = ko.get('all_find_companys', '')
        query_url = ko.get('query_url', '')
        time_cost = ko.get('time_cost')
        all_name = str(all_name)
        deal_ret.append((tel, query_url, all_name, time_cost))
    print("redis get done")
    with open("out.csv", 'w', encoding='utf8', newline='') as wh:
        cw = csv.writer(wh)
        cw.writerows(deal_ret)
    print("write file done")
    print(f"time cost:{time.time() - st}")


if __name__ == "__main__":
    input_data = load_data()
    run(input_data)