import json
import logging

from ..cipher.Cipher import Cipher

logger = logging.getLogger(__name__)

class Serialize():

    def __init__(self):
        pass

    def serialize(self, content_obj):
        '''
        encode content_obj to string ,then encrypt the string.
        for example:
        content_obj = {'a':'apple','b':'banana'}
        encode to string, then encrypt it, return encrypted string.
        '''
        msg = json.dumps(content_obj)
        c = Cipher()
        cmsg = c.encrypt(msg)
        return cmsg

    def unserialize(self, content_str):
        '''
        decrypt the content_str, then decode it to json object, then renturn object.
        '''
        if len(content_str) % 16 != 0:
            logger.info('not 16 multi bytes.')
            return {}

        c = Cipher()
        msg = c.decrypt(content_str)
        try:
            obj = json.loads(msg)
        except:
            logger.info('json loads error')
            logger.info( ":".join(hex(ord(c)) for c in msg) )
            return {}
        return obj

if __name__ == '__main__':
    s = Serialize()
    a = {'a':'apple','b':'banana'}
    print a
    b = s.serialize(a)
    a = 'ddd'
    b = s.serialize(a)
    print b
    c = s.unserialize(b)
    print c
    b = json.dumps(a)
    print b
    b = '1234567887654321'
    c = s.unserialize(b)
    print c

    if {} == c:
        print 'null dict'
