import requests
import asyncio
import aiohttp
from lxml import etree




def parse(url, html):
    ed = etree.HTML(html)
    try:
        title = ed.xpath('//*[@id="wrapper"]/div[3]/div/div[2]/h1/text()')[0]
        all = ed.xpath('//*[@id="wrapper"]/div[3]/div')[0]
        content = all.xpath('string(.)')
        with open(f"{title}.html", 'w', encoding='utf8') as wh:
            wh.write(content)
    except Exception as e:
        print('****%s' % e) 

async def task(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.read()
            parse(url, html)


async def deal(loop):
    tasks = []
    c = 0
    start_num = 12371902
    for i in range(start_num, start_num+50000, step=1):
        url = f'https://www.bequge.com/42_42237/{i}.html'
        tasks.append(loop.create_task(task(url)))
        c+=1
        if c % 20 == 0:
            await asyncio.wait(tasks)
            tasks = []
    if tasks:
        await asyncio.gather(*tasks)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deal(loop))


main()