import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_system_update():
    '''
    Manage tab_system_update database
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

    def upgrade_system_success(self, id, version, dev_version):
        '''
        update system success.
        Args:
            id:id
            version:version
            dev_version:version
            status:status
        Return:
            True/False:success/fail
        Raise:
        '''

        sql = "update tab_system_update set version='%s' , dev_version=%s , status=%s where id=%s" % (version, dev_version, 1, id)

        return self.db.execute(sql)


    def upgrade_system_fail(self, id, version, dev_version, description):
        '''
        update system fail.
        Args:
            id:id
            version:version
            dev_version:version
            description:description
        Return:
            True/False:success/fail
        Raise:
        '''

        sql = "update tab_system_update set version='%s' , dev_version=%s , status=%s description='%s' where id=%s" % (version, dev_version, 2, description, id)

        return self.db.execute(sql)

