import requests
from bs4 import BeautifulSoup
import logging
import os
import queue
import threading
import time
import random

home = 'D:\\luntuan_girls_thread\\'
success_count = 0
count_lock = threading.Lock()


def save_img(url):
    try:
        global home, success_count
        rsp = requests.get(url)
        name = url.split('/')[-1]
        full_path = "%s%s" % (home, name)
        with open(full_path, 'wb') as fh:
            fh.write(rsp.content)
        with count_lock:
            success_count += 1
    except Exception as e:
        logging.error(e)


def get_all_img(src_link):
    logging.info(src_link)
    for s in src_link:
        save_img(s)


def all_girl_src_list(bs_obj):
    key = '小树医生心理生理医务室'
    p_list = bs_obj.find_all('p')
    girl_img_url_list = []
    for p in p_list:
        a = p.text
        if key in a:
            girl_tag = p.find_next_sibling('p')
            next_p = girl_tag.find_next('img')
            try:
                girl_src = next_p['src']
                girl_img_url_list.append(girl_src)
                break
            except Exception as e:
                logging.error("except: %s, obj:%s", e, next_p)

    logging.info(girl_img_url_list)
    return girl_img_url_list


def parse_one(url, header):
    logging.info(url)
    req_obj = requests.get(url, headers=header)
    bs_obj = BeautifulSoup(req_obj.text, 'html.parser')
    l = all_girl_src_list(bs_obj)
    get_all_img(l)


def parse_one_thread(q, header):
    my_name = threading.current_thread().name
    while 1:
        try:
            url = q.get()
            if url == 'END':
                logging.info('%s:END', my_name)
                break
            logging.info(url)
            req_obj = requests.get(url, headers=header)
            bs_obj = BeautifulSoup(req_obj.text, 'html.parser')
            l = all_girl_src_list(bs_obj)
            get_all_img(l)
        except Exception as e:
            logging.error("e:%s, url:%s", e, url)
            time.sleep(5)


def get_all_link(url, header):
    global success_count
    thread_num = 1
    all_img_num = 0
    req_obj = requests.get(url, headers=header)
    bs_obj = BeautifulSoup(req_obj.text, 'html.parser')
    all_a = bs_obj.find_all('a', {'class':'blog-title'})
    a_list = []
    for a in all_a:
        a_list.append(a['href'])
    logging.info(a_list)
    q_list = [queue.Queue() for i in range(thread_num)]
    t_list = [threading.Thread(target=parse_one_thread, args=(q, header)) for q in q_list]
    for t in t_list:
        t.start()
    index = 0
    for href in a_list:
        all_img_num += 10
        q_list[index].put(href)
        index += 1
        index = index % 10
        if index == 9:
            for t in t_list:
                if not t.is_alive():
                    logging.info("%s dead", t.name)
                    old_index = t_list.index(t)
                    old_queue = q_list[old_index]
                    new_t = threading.Thread(target=parse_one_thread, args=(old_queue, header))
                    t_list.insert(old_index, new_t)
    for q in q_list:
        q.put("END")

    for t in t_list:
        t.join()

    logging.info("all done:should download: %d, success: %d", all_img_num, success_count)

if __name__ == "__main__":
    logging.basicConfig(filename='luntan.log', filemode='w', level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }
    header_list = [
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"},
        {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)"},
        {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"},
        #{"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"},
    ]
    try:
        if not os.path.exists(home):
            os.mkdir(home)
    except Exception as e:
        logging.error(e)

    for i in range(100):
        header_t = header_list[random.randint(0, len(header_list)-1)]
        main_url = 'https://my.oschina.net/xxiaobian/blog/?sort=time&p=%d' % (i+1)
        get_all_link(main_url, header_t)
        time.sleep(2)