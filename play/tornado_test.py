# coding:utf8
import subprocess
import multiprocessing
import os
import sys
import time
import pymongo
import random
import hashlib
from datetime import datetime , timedelta

def check_db(arg):
        db_host = '172.18.19.219'
        db_port = 27017
        db_name = 'crs'
        db_collection = 'sid_info_data_rpt'
        condition = {
            'rpt_date' : '%s' % arg,
        }

        handler = pymongo.MongoClient(db_host, db_port)
        db = handler[db_name][db_collection]
        a = db.find(condition)
        b = a.count()
        return b

def daily_fun(arg):
    def check_db(arg):
        db_host = '172.18.19.219'
        db_port = 27017
        db_name = 'crs'
        db_collection = 'sid_info_data_rpt'
        condition = {
            'rpt_date' : '%s' % arg,
        }

        handler = pymongo.MongoClient(db_host, db_port)
        db = handler[db_name][db_collection]
        a = db.find(condition)
        b = a.count()
        return b
    cmd = "http 127.0.0.1:8000/api/daily_report date==%s n==1 t==2 s==3" % arg
    a = subprocess.check_output(cmd)
    print arg, a, check_db(arg)

def xd_daily_fun(arg):
    def check_db_xd(arg):
        db_host = '172.18.19.219'
        db_port = 27017
        db_name = 'crs'
        db_collection = 'sid_info_data_rpt'
        condition = {
            'rpt_date' : '%s' % arg,
            'crawler_channel' : 'xinde'
        }

        handler = pymongo.MongoClient(db_host, db_port)
        db = handler[db_name][db_collection]
        a = db.find(condition)
        b = a.count()
        return b
    cmd = "http 127.0.0.1:8000/api/xd_daily_report date==%s n==1 t==2 s==3" % arg
    a = subprocess.check_output(cmd)
    print arg, a, check_db_xd(arg)

def check_db_list(arg):
        db_host = '172.18.19.219'
        db_port = 27017
        db_name = 'crs'
        db_collection = 'sid_info_data_rpt'
        condition = {
            'rpt_date' : {'$gte' :"%s"% arg, '$lte':'20181001'},
            'crawler_channel' : 'xinde',
            'telecom': "联通",
            'province': "北京",
        }

        handler = pymongo.MongoClient(db_host, db_port)
        db = handler[db_name][db_collection]
        a = db.find(condition)
        b = a.count()
        return b

def summary_list_fun(arg):
    cmd =u'http POST 127.0.0.1:8000/api/complex_report_summary start_date="%s" end_date="20181001"  cids:=[3,4,5,6]  telecom="联通" province="北京" crawler_channel="xinde" n=1 s=2 t=3' % arg
    a = subprocess.check_output(cmd.encode('gbk'))
    print arg, a, check_db_list(arg)


def summary_detail_fun(arg):
    cmd =u'http POST 127.0.0.1:8000/api/complex_report_detail start_date="%s" end_date="20181001"  cids:=[3,4,5,6]  telecom="联通" province="北京" crawler_channel="xinde" n=1 s=2 t=3' % arg
    a = subprocess.check_output(cmd.encode('gbk'))
    print arg, a, check_db_list(arg)

def bill_static_report(arg):
    cmd =u'http 127.0.0.1:8000/api/bill_static_report date==%s n==1 t==2 s==3' % arg
    a = subprocess.check_output(cmd.encode('gbk'))
    print arg, a, check_db(arg)

def gen_day(start, n):
    """
    start 20180506
    """
    start = datetime.strptime(start, "%Y%m%d")
    for i in range(1, n):
        start += timedelta(days=1)
        yield start.strftime("%Y%m%d")


def jq():
    time_v = int(time.time())
    nonce = random.randint(1000,10000)
    in_p = [api_key, api_secret, time_v, nonce]
    in_p.sort()
    in_str = ''.join(in_p)
    m = hashlib.md5()
    m.update(in_str)
    v1 = m.hexdigest()
    m2 = hashlib.md5()
    m2.update(v1)
    python_result = m2.hexdigest()
    print php_v, python_result
    print  python_result == php_v
api_key = '0aa2cb33d0eaedc4abe412348045dc8'
api_secret = '0b178ed2d1d049e46472711d8f92bf4'

if __name__ == "__main__":
    multiprocessing.freeze_support()


    pool = multiprocessing.Pool(processes=4)
    pool.map_async(xd_daily_fun, gen_day('20180101', 32))
    pool.close()
    pool.join()

    pool = multiprocessing.Pool(processes=4)
    pool.map_async(summary_detail_fun, gen_day('20180101', 32))
    pool.close()
    pool.join()

    pool = multiprocessing.Pool(processes=4)
    pool.map_async(summary_list_fun, gen_day('20180101', 32))
    pool.close()
    pool.join()

    pool = multiprocessing.Pool(processes=4)
    pool.map_async(bill_static_report, gen_day('20180101', 32))
    pool.close()
    pool.join()

    pool = multiprocessing.Pool(processes=4)
    pool.map_async(bill_static_report, gen_day('20180101', 32))
    pool.close()
    pool.join()
    print "main done"