import json
import csv
import time
import requests
import queue
import threading

file_root_path = '.'
file_name1 = 'dwa_d_ia_s_user_prod_0716u8.txt.csv'
file_name2 = 'dwa_d_ia_s_user_prod_transcoded.txt.csv'

def time_it(fun):
    def inner_fun(*argc, **argv):
        st = time.time()
        ret = fun(*argc, **argv)
        et = time.time()
        print(f"{fun} cost {et-st}")
        return ret
    return inner_fun


def load_data(f1):
    ret = []
    file = f'{file_root_path}/{f1}'
    with open(file, 'r', encoding='utf8') as fh:
        csv_reader = csv.reader(fh)
        for line in csv_reader:
            if not line:
                continue
            ret.append(line)
    return ret

def writer(q, f1):
    wh = open(f"{file_root_path}/{f1}_tel.csv", 'w', encoding='utf8', newline='')
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
    retry = 10
    while retry:
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                ret = json.loads(resp.text)['telNum']
                ep.append(ret)
                if ret:
                    break
        except Exception as e:
            print(e)
        retry -= 1
    q.put(ep)
    


def main(q, f1):
    src_data = load_data(f1)
    print("len: %d" % len(src_data))
    c = 0
    t_list = []
    for e in src_data:
        c += 1
        print(c)
        t = threading.Thread(target=get_one,args=(e, q))
        t.start()
        t_list.append(t)
        while len(t_list) >= 10:
            time.sleep(1)
            t_list = [tt for tt in t_list if tt.is_alive()]

    while len(t_list):
        time.sleep(1)
        t_list = [tt for tt in t_list if tt.is_alive()]
    q.put(None)

@time_it
def deal(f1):
    q = queue.Queue()
    wt = threading.Thread(target=writer, args=(q, f1))
    wt.start()
    main(q, f1)
    wt.join()
    print('done')

if __name__ == '__main__':
    deal(file_name1)
    deal(file_name2)