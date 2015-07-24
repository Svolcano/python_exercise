import MySQLdb

from mysql_basic_c import mysql_basic_c as database

class tab_domains():
    '''
    Manage tab_domains table
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

    def get_record_by_domain_id(self, domain_id):
        '''
        '''

        sql = "select * from tab_domains where domain_id=%s" % domain_id

        err, result = self.db.query(sql)

        if False == err:
            return (err,result)

        record = ()

        for row in result:
            record = row

        return (err,record)

    def get_record_by_realm_name(self, realm_name):
        '''
        '''

        sql = "select * from tab_domains where realm_name='%s'" % realm_name

        err, result = self.db.query(sql)

        if False == err:
            return (err,result)

        record = ()

        for row in result:
            record = row

        return (err,record)

    def get_all_realm_name(self):
        '''
        '''

        sql = "select realm_name from tab_domains"

        err, result = self.db.query(sql)

        if False == err:
            return (err,result)

        realm_name_list = []

        for row in result:
            for r in row:
                realm_name_list.append(r)

        return (err,realm_name_list)

    def get_type_of_realm_name(self, realm_name):
        '''
        '''

        sql = "select type from tab_domains where realm_name='%s'" % realm_name

        err, result = self.db.query(sql)

        if False == err:
            return (err,result)

        realm_type = ()

        for row in result:
            for r in row:
                realm_type = r

        return (err,realm_type)
  
