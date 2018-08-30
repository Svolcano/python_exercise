#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import time
import pathlib
import uuid
from pypinyin import lazy_pinyin
from lxml import etree
from .log import dprint
from .FormatTools import format_telnum_BQC
import requests
import random


resource_path = pathlib.Path(__file__).parents[2] / "data"

class WEBEngine(metaclass=ABCMeta):

    query_timeout = 30
    symbol = set(u"[]【】\\’'\"-—=+（）(). 。/？；:}{|*&^%$#@!~`…￥")

    short_name_len = 4
    company_title_len = 30

    # error_num
    no_content = "404_no_content"
    no_hit = "405_no_hit"
    no_response = "401_no_response"

    def __init__(self, tel, key_set=set(), company_suffix=set(), ap={}):
        self.ori_tel = tel.strip()
        self.new_tel = self.ori_tel
        self.query_url = None
        self.query_content = None
        self.query_retry = 3
        self.default_content_row_count = 5
        self.proxies = 'http://proxy.dianhua.cn:8080'
        self.key_set = key_set
        self.ap = ap
        self.company_suffix = company_suffix
        self.ret_res = {
            'i_tel':self.ori_tel,
            'format_tel':'',
            'hit_companys':[],
            'all_find_companys':[],
            'query_url':'',
            'o_ret':'',
            'o_name':'',
            'time_cost':'',
            'format_o_name':'',
            'tel_area_code':'',
            'tel_tail_numb':'',
        }

    @abstractmethod
    def build_query(self):
        pass

    @abstractmethod
    def get_all_nodes(self):
        pass

    @abstractmethod
    def get_url_content(self):
        pass

    def format_tel(self):
        """
        format tel num add - in it
        :return:
        """
        new_tel, area_code = format_telnum_BQC(self.ori_tel)
        self.ret_res['tel_area_code'] = area_code
        if area_code:
            self.ret_res['tel_tail_numb'] = new_tel[len(area_code)+1:]
        self.ret_res['format_tel'] = new_tel
        if new_tel:
            self.new_tel = new_tel

    def _gen_cookie_guid(self):
        u_str = uuid.uuid4()
        u_str = str(u_str)
        return u_str.replace('-', '')


    def parse(self):
        """
        process content
        resunt final result
        """
        st = time.time()
        self.format_tel()
        self.build_query()
        self.query_content = self.get_url_content()
        if not self.query_content:
            self.ret_res['o_ret'] = False
            self.ret_res['o_name'] = self.no_response
            self.ret_res['time_cost'] = time.time() - st
            return
        tag_objs = self.get_all_nodes()
        if not tag_objs:
            self.ret_res['o_ret'] = False
            self.ret_res['o_name'] = self.no_hit
            self.ret_res['time_cost'] = time.time() - st
            return
        for one in tag_objs:
            tt, abstract_str = one['title'], one['abstract']
            title_url = one['title_url']
            # title
            hit = False
            if self.new_tel in abstract_str:
                hit = True
            t_name = self.title_find(tt)
            a_name = self.abstract_find(abstract_str)
            if t_name:
                ele = (t_name,title_url)
                self.ret_res['all_find_companys'].append(ele)
                if hit:
                    self.ret_res['hit_companys'].append(ele)
            if a_name:
                self.ret_res['all_find_companys'].extend(a_name)
                if hit:
                    self.ret_res['hit_companys'].extend(a_name)
        self.select_name()
        self.ret_res['time_cost'] = time.time() - st

    def select_name(self):
        if self.ret_res['o_name']:
            return
        select_src = self.ret_res['hit_companys']
        # not hit return fisrt find company name
        if not select_src:
            all = self.ret_res['all_find_companys']
            if all:
                self.ret_res['o_name'] = all[0]
            return
        # reurn fisrt hit
        if select_src:
            self.ret_res['o_name'] = select_src[0]

    def get_company_name(self, src):
        """
        :param src: input string
        :return: company name in input
        """
        if src:
            long_len = 0
            long_key = u''
            for k in self.company_suffix:
                if k in src:
                    l_k = len(k)
                    if l_k > long_len:
                        long_len = l_k
                        long_key = k
            # print(src, long_key)
            special_symbol = u' :：_—-,。，、'
            if long_key:
                index_long_key = src.index(long_key)
                before = src[:index_long_key]
                len_before = len(before) - 1
                while len_before >= 0:
                    p = before[len_before]
                    if p in special_symbol or p.isdigit():
                        break
                    len_before -= 1
                if len_before != 0:
                    len_before += 1
                hit_str = before[len_before:] + long_key
                if len(hit_str) <= self.company_title_len:
                    return hit_str
        return ''


    @staticmethod
    def find_lcseque(s1, s2):
        # 生成字符串长度加1的0矩阵，m用来保存对应位置匹配的结果
        m = [[0 for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]
        # d用来记录转移方向
        d = [[None for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]

        for p1 in range(len(s1)):
            for p2 in range(len(s2)):
                if s1[p1] == s2[p2]:  # 字符匹配成功，则该位置的值为左上方的值加1
                    m[p1 + 1][p2 + 1] = m[p1][p2] + 1
                    d[p1 + 1][p2 + 1] = 'ok'
                elif m[p1 + 1][p2] > m[p1][p2 + 1]:  # 左值大于上值，则该位置的值为左值，并标记回溯时的方向
                    m[p1 + 1][p2 + 1] = m[p1 + 1][p2]
                    d[p1 + 1][p2 + 1] = 'left'
                else:  # 上值大于左值，则该位置的值为上值，并标记方向up
                    m[p1 + 1][p2 + 1] = m[p1][p2 + 1]
                    d[p1 + 1][p2 + 1] = 'up'
        (p1, p2) = (len(s1), len(s2))
        s = []
        while m[p1][p2]:  # 不为None时
            c = d[p1][p2]
            if c == 'ok':  # 匹配成功，插入该字符，并向左上角找下一个
                s.append(s1[p1 - 1])
                p1 -= 1
                p2 -= 1
            if c == 'left':  # 根据标记，向左找下一个
                p2 -= 1
            if c == 'up':  # 根据标记，向上找下一个
                p1 -= 1
        s.reverse()
        sub_str = u''.join(s)
        ls = len(sub_str)
        ln = len(s1)
        ratio = float(ls) / ln
        if ratio > WEBEngine._compare_ratio_seq:
            return True, s1
        else:
            return False, ''

    def title_find(self, title):
        """
        :param title: string
        :return:
        """
        got_company_name = self.get_company_name(title)
        if got_company_name:
            if title == got_company_name and not self.ret_res['o_name']:
                self.ret_res['o_name'] = got_company_name
            return self.format_find(got_company_name)
        return ''

    def abstract_find(self, src):
        res = []
        while True:
            got_company_name = self.get_company_name(src)
            if got_company_name:
                if not got_company_name.endswith("网站"):
                    res.append(got_company_name)
                src = src.replace(got_company_name, '')
            else:
                break
        return res

    @staticmethod
    def find_lcsubstr(s1, s2):
        """
        :param s1: name
        :param s2: html content
        :return:
        """
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
        sub_str = s1[p - mmax:p]
        ration = float(mmax) / len(s1)
        return sub_str, mmax, ration  # 返回最长子串及其长度

    def format_find(self, find_str):
        """
        format  find_str , make it approch to name
        :param find_str:
        :return:
        """
        find_str = find_str.strip()
        if not find_str:
            return find_str
        # remove symbol prefix
        for sp in self.symbol:
            find_str = find_str.replace(sp, u'')
        return find_str


class BaiduEngine(WEBEngine):

    def build_query(self):
        """
        build a query string for requests object
        """
        engine = 'https://www.baidu.com/s?wd=%s'
        self.query_url = engine % self.new_tel
        self.ret_res['query_url'] = self.query_url

    def get_url_content(self):
        """
        get content of query string
        """
        query_header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.baidu.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        }
        query_cookie = {
            "BAIDUID": "%s:FG=1" % self._gen_cookie_guid().upper(),
            "BD_CK_SAM": "1",
            "PSTM": "%s" % (int(time.time())),
            "PSINO": "1",
        }
        proxy_list = ["182.254.231.171:8080",
                      "119.29.169.211:8080",
                      "111.230.13.192:8080",
                      ]
        ip_p = random.choice(proxy_list)
        proxy_dict = {
            "http": f"http://{ip_p}",
            "https": f"https://{ip_p}",
        }
        try:
            resp = requests.get(self.query_url,
                                headers=query_header,
                                timeout=self.query_timeout,
                                cookies=query_cookie,
                                proxies=proxy_dict,
                                )
            if resp.status_code == 200:
                return resp.text
            else:
                return None
        except Exception as e:
            dprint(f"faild to get content: {self.query_url}, exceptions: {e}")

    def get_all_nodes(self):
        tag_objs = []
        ed = etree.HTML(self.query_content)
        all = ed.xpath("//*[@class='result c-container ']")
        if not all:
            return tag_objs
        c = 0
        for a in all[:5]:
            try:
                te = a.xpath("./h3/a")[0]
                title_url = te.get('href')
                tt = te.xpath("string(.)")
                ae = a.xpath('./div[@class="c-abstract"]')[0]
                aes = ae.xpath("string(.)")
                more = ae.xpath("./a")
                if more:
                    more_txt = more[0].xpath("string(.)")
                    aes = aes.replace(more_txt, '')
                one = {
                    'title':tt,
                    'title_url':title_url,
                    'abstract':aes,
                }
                # print(one)
                tag_objs.append(one)
            except Exception as e:
                continue
        return tag_objs
