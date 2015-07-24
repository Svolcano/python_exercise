import pycurl
import StringIO
import urllib
import logging

from lib.msg.RawSerialize import RawSerialize

from openam import authenticate
from openam import logout
from openam import change_password

logger = logging.getLogger(__name__)

def verify_passwd(user, password, ip, port):
    user     = user.encode('ascii','ignore')
    password = password.encode('ascii','ignore')
    realm_sep = '.'
    if realm_sep not in user:
        realm = "local"
    else:
        users = user.split(realm_sep)
        realm = users[0]
        users = users[1:]
        user  = realm_sep.join(users)
    cont = authenticate(user, password, ip, port, realm)
    print cont
    #print user,password
    if 'tokenId' in cont:
        raws = RawSerialize()
        obj = raws.unserialize(cont)
        tokenid = obj['tokenId']
        tokenid = tokenid.encode('ascii', 'ignore')
        cont = logout(tokenid, ip, port, realm)
        print cont
        return (True,'')

    if   'Invalid Password' in cont:
        return (False,'InvalidPassword')
    elif 'Authentication Failed' in cont:
        return (False,'InvalidCredentials')
    else:
        return (False,'Invalid')

def change_passwd(user, oldpassword, newpassword, ip, port):
    user        = user.encode('ascii','ignore')
    realm_sep = '.'
    if realm_sep not in user:
        realm = "local"
    else:
        users = user.split(realm_sep)
        realm = users[0]
        users = users[1:]
        user  = realm_sep.join(users)

    oldpassword = oldpassword.encode('ascii','ignore')
    newpassword = newpassword.encode('ascii','ignore')
    cont = authenticate(user, oldpassword, ip, port, realm)
    print cont
    if 'tokenId' in cont:
        raws = RawSerialize()
        obj = raws.unserialize(cont)
        tokenid = obj['tokenId']
        tokenid = tokenid.encode('ascii', 'ignore')
        cont = change_password(tokenid, user, oldpassword, newpassword, ip, port,realm)
        print cont
        cont_logout = logout(tokenid, ip, port, realm)
        print cont_logout
        if '{}' == cont:
            return (True,"")

        obj = raws.unserialize(cont)
        return (False,obj['message'])

    raws = RawSerialize()
    obj = raws.unserialize(cont)
    return (False,obj['message'])
 

