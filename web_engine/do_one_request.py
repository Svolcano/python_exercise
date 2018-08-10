
import requests
import ujson
import asyncio
import aiohttp
import random


async def fetch_one():
    query_header = {
        "Host": "www.sogou.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.sogou.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        }
    url = 'https://weixin.sogou.com/weixin?type=2&query=a&ie=utf8&s_from=input&_sug_=y&_sug_type_=' 
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=query_header) as resp:
            print(resp.text)
            for a,v in resp.cookies.items():
                print(v.key, v.value)
            


def fetch():
    proxies = {'http': 'http://proxy.dianhua.cn:8080'}
    url = 'http://weixin.sogou.com/weixin?type=2&query=a&ie=utf8&s_from=input&_sug_=y&_sug_type_='
    resp = requests.request('HEAD', url)
    print(resp)
    for a in resp.cookies:
        print(a.name , a.value)
    


if __name__ == "__main__":
    for i in range(10):
        fetch()
