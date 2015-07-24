import pycurl
import StringIO
import urllib
import logging

from lib.msg.RawSerialize import RawSerialize

logger = logging.getLogger(__name__)

def authenticate(user, password, ip, port, realm=""):
    c = pycurl.Curl()
    content = StringIO.StringIO()
    if "" == realm:
        url = 'http://%s:%s/openam/json/authenticate' % (ip, port)
    else:
        url = 'http://%s:%s/openam/json/%s/authenticate' % (ip, port, realm)
    post_data_dict = {}
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, urllib.urlencode(post_data_dict) )
    c.setopt(pycurl.HTTPHEADER,['X-OpenAM-Username: %s'%user.encode('ascii','ignore'),'X-OpenAM-Password: %s'%password,'Content-Type: application/json'])
    c.setopt(pycurl.WRITEFUNCTION, content.write)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(pycurl.TIMEOUT, 30)
    ret = ""
    try:
        ret = c.perform()
    except Exception,e:
        logger.info(e)
        c.close()
        return ""

    c.close()
    cont = content.getvalue()
    return cont

def logout(tokenid, ip, port, realm=""):
    c = pycurl.Curl()
    content = StringIO.StringIO()
    if "" == realm:
        url = 'http://%s:%s/openam/json/sessions/?_action=logout' % (ip, port)
    else:
        url = 'http://%s:%s/openam/json/%s/sessions/?_action=logout' % (ip, port, realm)
    post_data_dict = {}
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, urllib.urlencode(post_data_dict) )
    c.setopt(pycurl.HTTPHEADER,['iplanetDirectoryPro: %s'%tokenid,'Content-Type: application/json'])
    c.setopt(pycurl.WRITEFUNCTION, content.write)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(pycurl.TIMEOUT, 30)
    ret = ""
    try:
        ret = c.perform()
    except Exception,e:
        logger.info(e)
        c.close()
        return ""

    c.close()
    cont = content.getvalue()
    return cont

def get_user_list(tokenid, ip, port, realm=""):
    c = pycurl.Curl()
    content = StringIO.StringIO()
    if "" == realm:
        url = 'http://%s:%s/openam/json/users?_queryID=*' % (ip, port)
    else:
        url = 'http://%s:%s/openam/json/%s/users?_queryID=*' % (ip, port, realm)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.POST, 0)
    c.setopt(pycurl.HTTPHEADER,['iplanetDirectoryPro: %s'%tokenid,'Content-Type: application/json'])
    c.setopt(pycurl.WRITEFUNCTION, content.write)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(pycurl.TIMEOUT, 30)
    ret = ""
    try:
        ret = c.perform()
    except Exception,e:
        logger.info(e)
        c.close()
        return ""

    c.close()
    cont = content.getvalue()
    return cont

def change_password(tokenid, user, oldpasswd, newpasswd, ip, port, realm=""):
    user        = user.encode('ascii','ignore')
    oldpasswd   = oldpasswd.encode('ascii','ignore')
    newpasswd   = newpasswd.encode('ascii','ignore')

    c = pycurl.Curl()
    content = StringIO.StringIO()
    if "" == realm:
        url = 'http://%s:%s/openam/json/users/%s?_action=changePassword' % (ip, port, user)
    else:
        url = 'http://%s:%s/openam/json/%s/users/%s?_action=changePassword' % (ip, port, realm, user)

    post_data_dict = {"currentpassword":oldpasswd,"userpassword":newpasswd}
    raws = RawSerialize()
    post_data_dict = raws.serialize(post_data_dict)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, post_data_dict )
    c.setopt(pycurl.HTTPHEADER,['iplanetDirectoryPro: %s'%tokenid,'Content-Type: application/json'])
    c.setopt(pycurl.WRITEFUNCTION, content.write)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(pycurl.TIMEOUT, 30)
    ret = ""
    try:
        ret = c.perform()
    except Exception,e:
        logger.info(e)
        c.close()
        return ""

    c.close()
    cont = content.getvalue()
    return cont


