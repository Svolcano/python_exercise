#coding=utf-8
import time
from os import system
def shutdownSystem():
    runing = True
    while runing:
        input_cmd = input('shutdown(s)reboot(r)?quit(q)')
        input_cmd = input_cmd.lower()
        if input_cmd == 'q' or input_cmd == 'quit':
            runing = False
            print ('byebye')
            break
        seconds = int(input('aftime what seconds excute your command'))
        if seconds < 0:
            seconds = 0
        time.sleep(seconds)
        print ('pause time is :%d'%seconds)

        runing = False
        if input_cmd == 's' or input_cmd =='shutdown':
            print ('shutdowning....')
            system('halt')
        elif input_cmd == 'r' or input_cmd == 'reboot':
            print ('rebooting....')
            system('reboot')
        else:
            print ('invalid command!')
            runing = True
    print ('Over!')
if __name__ == '__main__':
    shutdownSystem()
      
