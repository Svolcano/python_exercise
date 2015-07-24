
from cmd_basic import cmd_basic
import logging

logger = logging.getLogger(__name__)

class BoxManager():
    '''
    manage containers.
    '''
    def __init__(self):
        '''
        init class.
        '''
        self.PORT_BASE = 5900
        self.cmd = cmd_basic()

    def start_sbox(self, hostname, user, geo, screennum, zonename,  netname, perm_mask, audit_mask):
        '''
        start container.
        Args:
            user:username
            geo:geometry
            screennum:the screen number
            zonename:zonename
            netname:netname
            perm_mask:Permission mask, import(bit 0), export(bit 1), to_untrust(bit 2)
            audit_mask:VNC audit record switch options, key(bit 0), screen(bit 1)
        Return:
        Raise:
        '''
        logger.info("enter start_sbox %s...", screennum)
        session_name = "'%s@%s:%s'" % (user,hostname,zonename)
        params = "-v -p %d -s %s -g %s -h /home/%s -n %s -P %d -a %d -u 1 %s" % (screennum + self.PORT_BASE, session_name, geo, user, netname, perm_mask, audit_mask, user)
        cmd = "start-sbox-opt.sh %s" % params
        self.cmd.call(cmd)
        logger.info("leave start_sbox %s...", screennum)

    def start_sbox_A(self, hostname, user, geo, screennum, zonename,  netname, perm_mask, audit_mask):
        '''
        start container.
        Args:
            user:username
            geo:geometry
            screennum:the screen number
            zonename:zonename
            netname:netname
            perm_mask:Permission mask, import(bit 0), export(bit 1), to_untrust(bit 2)
            audit_mask:VNC audit record switch options, key(bit 0), screen(bit 1)
        Return:
        Raise:
        '''
        logger.info("enter start_sbox %s...", screennum)
        session_name = "'%s@%s:%s'" % (user,hostname,zonename)
        params = "-v -A -p %d -s %s -g %s -h /home/%s -n %s -P %d -a %d -u 1 %s" % (screennum + self.PORT_BASE, session_name, geo, user, netname, perm_mask, audit_mask, user)
        cmd = "start-sbox-opt.sh %s" % params
        self.cmd.call(cmd)
        logger.info("leave start_sbox %s...", screennum)

    def stop_sbox(self,screennum):
        '''
        stop container.
        Args:
            screennum:the screen number
        Return:
        Raise:
        '''
        logger.info("enter stop_sbox %s...", screennum)
        params = "-v %d" % (screennum + self.PORT_BASE)
        cmd = "stop-sbox-by-port.sh %s" % params
        self.cmd.call(cmd)
        logger.info("leave stop_sbox %s...", screennum)

    def clean_sbox(self):
        '''
        stop all containers.
        Args:
        Return:
        Raise:
        '''
        cmd = "stop-sbox-all.sh -v"
        self.cmd.call(cmd)
        logger.info("all sbox servers are stoped")

    def resize_sbox_by_port(self, geo, screennum):
        logger.info("enter resize_sbox_by_port screennum:%s,geo:%s ...", screennum, geo)
        params = "%d" % (screennum + self.PORT_BASE)
        cmd = "resize-sbox-by-port.sh -v -s %s %s" % (geo, params)
        self.cmd.call(cmd)
        logger.info("leave resize_sbox_by_port screennum:%s,geo:%s ...", screennum, geo)
