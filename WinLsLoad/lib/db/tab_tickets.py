import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_tickets():
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

    def get_ticket_id_from_info(self, applicant_id, applicant_name, application_time, type, param_6):
        '''
        get ticket_id from other info.
        Args:
        Return:
            err,ticket_id
        Raise:
        '''

        sql = "select ticket_id from tab_tickets where applicant_id=%s and applicant_name='%s' and application_time='%s' and type=%s and param_6='%s'" % (applicant_id, applicant_name, application_time, type, param_6)

        err, result = self.db.query(sql)

        print result
        
        if False == err:
            return (err,result)

        ticket_id = ()
        for row in result:
            for r in row:
                ticket_id = r

        return (err,ticket_id)

    def get_ticket_id_from_info_b(self, applicant_name, application_time, type, param_6):
        '''
        get ticket_id from other info.
        Args:
        Return:
            err,ticket_id
        Raise:
        '''

        sql = "select ticket_id from tab_tickets where applicant_id is null and applicant_name='%s' and application_time='%s' and type=%s and param_6='%s'" % (applicant_name, application_time, type, param_6)

        err, result = self.db.query(sql)

        print result
        
        if False == err:
            return (err,result)

        ticket_id = ()
        for row in result:
            for r in row:
                ticket_id = r

        return (err,ticket_id)

    def get_ticket_from_id(self, id):
        '''
        get ticket from id.
        Args:
            id:ticket_id
        Return:
            err,ticket
        Raise:
        '''

        sql = "select * from tab_tickets where ticket_id=%s" % id

        err, result = self.db.query(sql)
        
        if False == err:
            return (err,result)

        tickets_list = ()
        for row in result:
            tickets_list = row

        return (err,tickets_list)

    def update_ticket_state_from_id(self, id, state):
        '''
        update ticket state from id.
        Args:
            id:ticket_id
            state:state
        Return:
            True/False
        Raise:
        '''

        sql = "update tab_tickets set state=%s where ticket_id=%s" % (state, id)

        return self.db.execute(sql)

    def update_inner_state(self, id, state):
        '''
        update ticket state from id.
        Args:
            id:ticket_id
            state:state
        Return:
            True/False
        Raise:
        '''

        sql = "update tab_tickets set inner_state=%s where ticket_id=%s" % (state, id)

        return self.db.execute(sql)

    def update_approve_time(self, id, str_time):
        '''
        update ticket state from id.
        Args:
            id:ticket_id
            state:state
        Return:
            True/False
        Raise:
        '''

        sql = "update tab_tickets set approval_time = '%s' where ticket_id = %d;" % (str_time, id)

        return self.db.execute(sql)

    def delete_ticket_from_id(self, id):
        '''
        delete ticket from id.
        Args:
            id:ticket_id
        Return:
            err,ticket
        Raise:
        '''

        sql = "delete from tab_tickets where ticket_id=%s" % id
        return self.db.execute(sql)

    def insert_ticket_for_request(self, applicant_id, applicant_name, application_time, application_method, type, content, state, inner_state, param_1, param_2, param_3, param_4, param_5, param_6, last_operation_time, operation_record):
        sql = "insert into tab_tickets(applicant_id,applicant_name,application_time,application_method,type,content,state,inner_state,param_1,param_2,param_3,param_4,param_5,param_6,last_operation_time,operation_record) values(%s, '%s', '%s', %s, %s, '%s', %s, %s, %s, %s, '%s', %s, %s, '%s', '%s', '%s')" % (applicant_id, applicant_name, application_time, application_method, type, content, state, inner_state, param_1, param_2, param_3, param_4, param_5, param_6, last_operation_time, operation_record)

        return self.db.execute(sql)

    def update_operation_record(self, ticket_id, add_msg):
        sql = "select operation_record from tab_tickets where ticket_id = %s" %ticket_id
        err, result = self.db.query(sql)
        logger.info("err:%s,result:%s", err, result)

        if False == err:
            return err
 
        if () == result or None == result:
            return False

        for row in result:
            for r in row:
                msg = r

        if None == msg:
            msg = add_msg
        else:
            msg = '%s' % msg
            msg = msg + add_msg

        now = "%s" % datetime.datetime.now()

        sql = "update tab_tickets set last_operation_time = '%s', operation_record = '%s' where ticket_id = %s" % (now, msg, ticket_id)

        return self.db.execute(sql)


    def update_approval_description(self,ticket_id,add_msg):
        sql = "select approval_description from tab_tickets where ticket_id = %d" %ticket_id
        err,result = self.db.query(sql)

        logger.info("err:%s,result:%s", err, result)
        if False == err:
            return err

        for row in result:
            msg = '%s' %row
            if (msg == None) or (msg == 'None') : 
                msg = add_msg
            else :
                msg = msg + add_msg
            sql = "update tab_tickets set approval_description = '%s' where ticket_id = %d" %(msg,ticket_id)
            err = self.db.execute(sql)
            return err

    def get_all_ticket_id(self):
        sql = "select ticket_id from tab_tickets"
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_applicant_id(self,ticket_id):
        sql = "select applicant_id from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def get_applicant_name(self,ticket_id):
        sql = "select applicant_name from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def get_application_time(self,ticket_id):
        sql = "select application_time from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def get_type(self,ticket_id):
        sql = "select type from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def get_param_1(self,ticket_id):
        sql = "select param_1 from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def get_param_2(self,ticket_id):
        sql = "select param_2 from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def get_param_3(self,ticket_id):
        sql = "select param_3 from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def get_param_4(self,ticket_id):
        sql = "select param_4 from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def get_param_5(self,ticket_id):
        sql = "select param_5 from tab_tickets where ticket_id=%d" %ticket_id
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)
        tickets_list = []
        for row in result:
            tickets_list.append(row)
        return (err, tickets_list)

    def delete_ticket_id_record(self,ticket_id):
        sql = "delete from tab_tickets where ticket_id = %d;" %ticket_id

        return self.db.execute(sql)
