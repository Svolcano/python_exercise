#_*_ coding:utf8 _*_
import requests
from bs4 import BeautifulSoup
import time
myfund_ids = ['519704']

def get(id):
    nt = time.time() * 1000
    url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery183005674756430820804_%d&fundCode=519704&pageIndex=1&pageSize=20&startDate=&endDate=&_=%d" %(
    (nt),(nt+200),
    )
    url_obj = requests.get(url)
    all_content = url_obj.content
    soup = BeautifulSoup(all_content, 'html.parser')
    print(soup.prettify())

if __name__ == "__main__":
    for id in myfund_ids:
        get(id)
