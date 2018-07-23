import requests
import json
import csv


def get_region(tel):

    url =('http://apisi.dianhua.cn/resolvetel/?v=1&'
    f'apikey=a9vXZcm5dnvimiNXyGNfLFwn37PdpyBB&uid=yulore_bqc&app=yulore_bqc&ver=1.0&tel={tel}')
    print(url)
    res = requests.get(url)
    obj = json.loads(res.text)
    print(obj.get('telloc', None))


def get_region_one(url):
    res = requests.get(url)
    obj = json.loads(res.text)
    print(obj, obj.get('telloc', None))

# with open('ori_src.csv', 'r', encoding='utf8') as fh:
#     csv_r = csv.reader(fh)
#     for line in csv_r:
#         tel = line[0]
#         try:
#             get_region(tel)
#         except Exception as e:
#             print(e, tel)

url = 'http://apisi.dianhua.cn/resolvetel/?v=1&apikey=a9vXZcm5dnvimiNXyGNfLFwn37PdpyBB&uid=yulore_bqc&app=yulore_bqc&ver=1.0&tel=07303326021'
#url = 'http://apisi.dianhua.cn/resolvetel/?v=1&apikey=a9vXZcm5dnvimiNXyGNfLFwn37PdpyBB&uid=yulore_bqc&app=yulore_bqc&ver=1.0&tel=07305641421'
get_region_one(url)
