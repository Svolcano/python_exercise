# coding: utf-8

"""
Created on Fri Apr 20 16:56:51 2018

@author: huang
"""

import pymongo
import time
import datetime
import json
import sys
import getopt
import pandas as pd
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
sys.path.append('../')
stdout = sys.stdout
reload(sys)
sys.stdout = stdout
sys.setdefaultencoding("utf8")

all_cols=[u'_id', u'bill_cache_hit_month_list', u'bill_fusion_cost_time', u'cache_time', 
          u'call_log_cache_hit_month_list', u'call_log_fusion_cost_time',
          u'call_log_missing_month_list', u'call_log_part_missing_month_list', 
          u'call_log_possibly_missing_month_list', u'cid', u'crawl_status',
          u'crawler_channel', u'cuishou_error_msg', u'cuishou_request_status', 
          u'cuishou_request_time', u'cuishou_sid', u'emergency_contact', u'end_time',
          u'expire_time', u'hasAlerted', u'job_id', u'login_status', u'login_time',
          u'message', u'original_channel', u'phone_bill_missing_month_list',
          u'report_create_time', u'report_message', u'report_used', u'sid',
          u'start_time', u'status', u'status_report', u'tel', u'tel_info',
          u'third_party_error_msg', u'third_party_status', u'third_party_token', 
          u'uid', u'user_info']

record_col=['cid','crawler_channel','province','telecom']

MONGO_CONFIG = {
#    'host': '127.0.0.1',
    'host': '172.18.21.117',
    'port': 27017,
    'db': 'crs'
}
BEGIN_DATE='20180522'
END_DATE='20180523'

if __name__=='__main__':
    opts, args = getopt.getopt(sys.argv[1:], "b:e:")
    for op, value in opts:
        if op == "-b":
            BEGIN_DATE = value
        elif op == "-e":
            END_DATE = value

class Pro_MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_pro_db_conn()

    def set_pro_db_conn(self):
        self.client = pymongo.MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[MONGO_CONFIG['db']]

    def export_data(self,begindate=BEGIN_DATE,enddate=END_DATE):
        timeArray = time.strptime(begindate, "%Y%m%d")
        self.begindate = time.mktime(timeArray)
        timeArray = time.strptime(enddate, "%Y%m%d")
        self.enddate = time.mktime(timeArray)
        data = self.conn['sid_info'].find({"end_time":{'$gte':self.begindate,'$lte':self.enddate}})
        
        self.data=pd.DataFrame(line for line in data)
        self.data=self.data.convert_objects(convert_numeric=True)
        return self.data
    
    def df_data_std(self):
        for col in all_cols:
            if col not in self.data.columns:
                self.data[col]=np.nan
    
    def fill_na(self):
        ts='[]'
        self.data['crawler_channel']=self.data['crawler_channel'].fillna('yulore')
        self.data['call_log_possibly_missing_month_list']=self.data['call_log_possibly_missing_month_list'].fillna(ts)
        self.data['call_log_missing_month_list']=self.data['call_log_missing_month_list'].fillna(ts)
        self.data['call_log_part_missing_month_list']=self.data['call_log_part_missing_month_list'].fillna(ts)
        self.data['phone_bill_missing_month_list']=self.data['phone_bill_missing_month_list'].fillna(ts)
        self.data['cid']=self.data['cid'].fillna('-1')
        self.data=self.data.fillna('miss')
    
    def modify_data(self):
#        print self.data['status']
        for x in self.data['tel_info']:
            if x=='miss':
                pass
            elif not x['province']:
                x['province']='miss'
#                print x
        self.data['province']=[x if x=='miss' else x['province'] for x in self.data['tel_info'] ]
        self.data['city']=[x if x=='miss' else x['city'] for x in self.data['tel_info'] ]
        self.data['telecom']=[x if x=='miss' else x['telecom'].replace('中国电信','电信').replace('中国联通','联通').replace('中国移动','移动')\
                  for x in self.data['tel_info'] ]
        self.data['flow_type']=[x if x=='miss' else x['flow_type'] for x in self.data['tel_info'] ]

    def group_by_cid_channel_prov_telecom(self,df):
        return df.groupby(['cid','crawler_channel','province','telecom'])
    
