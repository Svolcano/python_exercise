import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import hashlib
import logging

logger = logging.getLogger(__name__)

def get_file_hash(path):
    BUF_SIZE = (16*1024*1024)
    try:
        path = path.decode('utf8')
    except Exception, e:
        logger.info(e)
        return (False,"")

    sha1 = hashlib.sha1()
    try:
        f = open(path,'rb')
    except Exception,e:
        logger.info(e)
        return (False,"")

    while True:
        data = f.read(BUF_SIZE)
        if not data:
            f.close()
            break
        sha1.update(data)

    return (True,sha1.hexdigest())

if __name__ == '__main__':
    #print get_file_hash('/root/1.iso')
    print get_file_hash('/root/test3.txt')
