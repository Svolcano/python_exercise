# -*- coding: utf-8 -*-

import sys
import time
import inspect
import traceback

from base_state import BaseState
from state_tool import after_get_parameter, SUCCESS_STATUS, FAILED_STATUS
from setting.status_code import STATUS_CODE
from setting.api_config import ENV, STATE_TIME_OUT, CRAWLER_TIME_OUT
from worker.communicate import get_parameter, save_data, save_status, get_today_result

from worker.call_log_data_fusion import data_fusion as call_log_fusion
from worker.bill_data_fusion import data_fusion as bill_fusion
import copy

class StartState(BaseState):

    def __init__(self, **kwargs):
        super(StartState, self).__init__(**kwargs)
        self.parameters['tel'] = kwargs['tel']
        self.login_verify_type = \
            self.crawler.get_login_verify_type(**self.parameters)
        self.need_parameters = \
            self.crawler.need_parameters(**self.parameters)
        need_parameters_dict = {'need_full_name': 0,
                                'need_id_card': 0,
                                'need_pin_pwd': 0,
                                'need_sms_verify': 0,
                                'need_captcha_verify': 0}
        for parameter in self.need_parameters:
            need_parameters_dict['need_{}'.format(parameter)] = 1
        self.need_parameters = need_parameters_dict
        self.cache_time = get_today_result(self.parameters['tel'])
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        status = STATUS_CODE[SUCCESS_STATUS]
        self.execute_message = status['message']
        self.execute_status = status['status']
        if not self.login_verify_type:
            self.state_flag = 'WaitLogin'
        else:
            self.state_flag = 'WaitLoginVerifyRequest'
        self.log()

class WaitLoginVerifyRequestState(BaseState):

    def __init__(self, **kwargs):
        super(WaitLoginVerifyRequestState, self).__init__(**kwargs)
        self.next_action = 'Get{}'.format(self.login_verify_type)
        self.set_current_state()

    def execute(self, **kwargs):
        targets = [self.next_action]
        parameter_status, parameter_timeout, action, parameters = \
            get_parameter(state=self, targets=targets)
        status_code, state_flag = after_get_parameter(parameter_status,
                                                      parameter_timeout,
                                                      action)
        self.parameters.update(parameters)
        if not state_flag:
            self.state_flag = 'UnderLoginVerifyRequest'
        else:
            self.state_flag = state_flag
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.log()

class UnderLoginVerifyRequestState(BaseState):

    def __init__(self, **kwargs):
        super(UnderLoginVerifyRequestState, self).__init__(**kwargs)
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        start_time = int(time.time())
        code, key, image_str = self.crawler.send_login_verify_request(**self.parameters)
        time_used = int(time.time()) - start_time
        if code == 0 and time_used < STATE_TIME_OUT:
            status_code = STATUS_CODE[SUCCESS_STATUS]
            self.state_flag = 'WaitLogin'
        else:
            status_code = STATUS_CODE[key]
            if time_used > STATE_TIME_OUT:
                self.log(message='time_used:{}'.format(time_used))
                status_code = STATUS_CODE[FAILED_STATUS]
            self.state_flag = 'Failed'
        self.verify_content = image_str
        self.execute_status = status_code['status']
        self.execute_message= status_code['message']
        self.log()

class WaitLoginState(BaseState):

    def __init__(self, **kwargs):
        super(WaitLoginState, self).__init__(**kwargs)
        self.next_action = 'Login'
        self.set_current_state()

    def execute(self, **kwargs):
        send_target = 'Get{}'.format(self.login_verify_type)
        targets = [self.next_action, send_target]
        parameter_status, parameter_timeout, action, parameters = \
            get_parameter(state=self, targets=targets)
        status_code, state_flag = after_get_parameter(parameter_status,
                                                      parameter_timeout,
                                                      action)
        self.parameters.update(parameters)
        if not state_flag:
            if action == send_target:
                self.state_flag = 'UnderLoginVerifyRequest'
            else:
                self.state_flag = 'UnderLogin'
        else:
            self.state_flag = state_flag
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.log()