#    def all_data(self):
#        col=['cid','crawler_channel','province','telecom','sid','login_status','crawl_status','status','status_report','tel',
#            'call_log_possibly_missing_month_list','call_log_missing_month_list','call_log_part_missing_month_list','phone_bill_missing_month_list']
#        self.all_data= self.data[col]
#        return self.group_by_cid_channel_prov_telecom(self.all_data)    
    def total_nums(self):
        col=['cid','crawler_channel','province','telecom','sid','login_status','crawl_status','status','status_report','tel',
            'call_log_possibly_missing_month_list','call_log_missing_month_list','call_log_part_missing_month_list','phone_bill_missing_month_list']
        self.total_data= self.data[col]
        return self.group_by_cid_channel_prov_telecom(self.total_data)['sid']
    def authen_nums(self):
        self.auth_data=self.total_data.loc[self.total_data['login_status']==0]
        return self.group_by_cid_channel_prov_telecom(self.auth_data)['sid']
    def crawl_nums(self):
        self.crawl_data=self.auth_data[self.auth_data['status']==0 ]
        return self.group_by_cid_channel_prov_telecom(self.crawl_data)['sid']
    def final_nums(self):
        self.final_data=self.crawl_data[self.crawl_data['status']==0 ]
        return self.group_by_cid_channel_prov_telecom(self.final_data)['sid']
    def report_nums(self):
        self.report_data=self.final_data[self.final_data['status_report']==0 ]
        return self.group_by_cid_channel_prov_telecom(self.report_data)['sid']
    def call_log_intact_nums(self):
        self.call_log_intact_nums_data=self.crawl_data[self.crawl_data['call_log_possibly_missing_month_list'].map(len) <=2]
        self.call_log_intact_nums_data=self.call_log_intact_nums_data[self.call_log_intact_nums_data['call_log_missing_month_list'].map(len) <=2]
        #print self.call_log_intact_nums_data['call_log_part_missing_month_list'].map(len)
        self.call_log_intact_nums_data=self.call_log_intact_nums_data[self.call_log_intact_nums_data['call_log_part_missing_month_list'].map(len) <=2]
        return self.group_by_cid_channel_prov_telecom(self.call_log_intact_nums_data)['sid']
    def bill_intact_nums(self):
        self.bill_intact_nums_data=self.crawl_data[self.crawl_data['phone_bill_missing_month_list'].map(len) ==0]
        return self.group_by_cid_channel_prov_telecom(self.bill_intact_nums_data)['sid']
    def tel_nums(self):
        self.tel_data=self.crawl_data
        return self.group_by_cid_channel_prov_telecom(self.tel_data)
    def data_time(self):
        col=['cid','crawler_channel','province','telecom']
        report_data=self.data[self.data['status_report']==0 ]
        #print report_data['end_time']
        report_data=report_data[report_data['login_time'].map(str)<>'miss']
        report_data=report_data[report_data['start_time'].map(str)<>'miss']
        report_data=report_data[report_data['end_time'].map(str)<>'miss']
        report_data=report_data[report_data['report_used'].map(str)<>'miss']
        self.all_data_time= report_data[col]
        report_data=report_data.convert_objects(convert_numeric=True)
        self.all_data_time['authen_cost']=(report_data['login_time'].map(float)-report_data['start_time'].map(float)).map(abs)
        self.all_data_time['crawl_cost']=(report_data['end_time'].map(float)-report_data['login_time'].map(float)).map(abs)
        self.all_data_time['report_used']=(report_data['report_used'].map(float)).map(abs)
        return self.group_by_cid_channel_prov_telecom(self.all_data_time)
    
    def err_data(self):
        col=['cid','crawler_channel','province','telecom','status']
        self.err_datas= self.data[col]
        self.err_datas= self.err_datas[self.err_datas['status']<>0]
        return self.group_by_cid_channel_prov_telecom(self.err_datas)
    
    def dubious_tel_data(self):
        col=['sid','tel','status']
        self.dubious_tel_data_datas= self.data[col]
        record_list=[]
        data_tel=self.dubious_tel_data_datas.groupby('tel')
        for (tel),group in data_tel:
            line=[tel]
            record_list.append(line)
        record_list=np.array(record_list)
	if len(record_list)<1:
	    new_col=['tel','try_times']
            return pd.DataFrame(columns=new_col)
        record_df=pd.DataFrame(record_list,columns=['tel'],)
        record_df['try_times']=data_tel['sid'].count().values.reshape(-1,1)
        new_record_df=record_df[record_df['try_times']>3]
        return new_record_df
    
    def insert_data(self,data):
        ret = self.conn['sid_info_data_rpt'].insert_one(data)
        return ret
    def count_call_log_cache(self):
        ret = self.conn['call_log_details'].find({}).count()
        return ret



