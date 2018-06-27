#coding:utf8

import Queue
import threading
import time

def fun(in_q):
    while 1:
        a = in_q.get(block=True)
        print threading.current_thread().name, a
        if a is None:
            break
t_num = 4
in_q = Queue.Queue(maxsize=2)
t_l = [threading.Thread(target=fun, args=(in_q,)) for i in range(t_num)]
for t in t_l:
    t.start()

for i in range(10000):
    in_q.put(i)
for k in range(t_num):
    in_q.put(None)

for t in t_l:
    t.join()

print "done"

