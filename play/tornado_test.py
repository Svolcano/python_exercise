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


def jq():
    api_key = '0aa2cb33d0eaedc4abe412348045dc8'
    api_secret = '0b178ed2d1d049e46472711d8f92bf4'
    t = str(int(time.time()))
    nonce = str(random.randint(1000, 9999))
    in_p = [api_key, api_secret, t, nonce]
    in_p.sort()
    in_str = ''.join(in_p)
    m = hashlib.md5()
    m.update(in_str)
    v1 = m.hexdigest()
    m2 = hashlib.md5()
    m2.update(v1)
    python_result = m2.hexdigest()
    return nonce, t, python_result



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

def daily_fun(arg_in):
    arg, n, t, s = arg_in
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
    cmd = "http 127.0.0.1:18000/api/daily_report date==%s n==%s t==%s s==%s channel==xinde" % (arg, n, t, s)
    a = subprocess.check_output(cmd)
    print arg, a, check_db(arg)


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

def summary_list_fun(arg_in):
    arg, n, t, s = arg_in
    #cmd =u'http POST 127.0.0.1:18000/api/complex_report_summary start_date=="%s" end_date=="20181001"  cids==[3,4,5,6]  telecom=="联通" province=="北京" crawler_channel=="xinde" n==%s t==%s s==%s' % (arg, n, t, s)
    cmd =u'http POST 127.0.0.1:18000/api/complex_report_summary start_date=="%s" end_date=="20181001"  cids==[3,4,5,6]    crawler_channel=="xinde" n==%s t==%s s==%s' % (arg, n, t, s)
    a = subprocess.check_output(cmd.encode('gbk'))
    print arg, a, check_db_list(arg)


def summary_detail_fun(arg_in):
    arg, n, t, s = arg_in
    #cmd =u'http POST 127.0.0.1:18000/api/complex_report_detail start_date="%s" end_date=="20181001"  cids==[3,4,5,6]  telecom=="联通" province=="北京" crawler_channel=="xinde" n==%s t==%s s==%s' % (arg, n, t, s)
    cmd =u'http POST 127.0.0.1:18000/api/complex_report_detail start_date="%s" end_date=="20181001"   crawler_channel=="xinde" n==%s t==%s s==%s' % (arg, n, t, s)
    a = subprocess.check_output(cmd.encode('gbk'))
    print arg, a, check_db_list(arg)

def bill_static_report(arg_in):
    arg, n, t, s = arg_in
    cmd =u'http 127.0.0.1:18000/api/bill_static_report date==%s n==%s t==%s s==%s' % (arg, n, t, s)
    a = subprocess.check_output(cmd.encode('gbk'))
    print arg, a, check_db(arg)

def gen_day(start, n, r):
    """
    start 20180506
    """
    start = datetime.strptime(start, "%Y%m%d")
    for i in range(1, n):
        start += timedelta(days=1)
        yield (start.strftime("%Y%m%d"), r[0], r[1], r[2])


if __name__ == "__main__":
    multiprocessing.freeze_support()
    r = jq()
    print r
    # n = 4
    # a = list(gen_day('20180201', n, r))
    # print "dd---------------------------"
    # pool = multiprocessing.Pool(processes=4)
    # pool.map_async(daily_fun, a)
    # pool.close()
    # pool.join()
    # print "summary_detai---------------------------"
    # pool = multiprocessing.Pool(processes=4)
    # pool.map_async(summary_detail_fun, a)
    # pool.close()
    # pool.join()
    # print "summary_list---------------------------"
    # pool = multiprocessing.Pool(processes=4)
    # pool.map_async(summary_list_fun, a)
    # pool.close()
    # pool.join()
    # print "bill---------------------------"
    # pool = multiprocessing.Pool(processes=4)
    # pool.map_async(bill_static_report, a)
    # pool.close()
    # pool.join()

    # print "main done"