class UnderLoginState(BaseState):

    def __init__(self, **kwargs):
        super(UnderLoginState, self).__init__(**kwargs)
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        start_time = int(time.time())
        code, key = self.crawler.login(**self.parameters)
        time_used = int(time.time()) - start_time

        self.verify_type = self.crawler.get_verify_type(**self.parameters)
        if code == 0 and time_used < STATE_TIME_OUT:
            status_code = STATUS_CODE[SUCCESS_STATUS]
            if ENV == 'prod' and self.cache_time:
                self.state_flag = 'NoCrawl'
            elif not self.verify_type:
                self.state_flag = 'UnderCrawl'
            else:
                self.state_flag = 'WaitVerifyRequest'
        elif code in [1, 2]:
            status_code = STATUS_CODE[key]
            self.state_flag = 'WaitLogin'
            # if 'all_entry' in self.parameters.get('crawler', ''):
            #     self.state_flag = 'WaitLoginVerifyRequest'
        else:
            status_code = STATUS_CODE[key]
            if time_used > STATE_TIME_OUT:
                self.log(message='time_used:{}'.format(time_used))
                status_code = STATUS_CODE[FAILED_STATUS]
            self.state_flag = 'Failed'
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.log()

class WaitVerifyRequestState(BaseState):

    def __init__(self, **kwargs):
        super(WaitVerifyRequestState, self).__init__(**kwargs)
        self.next_action = 'Get{}'.format(self.verify_type)
        self.set_current_state()

    def execute(self, **kwargs):
        targets = [self.next_action,"Login"]
        parameter_status, parameter_timeout, action, parameters = \
            get_parameter(state=self, targets=targets)
        status_code, state_flag = after_get_parameter(parameter_status,
                                                      parameter_timeout,
                                                      action)
        self.parameters.update(parameters)
        if not state_flag:
            if "Login"  ==  action:
                self.state_flag = 'WaitVerifyRequest'
            else:
                if self.wait_code_get_login == True:
                    self.state_flag = 'WaitCode'
                else:
                    self.state_flag = 'UnderVerifyRequest'
        else:
            self.state_flag = state_flag
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.log()

class UnderVerifyRequestState(BaseState):

    def __init__(self, **kwargs):
        super(UnderVerifyRequestState, self).__init__(**kwargs)
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        start_time = int(time.time())
        code, key, image_str = self.crawler.send_verify_request(**self.parameters)
        time_used = int(time.time()) - start_time

        if code == 0 and time_used < STATE_TIME_OUT:
            status_code = STATUS_CODE[SUCCESS_STATUS]
            self.state_flag = 'WaitCode'
        else:
            status_code = STATUS_CODE[key]
            if time_used > STATE_TIME_OUT:
                self.log(message='time_used:{}'.format(time_used))
                status_code = STATUS_CODE[FAILED_STATUS]
            self.state_flag = 'Failed'
        self.verify_content = image_str
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.log()


class WaitCodeState(BaseState):

    def __init__(self, **kwargs):
        super(WaitCodeState, self).__init__(**kwargs)
        self.next_action = 'Verify'
        self.set_current_state()

    def execute(self, **kwargs):
        send_target = 'Get{}'.format(self.verify_type)
        targets = [self.next_action, send_target,'Login']
        parameter_status, parameter_timeout, action, parameters = \
            get_parameter(state=self, targets=targets)
        self.parameters.update(parameters)
        status_code, state_flag = after_get_parameter(parameter_status,
                                                      parameter_timeout,
                                                      action)
        if not state_flag:
            if action == send_target:
                self.state_flag = 'UnderVerifyRequest'
                # self.state_flag = 'WaitVerifyRequest'
            elif "Login"  ==  action:
                self.state_flag = 'WaitVerifyRequest'
                self.wait_code_get_login = True
            else:
                self.state_flag = 'UnderVerify'
        else:
            self.state_flag = state_flag
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.log()

