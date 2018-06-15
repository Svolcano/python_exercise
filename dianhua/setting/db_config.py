# -*- coding: utf-8 -*-

import copy
import importlib

from api_config import ENV

env = importlib.import_module('setting.env_{}'.format(ENV)).env


# REDIS_CONFIG
REDIS_CONFIG = {
    'host' : env['redis']['host'],
    'port' : env['redis']['port'],
    'db' : env['redis']['db'],
}

# MONGO_CONFIG
BASE_CONFIG = {
    'host': env['mongo']['host'],
    'port': env['mongo']['port'],
    'db': env['mongo']['db']
}

STATE_CONFIG = copy.deepcopy(BASE_CONFIG)
STATE_CONFIG['collection'] = 'state'

PARAMETER_CONFIG = copy.deepcopy(BASE_CONFIG)
PARAMETER_CONFIG['collection'] = 'params'

CALL_LOG_CONFIG = copy.deepcopy(BASE_CONFIG)
CALL_LOG_CONFIG['collection'] = 'call_log'

PHONE_BILL_CONFIG = copy.deepcopy(BASE_CONFIG)
PHONE_BILL_CONFIG['collection'] = 'phone_bill'

SID_INFO_CONFIG = copy.deepcopy(BASE_CONFIG)
SID_INFO_CONFIG['collection'] = 'sid_info'

USER_INFO_CONFIG = copy.deepcopy(BASE_CONFIG)
USER_INFO_CONFIG['collection'] = 'user_info'

RESULT_CONFIG = copy.deepcopy(BASE_CONFIG)
RESULT_CONFIG['collection'] = 'sid_info'

STATE_LOG_CONFIG = copy.deepcopy(BASE_CONFIG)
STATE_LOG_CONFIG['collection'] = 'state_log'

LOG_CONFIG = copy.deepcopy(BASE_CONFIG)
LOG_CONFIG['collection'] = 'log'

REPORT_CONFIG = copy.deepcopy(BASE_CONFIG)
REPORT_CONFIG['collection'] = 'report'


CALL_LOG_DETAILS_CONFIG = copy.deepcopy(BASE_CONFIG)
CALL_LOG_DETAILS_CONFIG['collection'] = 'call_log_details'

DAMA_CONFIG = copy.deepcopy(BASE_CONFIG)
DAMA_CONFIG['collection'] = 'dama_cfg'


OTHER_CALL_LOG_CONFIG = copy.deepcopy(BASE_CONFIG)
OTHER_CALL_LOG_CONFIG['collection'] = 'other_call_log'

PHONE_BILL_CACHE_CONFIG = copy.deepcopy(BASE_CONFIG)
PHONE_BILL_CACHE_CONFIG['collection'] = 'phone_bill_cache'

OTHER_PHONE_BILL_CONFIG = copy.deepcopy(BASE_CONFIG)
OTHER_PHONE_BILL_CONFIG['collection'] = 'other_phone_bill'

DB_CONFIG = {
    'base': BASE_CONFIG,
    'result': RESULT_CONFIG,
    'state': STATE_CONFIG,
    'params': PARAMETER_CONFIG,
    'user_info': USER_INFO_CONFIG,
    'call_log': CALL_LOG_CONFIG,
    'phone_bill': PHONE_BILL_CONFIG,
    'sid_info': SID_INFO_CONFIG,
    'state_log': STATE_LOG_CONFIG,
    'log': LOG_CONFIG,
    'report': REPORT_CONFIG,
    'call_log_details':CALL_LOG_DETAILS_CONFIG,
    'dama_cfg':DAMA_CONFIG,
    'other_call_log':OTHER_CALL_LOG_CONFIG,
    'phone_bill_cache':PHONE_BILL_CACHE_CONFIG,
    'other_phone_bill':OTHER_PHONE_BILL_CONFIG,
}
