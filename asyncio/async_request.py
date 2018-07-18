import json
import asyncio
import aiohttp
import csv
import time

root_path = 'C:/Users/station/Desktop/aaa/'


def load_data():
    ret = []
    file = f'{root_path}/a.txt'
    with open(file, 'r', encoding='utf8') as fh:
        csv_reader = csv.reader(fh)
        for line in csv_reader:
            if not line:
                continue
            ret.append(line)
    return ret

def writer(data):
    with open(f"{root_path}/out.txt", 'w', encoding='utf8') as wh:
        csv_writer = csv.writer(wh)
        for row in data:
            csv_writer.writerow(row)



async def get_one(md5):
    loop = asyncio.get_event_loop()
    url = "http://decrypt.dianhua.cn/decrypt/?apikey=yuloreInner&country=86&uid=yulore&app=decryptTel&ver=1.0&v=1&h=1&tel=%s" % md5
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.get(url=url) as response:
                text = await response.read()
                return json.loads(text)


async def main():
    src_data = load_data()
    print("len: %d" % len(src_data))
    c = 0
    for e in src_data:
        md5 = e[0]
        c += 1
        print(c)
        res = await get_one(md5)
        if res['status'] == '0':
            e[0] = res['telNum']
    writer(src_data)

if __name__ == '__main__':
    st = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    et = time.time()
    print("cost: %.3f" % (et-st))