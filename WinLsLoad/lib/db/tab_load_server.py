#!/usr/bin/python
# _*_ coding: utf-8 _*_

import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_load_server():
    '''
    Manage tab_load_server table.
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

    def get_servers_from_zonename(self, zone_name):
        '''
        get servers from zonename.
        Args:
            zonename:the zone name, map to tab_load_server field zone_id
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        sql = "select ip, user, password from tab_load_server inner join tab_zones on tab_load_server.zone_id = tab_zones.zone_id where zone_name = '%s'" % zone_name
        rtn, result = self.db.query(sql)
        if False == rtn:
            return (rtn, result)

        server_list = []
        for row in result:
            server_list.append(row)

        return (rtn, server_list)

    def get_servers(self):
        '''
        get servers.
        Args:
            null.
        Return:
            (False,None):database error
            (True,...):the normal record
        Raise:
        '''

        sql = "select ip, user, password from tab_load_server;"
        rtn, result = self.db.query(sql)
        if False == rtn:
            return (rtn, result)

        server_list = []
        for row in result:
            server_list.append(row)

        return (rtn, server_list)

