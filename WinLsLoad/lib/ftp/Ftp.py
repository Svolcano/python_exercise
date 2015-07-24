#!/usr/local/bin/python
#-*- coding: UTF-8 -*-
import types
import logging
from ftplib import FTP
import os,sys,string,datetime,time
import socket
import re
from PathNameHandle import *
import time
#sys.path.append("../..")
#from SvrConfig import *
#from ticket.lib.LoggerDebug import logging_init_debug
#from ticket.lib.LoggerBGlog import logging_init_BGlog
#from ticket.lib.GetScriptDir import current_file_directory

logger = logging.getLogger(__name__)
from MyFTP import MyFTP

class Ftp:
    '''
    ftp modular,put and get files according to ftp protocol
    '''
    def __init__(self):
        self.hostaddr      = ''
        self.username      = ''
        self.password      = ''
        self.remotedir     = ''
        self.type          = 0
        self.localdir      = ''
        self.port          = 0
        #self.ftp           = MyFTP()
        self.ftp           = FTP()
        self.file_list     = []
        self.root_user_dir = ''
        self.exist_files   = []
        self.interrupt_times = 0
        self.close_connect = False        
 
    def __del__(self):
        self.ftp.close()
    
    def close(self):
        self.close_connect = True
        try :
            self.ftp.close()
        except:
            logger.error(e)

    def login(self,msg):
        self.hostaddr      = msg['remote_ip']
        self.username      = msg['remote_usrname']
        self.password      = msg['remote_passwd']
        self.port          = self.long_to_int(msg['remote_port'])
        self.type          = msg['type']
        self.remotedir     = msg['remote_dir']
        if (self.remotedir == '') or (self.remotedir == None) :
            self.remotedir = '/'
        self.localdir      = '/BGsftp/ftp_transfer'
        self.root_file_num = len(split_path(self.localdir))

        logger.info("self.hostaddr:%s" %self.hostaddr)
        logger.info("self.username:%s" %self.username)
        logger.info("self.password:%s" %self.password)
        logger.info("self.type:%s" %self.type)
        logger.info("self.remotedir:%s" %self.remotedir)
        logger.info("self.localdir:%s" %self.localdir)
        logger.info("self.port:%d" %self.port)
        logger.info("self.root_file_num:%s" %self.root_file_num)

        ftp = self.ftp
        try:
            timeout = 60
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            logger.info('Connecting start %s' %(self.hostaddr))
            ftp.connect(self.hostaddr, self.port)
            logger.info('Connecting sucess %s' %(self.hostaddr))
            logger.info('begin logining in %s' %(self.hostaddr))
            ftp.login(self.username, self.password)
            logger.info('sucess logining in %s' %(self.hostaddr))
        except:
            logger.error("connect or login failed")
            return False
        self.root_user_dir = self.ftp.pwd()
        if len(self.root_user_dir) > 1 :
            if ('/' == self.remotedir) or (len(self.remotedir)<2) :
                self.remotedir = self.root_user_dir + self.remotedir
            else :
                self.remotedir = self.root_user_dir + os.sep + self.remotedir
        
        return True

    def is_same_size(self, localfile, remotefile):
        try:
            remotefile_size = self.ftp.size(remotefile)
        except:
            remotefile_size = -1
            
        try:
            localfile_size = os.path.getsize(localfile)
        except:
            localfile_size = -1
        
        if remotefile_size == localfile_size:
            return 1
        else:
            return 0
            
    def download_file(self, localfile, remotefile):
        #if self.is_same_size(localfile, remotefile):
        #    return
        #else:
        #    retval = remotefile.find("ZENG")
        #    if (retval != -1):
        #logger.info('download %s ........' %localfile)
        logger.info("localfile:%s, remotefile:%s" %(localfile, remotefile))
        try :
            file_handler = open(localfile, 'wb')
            self.ftp.retrbinary('RETR %s'%(remotefile), file_handler.write)
            file_handler.close()
        except Exception,e:
            logger.error(e)
            return False
        return True

    def download_files(self, localdir, remotedir):        
        #try:
        #    self.ftp.cwd(remotedir)
        #except:
        #    return
        #if not os.path.isdir(localdir):
        #    os.makedirs(localdir)
        #self.file_list = []
        #self.ftp.dir(self.get_file_list)
        #remotenames = self.file_list
        #for item in remotenames:
        #    filetype = item[0]
        #    filename = item[1]
        #    local = os.path.join(localdir, filename)
        #    if filetype == 'd':
        #        self.download_files(local, filename)
        #    elif filetype == '-':
        #        self.download_file(local, filename)
        #self.ftp.cwd('..')

        try :
            #self.ftp.cwd(remotedir)
            files_name_list = self.ftp.nlst(remotedir)
        except Exception,e:
            logger.error(e)
            return False

        if None == files_name_list :
            logger.info("There is no log in log_bak")
            return True

        flag = True
        logger.info('files_name_list:%s' %files_name_list)
        for i in range (0,len(files_name_list)) :
            path_list = split_path(files_name_list[i])
            dest = localdir  + os.sep + path_list[-1]
            src  = files_name_list[i]
            err  = self.download_file(dest,src)
            if err == True :
                logger.info("download_file right dest:%s,src:%s" %(dest,src))
            else :
                logger.info("download_file right dest:%s,src:%s" %(dest,src))
            flag = flag & err

        return flag
    
    def sp(self,line):
        l = line.split()
        count = len(l)
        str = ' '.join(l[8:]) 
        self.exist_files.append(str)

    def get_remotefile_name(self,remotefile,flag):
        num = 0
        file_name = remotefile
        if flag==True :
            logger.info('file_name:%s' %file_name)
            return file_name
        #logger.info("dir:%s" %dir)
        dir = self.ftp.pwd()
        files_name_list = self.ftp.dir(dir)
        while True :
            if file_name not in self.exist_files :
                logger.info('file_name:%s' %file_name)
                return file_name
            num = num + 1
            file_name = remotefile + str(num)

    def upload_file_one_time(self,localfile,split_pathed,remotedir,remotefile,flag_input):
        if_send_flag = False
        logger.info("remotedir:%s" %remotedir)
        self.ftp.cwd(remotedir)
        for i in range(self.root_file_num,len(split_pathed)-1) :
            dir_tmp = split_pathed[i]
            try:
                self.ftp.mkd(dir_tmp)
            except:
                logger.info('Directory already exists %s' %dir_tmp)
            self.ftp.cwd(dir_tmp)
            logger.info("self.ftp.pwd:%s"  %self.ftp.pwd())
        
        logger.info("remotefile:%s" %remotefile)
        #remotefile = self.get_remotefile_name(remotefile,flag_input)
        self.interrupt_times = 0
        try :
            statinfo = os.stat(localfile)
        except Exception,e:
            logger.error(e)
            return (flag_input,False)
        filesize = int(statinfo.st_size)
        if_send_flag = True
        while True : 
            try :
                file_handler = open(localfile, 'rb')
                #remotefile = '/ftp01' + os.sep + remotefile
                self.ftp.storbinary('STOR %s' %(remotefile), file_handler)
                #if True == flag_input :
                #    rest = self.ftp.size(remotefile)
                #    self.ftp.storbinary('STOR %s' % remotefile ,file_handler,filesize,rest)
                #else :
                #    self.ftp.storbinary('STOR %s' % remotefile ,file_handler,filesize,0)
                file_handler.close()
            except Exception,e:
                logger.error(e)
                self.interrupt_times = self.interrupt_times + 1
                if self.interrupt_times >= 5 :
                    return  (if_send_flag,False)
                continue
            break

        logger.info('remotedir:%s sending: %s' %(remotedir,localfile))
        return (if_send_flag,True)

    def upload_file(self, localfile, remotefile, flag_input):
        #time.sleep(10)
        logger.info("localfile:%s, remotefile:%s, flag_input:%d" %(localfile, remotefile, flag_input))
        if not os.path.isfile(localfile):
            logger.error('localfile :%s is not file' %localfile)
            return (flag_input,False)

        split_pathed = split_path(localfile)       
        self.ftp.cwd(self.root_user_dir)
        remote_usr_path_list = split_path(self.root_user_dir)
        remote_dir1_list = split_path(self.remotedir)

        logger.info("split_pathed:%s " %split_pathed)
        logger.info("remote_usr_path_list:%s " %remote_usr_path_list)
        logger.info("remote_dir1_list:%s " %remote_dir1_list)        

        for i in range(len(remote_usr_path_list),len(remote_dir1_list)):
            dir_tmp = remote_dir1_list[i]
            try:
                self.ftp.mkd(dir_tmp)
            except:
                logger.info('Directory already exists %s' %dir_tmp)
            finally:
                logger.info("mkdir :%s" %dir_tmp)
            self.ftp.cwd(dir_tmp)

        self.ftp.cwd(self.root_user_dir)
        return self.upload_file_one_time(localfile,split_pathed,self.remotedir,remotefile,flag_input)

    def upload_files(self, localdir, remotedir):
        if not os.path.isdir(localdir):
            logger.info(localdir)
            return
        localnames = os.listdir(localdir)
        
        self.ftp.cwd(remotedir)
        
        for item in localnames:
            src = os.path.join(localdir, item)
            if os.path.isdir(src):
                try:
                    self.ftp.mkd(item)
                except:
                    logger.info('Directory already exists %s' %item)
                self.upload_files(src, item)
            else:
                self.upload_file(src, item)
        self.ftp.cwd('..')

    def get_file_list(self, line):
        ret_arr = []
        file_arr = self.get_filename(line)
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)

    def get_filename(self, line):
        pos = line.rfind(':')
        while(line[pos] != ' '):
            pos += 1
        while(line[pos] == ' '):
            pos += 1
        file_arr = [line[0], line[pos:]]
        return file_arr

    def long_to_int(self,value):
        assert isinstance(value, (int, long))
        return int(value & sys.maxint)
        
if __name__ == '__main__':
    rootdir_local  = '/home/qqli/xinyaotest/11 22.txt'
    rootdir_remote = '11 22.txt'

    logging_init_debug('Ftp', current_file_directory(), "True","info")

    f = Ftp()
    f.login()
    print f.upload_file(rootdir_local, rootdir_remote)
    
