# -*- coding: utf-8 -*-
import pymongo
import sys

sys.path.append('../')
from worker.bill_data_fusion import data_fusion

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


if __name__ == '__main__':
    dev_conn = Dev_MongodbConnection()
    tel='13070194201'
    

    print '开始测试'
    #进行数据融合
    
    ret = dev_conn.conn['phone_bill'].find({'tel':tel},{'_id':0})
    for log in ret:
        missing_log_list=['201801', '201802']
        call_log=[]
        print 'missing_log_list={}'.format(missing_log_list)
        log=log['phone_bill']
#        print log
        for bill in log:
#            print  bill
            if bill['bill_month'] in missing_log_list:
                continue
            call_log.append(bill)
#    print call_log
        para_dict={'tel':tel,'final_bill_logs':call_log,
                   'missing_month_list':missing_log_list}
        call_log, missing_log_list, \
        cache_hit_month_list,fusion_cost_time=data_fusion(**para_dict)
        
        print '结束测试'
        print 'missing_log_list={}'.format(missing_log_list)
        print 'cache_hit_month_list={}'.format(cache_hit_month_list)
        print 'fusion_cost_time={}'.format(fusion_cost_time)
    #dev_conn.insert_call(call_log)
#    for x in call_log:
#        print call_log

