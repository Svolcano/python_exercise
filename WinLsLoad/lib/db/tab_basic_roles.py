import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_basic_roles():
    '''
    Manage tab_basic_roles table
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

    def get_role_id(self, role_name):
        '''
        insert userid, roleid
        Args:
            user_id:user_id
            role_id:role_id
        Return:
            True/False:success/fail
        Raise:
        '''

        sql = "select role_id from tab_basic_roles where role_name='%s'" % role_name

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        role_id = ()

        for row in result:
            for r in row:
                value = r

        return (err,value)

