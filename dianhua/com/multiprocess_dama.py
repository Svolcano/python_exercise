# -*- coding: utf-8 -*-


# ad   huang

from com.connection import db
import os, time, sys
from com.logger import logger

from setting.dama2 import DAMA2_CODE
from setting.yundama_config import YUNDAMA_CODE
from setting.feifeidama import fateadm_code
from setting.dama_type import DAMA_TYPE

from com.yundama import yundama
from com.dama2 import dama2
from com.feifeidama import fateadm
from multiprocessing import Process,Pipe
import traceback
'''
dama_pad_code
err_times
priority_level
'''

def cross():
    dama_cfg_info = db['dama_cfg'].find({})
    for one_cfg in dama_cfg_info:
        if one_cfg['priority_level']==2:
            db['dama_cfg'].update({'dama_pad_code':one_cfg['dama_pad_code']},{'$set':{'priority_level':1,'err_times':0}})
        elif one_cfg['priority_level']==3:
            db['dama_cfg'].update({'dama_pad_code':one_cfg['dama_pad_code']},{'$set':{'priority_level':2,'err_times':0}})
        elif one_cfg['priority_level']==1:
            db['dama_cfg'].update({'dama_pad_code':one_cfg['dama_pad_code']},{'$set':{'priority_level':3,'err_times':0}})
         
    return 
            

def get_dama_pad(proc_no):
    dama_cfg_info = db['dama_cfg'].find_one({'priority_level':1})
    if dama_cfg_info['err_times']>=10:
        cross()
    elif proc_no==0:
        return dama_cfg_info['dama_pad_code'],dama_cfg_info['dama_pad_code']
    else:
        dama_cfg_info = db['dama_cfg'].find_one({'priority_level':proc_no+1})
        return dama_cfg_info['dama_pad_code'],dama_cfg_info['dama_pad_code']
    return None

def __fateadm( img_data, code_type):
    dama_dict = DAMA_TYPE.get(str(code_type), {})
    # print dama_dict
    if not dama_dict:
        return 'crawl_error', u"打码类型错误:{}".format(code_type), "","__fateadm"
    dama_type = dama_dict.get('channel')[2]
    try:
        ret, cid, result = fateadm.Predict(dama_type, img_data)
        # print ret, result
        if ret == 0 and result != "":
            captcha_code = str(result).lower()
            return 'success', captcha_code, cid,"__fateadm"
        else:
            fateadm.Justice(cid)
            message = fateadm_code.get(str(ret), '').decode('utf-8')
            if ret == "4003":
                return 'crawl_error', u"打码欠费:\n{}".format(message), "","__fateadm"
            return 'website_busy_error', u"打码异常:\n{}".format(message), "","__fateadm"
    except:
        error = traceback.format_exc()
        return 'website_busy_error', u"打码异常:\n{}".format(error), "","__fateadm"



def __dama2( img_data, code_type):
    dama_dict = DAMA_TYPE.get(str(code_type), {})
#    print dama_dict
    if not dama_dict:
        return 'crawl_error', u"打码类型错误:{}".format(code_type), "","__dama2"
    dama_type = dama_dict.get('channel')[0]
#    print dama_type
    try:
        cid, result = dama2.decode(img_data, dama_type)
        print cid, result
    except:
        error = traceback.format_exc()
        return 'website_busy_error', u"打码异常:\n{}".format(error), "","__dama2"
    if cid > 0 and result != "":
        captcha_code = str(result).lower()
        return 'success', captcha_code, cid,"__dama2"
    else:
        dama2.reportError(cid)
        message = DAMA2_CODE.get(str(cid), '').decode('utf-8')
        if cid == "-304":
            return 'crawl_error', u"打码欠费:\n{}".format(message), "","__dama2"
        return 'website_busy_error', u"打码异常:\n{}".format(message), "","__dama2"

