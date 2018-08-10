import requests
import asyncio
import aiohttp
from lxml import etree

def parse(key, url, html):
    print("url: ", url)
    ed = etree.HTML(html)
    try:
        all = ed.xpath('//ol[@id="b_results"]/li[@class="b_algo"]')
        res = []
        c = 0
        print(len(all))
        c = 0
        for a in all:
            tt  = a.xpath('.//h2/a')
            if not tt:
                continue
            tt = tt[0]
            ts = tt.xpath("string(.)")
            summary = a.xpath('./div[@class="b_caption"]/p')[0]
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
    header = {
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding":"gzip, deflate, br",
        "accept-language":"zh-CN,zh;q=0.9",
        "referer":"https://cn.bing.com/",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=header) as resp:
            html = await resp.read()
            #print(html)
            parse(key, url, html.decode())


async def deal(loop):
    key = '15084796386'
    url = f'https://cn.bing.com/search?q={key}'
    tasks = []
    t =loop.create_task(task(key, url))
    tasks.append(t)
    await asyncio.wait(tasks)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deal(loop))

main()