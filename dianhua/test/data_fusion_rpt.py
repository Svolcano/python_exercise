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
#    'host': '127.0.0.1',
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
#        print self.begindate
#        print self.enddate
        data = self.conn['sid_info'].find({"end_time":{'$gte':self.begindate,'$lte':self.enddate},'status':0,
                        'call_log_cache_hit_month_list':{'$exists':True,'$ne':[],},'cid':{'$nin':['1','3']}},
                        {'tel':1,'call_log_cache_hit_month_list':1,
                         'end_time':1,'tel_info.telecom':1,'_id':0})
        return data
    
    def count_10010_miss(self,flag='10010'):
        all_sid = self.conn['sid_info'].find({"end_time":{'$gte':self.begindate,'$lte':self.enddate},'status':0,'tel_info.flow_type':flag,'cid':{'$nin':['1','3']}},{'tel':1,'_id':0})
        yulore_all_no_miss_sid = self.conn['sid_info'].find({"end_time":{'$gte':self.begindate,'$lte':self.enddate},'status':0,'tel_info.flow_type':flag,
                        'call_log_possibly_missing_month_list':[],
                        'call_log_part_missing_month_list':[],
                        'crawler_channel':{'$ne':'xinde'},
                        'call_log_missing_month_list':[],'cid':{'$nin':['1','3']}},{'tel':1,'_id':0})
        xinde_all_no_miss_sid = self.conn['sid_info'].find({"end_time":{'$gte':self.begindate,'$lte':self.enddate},'status':0,'tel_info.flow_type':flag,
                        'call_log_possibly_missing_month_list':[],
                        'crawler_channel':'xinde',
                        'call_log_missing_month_list':[],'cid':{'$nin':['1','3']}},{'tel':1,'_id':0})
        if (flag=='189' or flag=='10000'):
            print 'all_sid='+str(all_sid.count())
            print 'yulore_all_no_miss_sid='+str(yulore_all_no_miss_sid.count())
            print 'xinde_all_no_miss_sid='+str(xinde_all_no_miss_sid.count())
        miss_sid_count=all_sid.count()-yulore_all_no_miss_sid.count()-xinde_all_no_miss_sid.count()
        all_tel_list=[]
        for tel in all_sid:
            all_tel_list.append(tel['tel'])
        all_tel_count=len(list(set(all_tel_list)))
        
        no_miss_tel_list=[]
        for tel in yulore_all_no_miss_sid:
            no_miss_tel_list.append(tel['tel'])
        for tel in xinde_all_no_miss_sid:
            no_miss_tel_list.append(tel['tel'])
        no_miss_tel_count=len(list(set(no_miss_tel_list)))
        
        miss_tel_count=all_tel_count-no_miss_tel_count
        
        return miss_sid_count,miss_tel_count,all_tel_count,all_sid.count()
    
    
    def count_10010_hit(self,flag='10010'):
        hit_sid = self.conn['sid_info'].find({"end_time":{'$gte':self.begindate,'$lte':self.enddate},'status':0,
                        'tel_info.flow_type':flag,
                        'call_log_cache_hit_month_list':{'$exists':True,'$ne':[]},'cid':{'$nin':['1','3']}},{'tel':1,'_id':0})
        hit_sid_list=[]
        for sid in hit_sid:
            hit_sid_list.append(sid['tel'])
        hit_sid_count=len(hit_sid_list)
        hit_tel_count=len(list(set(hit_sid_list)))
        return hit_sid_count,hit_tel_count
    
    def count_10086_miss(self):
        return self.count_10010_miss('10086')
    
    def count_10086_hit(self):
        return self.count_10010_hit('10086')
    
    def count_189_miss(self):
        sid_189_miss,tel_189_miss,tel_189_all,sid_189_all= self.count_10010_miss('189')
        sid_10000_miss,tel_10000_miss,tel_10000_all,sid_10000_all= self.count_10010_miss('10000')
        print 'sid_189_miss='+str(sid_189_miss)
        print 'tel_189_miss='+str(tel_189_miss)
        print 'sid_10000_miss='+str(sid_10000_miss)
        print 'tel_10000_miss='+str(tel_10000_miss)
        return sid_189_miss+sid_10000_miss,tel_189_miss+tel_10000_miss,tel_189_all+tel_10000_all,sid_189_all+sid_10000_all
    
    def count_189_hit(self):
        sid_189_hit,tel_189_hit= self.count_10010_hit('189')
        sid_10000_hit,tel_10000_hit= self.count_10010_hit('10000')
        return sid_189_hit+sid_10000_hit,tel_189_hit+tel_10000_hit
    
    def insert_data(self,data):
        ret = self.conn['data_fusion_rpt'].insert_one(data)
        return ret
    def count_call_log_cache(self):
        ret = self.conn['call_log_details'].find({}).count()
        return ret

