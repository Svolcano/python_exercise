# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 16:56:51 2018

@author: admin
"""

import pymongo
import time
import datetime
import sys
import getopt
import pandas as pd
sys.path.append('../')
reload(sys)
sys.setdefaultencoding("utf8")


MONGO_CONFIG = {
    'host': '172.18.21.117',
    'port': 27017,
    'db': 'crs'
}
BEGIN_DATE='2017-04-20'
END_DATE='2018-04-21'
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

    def export_data(self,begindate=BEGIN_DATE,enddate=END_DATE):
        timeArray = time.strptime(begindate, "%Y-%m-%d")
        self.begindate = time.mktime(timeArray)
        timeArray = time.strptime(enddate, "%Y-%m-%d")
        self.enddate = time.mktime(timeArray)
#        data = self.conn['sid_info'].find({"end_time":{'$gte':self.begindate,'$lte':self.enddate},'status':0,
#                        'call_log_cache_hit_month_list':{'$exists':True,'$ne':[],}},
#                        {'tel':1,'call_log_cache_hit_month_list':1,
#                         'end_time':1,'tel_info.telecom':1,'_id':0})
#        return data
    
    def chax_miss(self,flag='10086'):
        count = self.conn['sid_info'].find({"end_time":{'$gte':self.begindate,'$lte':self.enddate},'status':0,
                        '$or':[{'call_log_possibly_missing_month_list':{'$exists':True,'$ne':[],}},
                        {'call_log_part_missing_month_list':{'$exists':True,'$ne':[],}},
                        {'call_log_missing_month_list':{'$exists':True,'$ne':[],}}]},
                               {'call_log_possibly_missing_month_list':1,
                                'call_log_part_missing_month_list':1,
                                'call_log_missing_month_list':1,'sid':1,'tel':1,'call_log_cache_hit_month_list':1,
                         'end_time':1,'tel_info.telecom':1,'_id':0})
        return count
    

if __name__=='__main__':
    pro_conn = Pro_MongodbConnection()
    opts, args = getopt.getopt(sys.argv[1:], "b:e:")
    for op, value in opts:
        if op == "-b":
            BEGIN_DATE = value
        elif op == "-e":
            END_DATE = value
    fusion_list=pro_conn.export_data(BEGIN_DATE,END_DATE)
    call_log_cache_hit_month_list=[]
    tel=[]
    end_time=[]
    telcom=[]
    sid=[]
    possibly_miss=[]
    part_miss=[]
    all_miss=[]
    err_miss=pro_conn.chax_miss()
    for x in err_miss:
        print x
        if x.has_key('call_log_possibly_missing_month_list'):
            possi=x['call_log_possibly_missing_month_list']
        else:
            possi=[]
        if x.has_key('call_log_part_missing_month_list'):
            part=x['call_log_part_missing_month_list']
        else:
            part=[]
        if x.has_key('call_log_missing_month_list'):
            miss=x['call_log_missing_month_list']
        else:
            miss=[]
            
        if x.has_key('call_log_cache_hit_month_list'):
            hit=x['call_log_cache_hit_month_list']
        else:
            hit=[]

        if list(set(possi).intersection(set(part)) or 
                list(set(possi).intersection(set(miss)))
                or list(set(part).intersection(set(miss)))):
            call_log_cache_hit_month_list.append(hit)
            tel.append(x['tel'])
            created_at=time.localtime(x['end_time'])
            created_at= time.strftime("%Y-%m-%d %H:%M:%S", created_at) 
            end_time.append(created_at)
            telcom.append(x['tel_info']['telecom'])
            sid.append(x['sid'])
            possibly_miss.append(x['call_log_possibly_missing_month_list'])
            part_miss.append(x['call_log_part_missing_month_list'])
            all_miss.append(x['call_log_missing_month_list'])
    rpt = pd.DataFrame({'call_log_cache_hit_month_list':call_log_cache_hit_month_list,'tel':tel,\
                        'end_time':end_time,'telcom':telcom,'sid':sid,
                        'possibly_miss':possibly_miss,'part_miss':part_miss,
                        'all_miss':all_miss})  
    rpt.to_csv(BEGIN_DATE+'data_fusion_err.csv',encoding = "gbk")
    
    print '异常记录总数= {} '.format(len(tel)) 
