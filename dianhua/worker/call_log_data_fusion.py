# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 10:57:38 2018

@author: huang
"""
import traceback
import sys
import time
import hashlib 
import copy
from com.logger import logger


from com.connection import db
sys.path.append('../')
from worker.communicate import insert_db_data



TABLE_COL_MAP={
        'call_method':'mtd',
        'tel':'tel',
        'call_from':'frm',
        'call_cost':'cot',
        'call_duration':'dur',
        'call_time':'tim',
        'call_tel':'cte',
        'month':'mon',
        'call_to':'cto',
        'call_type': 'tye',
        'status':'sts',
        'det':'det',
        'mtd':'call_method',
        'tel':'tel',
        'frm':'call_from',
        'cot':'call_cost',
        'dur':'call_duration',
        'tim':'call_time',
        'cte':'call_tel',
        'mon':'month',
        'cto':'call_to',
        'tye': 'call_type',
        'sts':'status', 
        'uti':'uti'     
}  


 

def insert_data(data):
    where_dict={'tel':data['tel']}
    ret = db['call_log_details'].update(where_dict,data,upsert=True)
    return ret

def get_tel_data(tel):
    where_dict={'tel':tel}
    ret = db['call_log_details'].find_one(where_dict,{'_id':0})
    return ret

def craw_data_std(tel,final_call_logs,all_miss_list):
    data_dict={}
    month_list=[]
    for i,x in enumerate(final_call_logs):
        # 过滤x
        new_x={'tel':tel}
        if not data_dict.has_key('tel') :
            data_dict={'tel':tel}
            data_dict['uti']=str(int(time.time()))
        for key,value in x.items():
            if  TABLE_COL_MAP.has_key(key):
                new_x[TABLE_COL_MAP[key]]=value
        if  not data_dict.has_key(new_x['mon']):
            month_list.append(new_x['mon'])
            if new_x['mon'] in all_miss_list:
                flag=3
            else:
                flag=1
            data_dict[new_x['mon']]={'sts':flag,'det':[]}
        if (len(new_x['mon'])>0):
            data_dict[new_x['mon']]['det'].append(new_x)
            
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

def md5sum(data_dict):
    mac_buff=[]
    mac_buff.append(data_dict['tel'])
#    mac_buff.append(data_dict['cot'])
    mac_buff.append(data_dict['dur'])
    mac_buff.append(data_dict['tim'])
    mac_buff.append(data_dict['cte'])
    my_md5 = hashlib.md5() #获取一个MD5的加密算法对象 
    my_md5.update(' '.join(mac_buff)) #得到MD5消息摘要  
    fmd5 = my_md5.hexdigest() #以16进制返回消息摘要，32位
    return fmd5  

def del_dict_list(src_list):
    new={}
    new_list=[]
    for i,sin_list in enumerate(src_list):
        md5=md5sum(sin_list)
        if not new.has_key(md5):
            new[md5]=i
    for value in new.values():
        new_list.append(src_list[value])
    return new_list

def fusion_status(cache_status,craw_status):
    if cache_status==1:
        return cache_status
    else:
        if craw_status==0:
            return cache_status
        else:
            return craw_status
            
    
def data_fusion_kernel(call_log_cache,craw_data,miss_list,miss_type):
    new_miss_list=[]
    cache_hit_month=[]
    move_miss={}
    if call_log_cache!=None:
        for i,miss_index in enumerate(miss_list):
            
            if not call_log_cache.has_key(miss_index):
                cache_data_month=[]
                call_log_cache[miss_index]={'sts':3,'det':[]}
            else:
                cache_data_month=call_log_cache[miss_index]['det']
            if not craw_data.has_key(miss_index):
                craw_data_month=[]
                craw_data[miss_index]={'sts':3,'det':[]}
            else:
                craw_data_month=craw_data[miss_index]['det']
            if cache_data_month==[] and craw_data_month==[]:
                call_log_cache.pop(miss_index)
                craw_data.pop(miss_index)
                new_miss_list.append(miss_index)
                continue
            
            call_log_cache[miss_index]['sts']=fusion_status(call_log_cache[miss_index]['sts'],miss_type)
            
            craw_data[miss_index]['sts']=miss_type
            craw_data_month=del_dict_list(craw_data_month)
            cache_data_month=del_dict_list(cache_data_month)
            cache_data_month.extend(craw_data_month)
            fusion_data=del_dict_list(cache_data_month)
            
            call_log_cache[miss_index]['det']=fusion_data
            craw_data[miss_index]['det']=fusion_data
            
            if call_log_cache[miss_index]['sts']==1:
                pass
            elif call_log_cache[miss_index]['sts']==miss_type:
                new_miss_list.append(miss_index)
            else:
                move_miss[miss_index]=call_log_cache[miss_index]['sts']
            if len(fusion_data)>len(craw_data_month):
                cache_hit_month.append(miss_index)

            call_log_cache[miss_index]['det']=fusion_data
            craw_data[miss_index]['det']=fusion_data
            
    else:
        call_log_cache=copy.deepcopy(craw_data)
        new_miss_list=copy.deepcopy(miss_list)
    cache_hit_month=list(set(cache_hit_month))
    return craw_data,call_log_cache,new_miss_list,cache_hit_month,move_miss

def data_cut(data,all_month):
    cache_month=[key for key in data.keys() if len(key)==6]
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
    #pub_param,final_call_logs, missing_month_list, possibly_missing_list, part_missing_list
    
    fusion_start_time=time.time()
    final_call_logs=kwargs['final_call_logs']
    missing_month_list=kwargs['missing_month_list']
    possibly_missing_list=kwargs['possibly_missing_list']
    part_missing_list=kwargs['part_missing_list']
    tel=kwargs['tel']
    call_log_cache=get_tel_data(tel)
    cache_hit_month=[]
    all_move_miss=[]
    all_miss_list=list(set(missing_month_list+possibly_missing_list+part_missing_list))
    if call_log_cache==None and len(final_call_logs)<1:
        return final_call_logs,missing_month_list,possibly_missing_list,part_missing_list,[],0
    try:
        #爬虫数据标准化
        craw_data,craw_month_list=craw_data_std(tel,final_call_logs,all_miss_list)

        all_miss_list=list(set(missing_month_list+possibly_missing_list+part_missing_list))
        craw_month_list=clean_month_list(craw_month_list,all_miss_list)
        all_month=list(set(craw_month_list+all_miss_list))
        if len(craw_month_list)>0 :
            craw_data,call_log_cache,craw_month_list,cache_hit_list,move_miss=data_fusion_kernel(call_log_cache,craw_data,craw_month_list,1)
            cache_hit_month.extend(cache_hit_list)
            all_move_miss.append(move_miss)
        if len(missing_month_list)>0 :
            craw_data,call_log_cache,missing_month_list,cache_hit_list,move_miss=data_fusion_kernel(call_log_cache,craw_data,missing_month_list,0)
            cache_hit_month.extend(cache_hit_list)
            all_move_miss.append(move_miss)
        if len(possibly_missing_list)>0 :
            craw_data,call_log_cache,possibly_missing_list,cache_hit_list,move_miss=data_fusion_kernel(call_log_cache,craw_data,possibly_missing_list,3)
            cache_hit_month.extend(cache_hit_list)
            all_move_miss.append(move_miss)
        if len(part_missing_list)>0 :
            craw_data,call_log_cache,part_missing_list,cache_hit_list,move_miss=data_fusion_kernel(call_log_cache,craw_data,part_missing_list,2)
            cache_hit_month.extend(cache_hit_list)
            all_move_miss.append(move_miss)

#        print all_move_miss
        for move_ in all_move_miss:
            for key,value in move_.items():
                if value==0:
                    missing_month_list.append(key)
                elif value==2:
                    part_missing_list.append(key)
                elif value==3:
                    possibly_missing_list.append(key)
        #    print craw_data
        craw_data=cross_key_name(craw_data)
    #    print craw_data
        #数据剪枝
        call_log_cache=data_cut(call_log_cache,all_month)
        craw_data=data_cut(craw_data,all_month)
    except:
        error_msg = traceback.format_exc()
        print error_msg
        return final_call_logs,missing_month_list,possibly_missing_list,part_missing_list,[],0
    
    try:
#        print call_log_cache
        ret=insert_data(call_log_cache)
        pass
    except:
        message = traceback.format_exc()
        print message
        return final_call_logs,missing_month_list,possibly_missing_list,part_missing_list,[],0
    call_log_list=[]
    for key,value in craw_data.items():
        if type(value).__name__=='dict':
            if value.has_key('status'):
                for x in value['det']:
                    x['month']=key
                    call_log_list.append(x)
    cache_hit_month=list(set(cache_hit_month))
    possibly_missing_list=list(set(possibly_missing_list))
    part_missing_list=list(set(part_missing_list))
    missing_month_list=list(set(missing_month_list))
    fusion_end_time=time.time()
    fusion_cost_time=fusion_end_time-fusion_start_time
    
    log_data = {
        'tel':tel,
        'cache_hit_month':cache_hit_month,
        'possibly_missing_list':possibly_missing_list,
        'part_missing_list': part_missing_list,
        'missing_month_list':missing_month_list,
        'fusion_cost_time':fusion_cost_time,
        'fusion_end_time':fusion_end_time,
        'all_move_miss':all_move_miss
    }
    logger('data_fusion', 'INFO','', **log_data)
    return call_log_list,missing_month_list,possibly_missing_list,part_missing_list,cache_hit_month,fusion_cost_time


def register_other_call_log(call_log):
    ret = insert_db_data('other_call_log', call_log)
    return ret
