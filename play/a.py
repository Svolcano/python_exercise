#coding:utf8

import ujson


param = {
    'start_date':'20180101',
    'end_date':'20180301',
    'cids':[3,4,5,6],
    'telcom':'移动',
    'province':'北京',
    'crawler_channel':'xinde'
}

str = ujson.encode(param)
print str