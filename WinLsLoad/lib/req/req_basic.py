import logging
import urllib2

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
        #logger.info("send %s:%s",url, obj)
        str_msg = s.serialize(obj)

        try:
            req = urllib2.Request(url,str_msg)
            response = urllib2.urlopen(req,timeout=60)
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


