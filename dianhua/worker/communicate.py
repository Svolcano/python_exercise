# -*- coding: utf-8 -*-
import time
import traceback

from setting.api_config import SID_EXPIRE_TIME, STEP_TIME
from setting.status_code import STATUS_CODE
from com.connection import db
from com.logger import logger

from mrq.context import  get_current_job

def reset_parameter(**kwargs):
    sid = kwargs['state'].sid
    state_name = kwargs['state'].state_name
    filter_data = {'sid': sid}
    update_data = {'$set':{'receive':True}}

    try:
        for _ in xrange(3):
            result = db['params'].update_one(filter_data, update_data, upsert=True)
            if result.modified_count:
                break
            time.sleep(0.1)
        else:
            logger('mongo_log', 'ERROR', 'update params receive error', **{'sid': sid, 'state': state_name})
    except:
        message = traceback.format_exc()
        logger('mongo_log', 'ERROR', message, **{'sid': sid, 'state': state_name})

def get_parameter(**kwargs):
    sid = kwargs['state'].sid

    # limu的渠道
    sid_info = db['sid_info'].find_one({'sid': sid, 'crawler_channel': {'$exists': True}})
    if sid_info:
        return True, False, 'Abort', {}

    targets = kwargs['targets']
    targets.append('Abort')
    filter_data = {'sid': sid, 'receive':False}

    for i in xrange(int(SID_EXPIRE_TIME/STEP_TIME)):
        result = list(db['params'].find(filter_data))
        if result:
            res_action = result[0]['action']
            for target in targets:
                if res_action == target:
                    parameters = result[0].get('parameters', {})
                    reset_parameter(state=kwargs['state'])
                    return True, False, target, parameters
            else:
                #处理不调短信直接验证的情况
                if kwargs['state'].next_action in ['GetSMS','GetSMSCaptcha'] and res_action in ['Login', 'Verify']:
                    reset_parameter(state=kwargs['state'])
                    return False, False, 'Error{}Flow'.format(res_action), {}
                message="Api_params:{}, Crawler_action:{}".format(result, targets)
                kwargs['state'].log(level='get_parameter', message=message)
                return False, False, '', {}
        time.sleep(STEP_TIME)
        
        #轮询中查看自身状态，判断状态机是否自杀
        ret = kill_machine(sid)
        if ret==False:
            message="Api_params:{}, Crawler_action:{}".format(result, targets)
            kwargs['state'].log(level='get_parameter', message=message)
            return False, False, 'interrupt', {}
    else:
        kwargs['state'].log(level='get_parameter', message="wait_params_timeout")
        return False, True, '', {}

def set_state(**kwargs):
    sid = kwargs['sid']
    state = kwargs['state']
    pre_state = kwargs['pre_state']
    info = kwargs['info']
    need_parameters = kwargs['need_parameters']
    receive = kwargs.get('receive', False)
    
    filter_data = {'sid': sid}
    update_data = {'sid': sid,
                   'state': state,
                   'receive': receive,
                   'pre_state': pre_state,
                   'need_parameters': need_parameters,
                   'info': info}
    try:
        for _ in xrange(3):
            result = db['state'].update_one(filter_data, {'$set':update_data}, upsert=True)
            if result.raw_result.get('ok') == 1:
                break
            time.sleep(0.1)
        else:
            logger('mongo_log', 'ERROR', 'update state error', **update_data)
    except:
        message = traceback.format_exc()
        logger('mongo_log', 'ERROR', message, **update_data)

def save_status(sid, status, message, cache_time=None):
    timestamp = int(time.mktime(time.localtime()))
    filter_data = {'sid': sid}
    update_data = {'status': status,
                   'message': message,
                   'end_time': timestamp}
    if cache_time:
        update_data.update({'cache_time':cache_time})

    # limu的渠道
    sid_info = db['sid_info'].find_one({'sid': sid, 'crawler_channel': {'$exists': True}})
    if sid_info:
        return True

    try:
        for _ in xrange(3):
            result = db['sid_info'].update_one(filter_data, {'$set':update_data}, upsert=True)
            if result.modified_count:
                break
            time.sleep(0.1)
        else:
            logger('mongo_log', 'ERROR', 'save status error', **{'sid': sid, 'update_data': update_data})
    except:
        message = traceback.format_exc()
        logger('mongo_log', 'ERROR', message, **{'sid': sid, 'update_data': update_data})
        return False
    return True

