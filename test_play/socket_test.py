#coding:utf-8

import socket
import time
def test():
    dest_ip = ('127.0.0.1', 5544)
    handle = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    ret = handle.sendto(b"hello world", dest_ip)
    print(ret)
    handle.close()

while 1:
    time.sleep(1)
    test()

