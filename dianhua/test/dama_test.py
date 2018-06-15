# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 14:49:09 2018

@author: huang
"""

import pymongo
import sys
import base64

sys.path.append('../')
from worker.data_fusion import data_fusion

DEV_MONGO_CONFIG = {
    'host': '172.18.19.219',
    'port': 27017,
    'db': 'crs'
}


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

    def insert_call(self,data):
        self.conn['call_log'].insert_many(data)

dev_conn = Dev_MongodbConnection()

#dama1_cfg={
#        'dama_pad_code':'__fateadm',
#        'err_times':0,
#        'priority_level':1
#        }
#dev_conn.conn['dama_cfg'].insert(dama1_cfg)
#
#
#dama1_cfg={
#        'dama_pad_code':'__dama2',
#        'err_times':0,
#        'priority_level':2
#        }
#dev_conn.conn['dama_cfg'].insert(dama1_cfg)
#
#
#dama1_cfg={
#        'dama_pad_code':'__yundama',
#        'err_times':0,
#        'priority_level':3
#        }
#dev_conn.conn['dama_cfg'].insert(dama1_cfg)

def main():
    from com.multiprocess_dama import multiprocess_dama
    sid='SID0091391449564f25a71c7cb031b477e8'
    image=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAEYAAAAUCAIAAAC\/CtwvAAACAklEQVR42s2XzyuEQRjHOaw2lG1zcNpSUkp+tlaJpEWx5SIUN1ycNpEoV5d1oLbIyWkPhJOyN1cSKxdpHfawBwda\/4Gvnpqmd+ad93ln36Q+e5hn3pmdz\/s882xbE6oNmZnoMOG53Bet5W5Q5SY1+FQKJTfMPm6rdvLDwLCtG6RksVDgraRldWuvSqWh\/jhRzemDVDL7cPhfSlqfaFcfoV3imBI+HLHm1CJx0BijSH4kDV6uo4CmvJUW7m+B+WrxlUT86eoTBKik+jiVEoVjYFAydwWtlRxRlZh1Iazk4ElbHHgUnlBykH9OA7Xk2otHldzsLzwl64skKx2uP5KMLJkNdwIfd4mU1Px4KrmVop0SmQBYOZIGn7uvCwGrPXj+EPGVpnM9vpSEiXCQTy\/QF15mIwXsfFQrQwMUVhwZ9fTarmCjxHmjQsngQ4VHVjSsb\/gA4vWLtNBw+SEJxHUy+7DuEj9FvpRwVljJ716YOB7WKk0uNflWmkqOAk6KzhKvQFUKz8XEM2rxUOFRrtzasbbpkY+9EidFspLb3Y1kvoHa9DgyDis5kp0JA5bS+Pa+iuHLtJ3nfOAUcM6KXMnD+c01wFloUtotRYB5vdaTr82x4st4tweOEgdrbb8ygzdjIMg\/F4FraysQ9F6+ARulP2alrgi0U7CSh6Tktk\/Lexmo8R9j\/2\/w1wc63QAAAABJRU5ErkJggg==')
    code_type='3004'
    status, code, cid,dama_flag=multiprocess_dama(sid,image,code_type)
    
    print type(code)
    print ('status='+status)
    print ('code='+code)
    print ('cid='+str(cid))
    print ('dama_flag='+str(dama_flag))
if __name__=='__main__':
    main()
    sys.exit(0)