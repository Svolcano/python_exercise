import MySQLdb
import time
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_client_runtime(object):
    '''
    Manage tab_client_runtime db table.
    '''
    def __init__(self, host, user, passwd, db):
        '''
        init class.
        Args:
            host:mysql database server host
            user:mysql database server user
            passwd:mysql database server password
            db:which database will be used
        Return:
        Raise:
        '''
        self._db = database(host, user, passwd, db)

    def get_clients(self, screennum):
        '''
        delete the record in db with the client_ip and the client_port
        Args:
            ip:client_ip field
            port:client_port field
        Return:
           True:ok
           False:database error
        Raise:
        '''
        sql = "select client_ip,client_port from tab_client_runtime where screennum=%s" % (screennum)
        err,result = self._db.query(sql)
      
        if False == err:
            return (err,result)

        ip_port_list = []
 
        for row in result:
            ip_port_list.append(row)

        return (True,ip_port_list)

    def delete(self, screennum, ip, port):
        '''
        delete the record in db with the client_ip and the client_port
        Args:
            ip:client_ip field
            port:client_port field
        Return:
           True:ok
           False:database error
        Raise:
        '''
        sql = "delete from tab_client_runtime where screennum=%s and client_ip='%s' and client_port=%s" % (screennum, ip, port)
        return self._db.execute(sql)

    def delete_screennum(self, screennum):
        sql = "delete from tab_client_runtime where screennum=%s" % screennum
        return self._db.execute(sql)

    def insert(self, screennum, user, zonename, client_ip, client_mac, client_port):
        '''
        insert the record
        Args:
            screennum:
            client_ip:
            client_mac:
            client_port:
        Return:
           True:ok
           False:database error
        Raise:
        '''
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        sql = "insert into tab_client_runtime(screennum, user, zonename, client_ip, client_mac, client_port, login_time) values(%s, '%s', '%s', '%s', '%s', %s, '%s')" % (screennum, user, zonename, client_ip, client_mac, client_port, now)
        return self._db.execute(sql)

    def delete_all(self):
        '''
        delete all record.
        Args:
        Return:
            False:database error
            True:success
        Raise:
        '''
        sql = "delete from tab_client_runtime"
        return self._db.execute(sql)


