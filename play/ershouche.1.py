import requests
import ujson
import csv
import threading
import time
import os
import asyncio
import aiohttp
import queue

#file_root_path = '/home/data/'
file_root_path = 'D:/pro_test_data'
file_name1 = 'dwa_d_ia_s_user_prod_0716.txt'
file_name2 = 'dwa_d_ia_s_user_prod_transcoded.txt'
md5_tel_dict = 'md5_tel.txt'


def produce(f):
    with open(f, 'r', encoding='utf8') as fh:
        for l in fh:
            l = l.strip()
            if not l:
                continue
            yield  l
            
def deal_line(line):
    print(line)
    lt = line.split(' ')
    lt = [a for a in lt if a]
    lt[0] = lt[0].lower()
    return lt


def consumer(src_file, dest_file):

    gg = produce(src_file)
    gg.send(None)
    while 1:
        data = gg.send(1)
        ret = deal_line(data)

def deal_with_file1(f=file_name1):
    file_path = f"{file_root_path}/{f}"
    out_file_path = file_path + '.out'
    consumer(file_path, out_file_path)



def ssort():
    st = time.time()
    deal_with_file1()
    et = time.time()
    print("merge done", et - st)





if __name__ == "__main__":
    ssort()

