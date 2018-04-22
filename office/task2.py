import time
import csv


def get_hmc(file_path):
    result = {}
    with open(file_path, 'r', newline='', encoding='utf8') as src_file:
        lines = csv.reader(src_file)
        try:
            for l in lines:
                sfz = l[2]
                gs = l[3]
                result[sfz] = gs
        except Exception as e:
            print(l)
            print(e)
    return result


def get_hyzj(file_path):
    result = {}
    with open(file_path, 'r', newline='', encoding='utf8') as src_file:
        lines = csv.reader(src_file)
        try:
            for l in lines:
                yhm = l[0]
                zj = l[1]
                result[yhm] = zj
        except Exception as e:
            print(l)
            print(e)
    return result


def mix_save(target_file_name, src_file, hmc, hyzj):
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
                sfz = row[9]
                row[10] = hmc.get(sfz, '')
                if yhm in hyzj:
                    row[11] = yhm
                else:
                    row[11] = ''
                row[12] = hyzj.get(yhm, '')
                target_writer.writerow(row)

if __name__ == "__main__":
    name_ph = {}
    st = time.time()
    hmc = get_hmc('hmc.csv')
    et1 = time.time()
    print("read1 cost : %.3f" % (et1-st))

    hyzj = get_hyzj('zj.csv')
    et1 = time.time()
    print("read1 cost : %.3f" % (et1 - st))
    mix_save("done.csv", 'hy.csv', hmc, hyzj)
    et2 = time.time()
    print("read2 cost : %.3f" % (et2 - et1))

