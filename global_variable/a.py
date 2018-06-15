#import threading
import multiprocessing as threading
class G():

    a = 10

def h():
    print threading.current_process().name, G.a

if __name__ == "__main__":
    print G.a
    G.a = 200
    t_list = []
    for i in range(3):
        t = threading.Process(target=h, )
        t_list.append(t)
    
    for t in t_list:
        t.start()

    for t in t_list:
        t.join()

    print "done"
