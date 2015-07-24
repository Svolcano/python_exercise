
class MsgBuilder():

    def __init__(self):
        pass

    def build_request_screennum(self, hostname, user, password, geometry, restart, zonename):
        msg = {}
        msg['request']  = 'screennum'
        msg['user']     = user
        msg['passwd']   = password
        msg['geometry'] = geometry
        msg['restart']  = restart
        msg['zonename'] = zonename
        msg['hostname'] = hostname
        return msg

    def build_response_screennum_auth_fail(self, user):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'auth-fail'
        msg['user']     = user
        return msg

    def build_response_screennum_hostname_error(self):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'hostname-error'
        return msg

    def build_response_screennum_timeout(self, user, zonename):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'timeout'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_screennum_force_offline(self, user, zonename):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'force_offline'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_screennum_ok(self, screennum, zonelist, status, ad):
        msg = {}
        msg['response']  = 'screennum'
        msg['return']    = 'ok'
        msg['screennum'] = screennum
        msg['zonelist']  = zonelist
        msg['status']    = status
        msg['ad']        = ad
        return msg

    def build_response_screennum_zone_not_match(self,zonelist):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'zonename-not-match'
        msg['zonelist'] = zonelist
        return msg

    def build_response_screennum_db_error(self, user, zonename):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'db-error'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_screennum_cannot_access(self, user, zonename):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'cannot-access'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_screennum_no_record(self, user, zonename):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'no-record'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_screennum_expire(self, user, zonename):
        msg = {}
        msg['response'] = 'screennum'
        msg['return']   = 'expire'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_request_zonelist(self, user, password):
        msg = {}
        msg['request'] = 'zonelist'
        msg['user']    = user
        msg['passwd']  = password
        return msg

    def build_response_zonelist_auth_fail(self, user):
        msg = {}
        msg['response'] = 'zonelist'
        msg['return']   = 'auth-fail'
        msg['user']     = user
        return msg

    def build_response_zonelist_hostname_error(self):
        msg = {}
        msg['response'] = 'zonelist'
        msg['return']   = 'hostname-error'
        return msg

    def build_response_zonelist_ok(self, user, zonelist):
        msg = {}
        msg['response'] = 'zonelist'
        msg['return']   = 'ok'
        msg['user']     = user
        msg['zonelist'] = zonelist
        return msg

    def build_response_zonelist_db_error(self, user):
        msg = {}
        msg['response'] = 'zonelist'
        msg['return']   = 'db-error'
        msg['user']     = user
        return msg

    def build_response_zonelist_cannot_access(self, user):
        msg = {}
        msg['response'] = 'zonelist'
        msg['return']   = 'cannot-access'
        msg['user']     = user
        return msg

    def build_response_zonelist_no_record(self, user):
        msg = {}
        msg['response'] = 'zonelist'
        msg['return']   = 'no-record'
        msg['user']     = user
        return msg

    def build_request_stop_container(self, user, passwd, zonename):
        msg = {}
        msg['request']  = 'stop_container'
        msg['user']     = user
        msg['passwd']   = passwd
        msg['zonename'] = zonename
        return msg

    def build_response_stop_container_ok(self, user, zonename):
        msg = {}
        msg['response']  = 'stop_container'
        msg['return']    = 'ok'
        msg['user']      = user
        msg['zonename']  = zonename
        return msg

    def build_response_stop_container_auth_fail(self, user):
        msg = {}
        msg['response']  = 'stop_container'
        msg['return']    = 'auth-fail'
        msg['user']      = user
        return msg

    def build_response_stop_container_timeout(self, user, zonename):
        msg = {}
        msg['response'] = 'stop_container'
        msg['return']   = 'timeout'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_stop_container_no_record(self, user, zonename):
        msg = {}
        msg['response']  = 'stop_container'
        msg['return']    = 'no-record'
        msg['user']      = user
        msg['zonename']  = zonename
        return msg

    def build_response_stop_container_db_error(self, user, zonename):
        msg = {}
        msg['response'] = 'stop_container'
        msg['return']   = 'db-error'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_stop_container_hostname_error(self):
        msg = {}
        msg['response'] = 'stop_container'
        msg['return']   = 'hostname-error'
        return msg

    def build_request_sftpport(self, user, passwd, zonename):
        msg = {}
        msg['request']  = 'sftpport'
        msg['user']     = user
        msg['passwd']   = passwd
        msg['zonename'] = zonename
        return msg

    def build_response_sftpport_auth_fail(self, user):
        msg = {}
        msg['response'] = 'sftpport'
        msg['return']   = 'auth-fail'
        msg['user']     = user
        return msg

    def build_response_sftpport_cannot_access(self, user, zonename):
        msg = {}
        msg['response'] = 'sftpport'
        msg['return']   = 'cannot-access'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_sftpport_db_error(self, user, zonename):
        msg = {}
        msg['response'] = 'sftpport'
        msg['return']   = 'db-error'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_sftpport_hostname_error(self):
        msg = {}
        msg['response'] = 'sftpport'
        msg['return']   = 'hostname-error'
        return msg

    def build_response_sftpport_no_record(self, user, zonename):
        msg = {}
        msg['response'] = 'sftpport'
        msg['return']   = 'no-record'
        msg['user']     = user
        msg['zonename'] = zonename
        return msg

    def build_response_sftpport_ok(self, sftpport, zonelist, ad):
        msg = {}
        msg['response'] = 'sftpport'
        msg['return']   = 'ok'
        msg['sftpport'] = sftpport
        msg['zonelist'] = zonelist
        msg['ad']       = ad
        return msg

    def build_response_sftpport_zone_not_match(self, zonelist):
        msg = {}
        msg['response'] = 'sftpport'
        msg['return']   = 'zonename-not-match'
        msg['zonelist'] = zonelist
        return msg

    def build_response_bad_data(self):
        msg = {}
        msg['return'] = 'bad-data'
        return msg

    def build_request_change_password(self, user, passwd, new_password):
        msg = {}
        msg['request']      = 'change_password'
        msg['user']         = user
        msg['passwd']       = passwd
        msg['new_password'] = new_password
        return msg

    def build_response_change_password_ok(self, user):
        msg = {}
        msg['response'] = 'change_password'
        msg['return']   = 'ok'
        msg['user']     = user
        return msg

    def build_response_change_password_auth_fail(self, user):
        msg = {}
        msg['response'] = 'change_password'
        msg['return']   = 'auth-fail'
        msg['user']     = user
        return msg

    def build_response_change_password_hostname_error(self):
        msg = {}
        msg['response'] = 'change_password'
        msg['return']   = 'hostname-error'
        return msg

    def build_response_change_password_db_error(self, user):
        msg = {}
        msg['response'] = 'change_password'
        msg['return']   = 'db-error'
        msg['user']     = user
        return msg

    def build_response_change_password_openam_error(self, user, message):
        msg = {}
        msg['response'] = 'change_password'
        msg['return']   = 'openam-error'
        msg['user']     = user
        msg['message']  = message
        return msg

    def build_response_change_password_timeout(self, user):
        msg = {}
        msg['response'] = 'change_password'
        msg['return']   = 'timeout'
        msg['user']     = user
        return msg

    def build_response_change_password_domain_error(self, user):
        msg = {}
        msg['response'] = 'change_password'
        msg['return']   = 'domain-error'
        msg['user']     = user
        return msg

