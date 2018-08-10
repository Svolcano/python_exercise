import requests
import asyncio
import aiohttp
from lxml import etree
import uuid

async def get_snuid():
    url = ("http://www.sogou.com/antispider/detect.php?"
            "sn=E9DA81B7290B940A0000000058BFAB0&wdqz22=12"
            "&4c3kbr=12&ymqk4p=37&qhw71j=42&mfo5i5=7&3rqpqk=14"
            "&6p4tvk=27&eiac26=29&iozwml=44&urfya2=38&1bkeul=41"
            "&jugazb=31&qihm0q=8&lplrbr=10&wo65sp=11"
            "&2pev4x=23&4eyk88=16&q27tij=27&65l75p=40"
            "&fb3gwq=27&azt9t4=45&yeyqjo=47&kpyzva=31"
            "&haeihs=7&lw0u7o=33&tu49bk=42&f9c5r5=12"
            "&gooklm=11&_=1488956271683")
    headers = {"Cookie":
                "ABTEST=0|1488956269|v17;\
                    IPLOC=CN3301;\
                    SUID=E9DA81B7290B940A0000000058BFAB7D;\
                    PHPSESSID=rfrcqafv5v74hbgpt98ah20vf3;\
                    SUIR=1488956269"
                }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                f = await resp.read()
                f = ujson.loads(f)
                Snuid = f["id"]
    except:
        Snuid = ""
    return Snuid


def parse(key, url, html):
    ed = etree.HTML(html)
    try:
        all = ed.xpath('//div[@class="results"]/div[@id and @class]')
        res = []
        c = 0
        for a in all:
            title = a.xpath('./h3/a')[0]
            ts = title.xpath('string(.)')
            summary = a.xpath('./div[@class="ft"]')[0]
            ss = summary.xpath("string(.)")
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
    url = f'https://www.sogou.com/web?query={key}&ie=utf8&tro=off'
    tasks = []
    t =loop.create_task(task(key, url))
    tasks.append(t)
    await asyncio.wait(tasks)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deal(loop))

main()