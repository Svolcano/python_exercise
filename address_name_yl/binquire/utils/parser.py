#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from itertools import islice
import logging
import pathlib
import re

import jieba
from jieba.posseg import pair
from zhconv import convert
import networkx as nx


from .loader import DistrictGraphGen
from . import region_re_pattern, chi_to_dig, normalize_region

jieba.setLogLevel(logging.INFO)

resource_folder = pathlib.Path(__file__).parents[2] / "resources"
ner_tokenizer = None
base_tokenizer = None
dist_graph = None


def string_to_lower(f):
    """decorate function to lower arg[0] string

    Example::
        @string_to_lower
        def foo(s):
            return s
        assert foo('ABC') == 'abc'
    """

    def wrapper(string):
        string = string.lower()
        return f(string)
    return wrapper


def string_handle_parentheses(f):
    """decorate function to normalize
        arg[0] string's Chinese Brackets to parentheses

        Example::
            @string_handle_parentheses
            def foo(s):
                return s
            assert foo('（ABC）') == '(ABC)'
    """

    def wrapper(string):
        string = string.replace('（', '(').replace('）', ')')
        return f(string)
    return wrapper


def string_chi_to_dig(f):
    """decorate function to normalize
        arg[0] string's Chinese number to Arabic

        Example::
            @string_chi_to_dig
            def foo(s):
                return s
            assert foo('九百货') == '9百货'
            assert foo('五十四工廠') == '54工廠'
            assert foo('五四工廠') == '54工廠'
    """

    def wrapper(string):
        return f(chi_to_dig(string))
    return wrapper


def trad_to_simp(f):
    """decorate function to normalize
            arg[0] string's chinese traditional to simplified

            Example::
                @trad_to_simp
                def foo(s):
                    return s
                assert foo('百貨') == '百货'
    """

    def wrapper(string):
        # string = HanziConv.toSimplified(string)
        string = convert(string, 'zh-cn')
        return f(string)
    return wrapper


@string_to_lower
@string_handle_parentheses
@trad_to_simp
@string_chi_to_dig
def preprocess_string(string):

    # process x分公司 -> 分公司
    string = re.sub('[第]?[1-9]+[分]','分',string)
    # process x廠 -> 廠
    string = re.sub('[f][1-9]厂', '厂', string)
    string = re.sub('\s','',string)
    return string


def cut_parentheses(string):
    """separate strings parentheses
    >>> cut_parentheses('1(2)345(67)')
    ('1345', ['(2)', '(67)'])
    """
    # _ = re.findall('(\((\w+)\))?([^()]*)', string)
    cut_pattern = re.compile('\(\w+\)')
    in_paretnheses = cut_pattern.findall(string)
    string = cut_pattern.sub('', string)
    string = re.sub('[^\w\s]', '',string)
    return string.strip(), in_paretnheses


def parser(string):
    """normalize company name to structure (region/x/industry/type)

    Usage::
    >>> parser('北京')
    [pair('北京', 'region')]

    >>> parser('北京小米科技有限公司')
    [pair('北京', 'region'), pair('小米', 'x'), pair('科技', 'industry'),
     pair('有限公司', 'type')]

    >>> parser('上海北京烤鸭')
    [pair('上海', 'region'), pair('北京', 'region'), pair('烤鸭', 'x')]
    """

    global ner_tokenizer, base_tokenizer
    if ner_tokenizer is None or base_tokenizer is None:
        ner_tokenizer = jieba.posseg.POSTokenizer(
            jieba.Tokenizer(dictionary=str(resource_folder / "dictionary")))
        base_tokenizer = jieba.Tokenizer()

    # string = re.sub(r'([^\(]+)\((\S+)\)(\S+)', r'\2\1\3',string)

    r = ner_tokenizer.cut(string, HMM=False)

    r = [ item if item.flag != 'eng' else pair(item.word,'x') for item in r ]

    result = reduce_type(r, 'x')
    return result


