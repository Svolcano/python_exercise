# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 10:57:38 2018

@author: huang
"""
import pymongo
import time
import redis
import hashlib 
import multiprocessing
import sys,getopt
import datetime
sys.path.append('../')
reload(sys)
sys.setdefaultencoding("utf8")


DEV_MONGO_CONFIG = {
#    'host': '127.0.0.1',
    'host': '172.18.21.117',
    'port': 27017,
    'db': 'crs'
}

PRO_MONGO_CONFIG = {
#    'host': '127.0.0.1',
    'host': '172.18.21.117',
    'port': 27017,
    'db': 'crs'
}



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
        'mtd':'mtd',
        'tel':'tel',
        'bat':'bat',
        'dsf':'dsf',
        'zzf':'zzf',
        'bed':'bed',
        'qta':'qta',
        'mon':'mon',
        'bpe':'bpe',
        'bec': 'bec',
        'uti':'uti'     
}  


process_size=1 
batch_size=1
checkpoint_sid=''

def USAG():
    print "-b   >>>>>>>   begin_date"
    print "-e   >>>>>>>   end_date"
    print "-t   >>>>>>>   test"
    print "-c   >>>>>>>   定时使用"
    print "-p   >>>>>>>   process total size"
    print "-h   >>>>>>>   help"
    print "-b   >>>>>>>   begin_date"
    

opts, args = getopt.getopt(sys.argv[1:], "p:hk:")
for op, value in opts:
    if op=="-p":
        process_size=int(value)
    elif op=='-k':
        checkpoint_sid=value
    elif op=='-h':
        USAG()
        exit()




class Read_MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_pro_db_conn()

    def set_pro_db_conn(self):
        self.client = pymongo.MongoClient(PRO_MONGO_CONFIG['host'], PRO_MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[PRO_MONGO_CONFIG['db']]

    def export_data(self,tel):
        data = self.conn['phone_bill'].find({'tel':tel},{'_id':0})
        return data
    def get_tel_set(self):
        begin_time=time.time()
        print begin_time
        data = self.conn['call_log_details'].find({},{'tel':1,'_id':0})
        tel_list=[]
        fp = open('bill_defusion_tel.pd','w+')
        for x in data:
            value=x['tel']
            print value
            fp.write(value+'\n')
            tel_list.append(value)
        fp.close()
        print '获取sid:'+str(len(tel_list))+'条花费:' + str(time.time()-begin_time)+'秒'
        return tel_list
    
    
class Write_MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_dev_db_conn()

    def set_dev_db_conn(self):
        self.client = pymongo.MongoClient(DEV_MONGO_CONFIG['host'], DEV_MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[DEV_MONGO_CONFIG['db']]

    def insert_data(self,data):
        ret = self.conn['phone_bill_cache'].insert_one(data)
        return ret
    
    def remove_data(self,data):
        ret = self.conn['phone_bill_cache'].remove(data)
        return ret
    
    def get_tel_data(self,tel):
        where_dict={'tel':tel}
        ret = self.conn['phone_bill_cache'].find_one(where_dict,{'_id':1})
        return ret
                                          

def cross_key_name(data):
    data_dict_fin={}
    for key,value in data.items():
        data_dict_fin[TABLE_COL_MAP[key]]=value
    return data_dict_fin

def call_log_std(data_dict):
    new_dict={}
#    print data_dict
    for key,value in  data_dict.items():
#        print key,value
        if value=='':
            value='0.00'
        new_dict[key]=value
#    data_dict['call_cost']= '%.2f'%(int(data_dict['call_cost'])*1.0/100)
    return new_dict
def sid_dual(tel_list):
    pro_conn = Read_MongodbConnection()
    dev_conn = Write_MongodbConnection()
    tel_len=len(tel_list)
    if tel_len<1:
        return 0
    for k,tel in enumerate(tel_list):
        begin_time=time.time()
        datas=pro_conn.export_data(tel)
        if datas.count()<1:
            continue
        data_dict={'tel':tel}
#        print tel
#        try:
#            ret=dev_conn.remove_data(data_dict)
#            if not ret['n']:
#                print ret
##            print ret
#        except:
#            pass
        for j,data in enumerate(datas):
            # 查询数据号内容是否存在

            for j,details in enumerate(data['phone_bill']):
                try:
                    details=call_log_std(details)
                except:
                    continue
                if details['bill_month']<'201711':
                    continue
                
                if  not data_dict.has_key(details['bill_month']):
                    details=cross_key_name(details)
                    data_dict[details['mon']]=details
                        
        if len(data_dict)>0:
            data_dict[TABLE_COL_MAP['uti']]=str(int(time.time()))
#            print data_dict
            dev_conn.insert_data(data_dict)
            
        end_time=time.time()
        print "("+ str(k)+"/"+ str(tel_len) +")"+tel + '有' + str(datas.count()) + '条记录需要处理!'
        print '当前进度:'+str(float(k)/tel_len) + ',共处理' + str(datas.count()) + '条记录花费:' + str(end_time-begin_time)+'秒'
        

    
   

if __name__ == '__main__':
#   sid_list_set
    start= time.time()
    if not checkpoint_sid:
        pro_conn = Read_MongodbConnection()
        sid_list_set=pro_conn.get_tel_set()
        del pro_conn 
    else:
        sid_list_set=[]
        flag=0
        file_p=open('bill_defusion_tel.pd','r')
        for one_line in file_p:
            value=one_line.replace('\n','').split(',')
#            print type(value)
            if value[0]==checkpoint_sid:
                flag=1
            if flag:
                sid_list_set.append(value)
            
    sid_dual(sid_list_set)

    print "The number of CPU is:" + str(multiprocessing.cpu_count()) 

    end = time.time()
    print '结束时间:'+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print '{} processes take {} seconds'.format(process_size, (end - start))   
        