import requests
from bs4 import BeautifulSoup
import threading
import time
import logging

logger = logging.getLogger()


def format_print(l):
    line = '\r\n'
    got_num = 0
    for i in l:
        print(line)
        for key , v in i.items():
            print("%s:%s" % (key, v))
        got_num += 1
        print(line)
    print(got_num)


def parse(url):
    # parse main url
    req_obj = requests.get(url)
    content = req_obj.text
    bs_obj = BeautifulSoup(content, 'html.parser')
    all_title = bs_obj.find_all('div', {'class':'post_item_body'})
    lnk_list = []
    for a in all_title:
        title_obj = a.find_next('a',{'class':'titlelnk'})
        content_obj = a.find_next('p',{'class':'post_item_summary'})
        t = {
            'title':title_obj.text,
            'link':"https:%s" % title_obj['href'],
            'summary':(content_obj.text).strip()
        }
        lnk_list.append(t)
    format_print(lnk_list)
    return len(lnk_list)


if __name__ == '__main__':
    log_f = "%(asctime)s-%(lineno)d-%(threadName)s-%(funcName)s-%(message)s"
    logging.basicConfig(filename='bky.log',
                        filemode='w',
                        format=log_f,
                        level=logging.DEBUG
                        )
    all_num = 0
    for i in range(30):
        main_url = 'https://www.cnblogs.com/news/#p%d' % i
        s_num = parse(main_url)
        all_num += s_num
    logging.info("all_num:%s print done", all_num)
