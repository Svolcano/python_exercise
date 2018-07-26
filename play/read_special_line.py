import os



file_root_path = 'D:/pro_test_data'
file_name1 = 'dwa_d_ia_s_user_prod_0716.txt'


def readline(f, n):
    with open(f, 'r', encoding='utf8') as fh:
        while n:
            fh.__next__()
            n -= 1
        line = fh.__next__()
    return line


print(readline(1))