# -*- coding: utf-8 -*-
"""
Created on Wed May 16 09:43:49 2018

@author: huang
"""
import traceback
import sys
import time
import copy
from com.logger import logger


from com.connection import db
sys.path.append('../')
from worker.communicate import insert_db_data



TABLE_COL_MAP={
        'bill_ext_sms':'bes',
        'tel':'tel',
        'bill_daishoufei':'dsf',
        'bill_amount':'bat',
        'bill_zengzhifei':'zzf',
        'bill_ext_data':'bed',
        'bill_qita':'qta',
        'bill_month':'mon',
        'bill_package':'bpe',
        'bill_ext_calls': 'bec',
        'bes':'bill_ext_sms',
        'dsf':'bill_daishoufei',
        'bat':'bill_amount',
        'zzf':'bill_zengzhifei',
        'bed':'bill_ext_data',
        'qta':'bill_qita',
        'mon':'bill_month',
        'bpe':'bill_package',
        'bec': 'bill_ext_calls',
        'uti':'uti'      
}  


 

def insert_data(data):
    where_dict={'tel':data['tel']}
    ret = db['phone_bill_cache'].update(where_dict,data,upsert=True)
    return ret

def get_tel_data(tel):
    where_dict={'tel':tel}
    ret = db['phone_bill_cache'].find_one(where_dict,{'_id':0})
    return ret

def craw_data_std(tel,final_bill_logs,missing_month_list):
    data_dict={}
    month_list=[]
#    print final_bill_logs,'59'
#    print len(final_bill_logs)
    if len(final_bill_logs)>0:
        for i,x in enumerate(final_bill_logs):
            # 过滤x
#            print x
            if len(x)<9:
                continue
#            print x['bill_month']
            if x['bill_month'] in missing_month_list:
                continue
            new_x={}
            if not data_dict.has_key('tel') :
                data_dict={'tel':tel}
                data_dict['uti']=str(int(time.time()))
            for key,value in x.items():
    #            print key,value
                if  TABLE_COL_MAP.has_key(key):
                    new_x[TABLE_COL_MAP[key]]=value
            if  not data_dict.has_key(new_x['mon']):
                
                month_list.append(new_x['mon'])
    #            print month_list,'75'
                data_dict[new_x['mon']]=new_x
        
    return data_dict,month_list


def cross_key_name(data):
    data_dict_fin={}
    for key,value in data.items():
        if key  in TABLE_COL_MAP:
            if type(value).__name__=='dict':
                data_dict_fin[TABLE_COL_MAP[key]]=cross_key_name(value)
            elif type(value).__name__=='list':
                new_list=[]
                for a_list in value:
                    new_list.append(cross_key_name(a_list))
                data_dict_fin[TABLE_COL_MAP[key]]=new_list
            else:
#                print key
                data_dict_fin[TABLE_COL_MAP[key]]=value
        else:
            if type(value).__name__=='dict':
                data_dict_fin[key]=cross_key_name(value)
            else:
                data_dict_fin[key]=value
#    print data_dict_fin
    return data_dict_fin


    
def data_fusion_kernel(bill_log_cache,craw_data,complete_list,miss_list):
    new_miss_list=[]
    cache_hit_month=[]
#    print complete_list,miss_list

    for i,miss_index in enumerate(miss_list):
        #缓存没有，爬虫没有
#        print bill_log_cache.has_key(miss_index)
#        print craw_data.has_key(miss_index)
        cache_data_month={}
        if not bill_log_cache.has_key(miss_index) and \
            not craw_data.has_key(miss_index):
#            cache_data_month={}
#            bill_log_cache[miss_index]={}
            new_miss_list.append(miss_index)
        #缓存有，爬虫没有
        elif bill_log_cache.has_key(miss_index) and \
            not craw_data.has_key(miss_index):
            cache_data_month=bill_log_cache[miss_index]
            craw_data[miss_index]=cache_data_month
            cache_hit_month.append(miss_index)
    for i,full_mon in enumerate(complete_list):
        if not bill_log_cache.has_key(full_mon) and \
            craw_data.has_key(full_mon):
            bill_log_cache[full_mon]=craw_data[full_mon]
        #缓存有，爬虫有
        elif bill_log_cache.has_key(full_mon) and \
            craw_data.has_key(full_mon):
            bill_log_cache[full_mon]=craw_data[full_mon]
    return craw_data,bill_log_cache,new_miss_list,cache_hit_month

