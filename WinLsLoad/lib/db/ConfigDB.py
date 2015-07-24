import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class ConfigDB(object):
    '''
    Manage config database tables.
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
        self._db = database(host, user, passwd, db)

    def is_user_zone_stop_login(self, user, zonename):
        '''
        is user zone stop login.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,()):no record
            (True,0/1):the normal value
        Raise:
        '''
        sql = "select tab_user_zone_relation.stop_login from tab_zones join tab_basic_users join tab_user_zone_relation where tab_basic_users.user_id=tab_user_zone_relation.user_id and tab_zones.zone_id=tab_user_zone_relation.zone_id and loginname='%s' and zone_name='%s'" % (user,zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        stop_login = ()

        for row in result:
            for r in row:
                stop_login = r

        return (err,stop_login)

    def is_zone_enable(self, zonename):
        '''
        is zone enable.
        Args:
            zonename:zonename
        Return:
            (False,None):database error
            (True,()):no record
            (True,0/1):the normal value
        Raise:
        '''
        sql = "select enable from tab_zones where zone_name='%s'" % zonename
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        enable = ()

        for row in result:
            for r in row:
                enable = r

        return (err,enable)

    def is_zone_audit_enable(self, zonename):
        '''
        is zone audit enable.
        Args:
            zonename:zonename
        Return:
            (False,None):database error
            (True,()):no record
            (True,0/1):the normal value
        Raise:
        '''
        sql = "select audit_enable from tab_zones where zone_name='%s'" % zonename
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        audit_enable = ()

        for row in result:
            for r in row:
                audit_enable = r

        return (err,audit_enable)

    def get_zoneid_from_network_name(self, network_name):
        '''
        get zoneid from network_name.
        Args:
            network_name:such as eth2
        Return:
            (False,None):database error
            (True,()):no record
            (True,zonename):the normal value
        Raise:
        '''
        sql = "select tab_zones.zone_id from tab_zones join tab_zone_network_relation join tab_networks where tab_zones.zone_id=tab_zone_network_relation.zone_id and tab_networks.network_id=tab_zone_network_relation.network_id and tab_networks.network_name='%s'" % network_name
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        zone_id = ()

        for row in result:
            for r in row:
                zone_id = r

        return (err,zone_id)

    def get_zonename_from_zoneid(self, zone_id):
        '''
        get zonename from zoneid.
        Args:
            zone_id:zone_id of tab_zones
        Return:
            (False,None):database error
            (True,()):no record
            (True,zonename):the normal value
        Raise:
        '''
        sql = "select zone_name from tab_zones where zone_id=%s" % zone_id
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        zonename = ()

        for row in result:
            for r in row:
                zonename = r

        return (err,zonename)

    def get_username_from_userid(self, user_id):
        '''
        get username for userid.
        Args:
            user_id:tab_basic_users field user_id
        Return:
            (False,None):database error
            (True,()):no record
            (True,username):the normal value
        Raise:
        '''
        sql = "select loginname from tab_basic_users where user_id=%s" % user_id
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        username = ()

        for row in result:
            for r in row:
                username = r

        return (err,username)

    def is_user_enable(self, user):
        '''
        is user enable.
        Args:
            user:username
        Return:
            (False,None):database error
            (True,()):no record
            (True,0/1):the normal value
        Raise:
        '''
        sql = "select enable from tab_basic_users where loginname='%s'" % user
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        enable = ()

        for row in result:
            for r in row:
                enable = r

        return (err,enable)

    def get_zone_userid_list(self, zonename):
        '''
        get userid list for zone.
        Args:
            zonename:zonename
        Return:
            (False,None):database error.
            (True,[]):no zone
            (True,['1','2']):the normal case
        Raise:
        '''
        sql = "select tab_basic_users.user_id from tab_container_runtime join tab_zones join tab_basic_users join tab_user_zone_relation where tab_user_zone_relation.user_id = tab_basic_users.user_id and tab_user_zone_relation.zone_id = tab_zones.zone_id and tab_zones.zone_name='%s' and tab_container_runtime.zonename='%s' and tab_container_runtime.user = tab_basic_users.loginname" % (zonename, zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        userid_list = []

        for row in result:
            for r in row:
                userid_list.append(r)

        return (err,userid_list)


    def get_user_zonelist(self, user):
        '''
        get zonelist for user.
        Args:
            user:username
        Return:
            (False,None):database error.
            (True,[]):no zone
            (True,['zone1','zone2']):the normal case
        Raise:
        '''
        sql = "select zone_name from tab_zones join tab_basic_users join tab_user_zone_relation where tab_user_zone_relation.user_id = tab_basic_users.user_id and tab_user_zone_relation.zone_id = tab_zones.zone_id and tab_basic_users.loginname='%s'" % user
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        zonelist = []

        for row in result:
            for r in row:
                zonelist.append(r)

        return (err,zonelist)

    def get_zone_application_info(self, zonename):

        sql = "SELECT ip FROM tab_zones JOIN tab_zone_applications WHERE zone_name='%s' AND tab_zones.zone_id = tab_zone_applications.zone_id" % zonename

        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        application_info = ()

        for row in result:
            application_info = row

        return (err,application_info)

    def get_user_zone_application_info(self, user, zonename):

        sql = "SELECT tab_basic_users.user_name,tab_basic_users.realm_name,ip FROM tab_basic_users JOIN tab_zones JOIN tab_user_zone_applications WHERE tab_basic_users.loginname='%s' AND zone_name='%s' AND tab_basic_users.user_id=tab_user_zone_applications.user_id AND tab_zones.zone_id = tab_user_zone_applications.zone_id" % (user,zonename)

        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        application_info = ()

        for row in result:
            application_info = row

        return (err,application_info)

    def get_user_zone_all_applications(self, user, zonename):
        '''
        get the applications items of user for zone.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,list):the normal audit items
        Raise:
        '''
        err,zone_application_list = self.get_zone_applications(zonename)
        if False == err:
            return (err,zone_application_list)

        err,user_zone_application_list = self.get_user_zone_applications(user, zonename)
        if False == err:
            return (err,user_zone_application_list)

        all_application_list = zone_application_list + user_zone_application_list[0]
        application_list_enable = set(all_application_list)
        application_list_disable = set(user_zone_application_list[1])
 
        application_list = application_list_enable - application_list_disable

        return (err,list(application_list))

    def get_zone_applications(self, zonename):
        '''
        get applications for the zone.
        Args:
            zonename:zonename
        Return:
            (False,None):database error.
            (True,list):the normal audit items
        Raise:
        '''
        sql = "SELECT tab_zone_applications.protocol FROM tab_zones JOIN tab_zone_applications WHERE zone_name='%s' AND tab_zones.zone_id = tab_zone_applications.zone_id" % zonename
        err,result = self._db.query(sql)
        
        if False == err:
            return (err,result)

        application_list = []

        for row in result:
            for r in row:
                application_list.append(r)

        return (err,application_list)

    def get_user_zone_applications(self, user, zonename):
        '''
        get applications of user for zone, but no consider applications of the zone.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,(enable_list,disable_list)):the audit items,enable_list is the enable audit list , disable_list is the disable audit list.
        Raise:
        '''
        sql = "SELECT protocol FROM tab_basic_users JOIN tab_zones JOIN tab_user_zone_applications WHERE tab_basic_users.loginname='%s' AND zone_name='%s' AND tab_basic_users.user_id=tab_user_zone_applications.user_id AND tab_zones.zone_id = tab_user_zone_applications.zone_id AND tab_user_zone_applications.enable=1" % (user,zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        application_list_enable = []

        for row in result:
            for r in row:
                application_list_enable.append(r)

        sql = "SELECT protocol FROM tab_basic_users JOIN tab_zones JOIN tab_user_zone_applications WHERE tab_basic_users.loginname='%s' AND zone_name='%s' AND tab_basic_users.user_id=tab_user_zone_applications.user_id AND tab_zones.zone_id = tab_user_zone_applications.zone_id AND tab_user_zone_applications.enable=0" % (user,zonename)

        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        application_list_disable = []

        for row in result:
            for r in row:
                application_list_disable.append(r)

        return (err,(application_list_enable, application_list_disable))

    def get_user_zone_all_audit_items(self, user, zonename):
        '''
        get the audit items of user for zone.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,list):the normal audit items
        Raise:
        '''
        err,zone_auditlist = self.get_zone_audit_items(zonename)
        if False == err:
            return (err,zone_auditlist)

        err,user_zone_auditlist = self.get_user_zone_audit_items(user, zonename)
        if False == err:
            return (err,user_zone_auditlist)

        all_auditlist = zone_auditlist + user_zone_auditlist[0]
        auditlist_enable = set(all_auditlist)
        auditlist_disable = set(user_zone_auditlist[1])
        auditlist = auditlist_enable - auditlist_disable

        return (err,list(auditlist))

    def get_zone_audit_items(self, zonename):
        '''
        get audit items for the zone.
        Args:
            zonename:zonename
        Return:
            (False,None):database error.
            (True,list):the normal audit items
        Raise:
        '''
        sql = "SELECT audit_item_name FROM tab_zones JOIN tab_zone_audititem_relation JOIN tab_audit_items WHERE zone_name='%s' AND tab_zones.zone_id = tab_zone_audititem_relation.zone_id AND tab_zone_audititem_relation.audit_item_id=tab_audit_items.audit_item_id" % zonename
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        auditlist = []

        for row in result:
            for r in row:
                auditlist.append(r)

        return (err,auditlist)

    def get_user_zone_audit_items(self, user, zonename):
        '''
        get audit items of user for zone, but no consider audit items of the zone.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,(enable_list,disable_list)):the audit items,enable_list is the enable audit list , disable_list is the disable audit list.
        Raise:
        '''
        sql = "SELECT audit_item_name FROM tab_basic_users JOIN tab_zones JOIN tab_user_zone_audititem_relation JOIN tab_audit_items WHERE loginname='%s' AND zone_name='%s' AND tab_basic_users.user_id=tab_user_zone_audititem_relation.user_id AND tab_zones.zone_id = tab_user_zone_audititem_relation.zone_id AND tab_user_zone_audititem_relation.audit_item_id=tab_audit_items.audit_item_id AND tab_user_zone_audititem_relation.enable=1" % (user,zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        auditlist_enable = []

        for row in result:
            for r in row:
                auditlist_enable.append(r)

        sql = "SELECT audit_item_name FROM tab_basic_users JOIN tab_zones JOIN tab_user_zone_audititem_relation JOIN tab_audit_items WHERE loginname='%s' AND zone_name='%s' AND tab_basic_users.user_id=tab_user_zone_audititem_relation.user_id AND tab_zones.zone_id = tab_user_zone_audititem_relation.zone_id AND tab_user_zone_audititem_relation.audit_item_id=tab_audit_items.audit_item_id AND tab_user_zone_audititem_relation.enable=0" % (user,zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        auditlist_disable = []

        for row in result:
            for r in row:
                auditlist_disable.append(r)

        return (err,(auditlist_enable, auditlist_disable))

    def get_user_zone_all_security_items(self, user, zonename):
        '''
        get all security items of the user for the zone.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,list):the security items
        Raise:
        '''
        err,zone_securitylist = self.get_zone_security_items(zonename)
        if False == err:
            return (err,zone_securitylist)

        err,user_zone_securitylist = self.get_user_zone_security_items(user, zonename)
        if False == err:
            return (err,user_zone_securitylist)

        all_securitylist = zone_securitylist + user_zone_securitylist[0]
        securitylist_enable = set(all_securitylist)
        securitylist_disable = set(user_zone_securitylist[1])
        securitylist = securitylist_enable - securitylist_disable

        return (err,list(securitylist))

    def get_zone_security_items(self, zonename):
        '''
        get security items of zone.
        Args:
            zonename:zonename
        Return:
            (False,None):database error
            (True,list):the security items
        Raise:
        '''
        sql = "SELECT security_item_name FROM tab_zones JOIN tab_zone_securityitem_relation JOIN tab_security_items WHERE zone_name='%s' AND tab_zones.zone_id = tab_zone_securityitem_relation.zone_id AND tab_zone_securityitem_relation.security_item_id=tab_security_items.security_item_id" % zonename
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        securitylist = []

        for row in result:
            for r in row:
                securitylist.append(r)

        return (err,securitylist)

    def get_user_zone_security_items(self, user, zonename):
        '''
        get security items of user for the zone.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,(enable_list,disable_list)):enable_list is the enable security list, disable_list is the disable security list.
        Raise:
        '''
        sql = "SELECT security_item_name FROM tab_basic_users JOIN tab_zones JOIN tab_user_zone_securityitem_relation JOIN tab_security_items WHERE loginname='%s' AND zone_name='%s' AND tab_basic_users.user_id=tab_user_zone_securityitem_relation.user_id AND tab_zones.zone_id = tab_user_zone_securityitem_relation.zone_id AND tab_user_zone_securityitem_relation.security_item_id=tab_security_items.security_item_id AND tab_user_zone_securityitem_relation.enable=1" % (user,zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        securitylist_enable = []

        for row in result:
            for r in row:
                securitylist_enable.append(r)

        sql = "SELECT security_item_name FROM tab_basic_users JOIN tab_zones JOIN tab_user_zone_securityitem_relation JOIN tab_security_items WHERE loginname='%s' AND zone_name='%s' AND tab_basic_users.user_id=tab_user_zone_securityitem_relation.user_id AND tab_zones.zone_id = tab_user_zone_securityitem_relation.zone_id AND tab_user_zone_securityitem_relation.security_item_id=tab_security_items.security_item_id AND tab_user_zone_securityitem_relation.enable=0" % (user,zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        securitylist_disable = []

        for row in result:
            for r in row:
                securitylist_disable.append(r)

        return (err,(securitylist_enable,securitylist_disable))

    def is_zone_for_user(self, user, zonename):
        '''
        if the zone for the user.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,True):the user has the zone
            (True,False):the user has not the zone
        Raise:
        '''
        err,zonelist = self.get_user_zonelist(user)

        if False == err:
            return (err,zonelist)

        if zonename in zonelist:
            return (err,True)
        else:
            return (err,False)

    def get_zonename_for_netname(self, netname):
        '''
        get the zonename of the netname.
        Args:
            netname:netname
        Return:
            (False,None):database error
            (True,()):no record
            (True,zonename):the zonename for the netname.
        Raise: 
        '''
        sql = "select zone_name from tab_zones join tab_networks join tab_zone_network_relation where tab_zone_network_relation.network_id = tab_networks.network_id and tab_zone_network_relation.zone_id = tab_zones.zone_id and tab_networks.network_name='%s'" % netname
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        zonename = ()

        for row in result:
            for r in row:
                zonename = r

        return (err,zonename)

    def get_netname_for_zone(self, zonename):
        '''
        get the netname of the zone.
        Args:
            zonename:zonename
        Return:
            (False,None):database error
            (True,()):no record
            (True,netname):the netname for the zone.
        Raise: 
        '''
        sql = "select network_name from tab_zones join tab_networks join tab_zone_network_relation where tab_zone_network_relation.network_id = tab_networks.network_id and tab_zone_network_relation.zone_id = tab_zones.zone_id and tab_zones.zone_name='%s'" % zonename
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        netname = ()

        for row in result:
            for r in row:
                netname = r

        return (err,netname)

    def get_ip_for_zone(self, zonename):
        '''
        get the network ip of the zone.
        Args:
            zonename:zonename
        Return:
            (False,None):database error
            (True,()):no record
            (True,network ip):the network ip for the zone.
        Raise: 
        '''
        sql = "select ip from tab_zones join tab_networks join tab_zone_network_relation where tab_zone_network_relation.network_id = tab_networks.network_id and tab_zone_network_relation.zone_id = tab_zones.zone_id and tab_zones.zone_name='%s'" % zonename
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        ip = ()

        for row in result:
            for r in row:
                ip = r

        return (err,ip)

    def get_sftpport_for_zone(self, zonename):
        '''
        get the sftpport of the zone.
        Args:
            zonename:zonename
        Return:
            (False,None):database error
            (True,()):no record
            (True,sftpport):the sftpport for the zone.
        Raise: 
        '''
        sql = "select sftpport from tab_zones where zone_name='%s'" % zonename
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        sftpport = ()

        for row in result:
            for r in row:
                sftpport = r

        return (err,sftpport)

    def get_passwd_for_user(self, user):
        '''
        get passwd for user.
        Args:
            user:username
        Return:
            (False,None):database error
            (True,()):no record
            (True,string):the normal passwd value
        Raise:
        '''
        sql = "select password from tab_basic_users where loginname='%s'" % user
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        passwd = ()

        for row in result:
            for r in row:
                passwd = r

        return (err,passwd)

    def get_network_record_from_networkid(self, network_id):
        '''
        get one record from tab_networks for network_id.
        Args:
            network_id:network id
        Return:
            (False,None):database error
            (True,()):no record
            (True,(...)):the normal record
        Raise:
        '''
        sql = "select * from tab_networks where network_id=%s" % network_id

        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        network_record = ()

        for row in result:
            network_record = row

        return (err,network_record)

    def get_networkid_list(self):
        '''
        get networkid list from tab_networks.
        Args:
        Return:
            (False,None):database error
            (True,[]):no record
            (True,[...]):the normal record
        Raise:
        '''
        sql = "select network_id from tab_networks"

        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        networkid_list = []

        for row in result:
            for r in row:
                networkid_list.append(r)

        return (err,networkid_list)

    def get_netname_from_zoneid(self,zoneid):
        '''
        get the netname of the zone.
        Args:
            zonename:zoneid
        Return:
            (False,None):database error
            (True,()):no record
            (True,netname):the netname for the zone.
        Raise: 
        '''
        sql = "select network_name from tab_zones join tab_networks join tab_zone_network_relation where tab_zone_network_relation.network_id = tab_networks.network_id \
        and tab_zone_network_relation.zone_id = tab_zones.zone_id and tab_zones.zone_id='%s'"  %zoneid
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        netname = ()

        for row in result:
            for r in row:
                netname = r

        return (err,netname)


    def get_username_for_userid(self,id) :
        sql = "select loginname from tab_basic_users where user_id = %d" %id
        err,result = self._db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_zonename_for_zoneid(self,id) :
        sql = "select zone_name from tab_zones where zone_id = %d" % int(id)
        err,result = self._db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

    def get_approval_zone(self):
        sql = "select loginname,zone_id from tab_basic_users \
               join tab_systemuser_zone_relation join \
               tab_basic_user_role_relation join \
               tab_basic_role_privilege_relation where \
               tab_basic_users.user_id = tab_systemuser_zone_relation.systemuser_id and \
               tab_systemuser_zone_relation.systemuser_id = tab_basic_user_role_relation.user_id and \
               tab_basic_user_role_relation.role_id = tab_basic_role_privilege_relation.role_id and \
               tab_basic_role_privilege_relation.privilege_id=7031"
        err,result = self._db.query(sql)
        if False == err:
            return (err,result)

        result_list = []
        for row in result:
            result_list.append(row)
        return (err, result_list)

if __name__ == '__main__':
    db = ConfigDB('localhost','sboxweb','Sbox123456xZ','sbox_db')
    db.get_user_zonelist('user1')
    db.get_netname_for_zone('zone1')
    print db.is_zone_for_user('user1','zone1')

    print '------'
    print db.is_user_enable('jmzhang')
    print db.is_zone_enable('zone1')
    print db.is_user_zone_stop_login('jmzhang','zone1')

    print '------'
    print 'qqli_zone1 audit:',db.get_user_zone_audit_items('qqli','zone1')
    print 'qqli_zone1 security:',db.get_user_zone_security_items('qqli','zone1')

    print '------'
    print 'zone1 audit:',db.get_zone_audit_items('zone1')
    print 'zone1 security:',db.get_zone_security_items('zone1')

    print '-----'
    print 'qqli_zone1 allaudit:',db.get_user_zone_all_audit_items('qqli','zone1')
    print 'qqli_zone1 allsecurity:',db.get_user_zone_all_security_items('qqli','zone1')

    print '------'
    print db.get_ip_for_zone('zone1')

    print '-----'
    print 'audit_enable',db.is_zone_audit_enable('zone2')

    print '-----'
    print 'sftpport:',type(db.get_sftpport_for_zone('zone1'))
    print 'sftpport:',db.get_sftpport_for_zone('zone2')
    print 'sftpport:',db.get_sftpport_for_zone('zone3')
    print '-----'
    print db.get_username_from_userid(1)
    print db.get_zonename_from_zoneid(11)
    print db.get_zone_userid_list('zone1')
