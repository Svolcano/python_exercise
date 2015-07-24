import MySQLdb

from mysql_basic_c import mysql_basic_c as database

class tab_services():

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

    def get_service_list(self):
        '''
        get service list from table services
        Args:
            none
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        service_list = []
        sql = "select service_name from tab_services"

        err,result = self.db.query(sql)

        if False == err:
            return (err,result)

        for row in result:
            for r in row:
                service_list.append(r)
        return (True,service_list)

    def update_service_status(self, service_name, service_state):
        '''
        update service status.
        Args:
            service_name:service_name in tab_services
            service_state:service_status value to update in tab_services, only 0 and 1
        Return:
            True/False:success/fail
        Raise:
        '''

        sql = "update tab_services set service_status='%d' where service_name='%s'" % (service_state, service_name)
        return self.db.execute(sql)

if __name__ == '__main__':
    table_service = tab_services('192.168.1.102','sjr','zx123456','sbox_db')
    service_list = table_service.get_service_list()
    for s in service_list:
        #table_service.update_service_status(s, 2)
        pass
