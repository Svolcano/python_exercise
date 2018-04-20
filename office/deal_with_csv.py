import time
import csv


def get_name_phone(file_path):
    result = {}
    with open(file_path, 'r', newline='', encoding='utf8') as src_file:
        lines = csv.reader(src_file)
        try:
            for l in lines:
                name = l[1]
                ph = l[4]
                result[name] = ph
        except Exception as e:
            print(l)
            print(e)
    return result


def mix_save(target_file_name, src_file, name_phone):
    with open(target_file_name, 'w', newline='', encoding='utf8') as tf:
        target_writer = csv.writer(tf)
        with open(src_file, 'r', newline='', encoding='utf8') as src_f:
            src_reader = csv.reader(src_f)
            title = True
            for row in src_reader:
                if not title:
                    name = row[1]
                    ph = name_phone.get(name, '-1')
                    row.append(ph)
                else:
                    row.append('手机号')
                    title = False
                target_writer.writerow(row)





if __name__ == "__main__":
    name_ph = {}
    st = time.time()
    name_ph = get_name_phone('截至4月17日8点会员数据.csv')
    et1 = time.time()
    print("read1 cost : %.3f" % (et1-st))
    mix_save("done.csv", '截至4月17日8点会员数据.csv', name_ph)
    et2 = time.time()
    print("read2 cost : %.3f" % (et2 - et1))

