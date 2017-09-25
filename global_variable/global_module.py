#coding:utf-8
import threading

class GG(object):
    global_a = 0
    global_b = 0
    global_lock = threading.Lock()