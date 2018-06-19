#coding:utf8
#all use utf8 encoding
import re
import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import logging
from logging.handlers import RotatingFileHandler
import jieba


def init_log(log_name=None):
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d]-%(funcName)s- %(levelname)s: %(message)s")
    #filename, mode='a', maxBytes=0, backupCount=0, encoding=None
    log_file_handler = RotatingFileHandler(log_name, maxBytes=20971520, backupCount=3, mode='w')
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


g_company_suffix = ['股份', '股份有限', '有限', '股份有限公司', '有限公司', '公司', '集团', '科技']
query_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
}
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
    logger.info("encoding:%s", encoding)
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


def direct_name_compared(k, src):
    '''
    :param k: key word
    :param src:  input string
    :return True, match_str
    '''
    logger.info("name: %s", k)
    result = False
    match_str = ''
    if k == src:
        return True, src
    #if company in title
    if k in src:
        return True, k
    return result, match_str


def find_lcsubstr(s1, s2):
    m = [[0 for i in range(len(s2) + 1)] for j in range(len(s1) + 1)]  # 生成0矩阵，为方便后续计算，比字符串长度多了一列
    mmax = 0  # 最长匹配的长度
    p = 0  # 最长匹配对应在s1中的最后一位
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                m[i + 1][j + 1] = m[i][j] + 1
                if m[i + 1][j + 1] > mmax:
                    mmax = m[i + 1][j + 1]
                    p = i + 1
    return s1[p - mmax:p], mmax  # 返回最长子串及其长度


def fc_name_compared(name, src):
    logger.info("")
    global g_company_suffix
    # src = format_title(src)
    sub_str, pos = find_lcsubstr(name, src)
    logger.info("sub_str:%s, name:%s", sub_str, name)
    for k in g_company_suffix:
        lk = len(k)
        if sub_str.endswith(k):
            sub_str = sub_str[:-lk]
        if name.endswith(k):
            name = name[:-lk]
    logger.info("sub_str:%s, name:%s", sub_str, name)
    if sub_str and sub_str not in g_company_suffix:
        ls = len(sub_str)
        ln = len(name)
        r = float(ls)/ln
        logger.info("len sub_str: %d, ln:%d, r:%f", ls, ln, r)
        if r > 0.3:
            return True, sub_str
    return False, ''




def fc_name_compared_old(name, src):
    """
    :param name: company name
    :param src: find in html
    :return:
    """
    logger.info("name: %s, src: %s", name, src)
    global g_company_suffix
    new_fc = jieba.cut(name, HMM=False, cut_all=True)
    new_fc = [fc.encode('utf8') for fc in new_fc]
    s, e = 0, 0
    ls = 0
    le = 0
    all_match = []
    for fc in new_fc:
        if fc in g_company_suffix:
            continue
        if fc in src:
            all_match.append(fc)
            if s == 0:
                s = src.index(fc)
                ls = len(fc)
            else:
                e = src.index(fc)
                le = len(fc)
    if (s or e) and s < e:
        if e != 0:
            r = src[s:e+le]
        else:
            r = src[s:s+ls]
        all_str = ''.join(all_match)
        lall = len(all_str)
        ln = len(name)
        if lall > ln*2:
            return False, ''
        ratio = float(lall)/ln
        logger.info("r:%s, name:%s, ratio: %f", r, name, ratio)
        if ratio < 0.7:
            return False, ''
        return True, r
    else:
        return False, ''


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
    return check_url(query, tel, name)


def check_url(query, tel, name):
    '''
    :param query:
    :param tel:
    :param name:
    :return:
    '''
    result = False
    find_name = ''
    global query_header
    try:
        response = requests.get(query, headers=query_header)
        content = response.text.encode(response.encoding)
        root = BeautifulSoup(content, 'html.parser')
        logger.info("response encoding: %s", response.encoding)
        body_text = root.find('body').text
        # body_text = body_text.encode('utf8')
        ret, result = direct_name_compared(name, body_text)
        if ret:
            return ret, result
        ret, result = fc_name_compared(name.decode('utf8'), body_text)
        if ret:
            return ret, result
    except Exception as e:
        logger.error("query: %s, tel:%s, name:%s, e:%s", query, tel, name, e)
    return False, ''


def deal_one(query_str, tel, name, query_header):
    logger.info("tel:%s, name: %s", tel, name)
    result = False
    find_name = ''
    reponse = requests.get(query_str, headers=query_header)
    content = reponse.text
    p = BeautifulSoup(content, 'html.parser')
    all_node = p.find_all('div', {'class': "result c-container ", 'mu': False}, limit=1)
    if not all_node:
        return False, "%s, %s, %s, %s" % ('can not find!', query_str, tel, name)
    title, abstrace, short_snap_url, url = parse_level1_content(all_node[0], reponse.encoding)
    # direct compare
    result, match_str = direct_name_compared(name, title)
    if result:
        return result, match_str
    # after deal compare
    result, match_str = fc_name_compared(name, title)
    print name, title, result, match_str
    if result:
        return result, match_str

    # check url
    result, match_str = check_url(url, tel, name)
    if result:
        return result, match_str
    # check snap short
    result, match_str = check_snap(short_snap_url, tel, name)
    if result:
        return result, match_str
    return result, ''


def output_to_file(out_file_name, data):
    with open(out_file_name, 'w') as fh:
        fh.writelines(data)


def main(csv_file):
    global query_header
    format_param = read_input(csv_file)
    query_engine = 'https://www.baidu.com/s?q2=%s&rn=5&tn=baiduadv'
    catch_count = 0
    out_data = []
    line_splitter = '-'*80
    for tel, name in format_param.items():
        qs = query_engine % tel
        result, find_name = deal_one(qs, tel, name, query_header)
        if result:
            catch_count += 1
        out_data.append("input: %s, %s \noutput: %s, %s\n%s\n" % (tel, name, result, find_name, line_splitter))
    all_num = len(out_data)
    out_data.append("total: %d, success: %d, success_pct:%.4f" % (all_num, catch_count, float(catch_count)/all_num))
    output_to_file('a.txt', out_data)


if __name__ =='__main__':
    csv_filename = '60a1.csv'
    main(csv_filename)





