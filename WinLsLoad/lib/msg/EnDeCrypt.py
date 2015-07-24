import binascii
import pyaes
import logging
logger = logging.getLogger(__name__)
class EnDeCrypt():
    def __init__(self):
        self.key = '*MYJSYBJWQT:!@$*'
        
    def encrypt(self,s):
        try:
            aes = pyaes.AESModeOfOperationCTR(self.key)
            encrypted = aes.encrypt(s)
        except Exception,e:
            logger.error(e)
            return None
        return encrypted.encode('hex')
    
    def decrypt(self, s):
        try :
            ss = binascii.a2b_hex(s)
        except Exception,e:
            logger.error(e)
            return None

        try:
            aes = pyaes.AESModeOfOperationCTR(self.key)
            decrypted = aes.decrypt(ss)
        except Exception,e:
            logger.error(e)
            return None       
        return decrypted 
