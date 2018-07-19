import requests
from bs4 import BeautifulSoup
import threading
import time
import logging
import random

logger = logging.getLogger(__name__)

def format_print(l):
    line = '\r\n'
    got_num = 0
    for i in l:
        #logger.info(line)
        for key, v in i.items():
            desc = "%s:%s" % (key, v)
            logger.info(desc)
        got_num += 1
        #logger.info(line)
    #logger.info(got_num)


def parse(req_obj, all_ids, h):
    #parse main url
    #req_obj = requests.get(url, headers=h)
    content = req_obj.text
    bs_obj = BeautifulSoup(content, 'html.parser')
    all_title = bs_obj.find_all('div', {'class':'post_item_body'})
    lnk_list = []
    for a in all_title:
        title_obj = a.find_next('a', {'class':'titlelnk'})
        content_obj = a.find_next('p', {'class':'post_item_summary'})
        href = title_obj['href']
        title = title_obj.text
        if title in all_ids:
            continue
        all_ids.add(title)
        t = {
            'title': title,
            'link': "https:%s" % href,
            'summary': (content_obj.text).strip()
        }
        lnk_list.append(t)
    #logger.info(" len: %d, ids:%s", len(all_ids), all_ids)
    format_print(lnk_list)
    return lnk_list

def get_log(s, e):
    header_list = [
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"},
        {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)"},
        {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"},
        {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"},
    ]
    main_url = 'https://www.cnblogs.com/mvc/AggSite/NewsList.aspx'
    h = header_list[0]
    all_data = []
    all_ids = set()
    while s <= e:
        payload = {"CategoryType": "News",
                   "ParentCategoryId": 0,
                   "CategoryId": -1,
                   "PageIndex": s,
                   "TotalPostCount": 3000,
                   "ItemListActionName": "NewsList"
                   }
        req_obj = requests.post(main_url, data=payload, headers=h)
        h = header_list[random.randint(0, 3)]
        d = parse(req_obj, all_ids, h)

        all_data.extend(d)
        s += 1
    return all_data

if __name__ == '__main__':
    log_f = "%(asctime)s-%(lineno)d-%(threadName)s-%(funcName)s-%(lineno)d-%(message)s"
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.FileHandler('bky.log', 'a', encoding='utf-8')
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_f)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logging.info("\n\n\n")
    all_num = 0
    all_ids = set()
    header_list = [
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"},
        {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)"},
        {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"},
        {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"},
    ]
    main_url = 'https://www.cnblogs.com/mvc/AggSite/NewsList.aspx'
    h = header_list[0]
    for i in range(4):
        payload = {"CategoryType":"News",
                   "ParentCategoryId":0,
                   "CategoryId":-1,
                   "PageIndex":i+1,
                   "TotalPostCount":3000,
                   "ItemListActionName":"NewsList"
                   }
        req_obj = requests.post(main_url, data=payload, headers=h)
        h = header_list[random.randint(0,3)]
        a_list = parse(req_obj, all_ids, h)
        all_num += len(a_list)
        time.sleep(1)

    logger.info(len(all_ids))
    logger.info("all_num:%s print done", all_num)
