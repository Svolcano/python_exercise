# -*- coding:utf-8 -*-
import sys
import codecs

with codecs.open(sys.argv[1], encoding='utf-16') as fp:
    data = [x.strip() for x in fp.readlines()]

with codecs.open(sys.argv[2], 'w', encoding='utf-8') as fp:
    for each in data:
        fp.write(u'{}\n'.format(each))

