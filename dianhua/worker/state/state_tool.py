# -*- coding: utf-8 -*-

from setting.status_code import STATUS_CODE

SUCCESS_STATUS = 'success'

FAILED_STATUS = 'timeout'

CRAWL_RETRY_TIMES = 3

def after_get_parameter(status, timeout, action):
    if action == 'interrupt':
        status_code = STATUS_CODE['user_exit']
        state_flag = 'interrupt'
    elif action == 'ErrorLoginFlow':
        status_code = STATUS_CODE['verify_error']
        state_flag = 'Failed'
    elif action == 'ErrorVerifyFlow':
        status_code = STATUS_CODE['verify_error']
        state_flag = 'WaitVerifyRequest'
    elif action == 'Abort':
        status_code = STATUS_CODE['user_exit']
        state_flag = 'Abort'
    elif timeout:
        status_code = STATUS_CODE['param_timeout']
        state_flag = 'Failed'
    elif not status:
        status_code = STATUS_CODE['param_error']
        state_flag = 'Failed'
    else:
        status_code = STATUS_CODE[SUCCESS_STATUS]
        state_flag = ''
    return status_code, state_flag

def get_need_verify_types(verify_type):
    if verify_type == 'SMSCaptcha':
        return ['Captcha', 'SMS']
    else:
        return [verify_type]

def get_next_verify_action(need_verify_request, sent_verify_request):
    for verify_request in need_verify_request:
        if verify_request not in sent_verify_request:
            return verify_request
    return ''

def generate_log_data(state, extend_log_func=None):
    result = {}
    result['sid'] = state.sid
    result['state_name'] = state.state_name
    result['parameters'] = state.parameters
    result['next_action'] = state.next_action
    result['execute_status'] = state.execute_status
    result['execute_message'] = state.execute_message
    result['execute_debug'] = state.execute_debug
    result['state_flag'] = state.state_flag
    if state.crawler is not None:
        result['crawler'] = state.crawler.__module__
    else:
        result['crawler'] = 'None'
    result['verify'] = {}
    result['verify']['login_verify_type'] = state.login_verify_type
    result['verify']['verify_type'] = state.verify_type
    result['verify']['verify_content'] = state.verify_content
    result['pre'] = {}
    if state.pre_state is not None:
        result['pre']['execute_status'] = state.pre_state.execute_status
        result['pre']['execute_message'] = state.pre_state.execute_message
        result['pre']['execute_debug'] = state.pre_state.execute_debug
    else:
        result['pre']['execute_status'] = -1
        result['pre']['execute_message'] = ''
        result['pre']['execute_debug'] = ''
    if extend_log_func is not None:
        result.update({'extend':extend_log_func(state)})
    return result
