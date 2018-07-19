import time
import csv


def get_hmc(file_path):
    result = {}
    with open(file_path, 'r', newline='', encoding='utf8') as src_file:
        lines = csv.reader(src_file)
        try:
            for l in lines:
                sfz = l[3]
                gs = l[4]
                result[sfz] = gs
        except Exception as e:
            print(l)
            print(e)
    return result


def get_tzyh(file_path):
    result = {}
    with open(file_path, 'r', newline='', encoding='utf8') as src_file:
        lines = csv.reader(src_file)
        try:
            for l in lines:
                result[l[1]] = l[1]
        except Exception as e:
            print(l)
            print(e)
    return result


def get_hygl(file_path):
    result = {}
    with open(file_path, 'r', newline='', encoding='utf8') as src_file:
        lines = csv.reader(src_file)
        try:
            for l in lines:
                yhm = l[2]
                zcly = l[4]
                result[yhm] = zcly
        except Exception as e:
            print(l)
            print(e)
    return result


def mix_save(target_file_name, src_file, hmc, tzyh, hygl):
    with open(target_file_name, 'w', newline='', encoding='utf8') as tf:
        target_writer = csv.writer(tf)
        with open(src_file, 'r', newline='', encoding='utf8') as src_f:
            src_reader = csv.reader(src_f)
            first_line = True
            for row in src_reader:
                if first_line:
                    first_line = False
                    target_writer.writerow(row)
                    continue
                yhm = row[1]
                sfz = row[13]
                row[14] = hmc.get(sfz, '')
                row[2] = tzyh.get(yhm, '')
                row[3] = hygl.get(yhm, '')
                target_writer.writerow(row)

if __name__ == "__main__":
    hmc = "/home/scw/10.1-12.31/花名册0410.csv"
    tzyh = "/home/scw/10.1-12.31/投资用户（截至4.23）.csv"
    hygl = "/home/scw/10.1-12.31/会员管理注册来源数据总.csv"
    smyh = "/home/scw/10.1-12.31/10.1-12.31实名用户.csv"
    name_ph = {}
    st = time.time()
    hmc = get_hmc(hmc)
    et1 = time.time()
    print("read1 cost : %.3f" % (et1-st))

    tzyh = get_tzyh(tzyh)
    et1 = time.time()
    print("read1 cost : %.3f" % (et1 - st))

    hygl = get_hygl(hygl)
    et1 = time.time()
    print("read1 cost : %.3f" % (et1 - st))
    mix_save("done.csv", smyh, hmc, tzyh, hygl)
    et2 = time.time()
    print("read2 cost : %.3f" % (et2 - et1))

