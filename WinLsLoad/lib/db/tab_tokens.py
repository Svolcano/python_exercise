import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_tokens():
    '''
    Manage tab_tickets table
    '''
    def __init__(self, host, user, passwd, db):
        '''
        init class.
        Args:
            host:mysql server host.
            user:mysql user
            passwd:mysql password
            db:database which is used.
        Return:
        Raise:
        '''
        self.db = database(host, user, passwd, db)

    def get_token_id_about_zone(self,chain_id,type,param_1,param_2):
        '''
        tokens who  match condition
        type:1 import ;2 export
        '''
        sql = ''
        if 11 == type :
            sql = "select token_id,priority,is_default from tab_tokens where chain_id=%d and type=%d and param_1='%d' and param_2='%d' and user_id is NULL and enable=1 \
                   order by priority asc" %(chain_id,type,param_1,param_2)
        elif 1 == type :
            sql = "select token_id,priority,is_default from tab_tokens where chain_id=%d and type=%d and param_2='%d' and user_id is NULL and enable=1 order by priority asc" \
                  %(chain_id,type,param_2)
        elif 2 == type :
            sql = "select token_id,priority,is_default from tab_tokens where chain_id=%d and type=%d and param_1='%d' and user_id is NULL and enable=1 order by priority asc" \
                  %(chain_id,type,param_1)
        else :
            logger.info("type is error")
            return (False,[])
            
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)
        return (err, tab_token_list)

    def get_token_id_about_user(self,chain_id,user_id,type,param_1,param_2):
        '''
        tokens who  match condition
        type:1 import ;2 export
        '''
        sql = ''
        if 11 == type :
            sql = "select token_id,priority,is_default from tab_tokens where chain_id=%d and user_id=%d and type=%d and param_1='%d' and param_2='%d' and enable=1 \
                  order by priority asc" %(chain_id,user_id,type,param_1,param_2)
        elif 1 == type :
            sql = "select token_id,priority,is_default from tab_tokens where chain_id=%d and user_id=%d and type=%d and param_2='%d' and enable=1 order by priority asc " \
                  %(chain_id,user_id,type,param_2)
        elif 2 == type :
            sql = "select token_id,priority,is_default from tab_tokens where chain_id=%d and user_id=%d and type=%d and param_1='%d' and enable=1 order by priority asc " \
                  %(chain_id,user_id,type,param_1)
        else :
            logger.info("type is error")
            return (False,[])

        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)
        return (err, tab_token_list)

    def get_name(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select name from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_policy(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select policy from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_param3(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select param_3 from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_param4(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select param_4 from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_param5(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select param_5 from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_param6(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select param_6 from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)   

    def get_status_1(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select status_1 from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_status_2(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select status_2 from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_priority(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select priority from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_is_default(self,token_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select id_default from tab_tokens where token_id=%d " %token_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def update_status_1(self, id, status_1):
        '''
        update ticket state from id.
        Args:
            id:ticket_id
            state:state
        Return:
            True/False
        Raise:
        '''

        sql = "update tab_tokens set status_1=%d where token_id=%s" % (status_1, id)
        return self.db.execute(sql) 

    def update_status_2(self, id, status_2):
        '''
        update ticket state from id.
        Args:
            id:ticket_id
            state:state
        Return:
            True/False
        Raise:
        '''
    
        sql = "update tab_tokens set status_2=%d where token_id=%s" % (status_2, id)
        return self.db.execute(sql)

    def get_default_token_id(self,chain_id):
        '''
        type: 1,import;2,export
        '''
        sql = "select token_id from tab_tokens where is_default=1 and chain_id=%d " %chain_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

if __name__ == '__main__':
    db = tab_tokens('192.168.1.139','sboxweb','Sbox123456xZ','sbox_db') 
    print '-------get_token_id_about_zone--------'
    print db.get_token_id_about_zone(1,'',11)
    print db.get_token_id_about_zone(2,11,'')
    print db.get_token_id_about_zone(11,11,12)
    print '-------get_token_id_about_user--------'
    print db.get_token_id_about_user(112,1,'',11)
    print db.get_token_id_about_user(112,2,11,'')
    print db.get_token_id_about_user(112,11,11,12)
    
