import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_basic_users():
    '''
    Manage tab_basic_users table
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

    def update_password(self, user, password):
        '''
        update password.
        Args:
            user:user
            password:password
        Return:
            True/False:success/fail
        Raise:
        '''

        sql = "update tab_basic_users set password='%s' where loginname='%s'" % (password, user)

        return self.db.execute(sql)

    def get_userid_from_username(self, username):
        '''
        get userid from username
        Args:
            username:the user name, map to tab_basic_users field loginname
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        sql = "select user_id from tab_basic_users where loginname='%s'" % username

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        user_id = ()

        for row in result:
            for r in row:
                user_id = r

        return (err,user_id)

    def get_user_id(self, realm_name, user_name):
        '''
        get user_id by realm_name and user_name
        Args:
            realm_name:realm_name
            user_name:the user name
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        sql = "select user_id from tab_basic_users where realm_name='%s' and user_name='%s'" % (realm_name,user_name)

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        user_id = ()

        for row in result:
            for r in row:
                user_id = r

        return (err,user_id)

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

        sql = "select email from tab_basic_users where loginname='%s'" % name

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        value = ()

        for row in result:
            for r in row:
                value = r

        return (err,value)


    def insert(self, loginname, realm_name, user_name):
        sql = "insert into tab_basic_users(loginname, realm_name, user_name) values('%s', '%s', '%s')" % (loginname, realm_name, user_name)

        return self.db.execute(sql)

    def delete(self, realm_name, user_name):
        sql = "delete from tab_basic_users where realm_name='%s' and user_name = '%s'" % (realm_name, user_name) 

        return self.db.execute(sql)

    def delete_by_realm_name(self, realm_name):
        sql = "delete from tab_basic_users where realm_name='%s'" % realm_name 
        return self.db.execute(sql)

    def get_userlist_by_realm_name(self, realm_name):
        '''
        get userid from username
        Args:
            username:the user name, map to tab_basic_users field loginname
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        sql = "select user_name from tab_basic_users where realm_name='%s'" % realm_name

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        user_list = []

        for row in result:
            for r in row:
                user_list.append(r)

        return (err,user_list)