def __yundama( img_data, code_type):
    dama_dict = DAMA_TYPE.get(str(code_type), {})
    # print dama_dict
    if not dama_dict:
        return 'crawl_error', u"打码类型错误:{}".format(code_type), "","__yundama"
    dama_type = dama_dict.get('channel')[1]
    try:
        cid, result = yundama.decode(img_data, dama_type)
        if cid > 0 and result != "":
            captcha_code = str(result).lower()
            return 'success', captcha_code, cid,"__yundama"
        else:
            yundama.report(cid)
            message = YUNDAMA_CODE.get(str(cid), '').decode('utf-8')
            if cid == "-1007":
                return 'crawl_error', u"打码欠费:\n{}".format(message), "","__yundama"
            return 'website_busy_error', u"打码异常:\n{}".format(message), "","__yundama"
        # print code_type, cid, result
    except:
        error = traceback.format_exc()
        return 'website_busy_error', u"打码异常:\n{}".format(error), "","__yundama"

def add_error_times(dama_pad_code):
    db['dama_cfg'].update({'dama_pad_code':dama_pad_code},{'$inc':{'err_times':1}})
    
def init_error_times(dama_pad_code):
    db['dama_cfg'].update({'dama_pad_code':dama_pad_code},{'$set':{'err_times':0}})
    

def dama_proccess(sid,img_data, code_type,proc_code,child_conn): 
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all()
    try:
        dama_pad,dama_pad_code=get_dama_pad(proc_code)
        if dama_pad==None:
            return 'crawl_error', u"获取打码平台编号失败", "",None
        dama_pad = globals().get(dama_pad)
#        print (dama_pad)
        task=gevent.spawn(dama_pad,img_data, code_type)
        timer = gevent.Timeout(60).start()
        try:
            task.join(timer)
            pass
        except gevent.Timeout, e:
            print( 'found error: thread 1 timeout.'+str(e))
            child_conn.close()
            add_error_times(dama_pad_code)
            return False
#        print task.value
        if task.value[0] == 'success':
            child_conn.send(task.value )
            init_error_times(dama_pad_code)
            child_conn.close()
        else:
            add_error_times(dama_pad_code)
    except:
        error = traceback.format_exc()
        print(error)
    return True


def multiprocess_dama(sid,img_data, code_type):
    log_name='multiprocess_dama'
    data={'sid':sid}
    parent_conn,child_conn = Pipe()
    begin_time=time.time()
    proccess_flag=0
    p1 = Process(target=dama_proccess, args=(sid,img_data, code_type,proccess_flag,child_conn,))  #申请子进程
    p1.deamon = True
    p1.start()     #运行进程
    proccess_flag=1
    print ('A进程启动完毕')
    data['p1']='p1'
    data['A进程启动完毕']='A进程启动完毕'
    while True:
        end_time=time.time()
#        print (end_time-begin_time)
        if end_time-begin_time>20 and proccess_flag==1:
            p2 = Process(target=dama_proccess, args=(sid,img_data, code_type,proccess_flag,child_conn,))  #申请子进程
            p2.deamon = True
            p2.start()     #运行进程
            proccess_flag=2
            print ('B进程启动完毕')
            data['B进程启动完毕']='B进程启动完毕'
            data['p2']='p2'
        if end_time-begin_time>40 and proccess_flag==2:
            p3 = Process(target=dama_proccess, args=(sid,img_data, code_type,proccess_flag,child_conn,))  #申请子进程
            p3.start()     #运行进程 
            p3.deamon = True
            proccess_flag=3
            print ('C进程启动完毕')
            data['C进程启动完毕']='C进程启动完毕'
            data['p3']='p3'

        data['proccess_flag']=proccess_flag
        if parent_conn.poll():
            task=parent_conn.recv()
            if len(task)>2:
                print ('收到管道信息'.format(task))
                data['收到管道信息']=task
                parent_conn.close()
                child_conn.close()
                logger(log_name, task[0],task[1], **data)
                return task
        if end_time-begin_time>60:
            break
        time.sleep(1)
        print (end_time-begin_time)
    logger(log_name, 'crawl_error','打码平台超时', **data)
    return  'crawl_error', u"打码平台超时", "",None
    
    
    