if __name__=='__main__':
    pro_conn = Pro_MongodbConnection()
    opts, args = getopt.getopt(sys.argv[1:], "b:e:")
    for op, value in opts:
        if op == "-b":
            BEGIN_DATE = value
        elif op == "-e":
            END_DATE = value
    fusion_list=pro_conn.export_data(BEGIN_DATE,END_DATE)
#    print fusion_list
    call_log_cache_hit_month_list=[]
    tel=[]
    end_time=[]
    telcom=[]
    count_10010_sid_miss,count_10010_tel_miss,count_10010_all_tel,count_10010_all_sid=pro_conn.count_10010_miss()
    count_10086_sid_miss,count_10086_tel_miss,count_10086_all_tel,count_10086_all_sid=pro_conn.count_10086_miss()
    count_10010_sid_hit,count_10010_tel_hit=pro_conn.count_10010_hit()
    count_10086_sid_hit,count_10086_tel_hit=pro_conn.count_10086_hit()
    count_189_sid_miss,count_189_tel_miss,count_189_all_tel,count_189_all_sid=pro_conn.count_189_miss()
    count_189_sid_hit,count_189_tel_hit=pro_conn.count_189_hit()
    count_call_log_cache=pro_conn.count_call_log_cache()
    for x in fusion_list:
        call_log_cache_hit_month_list.append(x['call_log_cache_hit_month_list'])
        tel.append(x['tel'])
        created_at=time.localtime(x['end_time'])
        created_at= time.strftime("%Y-%m-%d %H:%M:%S", created_at) 
        end_time.append(created_at)
        telcom.append(x['tel_info']['telecom'])
