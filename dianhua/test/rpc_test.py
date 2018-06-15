# -*- coding:utf-8 -*-
import uuid
import inspect
import traceback
import sys
import re
import copy

reload(sys)
sys.setdefaultencoding('utf8')


from nameko.standalone.rpc import ClusterRpcProxy

if __name__ == '__main__':
    import os
    import sys
    package_path = os.path.abspath(__file__)
    package_path = os.path.dirname(package_path)
    package_path = os.path.join(package_path, '..')
    sys.path.append(package_path)

from nameko.standalone.rpc import ClusterRpcProxy
#import asyncio


CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost"}

    
class adap():
    def post(self):

            operation = {
                        "action": 'send_info_pwd',
                        "city": "",
                        "flow_type": "crs",
                        "other": 0,
                        "province": "",
                        "sid": "",
                        "tel": "",
                        "work_flow_body":"{(1, 'send_info_pwd'): {'next': ['send_sms'],'sys_op': ['get_sms', 'get_cap'],'status':0},(2, 'send_sms_cap'): {'next': ['send_sms_cap'],'sys_op': ['get_sms', 'get_cap'],'status':0},(3, 'send_sms_cap'): {'next': ['finish'], 'sys_op': [''],'status':0}}",
                        "service_resp":None}
            with ClusterRpcProxy(CONFIG) as rpc:
                handler = rpc.Server_Master.Server_Master.call_async(operation)
                return handler.result()

#@asyncio.coroutine  # 声明一个协程
def customer(num):
    oper = adap()
    ret=oper.post()
    print ret
    print '返回码:{},返回信息:{}'.format(ret['status_code'],ret['message'])
    

if __name__ == '__main__':
    
#    loop = asyncio.get_event_loop()  # 获取一个event_loop
#    tasks = [customer(1, loop), customer(2, loop)]
#    loop.run_until_complete(asyncio.gather(*tasks))  # "阻塞"直到所有的tasks完成
#    loop.close()
    
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all()
    tasks = [ gevent.spawn(customer,i) for i in range(0,1)]
    gevent.joinall(tasks)
