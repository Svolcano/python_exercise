#!/usr/bin/env python2.6
# _*_ coding:utf-8 _*_

import logging
from datetime import datetime
from mysql_basic_c import mysql_basic_c as database


logger = logging.getLogger(__name__)

class tab_load_info():
    '''
    save load info to database:tab_load_info tables
    '''
    def __init__(self,host,user,passwd,db):
        '''
        init class.
        Args:
            host :mysql server host.
            user :mysql user name .
            passwd:mysql password.
            db:database which is used.
        Return:
        Raise:
        '''
        logger.info("tab_load_info init....")
        self.db = database(host,user,passwd,db)
        
    def get_current_datetime(self):
        ''' return current datatime string '''
        dt = datetime.now()
        strdt = dt.strftime("%Y-%m-%d %H:%M:%S")
        return strdt
    
    def save_load_result_to_db(self,result_list):
        '''
        save load_info to database
        return value:
            true: execute success
            false: failed to exectue
        '''
        if not result_list:
            return True
        strdt = self.get_current_datetime()
        for l in result_list:
            l.append(strdt)
        sql = (' insert into tab_load_info(server_ip,cpu_number,cpu_frequency,load_average,login_users,query_time) '
                  ' values(%s,%s,%s,%s,%s,%s) ')
        return  self.db.executemany(sql,result_list)
    
    def normal_query(self):
        '''' return nomarl query's result  '''
        last_time = self.last_time_query()
        d1 = self.most_cpu_cycle_query(last_time)
        d2 = self.least_user_query(last_time)         
       
        sql = (" select server_ip,cpu_number,cpu_frequency,load_average,login_users from tab_load_info " 
                " where query_time = \'%s\' " 
                " order by query_time desc " 
                " limit 0,5 ; " % last_time )
        
        rtn,d3 =  self.db.query(sql)
        if rtn and d1 and d2 :
            return  [d1,d2,d3]          
        else:
            return False
        
    def history_query(self):
        ''' 
        return history query result 
        erver ip erver day 's max cpu load_averyage limit 30 days 
        '''
        sql = (' select server_ip,max(load_average) as max,date(query_time) as d  from tab_load_info'
                ' group by server_ip,d limit 30;')
        rtn,data =  self.db.query(sql)
        if rtn :
            return data
        else:
            return False
        
    def most_cpu_cycle_query(self,last_time):
        ''' return most cpu cycle 5 servers '''
        if not last_time:
            return False
        sql = ("select server_ip,(cpu_number-load_average)*cpu_frequency as cpu_available from tab_load_info " 
                " where query_time = \'%s\' " 
                " order by cpu_available desc " 
                " limit 5 ; " % last_time)
        rtn,data = self.db.query(sql)       
        if rtn :
            tmp = []
            for l in data:
                tmp.append(l[0])
            return tmp
        else:
            return False       
        
    def least_user_query(self,last_time):
        ''' return least login user 5 servers'''
        if not last_time:
            return False
        sql = ("select server_ip from tab_load_info " 
                " where query_time = \'%s\' " 
                " order by login_users desc " 
                "  limit 5 ; " % last_time)
        rtn,data = self.db.query(sql)
        if rtn :
            res = []
            for l in data:
                res.append(l[0])                
            return res
        else:
            return False
        
    def last_time_query(self):
        ''' return last query time '''
        sql = ("select query_time from tab_load_info " 
                " order by query_time desc " 
                " limit 1 ;")
        rtn,data = self.db.query(sql)        
        if rtn:
            return data[0][0]           
        else:
            return False        
    
        

            
        
    
     