#        print x['tel'],created_at,x['call_log_cache_hit_month_list']
    rpt = pd.DataFrame({'call_log_cache_hit_month_list':call_log_cache_hit_month_list,'tel':tel,\
                        'end_time':end_time,'telcom':telcom})  
    rpt.to_csv(BEGIN_DATE+'data_fusion_rpt.csv',encoding = "gbk") 
    print "{} 0点到{} 0点 联通sid命中总数={}".format(BEGIN_DATE,END_DATE,count_10010_sid_hit)
    print "{} 0点到{} 0点 联通tel命中总数={}".format(BEGIN_DATE,END_DATE,count_10010_tel_hit)
    print "{} 0点到{} 0点 联通sid缺失总数={}".format(BEGIN_DATE,END_DATE,count_10010_sid_miss)
    print "{} 0点到{} 0点 联通tel缺失总数={}".format(BEGIN_DATE,END_DATE,count_10010_tel_miss)
    print "{} 0点到{} 0点 联通tel成功总数={}".format(BEGIN_DATE,END_DATE,count_10010_all_tel)
    print "{} 0点到{} 0点 联通sid成功总数={}".format(BEGIN_DATE,END_DATE,count_10010_all_sid)
    print "{} 0点到{} 0点 联通sid缓存命中率={}".format(BEGIN_DATE,END_DATE,count_10010_sid_hit*1.0/count_10010_sid_miss)
    print "{} 0点到{} 0点 联通tel缓存命中率={}".format(BEGIN_DATE,END_DATE,count_10010_tel_hit*1.0/count_10010_tel_miss)
    print "{} 0点到{} 0点 联通tel缓存命中/成功总tel数={}\n".format(BEGIN_DATE,END_DATE,count_10010_tel_hit*1.0/count_10010_all_tel)


    
    
    print "{} 0点到{} 0点 移动sid命中总数={}".format(BEGIN_DATE,END_DATE,count_10086_sid_hit)
    print "{} 0点到{} 0点 移动tel命中总数={}".format(BEGIN_DATE,END_DATE,count_10086_tel_hit)
    print "{} 0点到{} 0点 移动sid缺失总数={}".format(BEGIN_DATE,END_DATE,count_10086_sid_miss)
    print "{} 0点到{} 0点 移动tel缺失总数={}".format(BEGIN_DATE,END_DATE,count_10086_tel_miss)
    print "{} 0点到{} 0点 移动tel成功总数={}".format(BEGIN_DATE,END_DATE,count_10086_all_tel)
    print "{} 0点到{} 0点 移动sid成功总数={}".format(BEGIN_DATE,END_DATE,count_10086_all_sid)
    print "{} 0点到{} 0点 移动sid缓存命中率={}".format(BEGIN_DATE,END_DATE,count_10086_sid_hit*1.0/count_10086_sid_miss)
    print "{} 0点到{} 0点 移动tel缓存命中率={}".format(BEGIN_DATE,END_DATE,count_10086_tel_hit*1.0/count_10086_tel_miss)
    print "{} 0点到{} 0点 移动tel缓存命中/成功总tel数={}\n".format(BEGIN_DATE,END_DATE,count_10010_tel_hit*1.0/count_10086_all_tel)


    print "{} 0点到{} 0点 电信sid命中总数={}".format(BEGIN_DATE,END_DATE,count_189_sid_hit)
    print "{} 0点到{} 0点 电信tel命中总数={}".format(BEGIN_DATE,END_DATE,count_189_tel_hit)
    print "{} 0点到{} 0点 电信sid缺失总数={}".format(BEGIN_DATE,END_DATE,count_189_sid_miss)
    print "{} 0点到{} 0点 电信tel缺失总数={}".format(BEGIN_DATE,END_DATE,count_189_tel_miss)
    print "{} 0点到{} 0点 电信tel成功总数={}".format(BEGIN_DATE,END_DATE,count_189_all_tel)
    print "{} 0点到{} 0点 电信sid成功总数={}".format(BEGIN_DATE,END_DATE,count_189_all_sid)
    print "{} 0点到{} 0点 电信sid缓存命中率={}".format(BEGIN_DATE,END_DATE,count_189_sid_hit*1.0/count_189_sid_miss)
    print "{} 0点到{} 0点 电信tel缓存命中率={}".format(BEGIN_DATE,END_DATE,count_189_tel_hit*1.0/count_189_tel_miss)
    print "{} 0点到{} 0点 电信tel缓存命中/成功总tel数={}\n".format(BEGIN_DATE,END_DATE,count_189_tel_hit*1.0/count_189_all_tel)
    
    record={'rpt_date':BEGIN_DATE,
     'count_10010_sid_hit':count_10010_sid_hit,
     'count_10010_tel_hit':count_10010_tel_hit,
     'count_10010_sid_miss':count_10010_sid_miss,
     'count_10010_tel_miss':count_10010_tel_miss,
     'count_10010_all_tel':count_10010_all_tel,
     'count_10010_all_sid':count_10010_all_sid,
     'sid_10010_miss_hit_rate':'{0:.2f} %'.format(count_10010_sid_hit*1.0/count_10010_sid_miss*100),
     'tel_10010_miss_hit_rate':'{0:.2f} %'.format(count_10010_tel_hit*1.0/count_10010_tel_miss*100),
     'tel_10010_all_hit_rate':'{0:.2f} %'.format(count_10010_tel_hit*1.0/count_10010_all_tel*100),
     'count_10086_sid_hit':count_10086_sid_hit,
     'count_10086_tel_hit':count_10086_tel_hit,
     'count_10086_sid_miss':count_10086_sid_miss,
     'count_10086_tel_miss':count_10086_tel_miss,
     'count_10086_all_tel':count_10086_all_tel,
     'count_10086_all_sid':count_10086_all_sid,
     'sid_10086_miss_hit_rate':'{0:.2f} %'.format(count_10086_sid_hit*1.0/count_10086_sid_miss*100),
     'tel_10086_miss_hit_rate':'{0:.2f} %'.format(count_10086_tel_hit*1.0/count_10086_tel_miss*100),
     'tel_10086_all_hit_rate':'{0:.2f} %'.format(count_10086_tel_hit*1.0/count_10086_all_tel*100),
     'count_189_sid_hit':count_189_sid_hit,
     'count_189_tel_hit':count_189_tel_hit,
     'count_189_sid_miss':count_189_sid_miss,
     'count_189_tel_miss':count_189_tel_miss,
     'count_189_all_tel':count_189_all_tel,
     'count_189_all_sid':count_189_all_sid,
     'sid_189_miss_hit_rate':'{0:.2f} %'.format(count_189_sid_hit*1.0/count_189_sid_miss*100),
     'tel_189_miss_hit_rate':'{0:.2f} %'.format(count_189_tel_hit*1.0/count_189_tel_miss*100),
     'tel_189_all_hit_rate':'{0:.2f} %'.format(count_189_tel_hit*1.0/count_189_all_tel*100),
     'count_call_log_cache':count_call_log_cache,}
    print record
    try:
        pro_conn.insert_data(record)
    except:
        pass