def data_cut(data,all_month):
    cache_month=[key for key in data.keys() if len(key)==6]
    if (len(all_month)>4 and len(cache_month)>6 ):
        diff_mouth=list(set(cache_month)-set(all_month))
        for mouth in diff_mouth:
            data.pop(mouth)
    return data

def clean_month_list(craw_month_list,missing_list):
    if (len(missing_list)>0):
        for month in missing_list:
            if month in craw_month_list:
                craw_month_list.remove(month)
    return craw_month_list

def data_fusion(**kwargs):
    #pub_param,final_bill_logs, missing_month_list
    
    fusion_start_time=time.time()
    final_bill_logs=kwargs['final_bill_logs']
    missing_month_list=kwargs['missing_month_list']
    tel=kwargs['tel']
    sid=kwargs['sid']
    pad_code=kwargs['pad_code']
    bill_log_cache=get_tel_data(tel)
    cache_hit_month=[]
    craw_data=None
    all_miss_list=list(set(missing_month_list))
    
    if bill_log_cache==None:
        bill_log_cache={'tel':tel}
        bill_log_cache['uti']=str(int(time.time()))
        
    try:
        from datetime import datetime
        ori_dict={'sid':sid,'tel':tel,'pad_code':pad_code,'final_bill_logs':final_bill_logs,
           'missing_month_list':missing_month_list,'bill_log_cache':bill_log_cache,'expiretime':datetime.utcnow()}
        register_other_bill_log(ori_dict)
    except:
        error_msg = traceback.format_exc()
        print error_msg
        pass
    
    try:
        #爬虫数据标准化
#        print final_bill_logs
        craw_data,craw_month_list=craw_data_std(tel,final_bill_logs,missing_month_list)
#        print craw_month_list,'169'
        craw_month_list=clean_month_list(craw_month_list,all_miss_list)
        all_month=list(set(craw_month_list+all_miss_list))
        if len(craw_month_list)>0 or len(all_miss_list)>0:
            craw_data,bill_log_cache,missing_month_list,cache_hit_month=data_fusion_kernel(bill_log_cache,craw_data,craw_month_list,all_miss_list)
#        print bill_log_cache
        #    print craw_data
        craw_data=cross_key_name(craw_data)
    #    print craw_data
        #数据剪枝
        bill_log_cache=data_cut(bill_log_cache,all_month)
        craw_data=data_cut(craw_data,all_month)
    except:
        error_msg = traceback.format_exc()
        print error_msg
        return final_bill_logs,missing_month_list,[],0.00
    
    try:
#        print bill_log_cache
        ret=insert_data(bill_log_cache)
        pass
    except:
        message = traceback.format_exc()
        print message
        return final_bill_logs,missing_month_list,[],0.00
    call_log_list=[]
    for key,value in craw_data.items():
        if len(key)==6:
            call_log_list.append(value)
    cache_hit_month=list(set(cache_hit_month))
    missing_month_list=list(set(missing_month_list))
    fusion_end_time=time.time()
    fusion_cost_time=fusion_end_time-fusion_start_time
    
    log_data = {
        'tel':tel,
        'bill_cache_hit_month':cache_hit_month,
        'bill_missing_month_list':missing_month_list,
        'bill_fusion_cost_time':fusion_cost_time,
        'bill_fusion_end_time':fusion_end_time,
    }
    logger('bill_data_fusion', 'INFO','', **log_data)
    return call_log_list,missing_month_list,cache_hit_month,fusion_cost_time


def register_other_bill_log(call_log):
    ret = insert_db_data('other_phone_bill', call_log)
    return ret
