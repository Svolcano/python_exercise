import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_log_backup():
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


    def insert_record(self, path, time, size, hash):
        sql = "insert into tab_log_backup(path, last_modify_time, size, hash) values('%s', '%s', '%s', '%s')" % (path, time, size, hash)

        return self.db.execute(sql)


    def get_records_by_time(self, lbtime, btime):
        '''
        get records between last backup time and current backup time.
        Args:
            lbtime, btime:last backup time, backup time
        Return:
            err,records
        Raise:
        '''

        sql = "select * from tab_log_backup where last_modify_time between '%s' and '%s'" %(lbtime, btime)
 
        err, result = self.db.query(sql)

#         records = [(1, '/BGlog/bgeventlog-user11-192.168.1.113--57560-1422689981.bin', '2015-02-02 11:00:00'),]

        return (err,result)
    
    def delete_record_by_id(self, id):
        '''
        delete record by id.
        Args:
            id:id
        Return:
            err
x
        Raise:
        '''

        sql = "delete from tab_log_backup where id=%s" % id
        return self.db.execute(sql)