import logging

from Crypto.Cipher import AES

logger = logging.getLogger(__name__)

class Cipher:
    '''
    encrypt data with AES, decrypt data with AES.
    '''
    def __init__(self):
        self.obj = AES.new('abcdefgh12345678',AES.MODE_ECB)

    def encrypt(self,data):
        '''
        encrypt data with AES, ECB mode, key is abcdefgh12345678.
        padding with space to make data length multiple of 16 bytes.
        '''
        len_data = len(data)
        if len_data % 16 != 0:
            data = data + (16-(len_data%16))*' '
        return self.obj.encrypt(data)

    def decrypt(self,data):
        '''
        decrypt data with AES.
        '''
        try:
            ddata = self.obj.decrypt(data)
        except Exception,e:
            logger.info(e)
            logger.info("decrypt data(hex):%s",data.encode("hex"))
            return ""

        return ddata