# In[52]:


def one_nums_2_pd(totals,total_name):
    record_list=[]
    for (cid,channel,prov,telecom),group in totals:
        line=[cid,channel,prov,telecom]
        record_list.append(line)
    record_list=np.array(record_list)
    new_list=record_col+total_name.split(',')
    if len(record_list)<1:
        record_df = pd.DataFrame(columns=new_list)
        return record_df
    record_df=pd.DataFrame(record_list,columns=record_col,)
    record_df[total_name]=totals.count().values.reshape(-1,1)
    return record_df


# In[53]:


def tel_nums_2_pd(totals,total_name):
    record_list=[]
    for (cid,channel,prov,telecom),group in totals:
        line=[cid,channel,prov,telecom]
        record_list.append(line)
    record_list=np.array(record_list)
    if len(record_list)<1:
        return pd.DataFrame(columns=record_col+[total_name])
    record_df=pd.DataFrame(record_list,columns=record_col,)
    record_df[total_name]=totals.tel.nunique().values.reshape(-1,1)
    return record_df


# In[54]:


pro_conn = Pro_MongodbConnection()
data=pro_conn.export_data(BEGIN_DATE,END_DATE)
pro_conn.df_data_std()
pro_conn.fill_na()
pro_conn.modify_data()
total_nums=pro_conn.total_nums()
total_nums_df=one_nums_2_pd(total_nums,'total_nums')


# In[55]:


authen_nums=pro_conn.authen_nums()
authen_nums_df=one_nums_2_pd(authen_nums,'authen_nums')
authen_nums_df=pd.merge(total_nums_df,authen_nums_df,how='outer',on=['cid','crawler_channel','province','telecom'],suffixes=('_x','_y'))


# In[56]:


crawl_nums=pro_conn.crawl_nums()
crawl_nums_df=one_nums_2_pd(crawl_nums,'crawl_nums')
print authen_nums_df.shape
print crawl_nums_df.shape
crawl_nums_df=pd.merge(authen_nums_df,crawl_nums_df,how='outer',on=['cid','crawler_channel','province','telecom'],suffixes=('_x','_y'))


# In[57]:


print crawl_nums_df.shape


# In[58]:


final_nums=pro_conn.final_nums()
final_nums_df=one_nums_2_pd(final_nums,'final_nums')
final_nums_df=pd.merge(crawl_nums_df,final_nums_df,how='outer',on=['cid','crawler_channel','province','telecom'],suffixes=('_x','_y'))


# In[59]:


print final_nums_df.shape


# In[60]:


report_nums=pro_conn.report_nums()
report_nums_df=one_nums_2_pd(report_nums,'report_nums')
report_nums_df=pd.merge(final_nums_df,report_nums_df,how='outer',on=['cid','crawler_channel','province','telecom'],suffixes=('_x','_y'))


