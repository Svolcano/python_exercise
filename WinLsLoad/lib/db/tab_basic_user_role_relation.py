import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_basic_user_role_relation():
    '''
    Manage tab_basic_user_role_relation table
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

    def insert(self, user_id, role_id):
        '''
        insert userid, roleid
        Args:
            user_id:user_id
            role_id:role_id
        Return:
            True/False:success/fail
        Raise:
        '''

        sql = "insert into tab_basic_user_role_relation(user_id, role_id) values(%s,%s)" % (user_id, role_id)

        return self.db.execute(sql)

    def count_role_id(self, role_id):
        sql = "select count(*) from tab_basic_user_role_relation where role_id=%s" % role_id

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        count = ()

        for row in result:
            for r in row:
                value = r

        return (err,value)

