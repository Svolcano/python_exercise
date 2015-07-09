bin/python
#coding=utf-8
import time
from os import system
def shutdownSystem():
    runing = True
    while runing:
        input = raw_input('shutdown(s)reboot(r)?quit(q)')
        input = input.lower()
        if input == 'q' or input == 'quit':
            runing = False
            print 'byebye'
            break
        seconds = int(raw_input('aftime what seconds excute your command'))
        if seconds < 0:
            seconds = 0
        time.sleep(seconds)
        print 'pause time is :%d'%seconds

        runing = False
        if input == 's' or input =='shutdown':
            print 'shutdowning....'
            system('halt')
        elif input == 'r' or input == 'reboot':
            print 'rebooting....'
            system('reboot')
        else:
            print 'invalid command!'
            runing = True
    print 'Over!'

if __name__ == '__main__':
    shutdownSystem()
      
