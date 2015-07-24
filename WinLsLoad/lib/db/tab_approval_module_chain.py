import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_approval_module_chain():
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

    def get_one_chain(self,id):
        sql = "select chain_id,name,type,source_zone_id,destination_zone_id,chain,enable,priority from tab_approval_module_chain where chain_id = %d" %id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_all_chains(self):
        #chain_id | name | type | source_zone_id | destincation_zone_id | chain | enable |
        sql = "select chain_id,name,type,source_zone_id,destination_zone_id,chain,enable,priority from tab_approval_module_chain" 
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list) 
 