def postprocess(pairs):
    """process parse result to correct type"""
    # create a new type ( R+T ) T is branch
    pairs = reduce_region(pairs)
    pairs = reduce_type(pairs, 'x')

    pairs = handle_region_to_name(pairs)
    pairs = reduce_type(pairs, 'x')

    pairs = reduce_type(pairs, 'type')
    pairs = reduce_type(pairs, 'industry')
    # result = reduce_type(result,'region')

    return list(filter(lambda x: x.word != '', pairs))


def handle_region_to_name(pairs):
    global dist_graph
    if dist_graph is None:
        dist_graph = DistrictGraphGen().get_graph()

    # region + not_name => region + name
    if len(pairs) == 2 and pairs[0].flag == 'region' and pairs[1].flag != 'x':
            pairs[0].flag = 'x'
    elif len(pairs) > 2:
        has_name = False
        # if no name or name only is english
        for _pair in pairs:
            if _pair.flag == 'x' and not re.match('[a-zA-Z]',_pair.word) and len(_pair.word) > 1:
                has_name = True
                break
        if has_name is False:
            # region is not continuity pattern
            for idx in range(1,len(pairs)):
                if pairs[idx].flag == 'region' != pairs[idx-1].flag:
                    pairs[idx].word = region_re_pattern.sub('',pairs[idx].word)
                    pairs[idx].flag = 'x'
                    break

            for idx in range(len(pairs)-1):
                # if pairs[idx].flag == 'region' != pairs[idx+1].flag != 'x':
                # last region and parent region has no relationship
                if pairs[idx].flag == 'region' != pairs[idx+1].flag:
                    if idx != 0:
                        r1 = normalize_region(pairs[idx - 1].word)
                        r2 = normalize_region(pairs[idx].word)
                        if r1 in dist_graph and r2 in dist_graph:
                            has_path = nx.has_path(dist_graph,r1,r2)
                        else:
                            has_path = False

                        if not has_path:
                            pairs[idx].word = region_re_pattern.sub('', pairs[
                                idx].word)
                            pairs[idx].flag = 'x'
                            break
                    # no name
                    if pairs[idx + 1] != 'x':
                        pairs[idx].word = region_re_pattern.sub('',pairs[idx].word)
                        pairs[idx].flag = 'x'
                        break

    return pairs


def reduce_region(result):
    if not result:
        return result
    can_region = result[0].flag == 'region' or re.match('[1-9a-zA-z]+',result[0].word)
    del_idx = []
    for idx in range(1, len(result)):
        if result[idx].word == '(':
            can_region = True
            del_idx.append(idx)
            continue
        elif result[idx].word == ')':
            can_region = False
            del_idx.append(idx)
            continue
        if can_region and result[idx].flag == 'region':
            continue
        else:
            can_region = False
            if result[idx - 1].flag == 'type' and result[idx].flag == 'region':
                continue
            elif idx != len(result) - 1 and \
                    result[idx].flag == 'region' and result[idx+1].flag == 'type':
                continue
            elif result[idx].flag == 'region':
                result[idx].flag = 'x'

    return result


def reduce_type(iter, _type):

    result = []
    if isinstance(_type,str):
        _type = [_type]
    for flag_type in _type:

        if flag_type == 'region':
            word = ()
        else:
            word = ""

        for idx,item in enumerate(iter):
            # clear independent  char 区 省 市 县 路
            if region_re_pattern.search(item.word) and len(item.word) == 1:
                if idx != 0 and iter[idx-1].flag == 'region':
                    continue
            if item.flag == 'region' == flag_type:
                word += (item.word,)
            elif item.flag == flag_type:
                word += item.word
            else:
                if word:
                    result.append(pair(word.strip(), flag_type))
                    if type(word) == tuple:
                        word = ()
                    else:
                        word = ""
                result.append(item)
        if word:
            result.append(pair(word, flag_type))
        iter = result
        result = []

    return iter

def parser_wrapper(string):
    string = preprocess_string(string)
    string, cuts = cut_parentheses(string)
    r = parser(string)
    r = postprocess(r)
    return r, cuts