from global_module import GG
import random
import time
import threading
l = threading.Lock()
def r():

    st = random.randint(1,5)
    time.sleep(st)
    print("%s-->" % threading.current_thread().name, GG.global_a)
    if l.acquire():
        for i in range(10000):
            GG.global_a += 1
        l.release()

    print("%s-->" % threading.current_thread().name, st, GG.global_a)

t_list = []
for  i in range(10):
    name = "thread : %d" % i
    t1 = threading.Thread(target=r, name=name)
    t1.start()
    t_list.append(t1)

for t in t_list:
    t.join()

print("main->", GG.global_a)
print ('Game over!')





