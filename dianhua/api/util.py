# -*- coding:utf-8 -*-
import os
import re
import time
import codecs
import traceback

from mrq.job import queue_job, get_job_result, Job

import setting.api_config as config
from setting.status_code import STATUS_CODE
from com.connection import db
from com.redis_conn import redis_instance

def get_tel_info(tel_prefix):
    data = redis_instance.get(tel_prefix)
    if data:
        data_list = data.split(',')
        return {'telecom': data_list[0], 'province': data_list[1], 'city': data_list[2]}
    return {}

def tel_loc_info(tel):
    try:
        # check the tel which location it belongs
        tel_prefix = tel[:7]
        tel_info = get_tel_info(tel_prefix)
        if not tel_info:
            return {}
        telecom = tel_info['telecom'].decode('utf8')
        tel_info.update(config.TELECOM_FLOW_INFO[telecom])
        return tel_info
    except:
        # handle any uncertain exception
        return {}

def pass_crawler_params(sid, action, params):
    update_data = {'sid': sid, 'action': action, 'receive': False,
                   'parameters': params}
    ret = db['params'].update_one({'sid':sid}, {'$set':update_data}, upsert=True)
    return ret

def init_sid_info():
    try:
        db['sid_info'].create_index(('sid'), unique=True)
    except:
        print traceback.format_exc()
        return False
    return True

def get_sid_info(sid):
    ret = db['sid_info'].find_one({'sid':sid})
    if not ret:
        return {}
    # timestamp - expire_time to see if it is expired
    timestamp = int(time.mktime(time.localtime()))
    expire_time = ret['expire_time']
    if timestamp > expire_time:
        # expired
        ret['is_expired'] = True
    else:
        # not expired, and update the new expire time
        ret['is_expired'] = False
        update_data = {'expire_time': timestamp + config.SID_EXPIRE_TIME}
        db['sid_info'].update_one({'sid':sid}, {'$set':update_data})
    return ret

def set_sid_info(sid, tel, tel_info):
    timestamp = int(time.mktime(time.localtime()))
    insert_data = {
        'sid': sid,
        'tel': tel,
        'start_time': timestamp,
        'status': 1,
        'message': 'start to crawl',
        'end_time': timestamp,
        'expire_time': timestamp + config.SID_EXPIRE_TIME
    }
    insert_data.update(tel_info)

    try:
        db['sid_info'].insert_one(insert_data)
    except:
        print traceback.format_exc()
        return False

    return True

def undo_sid_info(sid,tel):
    try: 
        ret=db['sid_info'].find_one({'sid':sid,'tel':tel})
        if ret:
            # print ret
            #checkout state
            # job_id = ret.get('job_id', "")
            # try:
                # jobs = Job(job_id)
                # jobs.cancel()
            # except:
                # print traceback.format_exc()
            ret=db['sid_info'].remove({'sid':sid,'tel':tel})
            ret = db['state'].find_one({'sid': sid})
            if ret:
                # print ret
                ret=db['state'].remove({'sid':sid})

            ret=db['params'].find_one({'sid':sid})
            if ret:
                # print ret
                ret=db['params'].remove({'sid':sid})
            #init state
            return True
        return False

    except:
        print traceback.format_exc()
        return False

def send_crawl_task(sid, tel, flow_type, province, city, timeout=5, sleep_time=1):
    alive = check_crawler_alive(sid)
    if alive:
        return False
    else:
        # send job queue to start crawler
        params = {
            'sid': sid,
            'tel': tel,
            'flow_type': flow_type,
            'province': province,
            'city': city
        }
        job_id = queue_job(config.TASK_PATH, params, queue=config.QUEUE_NAME)
        
        if len(str(job_id))>11:    
            db['sid_info'].update_one(
                    {'sid': sid}, {'$set': {'job_id':job_id}}, upsert=True)
            return True
        else:
            return False


# db communicate util
# def check_sid_used(sid, tel):
#     mongo_config = _DB_CONFIG['sid']
#     client = pymongo.MongoClient(mongo_config['host'], mongo_config['port'])
#     c = client[mongo_config['db']][mongo_config['collection']]
#     ret = c.find_one({'sid': sid})
#     if ret or ret.get('tel', '') != tel:
#         return False
#     return True

def check_crawler_alive(sid):
    ret = db['state'].find_one({'sid': sid})
    if not ret:
        return False
    return True

def check_login_state(sid, timeout=config.STATE_TIME_OUT, sleep_time=config.STEP_TIME):
    max_retry = int(timeout/sleep_time)
    retry = 0
    while(retry < max_retry):
        retry += 1
        ret = db['state'].find_one({'sid':sid})
        if not ret:
            time.sleep(sleep_time)
        elif ret['state'] == 'Crawl':
            return True, ret
        elif ret['state'] == 'Wait Code Request':
            return True, ret
        elif 'Failed' in ret['state']:
            return False, ret
        else:
            time.sleep(sleep_time)
    return False, {}

#def check_crawler_state(sid, states, timeout=5, sleep_time=0.5):
def check_crawler_state(sid, timeout=config.STATE_TIME_OUT, sleep_time=config.STEP_TIME):
    max_retry = int(timeout/sleep_time)
    retry = 0
    ret = {}
    while(retry < max_retry):
        time.sleep(sleep_time)
        retry += 1
        #ret = c.find_one({'sid':sid, 'state': {'$in': states}})
        ret = db['state'].find_one({'sid':sid, 'receive': False})
        if ret:
            update_data = {'receive': True}
            db['state'].update_one({'sid':sid}, {'$set':update_data}, upsert=True)
            return True, ret

    ret = {
        'sid': sid,
        'info': {
            'next_action': 'Reset',
            'status': STATUS_CODE['timeout']['status'],
            'message': STATUS_CODE['timeout']['message']
        }
    }

    # api_log
    return False, ret

def check_sid_info_error(sid_info):
    timestamp = int(time.mktime(time.localtime()))
    if not sid_info:
        error = STATUS_CODE['invalid_sid']
    elif sid_info['expire_time'] < timestamp:
        error = STATUS_CODE['outdated_sid']
    elif sid_info['status'] != 1:
        error = STATUS_CODE['duplicate_sid']
    else:
        return {}

    error['next_action'] = 'Reset'
    return error