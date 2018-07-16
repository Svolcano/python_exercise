import time
import asyncio
import collections
import multiprocessing
import threading
import queue
import locale

result_path = "D:/pro_test_data/hyyzx"


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
    assert fen_ci('   ') == ['  ','  ','   ']
    assert fen_ci('中国') == ['中国']
    assert fen_ci('中') == ['中']
    assert fen_ci('') == []
    assert fen_ci(' ') == [' ']
    assert fen_ci(' 中1') == [' 中', '中1', ' 中1']
    assert fen_ci('123456') == ['12', '23', '34', '45', '56', '123', '234', '345', '456', '1234', '2345', '3456', '12345', '23456']
    print("check pass")


def part_reader(fh, start, number=100000):
    c = collections.Counter()
    all_lines = []
    most_common_num = 20000
    for i in fh:
        fc = fen_ci(i)
        for e in fc:
            c[e]+=1
    c = (+c)

def test():
    st = time.time()
    file = f"{result_path}/all_name.txt"
    with open(file, 'r', encoding='utf8') as fh:
        a = fh.readlines()
    et = time.time()
    intv = et-st
    print(f"cost: {intv}")


def calc(fid):
    a_list = []
    with open(gen_file_name(fid), 'r', encoding='utf8') as fh:
        a_list = fh.readlines()
    result = []
    with open(f'{result_path}/data_{fid}_out.txt', 'w', encoding='utf8') as wh:
        for i in a_list:
            fc = fen_ci(i.strip())
            result.extend(fc)
        wh.write('\n'.join(result))

def write_fies(data_list, fn):
    with open(fn, 'w', encoding='utf8') as wh:
        wh.write(''.join(data_list))


def split_files(file_number):
    data_path = f"{result_path}/all_name.txt"
    st = time.time()
    all_lines = []
    with open(data_path, 'r', encoding='utf8') as fh:
        all_lines = fh.readlines()
    all_len = len(all_lines)
    p_list = []
    div_num = file_number
    part_len = int(all_len / div_num)
    left = all_len - part_len*div_num
    for i in range(div_num):
        t_list = all_lines[i*part_len:(i+1)*part_len]
        p = threading.Thread(target=write_fies, args=(t_list,gen_file_name(i)))
        p_list.append(p)
    if left > 0:
        t_list = all_lines[-left:]
        p = threading.Thread(target=write_fies, args=(t_list,div_num))
        p_list.append(p)
    for p in p_list:
        p.start()
    for p in p_list:
        p.join()
    et = time.time()
    print(f"total cost{et - st}")

def gen_file_name(fid):
    return f"{result_path}/data_{fid}.txt"

def calc_all_files(file_number):
    t_list = []
    for i in range(file_number):
        t = threading.Thread(target=calc, args=(i,))
        t_list.append(t)
    
    c = 0
    tm = []
    for t in t_list:
        if c != 8:
            c += 1
            t.start()
            tm.append(t)
        else:
            c = 0
            t.start()
            for t in tm:
                t.join()
            t.join()
            tm = []
    for t in tm:
        t.join()


def analysis_one(fid):
    print(fid)
    c = collections.Counter()
    with open(f"{result_path}/data_{fid}_out.txt", 'r', encoding='utf8') as fh:
        for e in fh:
            if e in c:
                c[e] += 1
            else:
                c[e] = 0
        with open(f"{result_path}/data_{fid}_analysis.txt", 'w', encoding='utf8') as wh:
            all_ret = []
            for e in c.most_common():
                k, n = e
                ret = f"{k.strip()}\t{n}\n"
                all_ret.append(ret)
            wh.writelines(all_ret)

def analysis_all(file_number):
    p_list = []
    for i in range(file_number):
        p = threading.Thread(target=analysis_one, args=(i,))
        p_list.append(p)
    c = 0
    pm = []
    for p in p_list:
        if c != 16:
            c += 1
            p.start()
            pm.append(p)
        else:
            c = 0
            p.start()
            for p in pm:
                p.join()
            pm = []
            p.join()
    for p in pm:
        p.join()



def merge_all(file_number, mid):
    fid = 0
    merge_all_file = f"{result_path}/merge_{mid}_all.txt" 
    max_c = collections.Counter()
    merge_fh = open(merge_all_file, 'w', encoding='utf8')
    while fid < file_number:
        print(fid)
        c = mid
        fh_list = []
        while c and fid< file_number:
            fn = f"{result_path}/data_{fid}_analysis.txt"
            t_fh = open(fn, 'r', encoding='utf8') 
            fh_list.append(t_fh)
            c -= 1
            fid += 1
        while True:
            try:
                for t_fh in fh_list:
                    line = t_fh.readline()
                    if not line:
                        t_fh.close()
                        fh_list.remove(t_fh)
                        continue
                    tn, tc = line.split('\t')
                    tc = int(tc)
                    if tn in max_c:
                        max_c[tn] += tc
                    else:
                        max_c[tn] = tc
                    if len(max_c) == 3000:
                        ret_str = []
                        for e in max_c.most_common():
                            ret_str.append(f"{e[0]}\t{e[1]}\n")
                        merge_fh.writelines(ret_str)
                        merge_fh.flush()
                        max_c.clear()  
                if not fh_list:
                    break
            except Exception as e:
                print(e, line, t_fh)
                return 
        if len(max_c):
            ret_str = []
            for e in max_c.most_common():
                ret_str.append(f"{e[0]}\t{e[1]}\n")
            merge_fh.writelines(ret_str)
            max_c.clear()
    merge_fh.close()


def check_file(fid):
    with open(f"{result_path}/data_{fid}_analysis.txt", 'r', encoding='utf8') as fh:
        while True:
            line = fh.readline()
            if not line:
                break
            tn, tc = line.split('\t')
            print(tn, tc)

def got_region(dict_file='D:/python_practise/python_exercise/fenci_sort/dictionary0716'):
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
    result = list(set(result))
    return result


def filter(file=f"{result_path}/merge_10_all.txt" ):
    filter_dict = got_region()
    tar_fn = f"{result_path}/merge_10_all_no_region_compy.txt" 
    ret_fh = open(tar_fn, 'w', encoding='utf8')
    with open(file, 'r', encoding='utf8') as sh:
        ret_l = []
        for line in sh:
            name , c = line.split('\t')
            c = int(c)
            if '有限' in name or "公司" in name:
                continue
            if name in filter_dict:
                continue
            if c == 0:
                break
            ret_l.append(f"{name}\t{c}\n")
            if len(ret_l) == 5000:
                ret_fh.writelines(ret_l)
                ret_l.clear()
    if len(ret_l):
        ret_fh.writelines(ret_l)
        ret_l.clear()
    ret_fh.close()


if __name__ == '__main__':
    #merge_all(601, 10)
    filter()
    #got_region()

    