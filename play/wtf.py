import requests
import json
import csv

def t_bqc():
    tel = '05535312598'
    name = '安徽省芜湖鼎力电机有限公司'
    url = ("http://172.18.52.175:8000/v2/qualityname?"
    f"tel={tel}&third_party_api=1"
    f"&name={name}" 
    "&switch=1_2_3")
    print(url)  
    resp = requests.get(url)
    print(json.loads(resp.text))



t_bqc()



# url = "http://open.yscredit.com/api/request"
# params = dict([('uid', 'yulore'), ('api', 'A008'), ('args', '{"name":"安徽省芜湖鼎力电机有限公司"}'), ('sign', 'aecc9797a4ca009442c9d8f5952064cb')])

# a = requests.get(url, params)
# print(a.text)