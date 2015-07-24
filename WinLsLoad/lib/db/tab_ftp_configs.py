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

    def get_ids(self):
        '''
        get all ids from tab_ftp_configs.
        '''
        sql = 'select id from tab_ftp_configs'
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)
        return (err, tab_token_list)

    def get_remote_ip(self,id):
        '''
        get remote_ip
        '''
        sql = "select remote_ip from tab_ftp_configs where id=%d " %id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_remote_port(self,id):
        '''
        get remote_port
        '''
        sql = "select remote_port from tab_ftp_configs where id=%d " %id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_remote_usrname(self,id):
        '''
        get remote_usrname
        '''
        sql = "select remote_username from tab_ftp_configs where id=%d " %id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_remote_passwd(self,id):
        '''
        get remote_passwd
        '''
        sql = "select remote_password from tab_ftp_configs where id=%d " %id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_type(self,id):
        '''
        get type
        '''
        sql = "select type from tab_ftp_configs where id=%d " %id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    def get_remote_dir(self,id):
        '''
        get remote_dir
        '''
        sql = "select remote_dir from tab_ftp_configs where id=%d " %id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        tab_token_list = []
        for row in result:
            tab_token_list.append(row)

        return (err, tab_token_list)

    #def get_authority(self,id):
    #    '''
    #    get authority
    #    '''
    #    sql = "select authority from tab_ftp_configs where id=%d " %id
    #    err,result = self.db.query(sql)
    #    if False == err:
    #        return (err,result)

    #   tab_token_list = []
    #    for row in result:
    #        tab_token_list.append(row)

    #    return (err, tab_token_list)

    #def get_remote_dir1(self,id):
    #    '''
    #    get remote_dir1
    #    '''
    #    sql = "select remote_dir1 from tab_ftp_configs where id=%d " %id
    #    err,result = self.db.query(sql)
    #    if False == err:
    #        return (err,result)

    #    tab_token_list = []
    #    for row in result:
    #        tab_token_list.append(row)

    #    return (err, tab_token_list)

    #def get_remote_dir2(self,id):
    #    '''
    #    get remote_dir2
    #    '''
    #    sql = "select remote_dir2 from tab_ftp_configs where id=%d " %id
    #    err,result = self.db.query(sql)
    #    if False == err:
    #        return (err,result)

    #    tab_token_list = []
    #    for row in result:
    #        tab_token_list.append(row)

    #    return (err, tab_token_list)

    #def get_local_dir(self,id):
    #    '''
    #    get local_dir
    #    '''
    #    sql = "select local_dir from tab_ftp_configs where id=%d " %id
    #    err,result = self.db.query(sql)
    #    if False == err:
    #        return (err,result)

    #    tab_token_list = []
    #    for row in result:
    #        tab_token_list.append(row)

    #    return (err, tab_token_list)

    #def get_param_1(self,id):
    #    '''
    #    get param_1
    #    '''
    #    sql = "select param_1 from tab_ftp_configs where id=%d " %id
    #    err,result = self.db.query(sql)
    #    if False == err:
    #        return (err,result)

    #    tab_token_list = []
    #    for row in result:
    #        tab_token_list.append(row)

    #    return (err, tab_token_list)

    #def get_param_2(self,id):
    #    '''
    #    get param_2
    #    '''
    #    sql = "select param_2 from tab_ftp_configs where id=%d " %id
    #    err,result = self.db.query(sql)
    #    if False == err:
    #        return (err,result)

    #    tab_token_list = []
    #    for row in result:
    #        tab_token_list.append(row)

    #     return (err, tab_token_list)

    #def get_param_3(self,id):
    #    '''
    #    get param_3
    #    '''
    #    sql = "select param_3 from tab_ftp_configs where id=%d " %id
    #    err,result = self.db.query(sql)
    #    if False == err:
    #        return (err,result)

    #    tab_token_list = []
    #    for row in result:
    #        tab_token_list.append(row)

    #    return (err, tab_token_list)

    #def get_param_4(self,id):
    #    '''
    #    get param_4
    #    '''
    #    sql = "select param_4 from tab_ftp_configs where id=%d " %id
    #    err,result = self.db.query(sql)
    #    if False == err:
    #        return (err,result)

    #    tab_token_list = []
    #    for row in result:
    #        tab_token_list.append(row)

    #    return (err, tab_token_list)
 
