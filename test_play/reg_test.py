#coding:utf8
import re
pn = r"^(138|158)(\d){8}$"

a = "15801404228"
b = "13801404228"

m = re.match(pn, b)
if m:
    print(m.group())

an = r"a+"
ss = "aabb"
m = re.match(an, ss)
if m :
    print(m.group())



def yf(a):
    if a == -1:
        return 10
    else:
        yield a+1


a = yf(4)
try:
    b = a.__next__()
    print(b)
except Exception as e:
    print (e)