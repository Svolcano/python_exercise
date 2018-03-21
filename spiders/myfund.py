#_*_ coding:utf8 _*_
import requests
from bs4 import BeautifulSoup
import time
import re
from selenium import webdriver
from pylab import *


def draw_lsjz(data):
    x, y = [], []
    [x.append(i[0]) and y.append(float(i[1])) for i in data]
    plot_date(x, y, 'r*')
    show()



def draw_lines(data):
    '''
        lsjz 历史净值
        ljjz 累计净值
        rzzl 日增长率
    '''
    lsjz = []
    ljjz = []
    rzzl = []
    for d in data:
        ts = d['净值日期']
        lsjz.append((ts, d['单位净值']))
        ljjz.append((ts, d['累计净值']))
        rzzl.append((ts, d['日增长率']))
    draw_lsjz(lsjz)


def format_table_data(table):
    all_data = []
    tr_list = table.find_all('tr')
    tr_head = tr_list[0]
    v_keys = []
    for th in tr_head.find_all('th'):
        v_keys.append(th.text.strip())
    # print(v_keys)
    for tr in tr_list[1:]:
        tdata = {}
        i = 0
        all_td_list = tr.find_all('td')
        for td in all_td_list:
            tdata[v_keys[i]] = td.text.strip()
            i += 1
        all_data.append(tdata)
    return all_data


def get(hd, fid):
    url = "http://fund.eastmoney.com/f10/jjjz_%s.html" % (fid)
    hd.get(url)
    all_content = hd.page_source
    soup = BeautifulSoup(all_content, 'html.parser')
    table = soup.find('table', attrs={'class':"w782 comm lsjz"})
    all_data = format_table_data(table)
    draw_lines(all_data)


def get_my_fund_data():
    myfund_ids = ['519704', '004075']
    hd = webdriver.PhantomJS()
    for fid in myfund_ids:
        get(hd, fid)


if __name__ == "__main__":
    get_my_fund_data()