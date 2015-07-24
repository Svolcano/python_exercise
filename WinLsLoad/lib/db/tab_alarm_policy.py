import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_alarm_policy():
    '''
    Manage tab_alarm_policy table
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

    def get_policy_rules(self, src_type):
        err,rules = self.db.query("select * from tab_alarm_policy where src_type_list = %d"%src_type)

        return (err,rules)

    def delete_policy(self, policy_id):
        sql = "delete from tab_alarm_policy where policy_id = %d"%policy_id
        return self.db.execute(sql)

    def modify_policy(self, policy_id, detail):
        sql = "update tab_alarm_policy set %s where policy_id = %s"%(detail, policy_id)
        return self.db.execute(sql)

    def add_policy(self, detail):
        sql = """insert into tab_alarm_policy(%s, %s, %s, %s, %s, %s) 
            values('%s', '%s', '%s', '%s', '%s', '%s')"""%detail
        return self.db.execute(sql)

