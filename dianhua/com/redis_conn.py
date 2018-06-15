# -*- coding: utf-8 -*-
import redis

if __name__ == '__main__':
    import sys
    sys.path.append('../')
from setting.db_config import REDIS_CONFIG

class RedisWrapper(object):
    """
    Redis连接类
    """
    def __init__(self,db=0):
        self.conn = None
        self._set_db_conn(db)

    def _set_db_conn(self, db=0):
        connection_pool = redis.ConnectionPool(host=REDIS_CONFIG['host'], port=REDIS_CONFIG['port'], db=REDIS_CONFIG['db'][db])
        self.conn = redis.StrictRedis(connection_pool=connection_pool)

    def get_conn(self):
        db = self.conn
        return db

redis_instance = RedisWrapper().get_conn()

if __name__ == '__main__':
    # redis_instance.delete('test')
    print redis_instance.hmset('test', {'1233':"123****", '12':'12&&&&&&&'})
    import pdb; pdb.set_trace()
    print redis_instance.hget('test', '1233')
    print redis_instance.get('1867919')