class UnderVerifyState(BaseState):

    def __init__(self, **kwargs):
        super(UnderVerifyState, self).__init__(**kwargs)
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        start_time = int(time.time())
        code, key = self.crawler.verify(**self.parameters)
        time_used = int(time.time()) - start_time

        if code == 0 and time_used < STATE_TIME_OUT:
            status_code = STATUS_CODE[SUCCESS_STATUS]
            self.state_flag = 'UnderCrawl'
        elif code == 2:
            status_code = STATUS_CODE[key]
            self.state_flag = 'WaitCode'
            if key in ['user_id_error', 'user_name_error']:
                self.state_flag = 'Failed'
        else:
            status_code = STATUS_CODE[key]
            if time_used > STATE_TIME_OUT:
                self.log(message='time_used:{}'.format(time_used))
                status_code = STATUS_CODE[FAILED_STATUS]
            self.state_flag = 'Failed'
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.log()

class UnderCrawlState(BaseState):

    def __init__(self, **kwargs):
        super(UnderCrawlState, self).__init__(**kwargs)
        self.next_action = 'Finish'
        self.set_current_state()

    def execute(self, **kwargs):
        user_info = {}
        call_log = []
        phone_bill = []
        missing_log_list = []
        possibly_missing_list = []
        missing_bill_list = []
        open_date = ''

        # code, key, call_log, missing_log_list, possibly_missing_list = self.crawler.crawl_call_log(**self.parameters)
        # 临时修改, 以配合移动商城增加 缺页列表
        start_time = int(time.time())
        returns = self.crawler.crawl_call_log(**self.parameters)
        if len(returns) == 5:
            code, key, call_log, missing_log_list, possibly_missing_list = returns
            part_missing_list = []
        if len(returns) == 6:
            code, key, call_log, missing_log_list, possibly_missing_list, part_missing_list = returns
        status_code = STATUS_CODE[key]

        # 保存call_from_set字段的内容
        self.crawler.save_call_from_set()


        total_missing_list = missing_log_list + possibly_missing_list
        if (len(total_missing_list) == 6 or not call_log) and key == 'success':
            status_code = STATUS_CODE['crawl_error']
        
        
        # 只要crawl_call_log成功就算成功
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.state_flag = 'End'

        state = {}

        code, key, user_info = self.crawler.crawl_info(**self.parameters)
        status_part = STATUS_CODE[key]
        open_date = user_info.get('open_date', '')

        state['state_name'] = 'crawl_info'
        state['execute_status'] = status_part['status']
        state['execute_message'] = status_part['message']
        self.log(state=state)

        code, key, phone_bill, missing_bill_list = self.crawler.crawl_phone_bill(**self.parameters)
        status_part = STATUS_CODE[key]
        
        ####################账单融合#######################
        bill_cache_hit_month_list=[]
        bill_fusion_cost_time=0
        message=''
        try:
            #进行账单数据融合
            para_dict={'tel':self.tel,'sid':self.sid,'pad_code':'yulore',
                       'final_bill_logs':phone_bill,
                       'missing_month_list':missing_bill_list}
            phone_bill, missing_bill_list, \
            bill_cache_hit_month_list,bill_fusion_cost_time =bill_fusion(**para_dict)
        except:
            message = traceback.format_exc()
            print message
            pass 
        
        state['state_name'] = 'crawl_phone_bill'
        state['execute_status'] = status_part['status']
        state['execute_message'] = status_part['message']
        missing_bill_dict = {'phone_bill_missing_month_list':missing_bill_list,'message':message}
        self.log(state=state, missing_dict=missing_bill_dict)

        time_used = int(time.time()) - start_time

        # 处理20分钟超时问题
        if time_used >= CRAWLER_TIME_OUT:
            status_code = STATUS_CODE[FAILED_STATUS]
            self.execute_status = status_code['status']
            self.execute_message = status_code['message']
            self.state_flag = 'End'
            
        ####################详单融合#######################
        cache_hit_month_list=[]
        fusion_cost_time=0
        crawl_status=0
        try:
            #进行数据融合
            para_dict={'tel':self.tel,'final_call_logs':call_log,
                       'missing_month_list':missing_log_list,
                       'possibly_missing_list':possibly_missing_list,
                       'part_missing_list':part_missing_list}
            call_log, missing_log_list, \
            possibly_missing_list, part_missing_list, \
            cache_hit_month_list,fusion_cost_time =call_log_fusion(**para_dict)
        except:
            message = traceback.format_exc()
            print message
            pass
        
        # 缺失列表第二次判断
        total_missing_list = missing_log_list + possibly_missing_list
        if (len(total_missing_list) == 6 or not call_log) :
            pass
        elif status_code <> STATUS_CODE['success']:
            crawl_status=copy.deepcopy(status_code['status'])
            status_code = STATUS_CODE['success']
               
        
        # 只要crawl_call_log成功就算成功
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        self.state_flag = 'End'
        
        if open_date:
            time_struct = time.localtime(int(open_date))
            open_date_YM = '%d%02d'%(time_struct.tm_year, time_struct.tm_mon)
            # log_missing_set = sorted(set(missing_log_list + possibly_missing_list))
            # bill_missing_set = sorted(set(missing_bill_list))
            pattern = lambda x: [i for i in x if i > open_date_YM]
            missing_log_list = pattern(missing_log_list)
            possibly_missing_list = pattern(possibly_missing_list)
            missing_bill_list = pattern(missing_bill_list)
        
        save_data(self.sid, tel=self.tel, call_log=call_log, phone_bill=phone_bill,
            user_info=user_info, status=status_code['status'], message=status_code['message'],
            missing_log_list=missing_log_list, possibly_missing_list=possibly_missing_list, 
            missing_bill_list=missing_bill_list, part_missing_list=part_missing_list,
            cache_hit_month_list=cache_hit_month_list,fusion_cost_time=fusion_cost_time,
            crawl_status=crawl_status,bill_cache_hit_month_list=bill_cache_hit_month_list,
            bill_fusion_cost_time=bill_fusion_cost_time)

        call_log_missing_dict = {
            'call_log_missing_month_list':missing_log_list,
            'call_log_possibly_missing_month_list':possibly_missing_list,
            'call_log_part_missing_list': part_missing_list,
            'cache_hit_month_list':cache_hit_month_list,
            'data_fusion_cost_time':fusion_cost_time,
            'crawl_status':crawl_status,
            'bill_cache_hit_month_list':bill_cache_hit_month_list,
            'bill_fusion_cost_time':bill_fusion_cost_time
        }

        self.log(missing_dict=call_log_missing_dict)

