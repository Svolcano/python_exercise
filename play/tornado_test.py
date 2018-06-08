#coding:utf8
import commands
import multiprocessing
import os
import sys
import time
from datetime import datetime , timedelta


def fun(arg):
    cmd = "http 127.0.0.1:8000/api/xd_daily_report?date=%s" % arg
    print os.system(cmd)


def gen_day(start, n):
    """
    start 20180506
    """
    start = datetime.strptime(start, "%Y%m%d")
    for i in range(1, n):
        start += timedelta(days=1)
        yield start.strftime("%Y%m%d")
    

if __name__ == "__main__":
    multiprocessing.freeze_support()
    p_list = []
    for a in gen_day('20180201', 35):
        fun(a)

    print "main done"

    