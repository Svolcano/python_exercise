import logging

from ..msg.MsgBuilder import MsgBuilder

from req_basic import req_basic

logger = logging.getLogger(__name__)

class Request:
    '''
    request to server.
    '''
    def __init__(self):
        '''
        init class.

        Args:
        Return:
        Raise:  
        '''
        self.req = req_basic()

    def request_user_zonelist(self, hostname, user, password):
        '''
        request zonelist.
        Args:
            hostname:hostname
            user:username
            password:password
        Return:
            ok response
            auth-fail response
            dabase error response
            no record response
            hostname-error response
        '''
        builder = MsgBuilder()
        msg = builder.build_request_zonelist(user, password)

        response = self.req.request(hostname,msg)

        if None == response:
            hostname_error = builder.build_response_zonelist_hostname_error()
            return hostname_error
        
        if {} != response :
            return response
        else :
            return builder.build_response_bad_data() 

    def request_user_screennum(self, hostname, user, password, geometry, restart, zonename):
        '''
        request number of screen.
        Args:
            hostname:hostname
            user:user name
            password:password
            geometry:geometry
            restart:restart
            zonename:zonename
        Return:
            ok response
            auth-fail response
            zone-not match response
            database error response
            access deny response
            no record response
            hostname error response
        Raise:
        '''

        builder = MsgBuilder()
        msg = builder.build_request_screennum(hostname, user, password, geometry, restart, zonename)

        response = self.req.request(hostname,msg)

        if None == response:
            hostname_error = builder.build_response_screennum_hostname_error()
            return hostname_error

        return response

    def request_user_stop_container(self, hostname, user, password, zonename):
        '''
        request stop container.
        Args:
            hostname:hostname
            user:user name
            password:password
            zonename:zonename
        Return:
            ok response
            auth-fail response
            zone-not match response
            database error response
            access deny response
            no record response
            hostname error response
        Raise:
        '''

        builder = MsgBuilder()
        msg = builder.build_request_stop_container(user, password, zonename)

        response = self.req.request(hostname,msg)

        if None == response:
            hostname_error = builder.build_response_stop_container_hostname_error()
            return hostname_error

        return response

    def request_user_sftpport(self, hostname, user, password, zonename):
        '''
        request sftpport.
        Args:
            hostname:hostname
            user:user name
            password:password
            zonename:zonename
        Return:
            ok response
            auth-fail response
            zone-not match response
            database error response
            access deny response
            no record response
            hostname error response
        Raise:
        '''

        builder = MsgBuilder()
        msg = builder.build_request_sftpport(user, password, zonename)

        response = self.req.request(hostname,msg)

        if None == response:
            hostname_error = builder.build_response_sftpport_hostname_error()
            return hostname_error

        return response

    def request_user_change_password(self, hostname, user, password, new_password):
        '''
        request change password.
        Args:
            hostname:hostname
            user:user name
            password:password
            new_password:new password
        Return:
            ok response
            auth-fail response
            hostname error response
        Raise:
        '''

        builder = MsgBuilder()
        msg = builder.build_request_change_password(user, password, new_password)

        response = self.req.request(hostname,msg)

        if None == response:
            hostname_error = builder.build_response_change_password_hostname_error()
            return hostname_error

        return response

