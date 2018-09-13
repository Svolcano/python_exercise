#coding:utf-8

import threading
import multiprocessing
import requests
import time
import logging
import random
import time
import sys
import uuid
from lxml import etree

fm = "%(asctime)s-%(filename)s-%(threadName)s-%(funcName)s-%(levelname)s-%(lineno)d:\t%(message)s"
logging.basicConfig(filename='test_web.log',level=logging.INFO, format=fm)
logger = logging.getLogger()

class WEB(object):

    class_flag = "web"
    agent_list = [
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]

    def bd_get(self, tel=10086, proxy=None):
        process_name = multiprocessing.current_process().name
        content = ''
        url = f'http://www.baidu.com/s?wd={tel} 地址'
        try:
            query_header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "User-Agent":random.choice(WEB.agent_list),
            }
            query_cookie = {
            "BAIDUID": "%s:FG=1" % str(uuid.uuid4()).replace('-', '').upper(),
            "PSTM": "%s" % (int(time.time())),
            }
            resp = requests.get(url,
                                headers=query_header,
                                timeout=5,
                                proxies=proxy,
                                cookies=query_cookie
                                # verify=False,
                                )
            if resp.status_code == 200:
                content = resp.text
                content_name = f"./html/{process_name}-{tel}.html"
                encoding = resp.encoding
                with open(content_name, 'w', encoding=encoding) as wh:
                    wh.write(content)
            else:
                print('error')
        except Exception as e:
            print(e)

    def s60_get(self, formated_tel, proxy=None):
        content = ''
        find_url = ''
        url = f'https://www.so.com/s?q=7788'
        query_header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "User-Agent": random.choice(WEB.agent_list),
        }
        try:
            resp = requests.get(url,
                                headers=query_header,
                                timeout=5,
                                proxies=proxy,
                                # verify=False,
                                )
            if resp.status_code == 200:
                content = resp.text
                find_url=url
        except Exception as e:
            print(e)
        
        return content, find_url


def run(proxy=None, tel_header=''):
    # all_tel = ['0536-2081111', '0429-4447001', '0391-7291224', '0731-86240655', '023-68088882', '0769-82283187', '029-89581675', '025-58377516', '0371-27978107', '0411-88466794', '0372-2188521', '021-64191703', '0759-6633355', '0591-83621655', '0451-57753888', '0511-86857186', '0792-8906059', '0477-6213200', '010-56263335', '0576-87721558', '0558-2901266', '0512-62837080', '0576-88587778', '0934-6608777', '0760-85331222', '0519-87222787', '0797-6368368', '0431-88558689', '025-84930942', '0731-82764958', '0755-26900060', '0356-6866001', '0551-68821054', '021-61900502', '025-84896440', '0557-3053321', '0416-2199966', '0316-5994005', '0731-88938586', '0317-7105896', '0533-7691090', '0755-29651666', '0791-83812048', '0357-2317171', '0591-24377106', '0574-87935837', '0371-55605888', '0531-82767663', '0755-83561317', '028-89993808', '024-52673448', '0771-5552815', '0769-22184688', '0577-88628398', '021-61206688', '0359-5035510', '028-85754413', '0592-5738999', '0738-1558126', '0873-3045110', '0752-3277895', '0370-3133501', '0311-83862838', '0516-88258138', '010-85180966', '021-50801060', '0577-65766918', '0349-5028008', '0573-85851218', '029-84491889', '0769-83314860', '024-22837758', '0591-87270629', '0595-83050088', '0354-6762958', '010-89733256', '0473-8187549', '0511-88795242', '0755-27309102', '0871-67151788', '0379-65163888', '0791-85231988', '0391-3532315', '0519-88993351', '0527-80691042', '0372-5219088', '0372-8831238', '0755-84705888', '0510-85988888', '0355-5807720', '0371-23336631', '0512-86858999', '0370-2831898', '020-32223080', '029-88216989', '0371-58579109', '0755-82960345', '022-26980351', '021-62115900', '0755-89888888']
    all_tel = [f"{tel_header}%03d"%i for i in range(100) ]
    w = WEB()
    for t in all_tel:
        w.bd_get(t, proxy)

if __name__ =="__main__":
    proxy_list = [{"http":f"http://squidsz{i}.dianhua.cn:8080", "https":f"https://squidsz{i}.dianhua.cn:8080"} for i in range(61, 71)]
    proxy_num = len(proxy_list)
    thread_num = proxy_num * 10
    st = time.time()
    tel_header = ['023-680%02d'%i for i in range(thread_num)]
    # print(tel_header)
    t_list = [multiprocessing.Process(target=run, args=(proxy_list[i%proxy_num],tel_header[i])) for i in range(thread_num)]
    for t in t_list:
        t.start()

    for t in t_list:
        t.join()

    et = time.time()
    count = thread_num * 100
    cost = et-st
    print("thread_num: %d, total tps:%.3f, single tps:%.3f" % (thread_num, count/cost, 100/cost))
    

    
        