class FailedState(BaseState):

    def __init__(self, **kwargs):
        super(FailedState, self).__init__(**kwargs)
        self.next_action = 'Reset'
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        save_status(self.sid, self.pre_status, self.pre_message)
        self.log()

class AbortState(BaseState):

    def __init__(self, **kwargs):
        super(AbortState, self).__init__(**kwargs)
        self.next_action = 'Finish'
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        status = STATUS_CODE['user_exit']['status']
        message = STATUS_CODE['user_exit']['message']
        save_status(self.sid, status, message)
        self.log()

class EndState(BaseState):

    def __init__(self, **kwargs):
        super(EndState, self).__init__(**kwargs)
        self.next_action = 'Finish'
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        self.log()

class NoCrawlState(BaseState):

    def __init__(self, **kwargs):
        super(NoCrawlState, self).__init__(**kwargs)
        self.next_action = 'NoCrawlFinish'
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        status = STATUS_CODE['result_exists']['status']
        message = STATUS_CODE['result_exists']['message']
        save_status(self.sid, status, message, cache_time=self.cache_time)
        self.log()

class NoneState(BaseState):

    def __init__(self, **kwargs):
        super(NoneState, self).__init__(**kwargs)
        self.next_action = 'Unsupported'
        self.need_parameters = {
            'need_full_name': 0,
            'need_id_card': 0,
            'need_pin_pwd': 0,
            'need_sms_verify': 0,
            'need_captcha_verify': 0
        }
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        status = STATUS_CODE['no_supported_crawler']['status']
        message = STATUS_CODE['no_supported_crawler']['message']
        save_status(self.sid, status, message)
        self.log()

CLASS_LIST = inspect.getmembers(sys.modules[__name__], inspect.isclass)
CLASS_DICT = {pair[0]:pair[1] for pair in CLASS_LIST}

def state_interface(**kwargs):
    state_flag = kwargs.pop('state_flag')
    if not state_flag:
        return None
    state_flag = '{}State'.format(state_flag)
    return CLASS_DICT[state_flag](**kwargs)
