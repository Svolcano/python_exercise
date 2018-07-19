import threading
import datetime

class A(object):

    def __init__(self):
        pass



    def do_some_work(self):
        print (datetime.datetime.now())

a = A()

t = threading.Timer(3, a.do_some_work)
t.start()
print("main threading gone!")
