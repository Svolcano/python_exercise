#coding:utf-8
import threading

import queue

one_queue = queue.Queue()
two_queue = queue.Queue()
three_queue = queue.Queue()


def cache_one(one_queue,two_queue, three_queue, num_list):
    for i in num_list:
        print(i)
        if i % 5 == 0:
            one_queue.put(i)
        if i % 2 == 0:
            two_queue.put(i)
        if i % 7 == 0:
            three_queue.put(i)


num_list = range(10)
t = threading.Thread(target=cache_one, args=(one_queue,two_queue, three_queue, num_list))
t.start()
t.join()

try:
    while 1:
        a = one_queue.get_nowait()
        print("one_queue",a)
except Exception as e:
    print(e)
try:
    while 1:
        a = two_queue.get_nowait()
        print("two_queue", a)
except Exception as e:
    print(e)
try:
    while 1:
        a = three_queue.get_nowait()
        print("three_queue", a)
except Exception as e:
    print(e)