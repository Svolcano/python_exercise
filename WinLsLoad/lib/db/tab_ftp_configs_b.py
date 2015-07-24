import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_ftp_configs():
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

    def get_backup_ftp_config(self):
        '''
        get backup ftp config record.
        '''
        sql = 'select * from tab_ftp_configs where type=2'
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        ftp_config_record = ()
        for row in result:
            ftp_config_record = row

        return (err, ftp_config_record)


