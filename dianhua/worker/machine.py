# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    import os
    import sys
    package_path = os.path.abspath(__file__)
    package_path = os.path.dirname(package_path)
    package_path = os.path.join(package_path, '..')
    sys.path.append(package_path)
import importlib

from worker.state.standard_state import state_interface as interface
# import worker.state.multi_verify_state
from com.redis_que import redis_que

def choose_tool(flow_type, province, city):
    channel_dict = redis_que.get_channel()
    pattern = lambda x: channel_dict.get(x, '')
    new_flow_type = '{}-{}-{}'.format(flow_type, province, city)
    if not pattern(new_flow_type):
        new_flow_type = '{}-{}'.format(flow_type, province)
    if not pattern(new_flow_type):
        new_flow_type = flow_type
    if not pattern(new_flow_type):
        new_flow_type = 'none'
    return pattern(new_flow_type)

class Machine(object):

    def run(self, param):
        # get parameters
        flow_type = param['flow_type']
        province = param['province']
        city = param['city']
        sid = param['sid']
        tel = param['tel']

        # setting start state
        crawler_module_str = choose_tool(flow_type,province,city)

        if not crawler_module_str:
            # no supported crawler
            now_state = interface(state_flag='None',
                                  sid=sid,
                                  tel=tel,
                                  crawler=None)
        else:
            crawler_module = importlib.import_module(crawler_module_str)
            crawler = crawler_module.Crawler(sid=sid,crawler=crawler_module_str)
            now_state = interface(state_flag='Start',
                                  sid=sid,
                                  tel=tel,
                                  crawler=crawler)

        # start_working
        while True:
            # execute state
            # print type(now_state).__name__
            now_state.execute()
            
            if now_state.state_flag=='interrupt':
                break
            
            next_state_str = now_state.next_state()
            
            # create next state
            now_state = interface(state_flag=next_state_str,
                                  pre_state=now_state)
            
            if now_state is None or now_state.state_flag=='interrupt':
                break

        return True

if __name__ == '__main__':
    m = Machine()
    m.run({'sid':'unicom1', 'tel':'123', 'flow_type':'10010', 'location':'f'})
