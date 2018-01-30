import re
class A(object):
    SID = '1234'

    @staticmethod
    def hell(sid=SID):
        print(sid)
A.hell()
a = '192.168.1.1231'
m = re.match("(\d+\.){3}(\d+)", a)
if m :
    print(m.groups())
print("_"*20)
a = list(range(10))
b = {
    'a':123
}
a.extend(b)
print(a)

