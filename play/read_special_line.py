import os
import time



file_root_path = 'D:/pro_test_data'
file_name1 = 'dwa_d_ia_s_user_prod_0716.txt'


def readline(f, n):
    with open(f, 'r', encoding='utf8') as fh:
        while n >= 1:
            line = fh.__next__()
            n -= 1
    return line


def readline_v2(f, ns):
    f.seek(0)   
    line = ''
    k = []
    for i, l in enumerate(fh):
        if i == n-1:
            line = l
            break
    return line


def tt(f, n):
    st = time.time()
    l = (readline_v2(f, n))
    et = time.time()
    return n, et-st, l

if __name__ == '__main__':
    f = f"{file_root_path}/{file_name1}"
    fh = open(f, 'r', encoding='utf8')
    for k in range(1, 9000000, 100000):
        print(tt(fh, k))
    fh.close()