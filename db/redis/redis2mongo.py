import redis
import pymongo
import queue
import threading
import time

q = queue.Queue()

def redis_thread(q):
    host = '172.18.18.162'
    redis_port = 6379
    r = redis.Redis(host=host, port=redis_port, db=6)
    while 1:
        for k in r.keys():
            k = k.decode()
            v = r.get(k)
            v = v.decode()
            vs = v.split('___')
            one = {
                'tel':k,
                'name':vs[0],
                "addr":vs[1]
            }
            q.put(one)
            r.delete(k)
        time.sleep(30)

def mongo_thread(q):
    host = '172.18.18.162'
    mongo_port = 27017
    mh = pymongo.MongoClient(host=host, port=mongo_port)
    db = mh['bqc_tels_name']
    cols = db['tel_find_name']
    cols.create_index('tel', unique=True)
    cache = []
    while 1:
        try:
            one  = q.get()
            cache.append(one)
            if len(cache) == 1000:
                cols.insert_many(cache)
                cache = []
        except Exception as e:
            print(e)
    mh.close()



if __name__ == "__main__":
    rt = threading.Thread(target=redis_thread, args=(q,))
    rt.start()

    mt = threading.Thread(target=mongo_thread, args=(q,))
    mt.start()

    rt.join()
    mt.join()