def save_data(sid, **kwargs):
    #timestamp = datetime.datetime.utcnow()
    timestamp = int(time.mktime(time.localtime()))
    tel = kwargs['tel']
    status = kwargs['status']
    message = kwargs['message']
    mongo_error = STATUS_CODE['internal_error']

    insert_data = []
    for each in kwargs['call_log']:
        log_data = each
        log_data['update_time'] = timestamp
        log_data['tel'] = tel
        log_data['sid'] = sid
        insert_data.append(log_data)
    ret = insert_db_data('call_log', insert_data)
    if not ret:
        status = mongo_error['status']
        message = mongo_error['message']

    filter_data = {'tel': tel}
    update_data = kwargs.get('user_info', {})
    if not update_data:
        update_data = {}
    update_data['update_time'] = timestamp
    ret = update_db_data('user_info', filter_data, update_data)
    if not ret:
        status = mongo_error['status']
        message = mongo_error['message']

    if kwargs['phone_bill']:
        phone_bill_data = {}
        phone_bill_data['tel'] = tel
        phone_bill_data['sid'] = sid
        phone_bill_data['update_time'] = timestamp
        phone_bill_data['phone_bill'] = kwargs['phone_bill']
        ret = insert_db_data('phone_bill', phone_bill_data)
        # if not ret:
        #     return False

    filter_data = {'sid': sid}
    update_data = {
        "status": status,
        "message": message,
        "end_time": timestamp,
        "call_log_missing_month_list": kwargs.get('missing_log_list', []),
        "call_log_possibly_missing_month_list": kwargs.get('possibly_missing_list', []),
        "call_log_part_missing_month_list": kwargs.get('part_missing_list', []),
        "phone_bill_missing_month_list": kwargs.get('missing_bill_list', []),
        "call_log_cache_hit_month_list": kwargs.get('cache_hit_month_list', []),
        "call_log_fusion_cost_time": kwargs.get('fusion_cost_time', 0),
        "crawl_status": kwargs.get('crawl_status', 0),
        "bill_cache_hit_month_list": kwargs.get('bill_cache_hit_month_list', []),
        "bill_fusion_cost_time": kwargs.get('bill_fusion_cost_time', 0),
    }

    ret = update_db_data('sid_info', filter_data, update_data)
    return True

def insert_db_data(table, data):
    if not data:
        logger('mongo_log', 'ERROR', 'There is no data to insert', **{'insert_data': data})
        return True

    if type(data) is dict:
        result = db[table].insert_one(data)
        return result.inserted_id

    try:
        for retry_time in xrange(3):
            if db[table].insert_many(data):
                break
            time.sleep(0.1)
    except:
        message = traceback.format_exc()
        logger('mongo_log', 'ERROR', message, **{'insert_data': data})
        return False

    return True

def merge_two_dicts(x, y):
    # print x,y
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def update_db_data(collection, filter_data, update_data, upsert=True):
    try:
        for retry_time in xrange(3):
            res = db[collection].update_one(filter_data, {'$set':update_data}, upsert=True)
            if res.modified_count:
                break
            time.sleep(0.1)
        else:
            # logger('mongo_log', 'ERROR', 'update data error', **merge_two_dicts(filter_data, update_data))
            logger('mongo_log', 'ERROR', 'update data error', **filter_data)
    except:
        message = traceback.format_exc()
        # logger('mongo_log', 'ERROR', message, **merge_two_dicts(filter_data, update_data))
        logger('mongo_log', 'ERROR', message, **filter_data)
        return True

    return True

def get_best_info(sid_list):
    pattern = lambda x, y: y.get(x, [])
    min_len = 8
    len_idx = None
    for i, j in enumerate(sid_list):
        lenth = len(pattern('call_log_missing_month_list', j) + pattern('call_log_possibly_missing_month_list', j) + pattern('call_log_part_missing_month_list', j))
        min_len, len_idx = (lenth, i) if lenth < min_len else (min_len, len_idx)

    # 缺失月份大于2，不取缓存
    if min_len > 2 and not len_idx:
        return ''
    return sid_list[len_idx]

def get_today_result(tel):
    st_time = int(time.time())
    sid_list = list(db['sid_info'].find({'tel': tel, 'status': 0, 'end_time':{'$gt':st_time-86400, '$lt':st_time}}, 
                    {'sid':1, 'end_time':1, 'cache_time':1, 'call_log_missing_month_list':1, 
                    'call_log_part_missing_month_list':1, 'call_log_possibly_missing_month_list':1}, sort=[('_id', -1)]))
    
    sid_info = get_best_info(sid_list)
    

    if not sid_info:
        return ''

    last_cache_time = ''

    cache_time = sid_info.get('cache_time', '')
    if cache_time:
        if st_time - int(cache_time) > 86400:
            return ''
        else:
            last_cache_time = cache_time
    else:
        last_cache_time = sid_info.get('end_time', '')

    return last_cache_time


def kill_machine(sid):
    sid_info = db['sid_info'].find_one({'sid': sid}, {'job_id':1})
    if not sid_info:
        return False
#    print sid
    job=get_current_job()
#    print job
    
#    print 'sid_info:'+str(sid_info.get('job_id'))
      
#    print  job.id
    if job.exists() and str(job.id)==str(sid_info.get('job_id')):
        return True
    else:
        # print 'machine_job:'+str(job.id)+'将被终止!'
        return False
  