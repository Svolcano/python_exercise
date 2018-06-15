# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 14:57:58 2018

@author: huang
"""
from  log_export  import DEV_MONGO_CONFIG
import pymongo
import time
import pandas as pd  

class data_ansy(object):
    """
    数据分析
    """
    def __init__(self):
        self.conn = None
        self.set_dev_db_conn()

    def set_dev_db_conn(self):
        self.client = pymongo.MongoClient(DEV_MONGO_CONFIG['host'], DEV_MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[DEV_MONGO_CONFIG['db']]

    def get_err_code_data(self,err_code):
        data = self.conn['pro_log'].find({"state_log.execute_status":err_code})
        return data
    
    
if __name__ == '__main__':
    dev_conn = data_ansy()
    datas=dev_conn.get_err_code_data(4009)
    #print len(list(datas))
    create_date=[]
    sid=[]
    message=[]
    execute_status=[]
    failed_status=[]
    next_status=[]
    for data in datas:
        created_at=time.localtime(data['created_at'])
        created_at= time.strftime("%Y-%m-%d %H:%M:%S", created_at) 
        create_date.append(created_at)
        sid.append(data['sid'])
        message.append(data['message'])
        execute_status.append(data['state_log']['execute_status'])
        failed_status.append(data['state_log']['state_name'])
        next_status.append(data['state_log']['next_action'])
        
    rpt = pd.DataFrame({'create_date':create_date,'sid':sid,\
                        'message':message,'execute_status':execute_status,
                        'failed_status':failed_status,'next_status':next_status})  
    rpt.to_csv('4009_rpt.csv',encoding = "gbk") 
    
    
        
    
    