import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class tab_history_tickets():
    '''
    Manage tab_history_tickets table
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

    def insert_one_record_from_ticket_record(self, ticket_record):
        '''
        insert one record from ticket record.
        Args:
            ticket_record:tab_tickets record
        Return:
            True/False
        Raise:
        '''
        if None == ticket_record[0]:
            ticket_id = 'NULL'
        else:
            ticket_id = '%s' % ticket_record[0]
        
        if None == ticket_record[1]:
            applicant_id = 'NULL'
        else:
            applicant_id = '%s' % ticket_record[1]

        if None == ticket_record[2]:
            applicant_name = 'NULL'
        else:
            applicant_name = "'%s'" % ticket_record[2]

        if None == ticket_record[3]:
            application_time = 'NULL'
        else:
            application_time = "'%s'" % ticket_record[3]

        if None == ticket_record[4]:
            application_method = 'NULL'
        else:
            application_method = '%s' % ticket_record[4]

        if None == ticket_record[5]:
            type = 'NULL'
        else:
            type = '%s' % ticket_record[5]

        if None == ticket_record[6]:
            content = 'NULL'
        else:
            content = "'%s'" % ticket_record[6]

        if None == ticket_record[7]:
            begin_time = 'NULL'
        else:
            begin_time = "'%s'" % ticket_record[7]

        if None == ticket_record[8]:
            end_time = 'NULL'
        else:
            end_time = "'%s'" % ticket_record[8]

        if None == ticket_record[9]:
            state = 'NULL'
        else:
            state = '%s' % ticket_record[9]

        if None == ticket_record[10]:
            inner_state = 'NULL'
        else:
            inner_state = '%s' % ticket_record[10]

        if None == ticket_record[11]:
            approver_id = 'NULL'
        else:
            approver_id = '%s' % ticket_record[11]

        if None == ticket_record[12]:
            approver_name = 'NULL'
        else:
            approver_name = "'%s'" % ticket_record[12]

        if None == ticket_record[13]:
            approval_time = 'NULL'
        else:
            approval_time = "'%s'" % ticket_record[13]

        if None == ticket_record[14]:
            approval_description = 'NULL'
        else:
            approval_description = "'%s'" % ticket_record[14]

        if None == ticket_record[15]:
            param_1 = 'NULL'
        else:
            param_1 = "%s" % ticket_record[15]

        if None == ticket_record[16]:
            param_2 = 'NULL'
        else:
            param_2 = "%s" % ticket_record[16]

        if None == ticket_record[17]:
            param_3 = 'NULL'
        else:
            param_3 = "'%s'" % ticket_record[17]

        if None == ticket_record[18]:
            param_4 = 'NULL'
        else:
            param_4 = "%s" % ticket_record[18]

        if None == ticket_record[19]:
            param_5 = 'NULL'
        else:
            param_5 = "%s" % ticket_record[19]

        if None == ticket_record[20]:
            param_6 = 'NULL'
        else:
            param_6 = "'%s'" % ticket_record[20]

        if None == ticket_record[21]:
            last_operation_time = 'NULL'
        else:
            last_operation_time = "'%s'" % ticket_record[21]

        if None == ticket_record[22]:
            operation_record = 'NULL'
        else:
            operation_record = "'%s'" % ticket_record[22]

        sql = "insert into tab_history_tickets(ticket_id,applicant_id,applicant_name,application_time,application_method,type,content,begin_time,end_time,state,inner_state,approver_id,approver_name,approval_time,approval_description,param_1,param_2,param_3,param_4,param_5,param_6,last_operation_time,operation_record) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (ticket_id, applicant_id, applicant_name, application_time, application_method, type, content, begin_time, end_time, state, inner_state, approver_id, approver_name, approval_time, approval_description, param_1, param_2, param_3, param_4, param_5, param_6, last_operation_time, operation_record)

        return self.db.execute(sql)

    def get_sum_files_num_about_user_one(self,user_id,type,source_zone_id,dest_zone_id):
        sql = ''
        if 11 == type  :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and param_2=%s and type=%d  " %(user_id,source_zone_id,dest_zone_id,type)
        elif 1 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_2=%s and type=%d  " %(user_id,dest_zone_id,type)
        elif 2 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and type=%d  " %(user_id,source_zone_id,type)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])
        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_num_about_user_two(self,user_id,type,source_zone_id,dest_zone_id,end_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and param_2=%s and type=%d and \
                application_time <= '%s' " %(user_id,source_zone_id,dest_zone_id,type,end_time)
        elif 1 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_2=%s and type=%d and \
                application_time <= '%s' " %(user_id,dest_zone_id,type,end_time)
        elif 2 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and type=%d and \
                application_time <= '%s' " %(user_id,source_zone_id,type,end_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])
        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_num_about_user_three(self,user_id,type,source_zone_id,dest_zone_id,begin_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and param_2=%s and type=%d and \
                application_time >= '%s' " %(user_id,source_zone_id,dest_zone_id,type,begin_time)
        elif 1 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_2=%s and type=%d and \
                application_time >= '%s' " %(user_id,dest_zone_id,type,begin_time)
        elif 2 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and type=%d and \
                application_time >= '%s' " %(user_id,source_zone_id,type,begin_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_num_about_user_four(self,user_id,type,source_zone_id,dest_zone_id,begin_time,end_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and param_2=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(user_id,source_zone_id,dest_zone_id,type,begin_time,end_time)
        elif 1 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_2=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(user_id,dest_zone_id,type,begin_time,end_time)
        elif 2 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(user_id,source_zone_id,type,begin_time,end_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])
        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_num_about_zone_one(self,type,source_zone_id,dest_zone_id):
        sql = ''
        if 11 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_1=%s and param_2=%s and type = %d " %(source_zone_id,dest_zone_id,type)
        elif 1 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_2=%s and type = %d " %(dest_zone_id,type)
        elif 2 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_1=%s and type = %d " %(source_zone_id,type)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_num_about_zone_two(self,type,source_zone_id,dest_zone_id,end_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_1=%s and param_2=%s and type=%d and \
                application_time <= '%s' " %(source_zone_id,dest_zone_id,type,end_time)
        elif 1 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_2=%s and type=%d and \
                application_time <= '%s' " %(dest_zone_id,type,end_time)
        elif 2 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_1=%s and type=%d and \
                application_time <= '%s' " %(source_zone_id,type,end_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])
        
        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_num_about_zone_three(self,type,source_zone_id,dest_zone_id,begin_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_1=%s and param_2=%s and type=%d and \
                application_time >= '%s' " %(source_zone_id,dest_zone_id,type,begin_time)
        elif 1 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_2=%s and type=%d and \
                application_time >= '%s' " %(dest_zone_id,type,begin_time)
        elif 2 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_1=%s and type=%d and \
                application_time >= '%s' " %(source_zone_id,type,begin_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_num_about_zone_four(self,type,source_zone_id,dest_zone_id,begin_time,end_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_1=%s and param_2=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(source_zone_id,dest_zone_id,type,begin_time,end_time)
        elif 1 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_2=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(dest_zone_id,type,begin_time,end_time)
        elif 2 == type :
            sql = "select sum(param_4) from tab_history_tickets where state=90 and param_1=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(source_zone_id,type,begin_time,end_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_size_about_user_one(self,user_id,type,source_zone_id,dest_zone_id):
        sql = ''
        if 11 == type :
            sql = sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and param_2=%s and type=%d " \
                %(user_id,source_zone_id,dest_zone_id,type)
        elif 1 == type :
            sql = sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_2=%s and type=%d " \
                 %(user_id,dest_zone_id,type)
        elif 2 == type :
            sql = sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and type=%d " \
                 %(user_id,source_zone_id,type)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_size_about_user_two(self,user_id,type,source_zone_id,dest_zone_id,end_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and param_2=%s and type=%d and \
            application_time <= '%s' " %(user_id,source_zone_id,dest_zone_id,type,end_time)
        elif 1 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_2=%s and type=%d and \
            application_time <= '%s' " %(user_id,dest_zone_id,type,end_time)
        elif 2 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and type=%d and \
            application_time <= '%s' " %(user_id,source_zone_id,type,end_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_size_about_user_three(self,user_id,type,source_zone_id,dest_zone_id,begin_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and param_2=%s and type=%d and \
                application_time >= '%s' " %(user_id,source_zone_id,dest_zone_id,type,begin_time)
        elif 1 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_2=%s and type=%d and \
                application_time >= '%s' " %(user_id,dest_zone_id,type,begin_time)
        elif 2 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and type=%d and \
                application_time >= '%s' " %(user_id,source_zone_id,type,begin_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_size_about_user_four(self,user_id,type,source_zone_id,dest_zone_id,begin_time,end_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and param_2=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(user_id,source_zone_id,dest_zone_id,type,begin_time,end_time)
        elif 1 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_2=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(user_id,dest_zone_id,type,begin_time,end_time)
        elif 2 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and applicant_id=%d and param_1=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(user_id,source_zone_id,type,begin_time,end_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_size_about_zone_one(self,type,source_zone_id,dest_zone_id):
        sql = ''
        if 11 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_1=%s and param_2=%s and type = %d " %(source_zone_id,dest_zone_id,type)
        elif 1 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_2=%s and type = %d " %(dest_zone_id,type)
        elif 2 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_1=%s and type = %d " %(source_zone_id,type)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_size_about_zone_two(self,type,source_zone_id,dest_zone_id,end_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_1=%s and param_2=%s and type=%d and \
                application_time <= '%s' " %(source_zone_id,dest_zone_id,type,end_time)
        elif 1 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_2=%s and type=%d and \
                application_time <= '%s' " %(dest_zone_id,type,end_time)
        elif 2 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_1=%s and type=%d and \
                application_time <= '%s' " %(source_zone_id,type,end_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_size_about_zone_three(self,type,source_zone_id,dest_zone_id,begin_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_1=%s and param_2=%s and type=%d and \
                application_time >= '%s' " %(source_zone_id,dest_zone_id,type,begin_time)
        elif 1 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_2=%s and type=%d and \
                application_time >= '%s' " %(dest_zone_id,type,begin_time)
        elif 2 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_1=%s and type=%d and \
                application_time >= '%s' " %(source_zone_id,type,begin_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_sum_files_size_about_zone_four(self,type,source_zone_id,dest_zone_id,begin_time,end_time):
        sql = ''
        if 11 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_1=%s and param_2=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(source_zone_id,dest_zone_id,type,begin_time,end_time)
        elif 1 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_2=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(dest_zone_id,type,begin_time,end_time)
        elif 2 == type :
            sql = "select sum(param_5) from tab_history_tickets where state=90 and param_1=%s and type=%d and application_time>='%s' and \
                application_time<='%s' " %(source_zone_id,type,begin_time,end_time)
        else :
            logger.error('type:%d is error' %type)
            return (False,[])

        logger.info('sql:%s' %sql)
        err,result = self.db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

if __name__ == '__main__':
    db = tab_history_tickets('192.168.1.18','sboxweb','Sbox123456xZ','sbox_db')
    '''
    print 'get_sum_files_num_about_user_one'
    print db.get_sum_files_num_about_user_one(112,1,'',11)
    print db.get_sum_files_num_about_user_one(112,2,11,'')
    print db.get_sum_files_num_about_user_one(112,3,11,12)
    print db.get_sum_files_num_about_user_one(112,11,11,12)
    print 'get_sum_files_num_about_zone_one'
    print db.get_sum_files_num_about_zone_one(1,None,11)
    print db.get_sum_files_num_about_zone_one(2,11,None)
    print db.get_sum_files_num_about_zone_one(3,12,11)
    print db.get_sum_files_num_about_zone_one(11,11,12)
    print 'get_sum_files_num_about_user_two'
    print db.get_sum_files_num_about_user_two(112,1,None,11,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_user_two(112,2,11,None,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_user_two(112,3,11,12,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_user_two(112,11,11,12,'2015-02-13 10:10:10')
    print 'get_sum_files_num_about_zone_two'
    print db.get_sum_files_num_about_zone_two(1,None,11,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_zone_two(2,11,None,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_zone_two(3,11,12,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_zone_two(11,11,12,'2015-02-13 10:10:10')
    print 'get_sum_files_num_about_user_three'
    print db.get_sum_files_num_about_user_three(112,1,None,11,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_user_three(112,2,11,None,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_user_three(112,3,11,12,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_user_three(112,11,11,12,'2015-02-13 10:10:10')
    print 'get_sum_files_num_about_zone_three'
    print db.get_sum_files_num_about_zone_three(1,None,11,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_zone_three(2,11,None,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_zone_three(3,11,12,'2015-02-13 10:10:10')
    print db.get_sum_files_num_about_zone_three(11,11,12,'2015-02-13 10:10:10')
    '''

    print 'get_sum_files_num_about_user_four'
    print db.get_sum_files_num_about_user_four(2,1,None,11,'20150212 00:00:00','20150214 00:00:00')
    #print db.get_sum_files_num_about_user_four(112,2,11,None,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    #print db.get_sum_files_num_about_user_four(112,3,11,12,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    #print db.get_sum_files_num_about_user_four(112,11,11,12,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    '''
    print 'get_sum_files_num_about_zone_four'
    print db.get_sum_files_num_about_zone_four(1,None,11,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_num_about_zone_four(2,11,None,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_num_about_zone_four(3,11,12,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_num_about_zone_four(11,11,12,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    
    print 'get_sum_files_size_about_user_one'
    print db.get_sum_files_size_about_user_one(112,1,'',11)
    print db.get_sum_files_size_about_user_one(112,2,11,'')
    print db.get_sum_files_size_about_user_one(112,3,11,12)
    print db.get_sum_files_size_about_user_one(112,11,11,12)
    print 'get_sum_files_size_about_zone_one'
    print db.get_sum_files_size_about_zone_one(1,None,11)
    print db.get_sum_files_size_about_zone_one(2,11,None)
    print db.get_sum_files_size_about_zone_one(3,12,11)
    print db.get_sum_files_size_about_zone_one(11,11,12)
    print 'get_sum_files_size_about_user_two'
    print db.get_sum_files_size_about_user_two(112,1,None,11,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_user_two(112,2,11,None,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_user_two(112,3,11,12,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_user_two(112,11,11,12,'2015-02-13 10:10:10')
    print 'get_sum_files_size_about_zone_two'
    print db.get_sum_files_size_about_zone_two(1,None,11,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_zone_two(2,11,None,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_zone_two(3,11,12,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_zone_two(11,11,12,'2015-02-13 10:10:10')
    print 'get_sum_files_size_about_user_three'
    print db.get_sum_files_size_about_user_three(112,1,None,11,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_user_three(112,2,11,None,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_user_three(112,3,11,12,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_user_three(112,11,11,12,'2015-02-13 10:10:10')
    print 'get_sum_files_size_about_zone_three'
    print db.get_sum_files_size_about_zone_three(1,None,11,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_zone_three(2,11,None,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_zone_three(3,11,12,'2015-02-13 10:10:10')
    print db.get_sum_files_size_about_zone_three(11,11,12,'2015-02-13 10:10:10')
    '''
    print 'get_sum_files_size_about_user_four'
    print db.get_sum_files_size_about_user_four(112,1,None,11,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_size_about_user_four(112,2,11,None,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_size_about_user_four(112,3,11,12,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_size_about_user_four(112,11,11,12,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print 'get_sum_files_size_about_zone_four'
    print db.get_sum_files_size_about_zone_four(1,None,11,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_size_about_zone_four(2,11,None,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_size_about_zone_four(3,11,12,'2015-02-13 10:10:10','2015-02-15 10:10:10')
    print db.get_sum_files_size_about_zone_four(11,11,12,'2015-02-13 10:10:10','2015-02-15 10:10:10')
