import sqlite3
import logging

logger = logging.getLogger(__name__)

class sqlite_basic_c:
    '''
    Basicly Manage sqlite3 database.
    '''
    def __init__(self, path):
         '''
         init class.
         Args:
             path:db file path.
         Return:
         Raise:
         '''
         self.path = path

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
            conn = sqlite3.connect(self.path)
        except Exception, e:
            logger.info('path:%s,exception:%s', self.path, e)
            return (False, None)

        cursor = conn.cursor()

        try:
            n = cursor.execute(sql)
            rows = cursor.fetchall()
        except Exception, e:
            logger.info(e)
            cursor.close()
            conn.close()
            return (False, None)

        cursor.close()
        conn.close()

        return (True, rows)
        
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
            conn = sqlite3.connect(self.path)
        except Exception ,e:
            logger.info('path:%s,exception:%s', self.path, e)
            return False

        cursor = conn.cursor()

        try:
            n = cursor.execute(sql)
            conn.commit()
        except Exception, e:
            logger.info(e)
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
            conn = sqlit3.connect(self.path) 
        except Exception ,e:
            logger.info('path:%s,exception:%s', self.path, e)
            return False

        cursor = conn.cursor()

        try:
            n = cursor.executemany(sql, args)
            conn.commit()
        except Exception, e:
            logger.info(e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False

        cursor.close()
        conn.close()
        return True

