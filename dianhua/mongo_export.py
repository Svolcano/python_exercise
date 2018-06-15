# -*- coding: utf-8 -*-
import pymongo
import json
from bson.objectid import ObjectId

MONGO_CONFIG = {
    'host': '172.18.19.219',
    'port': 27017,
    'db': 'crs'
}

class MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_db_conn()

    def set_db_conn(self):
        self.client = pymongo.MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[MONGO_CONFIG['db']]

    def export_data(self):
        sid_list = ['SID730c88afb8b748aab804816abc70a885']
        for i in sid_list:
            tel = ''
            with open('{}.json'.format(i), 'a') as fp:
                for j in ['sid_info', 'call_log', 'report', 'phone_bill', 'log']:
                    data = self.conn[j].find({'sid':i},{'_id':0})
                    if j == 'sid_info':
                        tel = data[0].get('tel', '')
                    for k in data:
                        fp.write(json.dumps(k))
                    fp.write('\n\n')
                if tel:
                    data = self.conn['user_info'].find({'tel':tel},{'_id':0})
                    if data:
                        fp.write(json.dumps(data[0]))

if __name__ == '__main__':
    conn = MongodbConnection()
    conn.export_data()
    # conn.insert_data('SIDa6d88c69e7a74e4bb1ff5c765619fd0a')
