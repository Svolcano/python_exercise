# -*- coding: utf-8 -*-
"""
Created on Wed May 30 11:09:10 2018

@author: huang
"""

import pymongo
import time
import datetime
import json
import sys
import getopt
import pandas as pd
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
sys.path.append('../')
stdout = sys.stdout
reload(sys)
sys.stdout = stdout
sys.setdefaultencoding("utf8")

all_cols=[u'_id', u'bill_cache_hit_month_list', u'bill_fusion_cost_time', u'cache_time', 
          u'call_log_cache_hit_month_list', u'call_log_fusion_cost_time',
          u'call_log_missing_month_list', u'call_log_part_missing_month_list', 
          u'call_log_possibly_missing_month_list', u'cid', u'crawl_status',
          u'crawler_channel', u'cuishou_error_msg', u'cuishou_request_status', 
          u'cuishou_request_time', u'cuishou_sid', u'emergency_contact', u'end_time',
          u'expire_time', u'hasAlerted', u'job_id', u'login_status', u'login_time',
          u'message', u'original_channel', u'phone_bill_missing_month_list',
          u'report_create_time', u'report_message', u'report_used', u'sid',
          u'start_time', u'status', u'status_report', u'tel', u'tel_info',
          u'third_party_error_msg', u'third_party_status', u'third_party_token', 
          u'uid', u'user_info']

record_col=['cid','crawler_channel','province','telecom']

MONGO_CONFIG = {
#    'host': '127.0.0.1',
    'host': '172.18.21.117',
    'port': 27017,
    'db': 'crs'
}

if __name__=='__main__':
    opts, args = getopt.getopt(sys.argv[1:], "b:e:")
    for op, value in opts:
        if op == "-b":
            BEGIN_DATE = value
        elif op == "-e":
            END_DATE = value

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

    def export_data(self):
        self.data = self.conn['sid_info_data_rpt'].find({"cid":9999},{'cid':1,'_id':1})
        return self.data
    
    def modify_data(self):
#        print self.data['status']
        print self.data.count()
        for line in self.data:
            update_dict={}
            if line['cid']==9999:
                update_dict.update({ '$set' : {'cid':-1}})
                ret=self.update_data(line,update_dict)
                if ret['ok']=='OK':
                    pass
    
    def update_data(self,where,update_dict):
        ret = self.conn['sid_info_data_rpt'].update(where,update_dict)
        return ret



pro_conn = Pro_MongodbConnection()
data=pro_conn.export_data()
pro_conn.modify_data()