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
    'host': '127.0.0.1',
#    'host': '172.18.21.117',
    'port': 27017,
    'db': 'crs'
}

PRO_MONGO_CONFIG = {
    'host': '127.0.0.1',
#    'host': '172.18.21.117',
    'port': 27017,
    'db': 'crs'
}



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
        'mtd':'mtd',
        'tel':'tel',
        'frm':'frm',
        'cot':'cot',
        'dur':'dur',
        'tim':'tim',
        'cte':'cte',
        'mon':'mon',
        'cto':'cto',
        'tye': 'tye',
        'sts':'sts', 
        'uti':'uti'     
}  


BEGIN_DATE='2017-10-01'
END_DATE='2018-04-20'
#END_DATE='2017-10-02'
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
    

opts, args = getopt.getopt(sys.argv[1:], "tb:e:cp:hk:")
for op, value in opts:
    if op == "-b":
        BEGIN_DATE = value
    elif op == "-e":
        END_DATE = value
    elif op=="-t":
        BEGIN_DATE='2018-03-30'
        END_DATE='2018-03-31'
    elif op=="-p":
        process_size=int(value)
    elif op=="-c":
#        now_date =datetime.datetime.now().strftime("%Y-%m-%d")
#        print now_date
#        if CRONTAB_TASK.has_key(now_date):
#            BEGIN_DATE=CRONTAB_TASK[now_date][0]
#            END_DATE=CRONTAB_TASK[now_date][1]
        BEGIN_DATE='2017-10-01'
        END_DATE='2018-03-01'
    elif op=='-k':
        checkpoint_sid=value
    elif op=='-h':
        USAG()
        exit()

print 'BEGIN_DATE='+BEGIN_DATE
print 'END_DATE='+END_DATE



