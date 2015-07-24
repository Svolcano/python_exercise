import sys
import crypt,getpass
import os

def hashPassword(user, password):
    salt = '$6$%s$' %(user)
    return crypt.crypt(password, salt)

if __name__== '__main__': 
    if len(sys.argv)<3 :
        print 'Missing parameter'
        os._exit(0)
    username = sys.argv[1]
    password = sys.argv[2]
    print hashPassword(username,password)
    
