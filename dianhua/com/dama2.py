# -*- coding:utf-8 -*-

import hashlib
import requests
import json
import base64

if __name__ == '__main__':
    import sys
    sys.path.append('../')

from setting.dama2 import ID, KEY, USERNAME, PASSWORD, HOST, TIMEOUT

def md5str(string):
    m=hashlib.md5(string)
    return m.hexdigest()

class DamatuApi(object):
    def __init__(self):
        pass

    def getSign(self,param=''):
        return md5str(KEY + USERNAME + param)[:8]

    def getPwd(self):
        return md5str(KEY +md5str(md5str(USERNAME) + md5str(PASSWORD)))

    def post(self,path,params={}):
        url = HOST + path
        resp = requests.post(url, data=params)
        return resp.json()

    def getBalance(self):
        data={'appID': ID,
            'user': USERNAME,
            'pwd': self.getPwd(),
            'sign': self.getSign()
        }
        res = self.post('d2Balance',data)
        if res['ret'] == 0:
            return res['balance']
        else:
            return res['ret']

    def decode(self,imgdata, codetype):
        data={'appID':ID,
            'user':USERNAME,
            'pwd':self.getPwd(),
            'type':codetype,
            'fileDataBase64':base64.b64encode(imgdata),
            'sign':self.getSign(imgdata),
            'timeout': TIMEOUT
        }

        res = self.post('d2File',data)
        status = res.get('ret', -99999)
        cid = res.get('id', '')
        result = res.get('result', '')
        if status == 0:
            return cid , result
        else:
            return status, ''

    def reportError(self, cid):
        data={'appID':ID,
            'user':USERNAME,
            'pwd':self.getPwd(),
            'id':cid,
            'sign':self.getSign(str(cid))
        }
        res = self.post('d2ReportError',data)
        return res['ret']

dama2 = DamatuApi()

if __name__ == '__main__':
    import time
    with open('../test/img.txt', 'r') as fp:
        imgdata = base64.b64decode(fp.read())
    print dama2.getBalance() #查询余额
    start = time.time()
    codetype = '200'
    cid, resp = dama2.decode(imgdata, codetype) #上传打码
    print cid, resp
    # print dama2.reportError(str(cid)) #打码报错
    print time.time() - start
