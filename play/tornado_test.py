#coding:utf8
import commands
import multiprocessing
import os
import sys


def fun():
    cmd = "http 127.0.0.1:8000/api/daily_report?date=20180205"
    print os.system(cmd)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    p_list = []
    for i in range(10):
        p = multiprocessing.Process(target=fun)
        p_list.append(p)

    for p in p_list:
        p.start()

    for p in p_list:
        p.join()

    print "main done"