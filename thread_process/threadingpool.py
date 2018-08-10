import socket
import threading
from threading import Thread
import threading
import sys
import time
import random
from queue import Queue

host = ''
port = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(3)

class ThreadPoolManger():
    """线程池管理器"""
    def __init__(self, thread_num):
        # 初始化参数
        self.work_queue = Queue()
        self.thread_num = thread_num
        self.__init_threading_pool(self.thread_num)

    def __init_threading_pool(self, thread_num):
        # 初始化线程池，创建指定数量的线程池
        for i in range(thread_num):
            thread = ThreadManger(self.work_queue)
            thread.start()

    def add_job(self, func, *args):
        # 将任务放入队列，等待线程池阻塞读取，参数是被执行的函数和函数的参数
        self.work_queue.put((func, args))

class ThreadManger(Thread):
    """定义线程类，继承threading.Thread"""
    def __init__(self, work_queue):
        Thread.__init__(self)
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        # 启动线程
        while True:
            target, args = self.work_queue.get()
            target(*args)
            self.work_queue.task_done()

# 创建一个有4个线程的线程池
thread_pool = ThreadPoolManger(4)

# 处理http请求，这里简单返回200 hello world
def handle_request(conn_socket):
    recv_data = conn_socket.recv(1024)
    print("++", recv_data)
    reply = 'HTTP/1.1 200 OK \r\n\r\n'
    reply += 'hello world'
    print ('thread %s is running ' % threading.current_thread().name)
    conn_socket.send(reply.encode('utf8'))
    conn_socket.close()

# 循环等待接收客户端请求
while True:
    # 阻塞等待请求
    conn_socket, addr = s.accept()
    # 一旦有请求了，把socket扔到我们指定处理函数handle_request处理，等待线程池分配线程处理
    thread_pool.add_job(handle_request, *(conn_socket, ))

s.close()
