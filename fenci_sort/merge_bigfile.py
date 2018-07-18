import threading
import time
import time
import collections
import multiprocessing
import threading
import subprocess
import os
import queue

root_path = 'D:/pro_test_data/hyyzx/52'
src_file = 'all_name.txt'
dict_file = 'dictionary0716'


def time_it(fun):
    def inner(*argv, **argc):
        st = time.time()
        ret = fun(*argv, **argc)
        et = time.time()
        print(f"{fun} cost:{et-st}")
        return ret
    return inner


def fen_ci(input_str, short=2, long=5):
    results = []
    str_len = len(input_str)
    if not input_str:
        return results
    if long > str_len:
        long = str_len
    if str_len <= short:
        return [input_str]
    x = short
    while x <= long:
        for i in range(str_len + 1 - x):
            results.append(input_str[i:i + x])
        x += 1
    return results


def read_file(f, number=50000):
    with open(f, 'r', encoding='utf8') as fh:
        c = 0
        t_l = []
        for i in fh:
            c += 1
            t_l.append(i)
            if c == number:
                yield t_l
                c = 0
                t_l.clear()
        if t_l:
            yield t_l


@time_it
def got_region(dict_file=f'{root_path}/{dict_file}'):
    result = []
    sp = []
    with open(dict_file, 'r', encoding='utf8') as dh:
        all_lines = dh.readlines()
    for line in all_lines:
        n, a, t = line.strip().split(' ')
        if t == 'region':
            result.append(n)
        if t == 'type':
            sp.append(n)
    for k in sp:
        fc = fen_ci(k)
        result.extend(fc)
    result = set(result)
    return result

@time_it
def create_one_file(data, fid, filter_dict):
    fh = open(f"{root_path}/out_{fid}.txt", 'w', encoding='utf8')
    ct = collections.Counter()
    for d in data:
        d = d.strip()
        if not d:
            continue
        a = fen_ci(d)
        for ka in a:
            if ka in filter_dict:
                continue
            ct[ka] += 1
    all_ret = []
    for e in ct.most_common():
        k, n = e
        ret = f"{k.strip()}\t{n}\n"
        all_ret.append(ret)
    fh.writelines(all_ret)
    fh.close()


@time_it
def store_all_data(filter_dict):
    i = 0 
    t_list = []
    for a in read_file(f"{root_path}/{src_file}"):
        t = threading.Thread(target=create_one_file, args=(a, i, filter_dict))
        t.start()
        i += 1
        t_list.append(t)
        if len(t_list) >= 24:
            print('sleeping....')
            time.sleep(6)
            t_list = [t for t in t_list if t.is_alive()]
    while len(t_list):
        time.sleep(6)
        t_list = [t for t in t_list if t.is_alive()]
    return i
    
def inner_merge(fid_s, fid_e):
    k = fid_s
    f_list = []
    new_file = f"{root_path}/merge/merge_{fid_s}_{fid_e}.txt"
    wh = open(new_file, 'w', encoding='utf8')
    while k <= fid_e:
        f_name = f"{root_path}/out_{k}.txt"
        f_list.append(read_file(f_name, 500))
        k += 1
    ct = collections.Counter()
    while len(f_list):
        l = len(f_list)-1
        while l >= 0:
            f = f_list[l]
            try:
                data = f.__next__()
            except:
                f_list.remove(f)
                l -= 1
                continue
            for d in data:
                name, numb = d.split('\t')
                ct[name] += int(numb)
            l -= 1
        ret_str = []
        for e in ct.most_common():
            if e[1] <= 1:
                break
            ret_str.append(f"{e[0]}\t{e[1]}\n")
        wh.writelines(ret_str)
        ret_str.clear()
        ct.clear()
    wh.close()

@time_it
def merge(file_number=2780):
    cpu_number = 8
    flen = int(file_number/cpu_number)
    c = 0
    p_list = []
    for i in range(cpu_number):
        s = c
        e = c + flen
        if e>file_number:
            e = file_number
        p = multiprocessing.Process(target=inner_merge, args=(s,e))
        p.start()
        p_list.append(p)
        # if len(p_list) >= 8:
        #     time.sleep(20)
        #     p_plist = [pp for pp in p_list if pp.is_alive()]
        c += flen+1
    for p in p_list:
        p.join()


if __name__ == '__main__':
    # filter_dict = got_region()
    # file_number = store_all_data(filter_dict)
    # print(file_number)
    merge()
