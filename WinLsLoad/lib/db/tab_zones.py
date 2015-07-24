import MySQLdb

from mysql_basic_c import mysql_basic_c as database

class tab_zones():
    '''
    Manage tab_zones table
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

    def get_id_by_name(self, name):
        '''
        get zone id from zone name.
        Args:
            name:zone_name
        Return:
            err,zoneid
        Raise:
        '''

        sql = "select zone_id from tab_zones where zone_name = '%s'" % name

        err, result = self.db.query(sql)

        if False == err:
            return (err,result)

        id = ()

        for row in result:
            for r in row:
                id = r

        return (err,id)
    
    def get_ids(self):
        '''
        get zone ids from zone table.
        Return:
            err,zone ids
        Raise:
        '''

        sql = "select zone_id from tab_zones"

        err, result = self.db.query(sql)

        if False == err:
            return (err,result)

        ids = []

        for row in result:
            for r in row:
                ids.append(r)

        ids.sort()
        ids.reverse()
        return (err,ids)


