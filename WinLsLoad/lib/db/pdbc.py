#!/usr/bin/python
#coding=utf8
# Filename: pdbc.py
'''
Created on Oct 23, 2014

@author: hswang
'''

import MySQLdb
import logging

from lib.log.Logger import logging_init
from lib.log.GetScriptDir import current_file_directory

logger = logging.getLogger(__name__)

class PDBCManager(object):
    '''Responsible for access DataBase.
    
    It mainly includes some DB operations.'''
    
    SUCCESS = True
    FAILURE = False

    def __init__(self, server = '', user = '', password = '', db = ''):
        '''Initial PDBC object'''
        self.server = server
        self.user = user
        self.password = password
        self.db = db
        self.conn = None
        
    def setDBInfo(self, server, user, password, db):
        self.server = server
        self.user = user
        self.password = password
        self.db = db
        
    def setHost(self, server):
        '''Set the host which is installed DB'''
        self.server = server
        
    def getHost(self):
        '''Get Host'''
        return self.server
        
    def setUser(self, user):
        '''Set the user name'''
        self.user = user
        
    def getUser(self):
        '''Get user name'''
        return self.user
        
    def setPassword(self, password):
        '''Set user password'''
        self.password = password
        
    def getPassword(self):
        '''Get user password'''
        return self.password
        
    def setDBName(self, db):
        '''Set DB name'''
        self.db = db
        
    def getDBName(self):
        '''Get DB name'''
        return self.db
    
    def connectDB(self):
        '''Connect DB and return DB object'''
        rtn = PDBCManager.SUCCESS
        if not self.conn:
            try:
                self.conn = MySQLdb.connect(host = self.server, user = self.user, passwd = self.password, db = self.db, charset = 'utf8')
            except MySQLdb.Error, e:
                rtn = PDBCManager.FAILURE
                logger.error("[PDBC.connectDB]: error %d, %s." % (e.args[0], e.args[1]))
        
        return rtn
    
    def closeDB(self):
        '''Close DB cursor and DB object'''
        if self.conn:
            self.conn.cursor().close()
            self.conn.close()
            self.conn = None
    
    def query(self, sql):
        '''Execute SQL sentence and return results.'''
        rtn = PDBCManager.SUCCESS
        items = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            items = cur.fetchall()
        except MySQLdb.Error, e:
            rtn = PDBCManager.FAILURE
            logger.error("[PDBC.query]: failed to query records from table, %s." % (e.args[0]))
        
        return (rtn, items)
    
    def execute(self, sql, arg = ''):
        '''Execute SQL sentence and return no results'''
        rtn = PDBCManager.SUCCESS
        try:
            cur = self.conn.cursor()
            if len(arg) > 0:
                cur.execute(sql, arg)
            else:
                cur.execute(sql)
            self.conn.commit()
        except MySQLdb.Error, e:
            rtn = PDBCManager.FAILURE
            self.conn.rollback()
            logger.error("[PDBC.execute]: failed to execute sql sentence, %s." % (e.args[0]))
            
        return rtn
        
    def executeMany(self, sql, args):
        '''Execute SQL sentence and return no results'''
        rtn = PDBCManager.SUCCESS
        try:
            cur = self.conn.cursor()
            cur.executemany(sql, args)
            self.conn.commit()
        except MySQLdb.Error, e:
            rtn = PDBCManager.FAILURE
            self.conn.rollback()
            logger.error("[PDBC.executeMany]: failed to execute sql sentence, %s." % (e.args[0]))
            
        return rtn
    
if __name__ == '__main__':
    path_dat = current_file_directory()
    logging_init('pdbc', path_dat)
    
    