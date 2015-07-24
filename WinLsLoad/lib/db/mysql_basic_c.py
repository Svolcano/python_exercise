import MySQLdb
import logging

logger = logging.getLogger(__name__)

class mysql_basic_c(object):
    '''
    Basically, Manage mysql database tables.
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
        self.host   = host
        self.user   = user
        self.passwd = passwd
        self.db     = db

    def query(self, sql):
        '''
        query db, return results.
        Args:
            sql:sql statement
        Return:
            (False,None):database error
            (True,rows):the normal value
        Raise:
        '''
        try:
            conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
        except Exception,e:
            logger.info(e)
            return (False,None)

        cursor = conn.cursor()

        try:
            n = cursor.execute(sql)
            rows = cursor.fetchall()
        except Exception,e:
            logger.info("sql:%s,%s", sql, e)
            cursor.close()
            conn.close()
            return (False,None)

        cursor.close()
        conn.close()

        return (True,rows)

    def execute(self, sql):
        '''
        execute sql, no return.
        Args:
            sql:sql statement
        Return:
            False:database error
            True:success
        Raise:
        '''
        try:
            conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
        except Exception ,e:
            logger.info(e)
            return False

        cursor = conn.cursor()

        try:
            n = cursor.execute(sql)
            conn.commit()
        except Exception,e:
            logger.info("sql:%s,%s", sql, e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False

        cursor.close()
        conn.close()
        return True

    def executemany(self, sql, args):
        '''
        execute sql, no return.
        Args:
            sql:sql statement
        Return:
            False:database error
            True:success
        Raise:
        '''
        try:
            conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
        except Exception ,e:
            logger.info(e)
            return False

        cursor = conn.cursor()

        try:
            n = cursor.executemany(sql, args)
            conn.commit()
        except Exception,e:
            logger.info("sql:%s,%s", sql, e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False

        cursor.close()
        conn.close()
        return True
