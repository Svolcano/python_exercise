import os
import logging

import datetime
from subprocess import call

logger = logging.getLogger(__name__)

class Path(object):

    def __init__(self):
        pass

    def exist(self, path):
        try:
            path_exist = os.path.exists(path)
        except Exception, e:
            logger.info(e)
            return False

        if True != path_exist:
            return False

        return True

    def makedirs(self, dir_path):
        flag = self.exist(dir_path)
        if True == flag :
            if False == os.path.isdir(dir_path):
                if True == rm_path(dir_path) :
                    flag = False
                else:
                    return False
        if False == flag:
            try:
                os.makedirs(dir_path)
            except Exception,e:
                logger.error(e)
                return False
        return True

    def mv_path(self, path_src, path_dest):
        try:
             logger.debug('mv %s to %s begin' %(path_src,path_dest))
             ret = call(['mv', '-f', path_src, path_dest])
             logger.debug('mv %s to %s end' %(path_src,path_dest))
        except Exception, e:
             logger.error(e)
             return False

        if 0 == ret:
             return True

        return False

    def rm_path(self, path_src):
        try :
            call(['rm','-rf',path_src])
            logger.debug('rm -rf path_src:%s' %path_src)
        except Exception,e:
            logger.error(e)
            return False
        return True

    def is_file_open(self, path):
        try :
            is_open = call(["lsof",path])
        except Exception, e:
            logger.error(e)
            return True

        if 0 == is_open:
            return True

        return False

    def getsize(self, path):
        try:
            size = os.path.getsize(path)
        except Exception, e:
            logger.info(e)
            return (False,0)

        return (True,size)

    def getctime(self, path):
        try:
            mtime = str(datetime.datetime.fromtimestamp(os.path.getmtime(path)))
        except Exception, e:
            logger.info(e)
            return (False,"")

        return (True,mtime)

