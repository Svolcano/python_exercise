
import pycurl
import StringIO
import logging

logger = logging.getLogger(__name__)

def check_vnc_server(ip, port):
    c = pycurl.Curl()
    content = StringIO.StringIO()
    host = '%s:%s' % (ip,port)
    c.setopt(pycurl.URL, host)
    c.setopt(pycurl.WRITEFUNCTION, content.write)
    c.setopt(pycurl.CONNECTTIMEOUT, 3)
    c.setopt(pycurl.TIMEOUT, 3)
    ret = ""
    try:
        ret = c.perform()
    except Exception,e:
        logger.info(e)
        c.close()
        return ""

    c.close()
    return content.getvalue()


if __name__ == '__main__':
    c = check_vnc_server('127.0.0.1',5000)
    print type(c)
    print c
    a = check_vnc_server('127.0.0.1',5911)
    print '--'
    print type(a)
    print a
 

