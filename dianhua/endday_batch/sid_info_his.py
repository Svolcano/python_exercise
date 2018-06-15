# -*- coding: utf-8 -*-
"""
Created on Thu May 24 10:01:14 2018

@author: huang
"""

import pymongo
import time
import datetime
import json
import sys
import getopt
import os
import pandas as pd
import numpy as np
sys.path.append('../')
stdout = sys.stdout
reload(sys)
sys.stdout = stdout
sys.setdefaultencoding("utf8")

MONGO_CONFIG = {
    'host': '172.18.21.117',
#    'host': '127.0.0.1',
    'port': 27017,
    'db': 'crs'
}

end_date='20180529'

class Pro_MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_pro_db_conn()

    def set_pro_db_conn(self):
        self.client = pymongo.MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[MONGO_CONFIG['db']]

    def get_begin_date(self,enddate=end_date):
        timeArray = time.strptime(enddate, "%Y%m%d")
        self.enddate = time.mktime(timeArray)
        data = self.conn['sid_info'].find({"end_time":{'$lte':self.enddate}},{'end_time':1,'_id':0}).sort([('end_time',1)]).limit(1)   
        for x in data:
            time_temp=x['end_time']
        begin_date=time.strftime("%Y%m%d", time.localtime(time_temp))
        return begin_date
db_conn=Pro_MongodbConnection()
begin_date=db_conn.get_begin_date()
fp=open('cmd.sh','w+')
while(1):
    if begin_date>=end_date:
        break
    timeArray = time.strptime(begin_date, "%Y%m%d")
    timeArray = time.mktime(timeArray)
    one_day_date=timeArray+86400
    one_day_date=time.strftime("%Y%m%d", time.localtime(one_day_date))
    cmd='python /data/script_exec/sid_info_anly/sid_info_anly.py -b{0} -e{1}'.format(begin_date,one_day_date)
#    cmd='python sid_info_anly.py -b{0} -e{1}'.format(begin_date,one_day_date)
    begin_date=one_day_date
    fp.write(cmd+'\n')
fp.close()


    
    
fp=open('cmd.sh','r')
lines=fp.readlines()
for i,line in enumerate(lines):
    cmd=line.replace('\n','')
    print i,cmd
    p=os.popen(cmd)
    x=p.read()
    p.close()
fp.close
