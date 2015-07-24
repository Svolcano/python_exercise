import logging
import httplib

from ..msg.Serialize import Serialize

logger = logging.getLogger(__name__)

class req_basic:
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
        pass

    def request(self, hostname, obj):
        '''
        request zonelist.
        Args:
            hostname:hostname
            obj:jason object
        Return:
            ok response
            auth-fail response
            dabase error response
            no record response
            hostname-error response
        '''
        s       = Serialize()
        
        url     = 'http://%s:11900' % hostname
        logger.info("send %s:%s",url, obj)
        str_msg = s.serialize(obj)

        try:
            conn = httplib.HTTPSConnection(hostname, '11900', timeout=60)
            conn.request("POST", "/", str_msg)
            response = conn.getresponse()
        except Exception,e:
            logger.error(e)
            return None

        logger.info("urllib2.urlopen pass.")

        try:
            data = response.read()
        except Exception,e:
            logger.error(e)
            return None

        response_req = s.unserialize(data)
        logger.info("recv:%s", response_req)
 
        return response_req        


