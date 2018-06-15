# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import os
    import sys
    package_path = os.path.abspath(__file__)
    package_path = os.path.dirname(package_path)
    package_path = os.path.join(package_path,'..')
    sys.path.append(package_path)
from redis_conn import RedisWrapper
from setting.proxy_config import PROXIES_UNICOM_IP_POOLS, PROXIES_IP_POOLS
from setting.crawler_config import CHANNEL_MAPPING


class Redis_que(object):
    """
    Redis参数入队初始化
    """
    def __init__(self):
        self.conn = RedisWrapper(1).get_conn()

    def init_redis(self):
        self._set_proxies_que()
        self._set_channel_que()

    def _set_proxies_que(self):
        p = self.conn.pipeline()
        p.delete('bmp_crawl_proxies_cmcc')
        p.delete('bmp_crawl_proxies_cucc')
        pattern = lambda x,y: [p.lpush(y, i) for i in x]
        pattern(PROXIES_IP_POOLS, 'bmp_crawl_proxies_cmcc')
        pattern(PROXIES_UNICOM_IP_POOLS, 'bmp_crawl_proxies_cucc')
        p.execute()   

    def _set_channel_que(self):
        self.conn.hmset('bmp_crawl_channel', CHANNEL_MAPPING)

    def pop_proxies(self,ip_type='bmp_crawl_proxies_cmcc'):
        ip = self.conn.rpoplpush(ip_type, ip_type)
        # print 'proxies',ip,self.conn.llen(ip_type)
        return ip

    def get_channel(self):
        return self.conn.hgetall('bmp_crawl_channel')

redis_que = Redis_que()

if __name__ == '__main__':
    redis_que.init_redis()
    # print redis_que.get_channel()