class Pro_MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_pro_db_conn()

    def set_pro_db_conn(self):
        self.client = pymongo.MongoClient(PRO_MONGO_CONFIG['host'], PRO_MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[PRO_MONGO_CONFIG['db']]

    def export_data(self,sid):
        data = self.conn['call_log'].find({'sid':sid},{'call_method':1,'tel':1,'call_from':1,'call_cost':1,
                        'call_duration':1,
                        'call_time':1,
                        'call_tel':1,
                        'month':1,
                        'call_to':1,
                        'call_type':1,'_id':0})
        return data
    def get_sid_set(self,begindate=BEGIN_DATE,enddate=END_DATE):
        print "开始获取[%s]--[%s]期间sid!"%(begindate,enddate)
        timeArray = time.strptime(begindate, "%Y-%m-%d")
        begindate = time.mktime(timeArray)
        timeArray = time.strptime(enddate, "%Y-%m-%d")
        enddate = time.mktime(timeArray)
        begin_time=time.time()
#        print begindate,enddate
        data = self.conn['sid_info'].find({"end_time":{'$gte':begindate,'$lte':enddate},'status':0,'crawler_channel':'xinde'},{'tel':1,'sid':1,'_id':0})
        sid_list=[]
#        print data.count()
        fp = open('xinde_sid_tel.pd','w+')
        for x in data:
            print x['sid'],x['tel']
            value=[x['sid'],x['tel']]
            fp.write(','.join(value)+'\n')
            sid_list.append(value)
#        sid_list=list(set(sid_list))
        fp.close()
        print '获取sid:'+str(len(sid_list))+'条花费:' + str(time.time()-begin_time)+'秒'
        return sid_list
    
    
class Dev_MongodbConnection(object):
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
        ret = self.conn['call_log_details'].insert_one(data)
        return ret
    
    def remove_data(self,data):
        ret = self.conn['call_log_details'].remove(data)
        return ret
    
    def get_tel_data(self,tel):
        where_dict={'tel':tel}
        ret = self.conn['call_log_details'].find_one(where_dict,{'_id':1})
        return ret
                                          

def cross_key_name(data):
    data_dict_fin={}
    for key,value in data.items():
        data_dict_fin[TABLE_COL_MAP[key]]=value
    return data_dict_fin

def call_log_std(data_dict):
    data_dict['call_cost']= '%.2f'%(int(data_dict['call_cost'])*1.0/100)
    return data_dict
def sid_dual(sid_list):
    pro_conn = Pro_MongodbConnection()
    dev_conn = Dev_MongodbConnection()
    sid_len=len(sid_list)
    if sid_len<1:
        return 0
    err_fp = open('xinde_sid_tel.err','w+')
    for k,t_list in enumerate(sid_list):
        sid=t_list[0]
        tel=t_list[1]
        begin_time=time.time()
        datas=pro_conn.export_data(sid)
        data_dict={'tel':tel}
        print tel
        try:
            ret=dev_conn.remove_data({'tel':tel})
            if not ret['n']:
                print ret
                print sid
                err_fp.write(str(sid)+'\n')
                
#                ret=dev_conn.get_tel_data(tel)
#                print ret
        except:
            pass
        for j,data in enumerate(datas):
            # 查询数据号内容是否存在
            try:
                data=call_log_std(data)
            except:
                continue
            if len(data)>0 and data.has_key('month'):
#                if (data['tel']) not in data_dict.values():
#                    data_dict[TABLE_COL_MAP['tel']]=data['tel']
                if  not data_dict.has_key(data['month']):
                    details=[]
                    data_dict[data['month']]={TABLE_COL_MAP['status']:3,'det':details}
                timeArray = time.strptime('2017-11-01', "%Y-%m-%d")
                enddate = time.mktime(timeArray)
                if data['call_time'] < enddate:
                    continue
                data=cross_key_name(data)
                data_dict[data[TABLE_COL_MAP['month']]]['det'].append(data)

            
        if len(data_dict)>0:
            data_dict[TABLE_COL_MAP['uti']]=str(int(time.time()))
            dev_conn.insert_data(data_dict)
        end_time=time.time()
        err_fp.close()
        print "("+ str(k)+"/"+ str(sid_len) +")"+tel + '有' + str(datas.count()) + '条记录需要处理!'
        print '当前进度:'+str(float(k)/sid_len) + ',共处理' + str(datas.count()) + '条记录花费:' + str(end_time-begin_time)+'秒'
        

def single_process_gevent(sid_list_set):  
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all()
    print len(sid_list_set)
    if len(sid_list_set) <batch_size:
        batch=1
        step=len(sid_list_set)
    else:
        batch=batch_size
        step=len(sid_list_set)/batch_size
    tasks =[]
    for i in range(batch):
        begin=step*i
        end=step*(i+1)
#        print begin,end
        sid_list=sid_list_set[begin:end]
        tasks.append(gevent.spawn(sid_dual,sid_list))
    gevent.joinall(tasks)
    return True
    
   

if __name__ == '__main__':
#   sid_list_set
    
    if not checkpoint_sid:
        pro_conn = Pro_MongodbConnection()
        sid_list_set=pro_conn.get_sid_set()
        del pro_conn 
    else:
        sid_list_set=[]
        flag=0
        file_p=open('xinde_sid_tel.pd','r')
        for one_line in file_p:
            value=one_line.split(',')
            print type(value)
            if value[0]==checkpoint_sid:
                flag=1
            if flag:
                sid_list_set.append(value)
            
    list_len=len(sid_list_set)+1
    step=list_len/process_size
    start = time.time()
    pool = multiprocessing.Pool(processes = process_size)
    for i in range(process_size):
        begin=step*i
        end=step*(i+1)
#        print begin,end
        sid_list=sid_list_set[begin:end]
        pool.apply_async(single_process_gevent, (sid_list, ))  

    pool.close()
    pool.join()
    print "The number of CPU is:" + str(multiprocessing.cpu_count()) 

    end = time.time()
    print '结束时间:'+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print '{} processes take {} seconds'.format(process_size, (end - start))   
        