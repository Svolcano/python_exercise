import json
import logging

logger = logging.getLogger(__name__)

class RawSerialize():

    def __init__(self):
        pass

    def serialize(self, content_obj):
        '''
        encode content_obj to string.
        for example:
        content_obj = {'a':'apple','b':'banana'}
        encode to string, return the string.
        '''
        msg = json.dumps(content_obj,ensure_ascii=False)
        return msg

    def unserialize(self, content_str):
        '''
        decode it to json object, then renturn object.
        '''
        msg = content_str
        try:
            obj = json.loads(msg)
        except Exception, e:
            logger.info(e)
            obj = {}
        return obj

if __name__ == '__main__':
    s = RawSerialize()
    a = {'a':'apple','b':'banana'}
    print a
    b = s.serialize(a)
    print b
    c = s.unserialize(b)
    print c