if __name__ == '__main__':
    bder = MsgBuilder()
    # 1
    zonelist = ['zone1','zone2','zone3']
    rzok = bder.build_response_zonelist_ok('jmzhang',zonelist)
    print rzok

    # 2
    rzhe = bder.build_response_zonelist_hostname_error()
    print rzhe

    # 3
    rzaf = bder.build_response_zonelist_auth_fail('jmzhang')
    print rzaf

    # 4
    rsz = bder.build_response_screennum_zone_not_match(['zone1'])
    print rsz
    
    # 5
    rso = bder.build_response_screennum_ok(3,[])
    print rso

    # 6
    rshe = bder.build_response_screennum_hostname_error()
    print rshe

    # 7
    rsaf = bder.build_response_screennum_auth_fail('jmzhang')
    print rsaf

    # 8
    rqz = bder.build_request_zonelist('jmzhang', 'zx123456')
    print rqz

    # 9
    rqs = bder.build_request_screennum('jmzhang', 'zx123456', '1920x768', 0, 'zone1')
    print rqs

    # 14
    rqs = bder.build_request_stop_container('jmzhang','zx123456','zone1')
    print rqs

    # 15
    rqs = bder.build_response_stop_container_ok('jmzhang','zone1')
    print rqs

    # 16
    rqs = bder.build_response_stop_container_auth_fail('jmzhang')
    print rqs

    # 17
    rqs = bder.build_response_stop_container_no_record('jmzhang','zone1')
    print rqs

    # 18
    rqs = bder.build_response_zonelist_db_error('jmzhang')
    print rqs

    # 19
    rqs = bder.build_response_screennum_db_error('jmzhang','zone1')
    print rqs

    # 21
    rqs = bder.build_response_stop_container_db_error('jmzhang','zone1')
    print rqs

    # 22
    rqs = bder.build_response_screennum_cannot_access('jmzhang','zone1')
    print rqs

    # 24
    rqs = bder.build_response_zonelist_cannot_access('jmzhang')
    print rqs
