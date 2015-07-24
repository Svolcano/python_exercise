import logging
import ftplib
import ftputil
import ftputil.session
import os.path
import os

import sys
reload(sys)
sys.setdefaultencoding('utf8')


from lib.path.Path import Path

logger = logging.getLogger(__name__)

def ftp_upload_file(remote_ip, remote_port, remote_username, remote_password, remote_dir, local_file):
    my_session_factory = ftputil.session.session_factory(
                       base_class=ftplib.FTP,
                       port=remote_port,
                       encrypt_data_channel=True,
                       debug_level=0)

    ret = False

    path = Path()

    if False == path.exist(local_file):
        logger.info("local_file:%s not exist", local_file)
        return False

    with ftputil.FTPHost(remote_ip, remote_username, remote_password, session_factory=my_session_factory) as ftp:
        localfile = local_file
        logger.info('localfile:%s', localfile)
        remotefile = remote_dir + local_file
        logger.info('remotefile:%s', remotefile)
        remotedir  = os.path.dirname(remotefile)
        logger.info('remotedir:%s', remotedir)
        ftp.makedirs(remotedir)
        ftp.upload(localfile, remotefile)
        err,local_size = path.getsize(localfile)
        logger.info("err:%s,local_size:%s", err,local_size)
        if False == err:
            return False

        if False == ftp.path.exists(remotefile):
            return False

        remote_size = ftp.path.getsize(remotefile)
        logger.info("remote_size:%s", remote_size)
        if local_size == remote_size:
            ret = True

    return ret


if __name__ == '__main__':
    file = '/BGsftp/zh-Hans_windows_server_2008_datacenter_enterprise_standard_x64_dvd_x14-26746.iso1'
    print ftp_upload_file('192.168.1.151', 21, 'vsftp', 'vsftp', '/BGsftp/ftp_transfer/main', file)

