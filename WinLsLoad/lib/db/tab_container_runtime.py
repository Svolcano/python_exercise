import MySQLdb
import time
import logging

from mysql_basic_c import mysql_basic_c as database
from ..check.PortCheck import check_port

logger = logging.getLogger(__name__)

class tab_container_runtime(object):
    '''
    Manage tab_container_runtime db table.
    '''
    def __init__(self, host, user, passwd, db):
        '''
        init class.
        Args:
            host:mysql database server host
            user:mysql database server user
            passwd:mysql database server password
            db:which database will be used
        Return:
        Raise:
        '''
        self._db = database(host, user, passwd, db)


    def del_user_zone(self, user, zonename):
        '''
        delete the record in db with the user and the zonename.
        Args:
            user:user field
            zonename:zonename field
        Return:
           True:ok
           False:database error
        Raise:
        '''
        sql = "delete from tab_container_runtime where user='%s' and zonename='%s'" % (user,zonename)
        return self._db.execute(sql)

    def del_user(self, user):
        '''
        delete the record in db with the user.
        Args:
            user:user field
        Return:
           True:ok
           False:database error
        Raise:
        '''
        sql = "delete from tab_container_runtime where user='%s'" % user
        return self._db.execute(sql)

    def get_zone_list_for_user(self, user):
        '''
        get zone list for user.
        Args:
            user:user
        Return:
            (False,None):database error.
            (True,[]):no data
            (True,[zone1,zone2]):the normal case
        Raise:

        '''
        sql = "select zonename from tab_container_runtime where user='%s'" % user
        err,result = self._db.query(sql)
        if False == err:
            return (err,result)

        zone_list = []

        for row in result:
            for r in row:
                zone_list.append(r)

        return (err, zone_list)

    def get_user_list_for_zone(self, zonename):
        '''
        get user list for zone.
        Args:
            zonename:zonename
        Return:
            (False,None):database error.
            (True,[]):no data
            (True,[user1,user2]):the normal case
        Raise:

        '''
        sql = "select user from tab_container_runtime where zonename='%s'" % zonename
        err,result = self._db.query(sql)
        if False == err:
            return (err,result)

        user_list = []

        for row in result:
            for r in row:
                user_list.append(r)

        return (err, user_list)

    def get_screennum_list_for_user(self, user):
        '''
        get screennum list for user.
        Args:
            user:username
        Return:
            (False,None):database error.
            (True,[]):no data
            (True,[1,2]):the normal case
        Raise:

        '''
        sql = "select screennum from tab_container_runtime where user='%s'" % user
        err,result = self._db.query(sql)
        if False == err:
            return (err,result)

        screennum_list = []

        for row in result:
            for r in row:
                screennum_list.append(r)

        return (err,screennum_list)

    def get_screennum_for_user_zone(self, user, zonename):
        '''
        get the screen number for the user and zone.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,()): no record
            (True,...):the screen number of the user and zone.
        Raise:
        '''
        sql = "select screennum from tab_container_runtime where user='%s' and zonename='%s'" % (user, zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        screennum = ()

        for row in result:
            for r in row:
                screennum = r

        return (err,screennum)

    def get_info_for_user_fileinout(self, user):
        '''
        get the infomation(user,zonename,screennum) where filein True of fileout True for the user.
        Args:
            user:username
        Return:
            (False,None):database error.
            (True,()):no record
            (True,other):has record
        '''
        sql = "select user,zonename,screennum from tab_container_runtime where user='%s' and (filein=1 or fileout=1)" % (user,)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        ret = ()

        for row in result:
            ret = row

        return (err,ret)

    def get_screennum(self, hostname, user, zonename):
        '''
        get free screen number for the user and zonename.
        Args:
            hostname:hostname
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,{"status":"old","screennum":screennum}): the old screennum
            (True,{"status":"new","screennum":screennum}): the new screennum
        Raise:

        '''
        sql = "select screennum from tab_container_runtime where user='%s' and zonename='%s'" % (user, zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        screennum = ()

        for row in result:
            for r in row:
                screennum = r

        if () != screennum:
            return (err,{"status":"old","screennum":screennum})
        else:
            screennum_list = []
            sql = "select screennum from tab_container_runtime"
            err,result = self._db.query(sql)

            if False == err:
                return (err,result)

            for row in result:
                for r in row:
                    screennum_list.append(r)

            for i in range(1,2000):
                if not i in screennum_list:
                    if 0 != check_port(hostname, 5900+i):
                        logger.info("host:%s, port:%s is not used.", hostname, 5900+i)
                        break
                    else:
                        logger.info("host:%s, port:%s is used.", hostname, 5900+i)
            screennum = i
            return (err,{"status":"new","screennum":screennum,"user":user,"zonename":zonename,"screenum_list":screennum_list})

    def save_info(self, user, screennum, geometry, zonename, netname, filein, fileout, internet, transfer):
        '''
        insert a active container record.
        Args:
            user:username
            screennum: the screen number
            geometry:geometry
            zonename:zone name
            netname:netname,such as br0
            filein:if import
            fileout:if export
            internet:if access external internet
            transfer:transfer between zones
        Return:
            False:database error
            True:success
        Raise:
        '''
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        sql = "insert into tab_container_runtime(user,zonename,netname,start_time,geometry,screennum,filein,fileout,internet,transfer) values('%s','%s','%s','%s','%s',%d,%d,%d,%d,%s)" % (user,zonename,netname,now,geometry,screennum,filein,fileout,internet,transfer)
        return self._db.execute(sql)

    def update_info(self, user, screennum, geometry, zonename, netname, filein, fileout, internet, transfer, update_time=True):
        '''
        update a active container record.
        Args:
            user:username
            screennum: the screen number
            geometry:geometry
            zonename:zone name
            netname:netname,such as br0
            filein:if import
            fileout:if export
            internet:if access external internet
            transfer:transfer between zones
        Return:
            False:database error
            True:success
        Raise:
        '''
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        if True == update_time:
            sql = "update tab_container_runtime set user='%s', zonename='%s', netname='%s', start_time='%s', geometry='%s', screennum=%s, filein=%s, fileout=%s, internet=%s , transfer=%s where user='%s' and zonename='%s'" % (user,zonename,netname,now,geometry,screennum,filein,fileout,internet,transfer,user,zonename)
        else:
            sql = "update tab_container_runtime set user='%s', zonename='%s', netname='%s', geometry='%s', screennum=%s, filein=%s, fileout=%s, internet=%s, transfer=%s where user='%s' and zonename='%s'" % (user,zonename,netname,geometry,screennum,filein,fileout,internet,transfer,user,zonename)
        return self._db.execute(sql)

    def delete_all(self):
        '''
        delete all record.
        Args:
        Return:
            False:database error
            True:success
        Raise:
        '''
        sql = "delete from tab_container_runtime"
        return self._db.execute(sql)

    def is_force_offline_for_user_zone(self, user, zonename):
        '''
        get the force_offline for the user and zone.
        Args:
            user:username
            zonename:zonename
        Return:
            (False,None):database error
            (True,()):the empty value
            (True,0/1):the force offline of the user and zone.
        Raise:
        '''
        sql = "select force_offline from tab_container_runtime where user='%s' and zonename='%s'" % (user, zonename)
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        force_offline = ()

        for row in result:
            for r in row:
                force_offline = r

        return (err,force_offline)

    def get_screennum_list(self):
        '''
        get all screen numbers.
        Args:
        Return:
            (False,[]):null
            (True,[1,2,4]): the normal case
        Raise:

        '''
        sql = "select screennum,user,zonename from tab_container_runtime"
        err,result = self._db.query(sql)

        if False == err:
            return (err,result)

        screennum_list = []

        for row in result:
            screennum_list.append(row)

        return (True,screennum_list)

if __name__ == '__main__':
    ac = tab_container_runtime('192.168.1.130','sboxweb','Sbox123456xZ','sbox_db')
    print ac.get_screennum('user2', 'zone1')
    print ac.get_screennum('jmzhang','zone1')
    print ac.save_info('qqli',3,'1920x1080','zone1','br0',0,0,0,'192.168.1.155')
    ac.get_info_for_user_fileinout('jmzhang')

