import json
import csv
import time
import requests
import queue
import threading

root_path = 'C:/Users/station/Desktop/aaa/'

def time_it(fun):
    def inner_fun(*argc, **argv):
        st = time.time()
        ret = fun(*argc, **argv)
        et = time.time()
        print(f"{fun} cost {et-st}")
        return ret
    return inner_fun


def load_data():
    ret = []
    file = f'{root_path}/a.txt'
    with open(file, 'r', encoding='utf8') as fh:
        csv_reader = csv.reader(fh)
        for line in csv_reader:
            if not line:
                continue
            ret.append(line)
    return ret

def writer(q):
    wh = open(f"{root_path}/out.txt", 'w', encoding='utf8')
    csv_writer = csv.writer(wh)
    while True:
        d = q.get()
        if d is None:
            break
        csv_writer.writerow(d)
    wh.close()



def get_one(ep, q):
    md5 = ep[0]
    url = "http://decrypt.dianhua.cn/decrypt/?apikey=yuloreInner&country=86&uid=yulore&app=decryptTel&ver=1.0&v=1&h=1&tel=%s" % md5
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            ret = json.loads(resp.text)['telNum']
            ep[0] = ret
    except Exception as e:
        print(e)
    q.put(ep)
    


def main(q):
    src_data = load_data()
    print("len: %d" % len(src_data))
    c = 0
    t_list = []
    for e in src_data:
        c += 1
        print(c)
        t = threading.Thread(target=get_one,args=(e, q))
        t.start()
        t_list.append(t)
        while len(t_list) >= 200:
            time.sleep(1)
            t_list = [tt for tt in t_list if tt.is_alive()]

    while len(t_list):
        time.sleep(1)
        t_list = [tt for tt in t_list if tt.is_alive()]
    q.put(None)

@time_it
def deal():
    q = queue.Queue()
    wt = threading.Thread(target=writer, args=(q,))
    wt.start()
    main(q)
    wt.join()
    print('done')

if __name__ == '__main__':
    deal()