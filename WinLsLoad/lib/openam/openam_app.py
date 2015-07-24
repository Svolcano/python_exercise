import pycurl
import StringIO
import urllib
import logging

from lib.msg.RawSerialize import RawSerialize

from openam import authenticate
from openam import logout
from openam import change_password
from openam import get_user_list

logger = logging.getLogger(__name__)

def get_realm_user_list(realm, ip, port):
    err = False
    ret = []
    cont = authenticate('amAdmin', 'zx123456', ip, port)
    logger.info("authenticate:%s", cont)
    if 'tokenId' in cont:
        raws = RawSerialize()
        obj = raws.unserialize(cont)
        tokenid = obj['tokenId']
        tokenid = tokenid.encode('ascii', 'ignore')
        cont = get_user_list(tokenid, ip, port, realm)
        logger.info("realm:%s,get_user_list:%s", realm, cont)
        obj  = raws.unserialize(cont)
        if 'result' in obj:
            ret  = obj['result']
            err  = True
        cont = logout(tokenid, ip, port)
        logger.info("logout:%s", cont)

    return (err,ret)


