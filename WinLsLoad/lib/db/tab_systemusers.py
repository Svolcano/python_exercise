import MySQLdb

from mysql_basic_c import mysql_basic_c as database

class tab_systemusers():
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

    def get_email_address(self, name):
        '''
        get value of name
        Args:
            name:the user name
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        sql = "select email from tab_systemusers where loginname='%s'" % name

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        value = ()

        for row in result:
            for r in row:
                value = r

        return (err,value)

