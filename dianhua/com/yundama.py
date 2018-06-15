# -*- coding: utf-8 -*-

import json, time, requests

if __name__ == '__main__':
    import sys
    sys.path.append('../')
from setting.yundama_config import *

class YDMHttp(object):
    """
    云打码类
    Usage:
        1. 初始化
        yundama = YDMHttp()
        2. 登陆云打码(可省)
        uid = yundama.login()
        print('uid: %s' % uid)
        3. 查询余额(可省)
        balance = yundama.balance()
        print('balance: %s' % balance)
        4. 识别, 上传图片str, 验证码类型ID, 返回识别结果
        cid, result = yundama.decode(image_str, codetype)
        print('cid: %s, result: %s' % (cid, result))
        5. 打码失败，上报cid，免此次费用
        ret = yundama.report(cid)
        print('ret: %s' % ret)
    """
    def __init__(self):
        """
        初始化参数
        """
        self.apiurl = APIURL
        self.username = USERNAME
        self.password = PASSWORD
        self.appid = str(APPID)
        self.appkey = APPKEY
        self.timeout = str(TIMEOUT)

    def post_url(self, url, data, files=''):
        """
        request请求
        params:
            url: str requests所需的url
            data: dict requests所需的data
            files: str requests所需的files
        return:
            response: str requests返回json值
        """
        res = requests.post(url, files=files, data=data)
        return res.text

    def request(self, data, files=''):
        """
        处理request请求, 并反序列化
        params:
            data: dict requests所需的data
            files: str requests所需的files
        return:
            response: dict 反序列化后response
        """
        response = self.post_url(self.apiurl, data, files)
        response = json.loads(response)
        return response

    def balance(self):
        """
        查询余额
        return:
            balance: str 账户余额/失败状态码
        """
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001

    def report(self, cid, flag='0'):
        """
        打码失败，上报cid，免此次费用
        params:
            self: object
            cid: int 验证码cid
            flag: 打码状态，"0"失败、"1"成功
        return:
            response: str 上报返回值/失败状态码
        """
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid,'appkey': self.appkey, 'cid': str(cid),'flag': flag}
        response = self.request(data)
        if (response):
            return response['ret']
        else:
            return -9001

    def login(self):
        """
        登陆云打码
        return:
            uid: str 用户uid/失败状态码
        """
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, image_str, codetype):
        """
        上传图形验证码str进行打码
        params:
            image_str: str 验证码文本
            codetype: int 验证码类型, 详见setting/yundama_type.py
        return:
            cid: int 验证码cid/失败状态码
        """
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'codetype': str(codetype), 'timeout': self.timeout}
        files = {'file': image_str}
        response = self.request(data, files)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        """
        打码结果获取
        params:
            cid: int 验证码cid
        return:
            captcha_code: str 打码结果/''
        """
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, image_str, codetype):
        """
        上传验证码文本进行打码，并轮询打码是否结束，获取打码结果
        params:
            image_str: str 验证码文本
            codetype: int 验证码类型, 详见setting/yundama_type.py
        return:
            cid: int 验证码cid/失败状态码
            result: str 打码结果/''
        """
        cid = self.upload(image_str, codetype)
        if (cid > 0):
            for i in range(0, TIMEOUT):
                result = self.result(cid)
                # print result,type(result)
                if (result != ''):
                    return cid, result
                else:
                    time.sleep(0.5)
            return -3003, ''
        else:
            return cid, ''

yundama = YDMHttp()

if __name__ == '__main__':
    import base64
    # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype = 1006
    # 验证码字符串
    with open('../test/img.txt', 'r') as fp:
        imgdata = base64.b64decode(fp.read())
    # 初始化
    yundama = YDMHttp()
    # 登陆云打码
    # uid = yundama.login()
    # print('uid: %s' % uid)
    # 查询余额
    # balance = yundama.balance()
    # print('balance: %s' % balance)
    # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
    start = time.time()
    cid, result = yundama.decode(imgdata, codetype)
    print time.time()-start
    print('cid: %s, result: %s' % (cid, result))
