from ftplib import FTP  
import os  
import sys  

class MyFTP(FTP): 
    '''
    break point continue sending
    ''' 
    def storbinary(self, cmd , fd,fsize=0,rest=0):
        blocksize=1048576
        cmpsize=rest
        conn = self.transfercmd(cmd, rest)
        buf = ''
        while 1:
            if rest==0:
                buf=fd.read(blocksize)
            else:
                fd.seek(cmpsize)
                buf=fd.read(blocksize)
            if buf != '':
                conn.send(buf)
            else:
                break
            cmpsize+=blocksize
        conn.close()
        fd.close()

if __name__ == '__main__':
    print "MyFtp testing!" 
