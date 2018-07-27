import requests
import json
import csv

def t_bqc():
    tel = '089866836608'
    name = '海口市菜篮子运营公司'
    url = ("http://172.18.19.152:8000/v2/qualityname?"
    f"tel={tel}&third_party_api=1"
    f"&name={name}"
    "&switch=_1_2_3 ")
    print(url)
    resp = requests.get(url)
    print(json.loads(resp.text))

def format_file():
    root = 'D:/pro_test_data/yx/'
    in_f = 'src.txt'
    o_f = 'aa.csv'
    aa = []
    with open(f'{root}{in_f}', "r", encoding='utf8' ) as fh:
        fh.__next__()
        cr = csv.reader(fh)
        for l in cr:
            aa.append((l[0].strip(), l[1].strip()))
    
    with open(f"{root}{o_f}", 'w', encoding='utf8', newline='') as wh:
        cw = csv.writer(wh)
        cw.writerows(aa)


format_file()