import pandas as pd
import csv
import collections
file_root_path = 'D:/pro_test_data/only_webengine'
file_name1 = 's.csv'
aa = 'aa.csv'

res = []
with open(f'{file_root_path}/{file_name1}', 'r', encoding='gbk') as fh:
    cr = csv.reader(fh)
    for i in cr:
        res.append((i[1], i[0]))
        
with open(f'{file_root_path}/{aa}', 'w', encoding='utf8', newline='') as fh:
    cr = csv.writer(fh)
    cr.writerows(res)