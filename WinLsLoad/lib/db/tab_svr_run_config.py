import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_svr_run_config():
    '''
    Manage tab_global_config database
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

    def get_value(self, name):
        '''
        get value of name
        Args:
            name:the item name
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        sql = "select value from tab_svr_run_config where name='%s'" % name

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        value = ()

        for row in result:
            for r in row:
                value = r

        return (err,value)
    
    def get_names(self):
        '''
        get condig names
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        sql = "select name from tab_svr_run_config"

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        names = []

        for row in result:
            for r in row:
                names.append(r)

        return (err,names)
    
    def update_value(self, name, value):
        '''
        '''

        sql = "update tab_svr_run_config set value = '%s' where name='%s'" %(value, name)

        return self.db.execute(sql)

    def insert_value(self, name, value):
        '''
        '''

        sql = "insert into tab_svr_run_config(name, value ) values('%s', '%s')" %(name, value)

        return self.db.execute(sql)



