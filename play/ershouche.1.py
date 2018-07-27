import pandas as pd
import csv
import collections
file_root_path = 'D:/pro_test_data'
file_name1 = 'dwa_d_ia_s_user_prod_0716.txt'
md5_tel_dict = 'md5_tel.txt'



class my_dialect(csv.excel):
    delimiter = ' '
    skipinitialspace = True
c = collections.Counter()
with open(f'{file_root_path}/{file_name1}', 'r', encoding='utf8') as fh:
    cr = csv.reader(fh, my_dialect)
    for i in cr:
        l = len(i)
        c[l] += 1
        
print(c)