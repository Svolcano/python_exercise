import requests
import types
import asyncio
import os
import re
import chardet
import threading
import queue

def gen_url():
    for i in range(1, 10):
        for j in range(1, 10):
            name = f"ch0{i}0{j}.html"
            base = f"http://www2.edu-edu.com.cn/lesson_crs78/self/j_0022/soft/{name}"
            yield base, name

# for u in gen_url():
#     print (u)
# print (type(gen_url()), type(gen_url))
def makedir(path):
    os.makedirs(path, exist_ok=True)

def get_image_thread(q):
    while True:
        url = q.get(block=True)
        if url is None:
            break
        get_image(url)


async def get_all_images(url_list, name):
    t_num = 10
    print (f"get image: {name}")
    q_list = [queue.Queue() for i in range(t_num)]
    t_list = [threading.Thread(target=get_image_thread, args=(q, )) for q in q_list]
    for t in t_list:
        t.start()
    q_index = 0
    for url in url_list:
        q = q_list[q_index % t_num]
        q_index += 1
        q.put(url)
        for t in t_list:
            if not t.is_alive():
                t_index = t_list.index(t)
                new_t = threading.Thread(target=get_image_thread, args=(q_list[t_index], ))
                new_t.start()
                t_list[t_index] = new_t
    for q in q_list:
        q.put(None)

def get_image(rel_url):
    base = f"http://www2.edu-edu.com.cn/lesson_crs78/self/j_0022/soft/{rel_url}"
    prefix_path, name = os.path.split(rel_url)
    makedir(prefix_path)
    try:
        cur_path = os.path.abspath(os.path.curdir)
        image_path = os.path.join(cur_path, prefix_path)
        resp = requests.get(base)
        if resp.status_code == 200:
            with open(rel_url, 'wb') as fh:
                fh.write(resp.content)
    except Exception as e:
        print("get_images", e, rel_url) 
    

async def get_content(url, name):
    try:
        print (f"get_content{name}")
        resp = requests.get(url, timeout=1)
        if resp.status_code == 200:
            content = resp.content.decode('utf8')
            with open(name, 'w', encoding='utf8') as fh:
                fh.write(content)
            all_images = re.findall(r'<img.*?src="(.*?)".*?>', resp.text)
            await get_all_images(all_images, name)
    except Exception as e:
        print(e, name) 
    

async def main():
    for url, name in gen_url():
        await get_content(url, name)
        #await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
print("done")
