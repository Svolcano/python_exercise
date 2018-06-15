# -*- coding: utf-8 -*-
import pymongo
import sys

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


if __name__ == '__main__':
    dev_conn = Dev_MongodbConnection()
    tel='13070194201'
    missing_log_list=['201801', '201802']
    possibly_missing_list=[]
    part_missing_list=[ '201712', '201711']
#    missing_log_list=[]
#    possibly_missing_list=[]
#    part_missing_list=[]
    print '开始测试'
    print 'missing_log_list={}'.format(missing_log_list)
    print 'possibly_missing_list={}'.format(possibly_missing_list)
    print 'part_missing_list={}'.format(part_missing_list)
    #进行数据融合
    call_log = dev_conn.conn['call_log'].find({'tel':tel},{'_id':0})
    para_dict={'tel':tel,'final_call_logs':call_log,
               'missing_month_list':missing_log_list,
               'possibly_missing_list':possibly_missing_list,
               'part_missing_list':part_missing_list}
    call_log, missing_log_list, \
    possibly_missing_list, part_missing_list, \
    cache_hit_month_list,fusion_cost_time=data_fusion(**para_dict)
    
    print '结束测试'
    print 'missing_log_list={}'.format(missing_log_list)
    print 'possibly_missing_list={}'.format(possibly_missing_list)
    print 'part_missing_list={}'.format(part_missing_list)
    print 'cache_hit_month_list={}'.format(cache_hit_month_list)
    print 'fusion_cost_time={}'.format(fusion_cost_time)
    #dev_conn.insert_call(call_log)
#    for x in call_log:
#        print call_log

if __name__ == '__main__':
    dev_conn = Dev_MongodbConnection()
    tel='13070194201'
    missing_log_list=['201803']
    possibly_missing_list=['201804']
    part_missing_list=['201801',]
#    missing_log_list=[]
#    possibly_missing_list=[]
#    part_missing_list=[]
    print '开始测试'
    print 'missing_log_list={}'.format(missing_log_list)
    print 'possibly_missing_list={}'.format(possibly_missing_list)
    print 'part_missing_list={}'.format(part_missing_list)
    #进行数据融合
    call_log = dev_conn.conn['call_log'].find({'tel':tel},{'_id':0})
    para_dict={'tel':tel,'final_call_logs':call_log,
               'missing_month_list':missing_log_list,
               'possibly_missing_list':possibly_missing_list,
               'part_missing_list':part_missing_list}
    call_log, missing_log_list, \
    possibly_missing_list, part_missing_list, \
    cache_hit_month_list,fusion_cost_time=data_fusion(**para_dict)
    
    print '结束测试'
    print 'missing_log_list={}'.format(missing_log_list)
    print 'possibly_missing_list={}'.format(possibly_missing_list)
    print 'part_missing_list={}'.format(part_missing_list)
    print 'cache_hit_month_list={}'.format(cache_hit_month_list)
    print 'fusion_cost_time={}'.format(fusion_cost_time)  
            
        
                
                
