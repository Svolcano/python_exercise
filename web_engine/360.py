import requests
import asyncio
import aiohttp
from lxml import etree
import uuid




def parse(key, url, html):
    ed = etree.HTML(html)
    try:
        all = ed.xpath('//ul[@class="result"]/li')
        res = []
        c = 0
        for a in all:
            tt  = a.xpath('./h3/a')
            if not tt:
                continue
            tt = tt[0]
            ts = tt.xpath("string(.)")
            summary = a.xpath('./p[@class="res-desc"]')[0]
            ss = summary.xpath("string(.)")
            print(ss)
            if key in ts or key in ss:
                res.append((ts, ss))
                c += 1
                if c == 3:
                    break
        print(res)        
            
    except Exception as e:
        print('****%s' % e) 

async def task(key, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.read()
            parse(key, url, html)


async def deal(loop):
    key = '0354-6322020'
    url = f'https://www.so.com/s?ie=utf-8&q={key}'
    tasks = []
    t =loop.create_task(task(key, url))
    tasks.append(t)
    await asyncio.wait(tasks)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deal(loop))

# main()
import time
def check(i):
    uid = str(uuid.uuid4()).replace('-', '').lower()
    url = 'https://www.so.com/s?q=hfghfgh&src=srp&fr=none&psid={uid}}'
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate", 
    "Cookie": f"QiHooGUID={str(uuid.uuid4()).replace('-', '').upper()}.{int(time.time())};",
    }
    a = requests.get(url, headers=headers)
    t = a.text

    if '系统检测到您操作过于频繁' in t:
        print('block')
        with open(f"{i}.html", 'w', encoding='utf8') as wh:
            wh.write(t)
    if '公司首页-项目网' in t:
        print('ok')
    else:
        print('error')
        with open(f"{i}.html", 'w', encoding='utf8') as wh:
            wh.write(t)
n=100
while n:
    check(n)
    n -= 1