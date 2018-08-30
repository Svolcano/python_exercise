import threading
import requests
import csv
import ujson
import queue

def load_data():
    fn = "aa.csv"
    res = []
    i = 0
    count = 100000
    tel_set = set()
    with open(fn, "r", encoding='utf8') as fh:
        cr = csv.reader(fh)
        for line in cr:
            tel = line[0].strip()
            tel_set.add(tel)
            res.append(tel)
            i+=1
            if i > count:
                break
    return res

api_url = 'http://apisi.dianhua.cn/resolvetel/?v=1&apikey=a9vXZcm5dnvimiNXyGNfLFwn37PdpyBB&uid=yulore_bqc&app=yulore_bqc&ver=1.0&tel=%s'


def get_one(q, oq):
    while True:
        tel = q.get()
        if tel == None:
            break
        resp = requests.get(api_url % tel)
        if resp.status_code == 200:
            a = resp.text
            ao = ujson.loads(a)
            oq.put((tel, ao.get('name', '')))
        else:
            oq.put((tel, ''))


def run(data):
    q_size = 20
    o_q = queue.Queue()
    q_list = [queue.Queue() for i in range(q_size)]
    t_list = [threading.Thread(target=get_one, args=(q, o_q)) for q in q_list]
    for t in t_list:
        t.start()

    i = 0
    for d in data:
        q_list[i].put(d)
        i = (i+1) % q_size

    for q in q_list:
        q.put(None)

    for t in t_list:
        t.join()
    all = []
    while True:
        try:
            res = o_q.get(block=False)
            all.append(f"{res[0]},{res[1]}")
        except Exception as e:
            break

    with open("m.csv", 'w', encoding='utf8') as wh:
        wh.write("\n".join(all))


if __name__ == "__main__":
    data = load_data()
    run(data)

