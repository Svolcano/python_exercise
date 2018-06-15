# -*- coding: utf-8 -*-

from worker.communicate import set_state
from setting.status_code import STATUS_CODE
from com.logger import logger
from worker.communicate import kill_machine

class BaseState(object):

    def __init__(self, **kwargs):
        self.state_name = type(self).__name__.replace('State', '')

        self.pre_state = kwargs.get('pre_state', None)
        if self.pre_state is not None:
            self.sid = self.pre_state.sid
            self.cache_time = self.pre_state.cache_time
            self.tel = self.pre_state.tel
            self.parameters = self.pre_state.parameters
            self.crawler = self.pre_state.crawler
            self.pre_state_name = type(self.pre_state).__name__.replace('State', '')
            self.pre_status = self.pre_state.execute_status
            self.pre_message = self.pre_state.execute_message
            self.verify_type = self.pre_state.verify_type
            self.login_verify_type = self.pre_state.login_verify_type
            self.verify_content = self.pre_state.verify_content
            self.need_parameters = self.pre_state.need_parameters
            self.wait_code_get_login = self.pre_state.wait_code_get_login
        else:
            self.sid = kwargs['sid']
            self.cache_time = ''
            self.tel = kwargs['tel']
            self.crawler = kwargs['crawler']
            kwargs['crawler'] = kwargs['crawler'].__module__ if kwargs['crawler'] else None
            self.parameters = kwargs
            self.pre_state_name = ''
            self.pre_status = STATUS_CODE['success']['status']
            self.pre_message = ''
            self.verify_type = ''
            self.login_verify_type = ''
            self.verify_content = ''
            self.need_parameters = []
            self.wait_code_get_login = False

        self.state_flag = ''
        self.execute_status = 0
        self.execute_message = ''

        try:
            self.next_action
        except:
            self.next_action = ''

    def set_current_state(self, receive=False):
        return_info = {'status': self.pre_status,
                       'message': self.pre_message,
                       'next_action': self.next_action,
                       'content': self.verify_content}
        ret = kill_machine(self.sid)
        if ret==False:
            self.state_flag = 'interrupt'
            return
        set_state(sid=self.sid,
                  state=self.state_name,
                  info=return_info,
                  pre_state=self.pre_state_name,
                  need_parameters=self.need_parameters,
                  receive=receive)

    def log(self, level='ERROR', message=None, state=None, missing_dict=None):
        """
        状态机日志调用：
        usage：
            self.log("ERROR", "crawl_error", message, response)
        """
        data = {}
        log_name = 'state_log'
        state_log = {}

        if self.crawler is not None:
            crawler = self.crawler.__module__.replace("worker.crawler.","").replace(".main","")
        else:
            crawler = 'None'

        if not message:
            message = '{}:{}'.format(self.execute_message, self.state_name)

            state_log = {
                'state_name': self.state_name,
                'execute_status': self.execute_status,
                'execute_msg': self.execute_message,
                'next_action': self.next_action,
                'state_flag': self.state_flag
            }

        if self.state_name in ['UnderVerify', 'UnderLogin']:
            parameters = self.parameters
            parameters.pop('sid', None)
            parameters.pop('crawler', None)
            state_log['parameters'] = parameters

        if missing_dict:
            state_log.update(missing_dict)

        if state:
            state_log['state_name'] = state.get('state_name', '')
            state_log['execute_status'] = state.get('execute_status', '')
            state_log['execute_msg'] = state.get('execute_message', '')

        data.update({
            'sid':self.sid,
            'crawler':crawler,
            'state_log':state_log
        })
        logger(log_name, level, message, **data)


    def next_state(self, **kwargs):
        return self.state_flag

    def execute(self, **kwargs):
        pass
