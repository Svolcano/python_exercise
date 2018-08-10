
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import time
import collections
import multiprocessing
import threading
import subprocess
import os
import queue


result_path = "/home/data/vvv/"


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


def check():
    print("start check")
    assert fen_ci('人民共和国') == ['人民', '民共', '共和', '和国', '人民共', '民共和', '共和国', '人民共和', '民共和国', '人民共和国']
    assert fen_ci('   ') == ['  ', '  ', '   ']
    assert fen_ci('中国') == ['中国']
    assert fen_ci('中') == ['中']
    assert fen_ci('') == []
    assert fen_ci(' ') == [' ']
    assert fen_ci(' 中1') == [' 中', '中1', ' 中1']
    assert fen_ci('123456') == ['12', '23', '34', '45', '56', '123', '234', '345', '456', '1234', '2345', '3456',
                                '12345', '23456']
    print("check pass")

@time_it
def calc(fid, filter_dict):
    with open(gen_file_name(fid), 'r', encoding='utf8') as fh:
        a_list = fh.readlines()
    c = collections.Counter()
    with open(f'{result_path}/data_{fid}_out.txt', 'w', encoding='utf8') as wh:
        fen_ci_all = []
        ccc = 0
        for i in a_list:
            print(ccc)
            ccc += 1
            fc = fen_ci(i.strip())
            fen_ci_all.extend(fc)
        print("fen_ci done!")
        for f in fen_ci_all:
            # if '有限' in f or "公司" in f:
            #     continue
            # if f in filter_dict:
            #     continue
            if f in c:
                c[f] += 1
            else:
                c[f] = 0
        print("collect done!")
        all_ret = []
        for e in c.most_common():
            k, n = e
            ret = f"{k.strip()}\t{n}\n"
            all_ret.append(ret)
        wh.writelines(all_ret)

@time_it
def split_files(file_len=50000):
    data_path = f"{result_path}/all_name.txt"
    cmd = f'split -l {file_len} {data_path} -d -a 4 --additional-suffix=.txt {result_path}/split_files/data_'
    ret, output = subprocess.getstatusoutput(cmd)
    print(ret, output)
    print(f"total cost{et - st}")
    rename_them_all()


def gen_file_name(fid):
    return f"{result_path}/split_files/data_{fid}.txt"

@time_it
def rename_them_all():
    i = 0
    root_dir = f"{result_path}/split_files"
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            os.rename(os.path.join(root_dir, f), os.path.join(root_dir, f"data_{i}.txt"))
            i += 1

@time_it
def calc_all_files(file_number, filter_dict):
    t_list = []
    i = 2650
    while i < file_number:
        t = multiprocessing.Process(target=calc, args=(i, filter_dict))
        t.start()
        t_list.append(t)
        if len(t_list) >= 8:
            time.sleep(10)
            t_list = [tt for tt in t_list if tt.is_alive()]
        i += 1

    while len(t_list):
        time.sleep(10)
        t_list = [tt for tt in t_list if tt.is_alive()]
        print('sleep.... len:%d' % len(t_list))

@time_it
def analysis(file_number, filter_dict):
    @time_it
    def _ana_one(f, fid):
        with open(f, 'r', encoding='utf8') as fh:
            ret_list = []
            for line in fh:
                name, number = line.split('\t')
                if name in filter_dict:
                    continue
                ret_list.append(line)
            print("1 done")
            with open(f"{result_path}/data_{fid}_analysis.txt", 'w', encoding='utf8') as wh:
                wh.writelines(ret_list)
    t_list = []
    i = 1902
    while i < file_number:
        file_name = f"{result_path}/data_{i}_out.txt"
        t = multiprocessing.Process(target=_ana_one, args=(file_name, i))
        t.start()
        t_list.append(t)
        if len(t_list) >= 16:
            time.sleep(5)
            t_list = [ttt for ttt in t_list if ttt.is_alive()]
        i += 1
    while len(t_list):
        time.sleep(5)
        t_list = [ttt for ttt in t_list if ttt.is_alive()]
    print('done!')


def read_file(f, number=30000):
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
def merge_two(f1, f2, merge_new):
    print(f1, f2)
    max_c = {}
    gen_f1 = read_file(f1)
    gen_f2 = read_file(f2)
    f1_done = False
    f2_done = False
    wh = open(merge_new, 'w', encoding='utf8')
    while True:
        try:
            f1_part = next(gen_f1)
        except:
            f1_part = []
            f1_done = True
        try:
            f2_part = next(gen_f2)
        except:
            f2_part = []
            f2_done = True
        f1_part.extend(f2_part)
        for line in f1_part:
            try:
                tn, tc = line.split('\t')
            except:
                continue
            tc = int(tc)
            if tn in max_c:
                max_c[tn] += tc
            max_c[tn] = tc
        ret_str = []
        for e in max_c.items():
            ret_str.append(f"{e[0]}\t{e[1]}\n")
        wh.writelines(ret_str)
        max_c.clear()
        if f1_done and f2_done:
            break
    wh.close()
    os.system(f'rm -f {f2} {f1}')

@time_it
def merge_all():
    all_ana_list = []
    for file in os.listdir(result_path):
        t_p = f"{result_path}/{file}"
        if os.path.isfile(t_p):
            all_ana_list.append(t_p)
    all_len = len(all_ana_list)
    if all_len == 1:
        return
    p_list = []
    i = 0
    while i < all_len:
        fn = all_ana_list[i]
        i += 1
        if i >= all_len:
            break
        fn2 = all_ana_list[i]
        i += 1
        p = multiprocessing.Process(target=merge_two, args=(fn, fn2, f"{result_path}/mergej_{i}_data.txt"))
        p.start()
        p_list.append(p)
        p_l = len(p_list)
        if p_l >= 8:
            while len(p_list):
                time.sleep(5)
                p_list = [pp for pp in p_list if pp.is_alive()]
    if len(p_list):
        while len(p_list):
            time.sleep(2)
            p_list = [pp for pp in p_list if pp.is_alive()]
@time_it
def got_region(dict_file='/home/data/dictionary0716'):
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
    fh = open(f"{result_path}/out_{fid}.txt", 'w', encoding='utf8')
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
def store_all_data(filter_dict, file_len=50000):
    es = Elasticsearch('172.18.52.176')
    query = {"query": {"match_all": {}}}
    scanResp = helpers.scan(client=es, query=query, scroll="10m", timeout="10m")
    all_name_set = set()
    i = 0
    t_list = []
    for resp in scanResp:
        source = resp['_source']
        name = source.get('name', '')
        if not name:
            continue
        all_name_set.add(name + "\n")
        l = len(all_name_set)
        print("set len: %d" % l)
        if l == file_len:
            t = threading.Thread(target=create_one_file, args=(list(all_name_set), i, filter_dict))
            t.start()
            i += 1
            t_list.append(t)
            if len(t_list) >= 24:
                print('sleeping....')
                time.sleep(6)
                t_list = [t for t in t_list if t.is_alive()]
            all_name_set.clear()
    if len(all_name_set):
        i+=1
        t = threading.Thread(target=create_one_file, args=(list(all_name_set), i))
        t.start()
        t_list.append(t)
    while len(t_list):
        time.sleep(6)
        t_list = [t for t in t_list if t.is_alive()]
    return i

if __name__ == '__main__':
    filter_dict = got_region()
    file_number = store_all_data(filter_dict)


