import string
import random
import time


def gen_test_data():
    data_set = string.ascii_letters
    file_size = 1000
    with open("a.txt", 'w', encoding='utf-8') as wh:
        i = 0
        while i < file_size:
            wh.write("%s %d\n" % (random.choice(data_set), random.randint(1, 10)))
            i += 1
    with open("b.txt", 'w', encoding='utf-8') as wh:
        i = 0
        while i < file_size:
            wh.write("%s %d\n" % (random.choice(data_set), random.randint(1, 10)))
            i += 1


def sort_one(file_name, target):
    fh = open(file_name, 'r', encoding='utf-8')
    data = {

    }
    for l in fh:
        u, v = l.split(' ')
        c = data.get(u, 0)
        data[u] = c + int(v)

    fh.close()
    ret = sorted(data.items(), key=lambda item: -item[1])
    with open(target, 'w', encoding='utf-8') as wh:
        ss = '\n'.join(["%s %d" % (k, v) for k, v in ret])
        wh.write(ss)


def read_num(fh, num=5):
    ret = []
    c = 0
    while 1:
        try:
            l = fh.__next__()
            l = l.strip()
            u, v = l.split(' ')
            ret.append((u, int(v)))
            c += 1
            if c >= num:
                yield ret
                ret = []
                c = 0
        except Exception as e:
            break
    yield ret


def merge(pa, pb):
    len_c = {}
    pa.extend(pb)
    for u, v in pa:
        c = len_c.get(u, 0)
        len_c[u] = c + v

    return sorted(len_c.items(), key=lambda item: -item[1])


def merge2(a="sa.txt", b="sb.txt", target='c.txt'):
    fa = open(a, 'r')
    fb = open(b, 'r')
    ft = open(target, 'w')
    pa = read_num(fa, 20)
    pb = read_num(fb, 20)
    while 1:
        try:
            pad = pa.__next__()
        except Exception as e:
            pad = []
        try:
            pbd = pb.__next__()
        except Exception as e:
            pbd = []
        if not pad and not pbd:
            break
        mc = merge(pad, pbd)
        mcs = [str(kk) for kk in mc]
        ft.write('\n'.join(mcs))

    fa.close()
    fb.close()
    ft.close()


if __name__ == "__main__":
    merge2()
