#coding:utf8

import re
import requests
from bs4 import BeautifulSoup
import csv

input_param = u'''
051983987101	常州百树厨艺酒店用品有限公司		无法匹配
051286178363	汇通金融数据服务有限公司		无法匹配
051088703333	红星美凯龙颐达华瑞壁纸专卖店		无法匹配
051486545809	江苏中海工业有限公司		无法匹配
057187980169	美妍服饰		无法匹配
'''


def read_input(file_name):
    '''
    :param file_name:  csv file name, which give param
    :return:
    '''
    input_obj = {}
    with open(file_name, 'r') as fh:
        csv_reader = csv.reader(fh)
        for row in csv_reader:
            tel = row[0]
            tel = tel.strip()
            tel = tel[:4] + '-' + tel[4:]
            name = row[1].strip()
            input_obj[tel] = name
    return input_obj


def parse_param(i_str):
    obj = {}
    a = input_param.split('\n')
    for i in a:
        if i:
            k, v = i.split('\t')[:2]
            k = k.strip()
            k = k[:4] + '-' + k[4:]
            v = v.strip()
            obj[k.strip()] = v.strip()
    return obj


def parse_level1_content(tag_obj):
    header_tag = tag_obj.find('h3')
    title_tag = header_tag.find('a')
    tt = title_tag.text
    url = title_tag.attrs['href']
    abstract_tag = tag_obj.find('div', {'class': 'c-abstract'})
    abstract_str = abstract_tag.text
    snap_tag = tag_obj.find('div', {'class': 'f13'}).find('a', {'data-click': True})
    snap_url = snap_tag.attrs['href']
    # print 'title', tt
    # print 'abstrace', abstract_str
    # print 'short_snap_url', snap_url
    # print 'url', url
    return tt, abstract_str, snap_url, url


def format_name(name):
    '''
    :param name:  input company name
    :return:
    '''
    suffix = [u'股份有限公司', u'有限公司', u'公司', u'集团',]
    for k in suffix:
        if name.endswith(k):
            len_k = len(k)
            name = name[:-len_k]
    return name


def name_compared(k, src):
    '''
    :param k: key word
    :param src:  input string
    :return True, match_str
    '''
    result = False
    match_str = ''
    if k == src:
        return True, src
    #if company in title
    if k in src:
        n = format_title(src)
        return True, n
    return result, match_str


def format_title(title):
    '''
    :param search result title:
    :return: comany name in title whick is before 公司
    '''
    suffix = [u'公司', u'集团', ]
    for k in suffix:
        if k in title:
            fi = title.find(k)
            return title[:fi] + k
    return title


def check_snap(query, tel, name):
    '''
    :param query:
    :param tel:
    :param name:
    :return:
    '''
    result = False
    find_name = ''
    return result, find_name


def check_url(query, tel, name):
    '''
    :param query:
    :param tel:
    :param name:
    :return:
    '''
    result = False
    find_name = ''
    return result, find_name


def deal_one(query_str, tel, name, query_header):
    result = False
    find_name = ''
    reponse = requests.get(query_str, headers=query_header)
    content = reponse.text.encode(reponse.encoding).decode('utf8')
    p = BeautifulSoup(content, 'html.parser')
    all_node = p.find_all('div', {'class': "result c-container ", 'mu': False}, limit=1)
    title, abstrace, short_snap_url, url = parse_level1_content(all_node[0])
    result, match_str = name_compared(name, title)
    if result:
        return result, match_str
    new_name = format_name(name)
    result, match_str = name_compared(name, title)
    if result:
        return result, match_str
    result, match_str = check_url(url, tel, name)
    if result:
        return result, match_str

    result, match_str = check_snap(short_snap_url, tel, name)
    if result:
        return result, match_str

    return result, title


def main(csv_file):
    format_param = read_input(csv_file)
    query_header = {
    'Host' : 'www.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
    }
    query_engine = 'https://www.baidu.com/s?q2=%s&rn=5&tn=baiduadv'
    catch_count = 0
    for tel, name in format_param.items():
        print "input : %s, %s" % (tel, name)
        qs = query_engine % tel
        result, find_name = deal_one(qs, tel, name, query_header)
        print result, find_name
        if result:
            catch_count += 1
        print "*" * 20
    print catch_count


if __name__ =='__main__':

    main('a.csv')





