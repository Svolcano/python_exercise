#coding:utf-8
from urllib import request
import re

def get_values(url):
    response = request.urlopen(url)
    page = response.read()
    page = page.decode('utf-8')
    return page

def parse(data):
    cp = '¥'
    ap = '$'
    # $10.00/$9.26
    #¥20.00
    r = re.compile(r'<td align="right">(.\d+\.\d+)(/\$\d+\.\d+){0,1}</td>')
    dd = r.findall(data)
    res = []
    #print(dd)
    for d in dd:
        d  = d[0]
        if d.startswith(cp):
            res.append(float(d[1:]))
        elif d.startswith(ap):
            print (d)
            res.append(6.8*float(d[1:]))
    return res


def calc(data):
    sum = 0.0
    min = 10000000000
    max = 0.0
    for d in data:
        sum += d
        if d < min:
            min = d
        if d > max:
            max = d
    return sum, min, max


if __name__ == "__main__":
    url = 'http://visualfc.github.io/support/'
    data = get_values(url)
    money = parse(data)
    sum, min, max  = calc(money)
    print ("sum=%s, min=%s, max=%s" % (sum, min, max))
