#coding:utf8
#all use utf8 encoding
import re
import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def init_log(log_name=None):
    formatter = logging.Formatter("%(message)s")
    #filename, mode='a', maxBytes=0, backupCount=0, encoding=None
    log_file_handler = RotatingFileHandler(log_name, maxBytes=10485760, backupCount=3)
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(logging.INFO)
    logger = logging.getLogger(log_name)
    logger.addHandler(log_file_handler)
    logger.setLevel(logging.INFO)

def toutf8(s, src_encoding=None):
    """
    :param s: input string
    :param src_encoding: input string's encoding
    :return: utf8 string
    """
    if src_encoding is None:
        src_encoding = sys.getdefaultencoding()
    if isinstance(s, unicode):
        return s.encode(src_encoding)
    else:
        return s.decode(src_encoding).encode('utf8')

g_company_suffix = [u'股份有限公司', u'有限公司', u'公司', u'集团',]
g_company_suffix = [toutf8(i, 'gbk') for i in g_company_suffix]

log_name = os.path.split(__file__)[1][:-3] + '.log'
init_log(log_name)
logger = logging.getLogger(log_name)

def read_input(file_name):
    '''
    :param file_name:  csv file name, which give param
    :return:
    '''
    input_obj = {}
    csv_file_encoding = 'gbk'
    with open(file_name, 'r') as fh:
        csv_reader = csv.reader(fh)
        for row in csv_reader:
            tel = row[0]
            tel = tel.strip()
            tel = tel[:4] + '-' + tel[4:]
            tel = toutf8(tel, csv_file_encoding)
            name = row[1].strip()
            name = toutf8(name, csv_file_encoding)
            input_obj[tel] = name
    return input_obj

def parse_level1_content(tag_obj, encoding):
    header_tag = tag_obj.find('h3')
    title_tag = header_tag.find('a')
    tt = title_tag.text
    url = title_tag.attrs['href']
    abstract_tag = tag_obj.find('div', {'class': 'c-abstract'})
    abstract_str = abstract_tag.text
    snap_tag = tag_obj.find('div', {'class': 'f13'}).find('a', {'data-click': True})
    snap_url = u''
    if snap_tag:
        snap_url = snap_tag.attrs['href']
    ret = [tt, abstract_str, snap_url, url]
    ret = [toutf8(i, encoding) for i in ret]
    return ret


def format_name(name):
    '''
    :param name:  input company name
    :return:
    '''
    global g_company_suffix
    for k in g_company_suffix:
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
    global g_company_suffix
    for k in g_company_suffix:
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
    content = reponse.text.encode(reponse.encoding)
    p = BeautifulSoup(content, 'html.parser')
    all_node = p.find_all('div', {'class': "result c-container ", 'mu': False}, limit=1)
    if not all_node:
        return False, "%s, %s, %s, %s" % ('can not find!', query_str, tel, name)
    title, abstrace, short_snap_url, url = parse_level1_content(all_node[0], reponse.encoding)
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


def ouput_to_file(out_file_name, data):
    with open(out_file_name, 'w') as fh:
        fh.writelines(data)


def main(csv_file):
    format_param = read_input(csv_file)
    query_header = {
    'Host' : 'www.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
    }
    query_engine = 'https://www.baidu.com/s?q2=%s&rn=5&tn=baiduadv'
    catch_count = 0
    out_data = []
    line_splitter = '-'*80
    for tel, name in format_param.items():
        qs = query_engine % tel
        try:
            result, find_name = deal_one(qs, tel, name, query_header)
        except Exception as e:
            logger.error('Error, %s, %s, %s', qs, tel, e)
        if result:
            catch_count += 1
        out_data.append("input: %s, %s \noutput: %s, %s\n%s\n" % (tel, name, result, find_name, line_splitter))
    all_num = len(out_data)
    out_data.append("total: %d, success: %d, success_pct:%.4f" % (all_num, catch_count, float(catch_count)/all_num))
    ouput_to_file('a.txt', out_data)


if __name__ =='__main__':
    csv_filename = '60a.csv'
    main(csv_filename)





