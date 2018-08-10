import requests
import asyncio
import aiohttp
from lxml import etree




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

main()