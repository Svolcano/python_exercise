# -*- coding: utf-8 -*-
import sys
if __name__ == '__main__':
    sys.path.append('../..')
import copy
import logging
import inspect

from mongolog.handlers import MongoHandler

from base_state import BaseState
from state_tool import after_get_parameter, get_need_verify_types, \
                       get_next_verify_action, generate_log_data,\
                       SUCCESS_STATUS, CRAWL_RETRY_TIMES

from setting.db_config import DB_CONFIG
from setting.status_code import STATUS_CODE

from worker.communicate import get_parameter, success_data, \
                               save_data, save_status, get_today_result

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
db_config = DB_CONFIG['state_log']
logger.addHandler(MongoHandler.to(host=db_config['host'],
                                  port=db_config['port'],
                                  db=db_config['db'],
                                  collection=db_config['collection']))

def extend_log_func(state):
    result = {'verify': {}}
    result['verify']['need_verify_request'] = state.need_verify_request
    result['verify']['sent_verify_request'] = state.sent_verify_request
    result['verify']['now_verify_request'] = ''
    return result

class StartState(BaseState):

    def __init__(self, **kwargs):
        super(StartState, self).__init__(**kwargs)
        self.parameters['tel'] = kwargs['tel']
        self.need_verify_request = []
        self.sent_verify_request = []
        self.now_verify_request = ''
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
        self.data_sid = get_today_result(self.parameters['tel'])
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        status = STATUS_CODE[SUCCESS_STATUS]
        self.execute_message = status['message']
        self.execute_status = status['status']
        self.state_flag = 'WaitLogin'
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class WaitLoginState(BaseState):

    def __init__(self, **kwargs):
        super(WaitLoginState, self).__init__(**kwargs)
        self.next_step = 'Login'
        self.login_verify_type = \
            self.crawler.get_login_verify_type(**self.parameters)
        self.need_verify_request = \
            get_need_verify_types(self.login_verify_type)
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = ''
        tmp_next_action = get_next_verify_action(self.need_verify_request,
                                                 self.sent_verify_request)
        if not tmp_next_action:
            self.next_action = self.next_step
        else:
            self.next_action = 'Get{}'.format(tmp_next_action)
        self.set_current_state()

    def execute(self, **kwargs):
        targets = [self.next_step]
        for verify_type in self.need_verify_request:
            send_target = 'Get{}'.format(verify_type)
            targets.append(send_target)
        parameter_status, parameter_timeout, action, parameters = \
            get_parameter(sid=self.sid, targets=targets)
        status_code, state_flag = after_get_parameter(parameter_status,
                                                      parameter_timeout,
                                                      action)
        if not state_flag:
            self.parameters.update(parameters)
            if action == self.next_step:
                self.state_flag = 'UnderLogin'
            else:
                self.now_verify_request = action.remove('Get')
                self.state_flag = 'UnderLoginVerifyRequest'
        else:
            self.state_flag = state_flag
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class UnderLoginVerifyRequestState(BaseState):

    def __init__(self, **kwargs):
        super(UnderLoginVerifyRequestState, self).__init__(**kwargs)
        self.need_verify_request = self.pre_state.need_verify_request
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = self.pre_state.now_verify_request
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        if self.now_verify_request == 'SMS':
            key, level, message, image_str = \
                self.crawler.send_login_sms_request(**self.parameters)
        elif self.now_verify_request == 'Captcha':
            key, level, message, image_str = \
                self.crawler.send_login_captcha_request(**self.parameters)

        if level == 0:
            status_code = STATUS_CODE[SUCCESS_STATUS]
            self.sent_verify_request.append(self.now_verify_request)
            self.state_flag = 'WaitLogin'
        else:
            status_code = STATUS_CODE[key]
            self.state_flag = 'Failed'
        self.verify_content = image_str
        self.execute_status = status_code['status']
        self.execute_message = message
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class UnderLoginState(BaseState):

    def __init__(self, **kwargs):
        super(UnderLoginState, self).__init__(**kwargs)
        self.need_verify_request = self.pre_state.need_verify_request
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = ''
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        key, level, message = self.crawler.login(**self.parameters)

        self.verify_type = \
            self.crawler.get_verify_type(**self.parameters)
        if level == 0:
            status_code = STATUS_CODE[SUCCESS_STATUS]
            if self.data_sid:
                self.state_flag = 'NoCrawl'
            elif not self.verify_type:
                self.state_flag = 'UnderCrawl'
            else:
                self.state_flag = 'WaitCode'
        elif level in [1, 2]:
            status_code = STATUS_CODE[key]
            self.state_flag = 'WaitLogin'
        else:
            status_code = STATUS_CODE[key]
            self.state_flag = 'Failed'
        self.execute_status = status_code['status']
        self.execute_message = message
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class WaitCodeState(BaseState):

    def __init__(self, **kwargs):
        super(WaitCodeState, self).__init__(**kwargs)
        self.next_step = 'Verify'
        self.need_verify_request = \
            get_need_verify_types(self.verify_type)
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = ''
        tmp_next_action = get_next_verify_action(self.need_verify_request,
                                                 self.sent_verify_request)
        if not tmp_next_action:
            self.next_action = self.next_step
        else:
            self.next_action = 'Get{}'.format(tmp_next_action)
        self.set_current_state()

    def execute(self, **kwargs):
        targets = [self.next_step]
        for verify_type in self.need_verify_request:
            send_target = 'Get{}'.format(verify_type)
            targets.append(send_target)
        parameter_status, parameter_timeout, action, parameters = \
            get_parameter(sid=self.sid, targets=targets)
        status_code, state_flag = after_get_parameter(parameter_status,
                                                      parameter_timeout,
                                                      action)
        if not state_flag:
            self.parameters.update(parameters)
            if action == self.next_step:
                self.state_flag = 'UnderVerify'
            else:
                self.now_verify_request = action.remove('Get')
                self.state_flag = 'UnderVerifyRequest'
        else:
            self.state_flag = state_flag
        self.execute_status = status_code['status']
        self.execute_message = status_code['message']
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class UnderVerifyRequestState(BaseState):

    def __init__(self, **kwargs):
        super(UnderVerifyRequestState, self).__init__(**kwargs)
        self.need_verify_request = self.pre_state.need_verify_request
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = self.pre_state.now_verify_request
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        if self.now_verify_request == 'SMS':
            key, level, message, image_str = \
                self.crawler.send_sms_request(**self.parameters)
        elif self.now_verify_request == 'Captcha':
            key, level, message, image_str = \
                self.crawler.send_captcha_request(**self.parameters)

        if level == 0:
            status_code = STATUS_CODE[SUCCESS_STATUS]
            self.sent_verify_request.append(self.now_verify_request)
            self.state_flag = 'WaitCode'
        else:
            status_code = STATUS_CODE[key]
            self.state_flag = 'Failed'
        self.verify_content = image_str
        self.execute_status = status_code['status']
        self.execute_message = message
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class UnderVerifyState(BaseState):

    def __init__(self, **kwargs):
        super(UnderVerifyState, self).__init__(**kwargs) 
        self.need_verify_request = self.pre_state.need_verify_request
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = ''
        self.set_current_state(receive=True)

    def execute(self, **kwargs):
        key, level, message = self.crawler.verify(**self.parameters)

        if level == 0:
            status_code = STATUS_CODE[SUCCESS_STATUS]
            self.state_flag = 'UnderCrawl'
        elif level == 2:
            status_code = STATUS_CODE[key]
            self.state_flag = 'WaitCode'
        else:
            status_code = STATUS_CODE[key]
            self.state_flag = 'Failed'
        self.execute_status = status_code['status']
        self.execute_message = message
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class UnderCrawlState(BaseState):

    def __init__(self, **kwargs):
        super(UnderCrawlState, self).__init__(**kwargs)
        self.need_verify_request = self.pre_state.need_verify_request
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = ''
        self.next_action = 'Finish'
        self.set_current_state()

    def execute(self, **kwargs):
        user_info = {}
        call_log = []

        parse_call_log = True

        for retry_time in xrange(CRAWL_RETRY_TIMES):
            key, level, message, user_info = \
                self.crawler.crawl_info(**self.parameters)
            if level == 0 and user_info['full_name']:
                break
            time.sleep(3)
        else:
            status_code = STATUS_CODE[key]
            save_data(self.sid, tel=self.tel,
                      user_info=user_info, call_log=call_log,
                      status=status_code['status'], message=message)
            parse_call_log = False
        if parse_call_log:
            for retry_time in xrange(CRAWL_RETRY_TIMES):
                key, level, message, call_log = \
                    self.crawler.crawl_call_log(**self.parameters)
                if level == 0:
                    status_code = STATUS_CODE[SUCCESS_STATUS]
                    break
                else:
                    status_code = STATUS_CODE[key]
                time.sleep(3)
            save_data(self.sid, tel=self.tel,
                      user_info=user_info, call_log=call_log,
                      status=status_code['status'], message=message)
            if level == 0:
                success_data(self.sid)
        self.execute_status = status_code['status']
        self.execute_message = message
        self.state_flag = 'End'
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class FailedState(BaseState):

    def __init__(self, **kwargs):
        super(FailedState, self).__init__(**kwargs)
        self.next_action = 'Reset'
        self.need_verify_request = self.pre_state.need_verify_request
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = ''
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        save_status(self.sid, self.pre_status, self.pre_message)
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class AbortState(BaseState):

    def __init__(self, **kwargs):
        super(AbortState, self).__init__(**kwargs)
        self.next_action = 'Finish'
        self.need_verify_request = self.pre_state.need_verify_request
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = ''
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        status = STATUS_CODE['user_exit']['status']
        message = STATUS_CODE['user_exit']['message']
        save_status(self.sid, status, message)
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class EndState(BaseState):

    def __init__(self, **kwargs):
        super(EndState, self).__init__(**kwargs)
        self.next_action = 'Finish'
        self.need_verify_request = self.pre_state.need_verify_request
        self.sent_verify_request = self.pre_state.sent_verify_request
        self.now_verify_request = ''
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

class NoCrawlState(BaseState):

    def __init__(self, **kwargs):
        super(NoCrawlState, self).__init__(**kwargs)
        self.need_verify_request = []
        self.sent_verify_request = []
        self.now_verify_request = ''
        self.next_action = 'NoCrawlFinish'
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        message = generate_log_data(self, extend_log_func)
        logger.info(message)

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
        self.need_verify_request = []
        self.sent_verify_request = []
        self.now_verify_request = ''
        self.set_current_state()

    def execute(self, **kwargs):
        self.state_flag = ''
        status = STATUS_CODE['no_supported_crawler']['status']
        message = STATUS_CODE['no_supported_crawler']['message']
        save_status(self.sid, status, message)
        message = generate_log_data(self, extend_log_func)
        logger.info(message)


CLASS_LIST = inspect.getmembers(sys.modules[__name__], inspect.isclass)
CLASS_DICT = {pair[0]:pair[1] for pair in CLASS_LIST}

def state_interface(**kwargs):
    state_flag = kwargs['state_flag']
    if not state_flag:
        return None
    state_flag = '{}State'.format(state_flag)
    return CLASS_DICT[state_flag](**kwargs)
