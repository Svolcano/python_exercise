

key_list = ["二手车", "人人车", '好车无忧', '我卖我车网']


file_root_path = 'D:/pro_test_data'
file_name1 = 'dwa_d_ia_s_user_prod_0716.txt'
file_name2 = 'dwa_d_ia_s_user_prod_transcoded.txt'


def save_files(data, file_name):
    with open(file_name, 'w', encoding='utf8') as wh:
        for d in data:
            wh.write(f"{d[0]},{d[1]}\n")


def deal_with_file1():
    file_path = f"{file_root_path}/{file_name1}"
    calc_list = []
    with open(file_path, 'r', encoding='utf8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            lt = line.split(' ')
            lt = [a for a in lt if a]
            try:
                md5 = lt[0].lower()
                name = lt[1]
            except  Exception as e:
                print(e, line)
                continue
            for key in key_list:
                if key in name:
                    calc_list.append((md5, name))
    save_files(calc_list, f"{file_root_path}/{file_name1}.csv")


def deal_with_file2():
    file_path = f"{file_root_path}/{file_name2}"
    calc_list = []
    with open(file_path, 'r', encoding='utf8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            lt = line.split(' ')
            lt = [a for a in lt if a]
            try:
                md5 = lt[0].lower()
                name = lt[2]
            except  Exception as e:
                print(e, lt)
                continue
            for key in key_list:
                if key in name:
                    calc_list.append((md5, name))
    save_files(calc_list, f"{file_root_path}/{file_name2}.csv")

if __name__ == "__main__":
    file_lsit = ['dwa_d_ia_s_user_prod_0716.txt', 'dwa_d_ia_s_user_prod_transcoded.txt']
    c = set()
    for f in file_lsit:
        with open(f, 'r', encoding='utf8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                md5 = line.split(' ')[0]
                c.add(md5)
        print(f, len(c))
    c = list(c)
    with open("out.txt", 'w')  as wh:
        for i in c:
            wh.write(i+"\n") 