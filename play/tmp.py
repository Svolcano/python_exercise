import threading
import requests
import queue
import time



def do_get(q):
    while 1:
        # url = 'localhost:9080'
        url = q.get()
        if url is None:
            break
        resp = requests.get(url)
        if resp.status_code == 200:
            # print(resp.text)
            pass
        else:
            print('failed')


thread_num = 20

q_list = [queue.Queue() for i in range(thread_num)]
t_list = [threading.Thread(target=do_get, args=(q,)) for q in q_list ]

for t in t_list:
    t.start()

all_requests_number = 10000
index = 0
st = time.time()
url = 'http://172.18.18.175:9080'
while all_requests_number:
    q_list[index].put(url)
    index = (index+1) % thread_num
    all_requests_number -= 1

for q in q_list:
    q.put(None)

for t in t_list:
    t.join()

print("all_done", time.time()-st)