# In[61]:


print report_nums_df.shape


# In[62]:


call_log_intact_nums=pro_conn.call_log_intact_nums()
call_log_intact_nums_df=one_nums_2_pd(call_log_intact_nums,'call_log_intact_nums')
call_log_intact_nums_df=pd.merge(report_nums_df,call_log_intact_nums_df,how='outer',on=['cid','crawler_channel','province','telecom'],suffixes=('_x','_y'))


# In[63]:


print call_log_intact_nums_df.shape


# In[64]:


bill_intact_nums=pro_conn.bill_intact_nums()
bill_intact_nums_df=one_nums_2_pd(bill_intact_nums,'bill_intact_nums')
bill_intact_nums_df=pd.merge(call_log_intact_nums_df,bill_intact_nums_df,how='outer',on=['cid','crawler_channel','province','telecom'],suffixes=('_x','_y'))


# In[65]:


print bill_intact_nums_df.shape


# In[66]:


tel_nums=pro_conn.tel_nums()
tel_nums_df=tel_nums_2_pd(tel_nums,'tel_nums')
tel_nums_df=pd.merge(bill_intact_nums_df,tel_nums_df,how='outer',on=['cid','crawler_channel','province','telecom'],suffixes=('_x','_y'))
tel_nums_df=tel_nums_df.fillna(0)

tel_nums_df['authen_pct']=tel_nums_df['authen_nums'].map(float)/tel_nums_df['total_nums'].replace(0.0,1).map(float)
tel_nums_df['crawl_pct']=tel_nums_df['crawl_nums'].map(float)/tel_nums_df['authen_nums'].replace(0.0,1).map(float)
tel_nums_df['final_pct']=tel_nums_df['final_nums'].map(float)/tel_nums_df['crawl_nums'].replace(0.0,1).map(float)
tel_nums_df['report_pct']=tel_nums_df['report_nums'].map(float)/tel_nums_df['final_nums'].replace(0.0,1).map(float)
tel_nums_df['log_loss_pct']=(tel_nums_df['final_nums'].map(float)-tel_nums_df['call_log_intact_nums'].map(float))/tel_nums_df['final_nums'].replace(0.0,1).map(float)
tel_nums_df['bill_loss_pct']=(tel_nums_df['final_nums'].map(float)-tel_nums_df['bill_intact_nums'].map(float))/tel_nums_df['final_nums'].replace(0.0,1).map(float)
tel_nums_df['tel_repeat_pct']=(tel_nums_df['final_nums'].map(float)-tel_nums_df['tel_nums'].map(float))/tel_nums_df['final_nums'].replace(0.0,1).map(float)
tel_nums_df=tel_nums_df.fillna(0)


# In[67]:


print tel_nums_df.shape


# In[68]:


data_time=pro_conn.data_time()


# In[69]:


def data_time_2_pd(data_time,data_name):
    record_list=[]
    for (cid,channel,prov,telecom),group in data_time:
        line=[cid,channel,prov,telecom]
        record_list.append(line)
    record_list=np.array(record_list)
    if len(record_list)<1:
        new_col=record_col+[data_name+'_min',data_name+'_max',data_name+'_75',data_name+'_99',data_name+'_mean']
        return pd.DataFrame(columns=new_col)
    record_df=pd.DataFrame(record_list,columns=record_col,)
    record_df[data_name+'_min']=data_time.min().values.reshape(-1,1)
    record_df[data_name+'_max']=data_time.max().values.reshape(-1,1)
    record_df[data_name+'_75']=data_time.quantile(0.75).values.reshape(-1,1)
    record_df[data_name+'_99']=data_time.quantile(0.99).values.reshape(-1,1)
    record_df[data_name+'_mean']=data_time.mean().values.reshape(-1,1)
    return record_df


