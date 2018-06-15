#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from itertools import islice
import re

__all__ = ('parser', 'window', 'normalize_region',
           'region_re_pattern', 'chi_to_dig', 'preprocess_string',
           'postprocess', 'DictionaryGen', 'DistrictGraphGen','cut_parentheses',
           'ChinaAddress','JacardCaompare')

region_re_pattern = re.compile('[区省市县路]')


def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def normalize_region(region):
    return region_re_pattern.sub('',region)


def chi_to_dig(raw_string):
    if '百货' not in raw_string and ('百' in raw_string or '十' in raw_string):
        # Chinese Digits To Arabic
        n = a = 0
        string = ""
        for c in raw_string:
            d = " 一二三四五六七八九十百".find(c)
            if d != -1:
                n += [0, 10 * a ** (a > 0), a * 100][max(d - 9, 0)]
                a = d * (d < 10)
                if a == n == 0:
                    string += c
            else:
                if n+a != 0:
                    string += str(n+a)
                    n = a = 0
                string += c
        if n + a != 0:
            string += str(n + a)
    else:
        ch_dig = '零一二三四五六七八九十'
        for idx, char in enumerate(ch_dig, 0):
            raw_string = raw_string.replace(char, str(idx))
        string = raw_string

    return string


def wrapper_run_async(coroutine, loop=None):
    loop = loop or asyncio.get_event_loop()
    task = asyncio.ensure_future(coroutine)
    rslt = loop.run_until_complete(task)
    return rslt


from .parser import parser, preprocess_string
from .parser import postprocess,cut_parentheses
from .loader import DictionaryGen, DistrictGraphGen
from .address import ChinaAddress
from .compare import JacardCaompare
