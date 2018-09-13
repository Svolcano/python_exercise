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
import asyncio
import aiohttp


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
        content = ''
        url = f'http://www.baidu.com/s?wd={tel} 地址'
        try:
            resp = requests.get(url, proxies=proxy)
            if resp.status_code == 200:
                content = resp.text
                print(len(content))
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


def run(n=1000, proxy=None):
    while n:
        w = WEB()
        w.bd_get(proxy)
        n-=1



async def fetch(session, url, proxy="squidsz61.dianhua.cn:8080"):
    query_header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "User-Agent": random.choice(WEB.agent_list),
        }
    
    async with session.get(url, headers=query_header, proxy=None) as response:
        return await response.text()

async def main():
    all_tel = ['05362081111', '04294447001', '03917291224', '073186240655', '02368088882', '076982283187', '02989581675', '02558377516', '037127978107', '041188466794', '03722188521', '02164191703*890', '07596633355', '059183621655', '045157753888', '051186857186', '07928906059', '04776213200', '01056263335', '057687721558', '05582901266', '051262837080', '057688587778', '09346608777', '076085331222', '051987222787', '07976368368', '043188558689', '02584930942', '073182764958', '075526900060', '03566866001', '055168821054', '02161900502', '02584896440', '05573053321', '04162199966', '03165994005', '073188938586*8893859', '03177105896', '05337691090', '075529651666', '079183812048', '03572317171', '059124377106', '057487935837', '037155605888', '053182767663', '075583561317', '02889993808', '02452673448', '07715552815', '076922184688', '057788628398', '02161206688', '03595035510', '02885754413', '05925738999', '07381558126*3080', '08733045110', '07523277895', '03703133501', '031183862838', '051688258138', '01085180966', '02150801060', '057765766918', '03495028008', '057385851218', '02984491889', '076983314860', '02422837758', '059187270629', '059583050088*8305008', '03546762958', '01089733256', '04738187549', '051188795242', '075527309102', '087167151788', '037965163888', '079185231988', '03913532315', '051988993351', '052780691042', '03725219088', '03728831238', '075584705888', '051085988888', '03555807720', '037123336631', '051286858999*5555', '03702831898', '02032223080', '02988216989', '037158579109', '075582960345', '02226980351', '02162115900', '075589888888']
    
    for t in all_tel:
        url = f'http://www.baidu.com?wd={t} 地址'
        query_cookie = {
        "BAIDUID": "%s:FG=1" % str(uuid.uuid4()).replace('-', '').upper(),
        "PSTM": "%s" % (int(time.time())),
        }
        async with aiohttp.ClientSession(cookies=query_cookie) as session:
            html = await fetch(session, url)
            print(len(html))

if __name__ =="__main__":
    proxy_list = [{"http":f"http://squidsz{i}.dianhua.cn:8080", "https":f"https://squidsz{i}.dianhua.cn:8080"} for i in range(61, 71)]
    proxy_num = len(proxy_list)
    st = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    et = time.time() - st
    print("cost: %.3f" % et, "tps:", 100/et)

    
        