# In[70]:


authen_cost=data_time_2_pd(data_time['authen_cost'],'authen_cost')
crawl_cost=data_time_2_pd(data_time['crawl_cost'],'crawl_cost')
report_used=data_time_2_pd(data_time['report_used'],'report_used')


# In[71]:


authen_cost=pd.merge(authen_cost,crawl_cost,how='outer',on=['cid','crawler_channel','province','telecom'])
report_used=pd.merge(authen_cost,report_used,how='outer',on=['cid','crawler_channel','province','telecom'])


# In[72]:


print report_used.shape


# In[73]:


def err_data_topn(err_data,n):
    err_data=err_data.set_index(["status", "cid"]).count(level="status")
    err_data=err_data['telecom'].sort_values(ascending=False)
    ret={}
    for i,(x,y) in enumerate(zip(err_data.index,err_data)):
        if i >=n:
            break
        ret[str(x)]=str(y)
    return ret


# In[74]:


def err_data_2_pd(err_data):
    record_list=[]
    _col=record_col
    err_code_top10=[]
    for (cid,channel,prov,telecom),group in err_data:
        line=[cid,channel,prov,telecom]
        err_topn_np=err_data_topn(group,10)
        err_code_top10.append(err_topn_np)
        record_list.append(line)
    record_list=np.array(record_list)
    if len(record_list)<1:
        new_col=record_col+['err_code_top10']
        return pd.DataFrame(columns=new_col)
    record_df=pd.DataFrame(record_list,columns=_col,)
    record_df['err_code_top10']=np.array(err_code_top10).reshape(-1,1)
    return record_df


# In[75]:


err_data=pro_conn.err_data()
err_data=err_data_2_pd(err_data)
err_data.shape


# In[76]:


all_retults=pd.merge(tel_nums_df,report_used,how='outer',on=['cid','crawler_channel','province','telecom'])
print all_retults.shape
all_retults=all_retults.fillna(0)
all_retults=pd.merge(all_retults,err_data,how='outer',on=['cid','crawler_channel','province','telecom'])
print all_retults.shape
all_retults
all_retults=all_retults.fillna('{}')

#print all_retults['cid']
all_retults['cid']=all_retults['cid'].map(float).map(int)
all_retults['total_nums']=all_retults['total_nums'].map(int)
all_retults['authen_nums']=all_retults['authen_nums'].map(int)
all_retults['crawl_nums']=all_retults['crawl_nums'].map(int)
all_retults['final_nums']=all_retults['final_nums'].map(int)
all_retults['report_nums']=all_retults['report_nums'].map(int)
all_retults['call_log_intact_nums']=all_retults['call_log_intact_nums'].map(int)
all_retults['bill_intact_nums']=all_retults['bill_intact_nums'].map(int)
all_retults['tel_nums']=all_retults['tel_nums'].map(int)


dubious_tel_data=pro_conn.dubious_tel_data()
dubious_tel_data=dubious_tel_data.reset_index(drop=True)
# In[81]:


all_retults_list=all_retults.to_dict(orient='records')
data_info={'rpt_date':BEGIN_DATE}
for line in all_retults_list:
    line.update(data_info)
    try:
        pro_conn.insert_data(line)
    except:
        pass

from lxml import etree
# lxml 库的 etree 解析字符串为 html 代码，并写入文件
root = "<title>sid_info日终批量汇总信息</title>"
cid_chanel_prov_tele_des = """<h1>"""+BEGIN_DATE+"""日客户+渠道+地区+运营商信息汇总</h1>"""+all_retults.to_html()
dubious_tel_des = """<h1>"""+BEGIN_DATE+"""日可疑客户手机号标记</h1>"""+dubious_tel_data.to_html()
root=root+cid_chanel_prov_tele_des+dubious_tel_des
html = etree.HTML(root)
tree = etree.ElementTree(html)
tree.write('sid_info_anly.html')


    
    
