import logging
import pam 

logger = logging.getLogger(__name__)

def local_verify_passwd(user, password):
    p = pam.pam()
    ret = p.authenticate(user.encode('utf-8'), password.encode('utf-8') )
    reason = p.reason
    return (ret,reason)

if __name__ == '__main__':
    print local_verify_passwd('user1','1')
    print local_verify_passwd('user1','2')
    print local_verify_passwd('test2','1')


