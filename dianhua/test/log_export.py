# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 10:57:38 2018

@author: huang
"""

# -*- coding: utf-8 -*-
import pymongo
import time

DEV_MONGO_CONFIG = {
    'host': '172.18.19.219',
    'port': 27017,
    'db': 'crs'
}

PRO_MONGO_CONFIG = {
    'host': '172.18.21.117',
    #'host': '172.18.19.219',
    'port': 27017,
    'db': 'crs'
}

class Pro_MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_pro_db_conn()
        self.sid_list=self.get_sid_set('2018-03-15','2018-03-23')

    def set_pro_db_conn(self):
        self.client = pymongo.MongoClient(PRO_MONGO_CONFIG['host'], PRO_MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[PRO_MONGO_CONFIG['db']]

    def export_data(self,sid):
        data = self.conn['log'].find({'sid':sid})
        return data
    def get_sid_set(self,begindate,enddate=int(time.time()),err_code=3003):
        timeArray = time.strptime(begindate, "%Y-%m-%d")
        begindate = time.mktime(timeArray)
        timeArray = time.strptime(enddate, "%Y-%m-%d")
        enddate = time.mktime(timeArray)
        data = self.conn['sid_info'].find({"end_time":{'$gte':begindate,'$lte':enddate},'status':err_code})
        sid_list=[]
        for x in data:
            sid_list.append(x['sid'])
        return sid_list
    
class Dev_MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_dev_db_conn()

    def set_dev_db_conn(self):
        self.client = pymongo.MongoClient(DEV_MONGO_CONFIG['host'], DEV_MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[DEV_MONGO_CONFIG['db']]

    def insert_data(self,data):
        ret = self.conn['pro_log'].insert_one(data)
        return ret


if __name__ == '__main__':
    pro_conn = Pro_MongodbConnection()
    dev_conn = Dev_MongodbConnection()

    for  sid in pro_conn.sid_list:
        print sid
        datas=pro_conn.export_data(sid)
        for data in datas:
            if (data)>0:
                dev_conn.insert_data(data)
        
    

        
        
        
        