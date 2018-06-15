# -*- coding: utf-8 -*-
import hashlib
import re

from Crypto.Cipher import AES
import base64
import time
import sys
reload(sys)
sys.setdefaultencoding("utf8")

def aes_encrypt(n):
    # this is the porting from telecom javascript
    BS = 16
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    n = pad(n)
    e = hashlib.md5('login.189.cn')
    t = e.hexdigest()
    i = t.encode('utf-8')
    r  = u'1234567812345678'.encode('utf-8')
    encryption_suite = AES.new(i, AES.MODE_CBC, r)
    cipher_text = encryption_suite.encrypt(n)
    base64.b64encode(cipher_text)
    return base64.b64encode(cipher_text)

def parse_call_record(self, data, query_month):
    """
    | `update_time` | string | 更新时间戳 |
    | `call_cost` | string | 爬取费用 |
    | `call_time` | string | 通话起始时间 |
    | `call_method` | string | 呼叫类型（主叫, 被叫） |
    | `call_type` | string | 通话类型（本地, 长途）  |
    | `call_from` | string | 本机通话地 |
    | `call_to` | string | 对方归属地 |
    | `call_duration` | string | 通话时长 |
    """
    records = []
    items = data['items']
    for item in items:
        data = {}
        # 统计字段 {\"total\":0.0,\"duration\":4366,\"feeName\":\"null\",\"baseFee\":36.8,\"indbDate\":null,\"otherFee\":0.0,\"roamType\":null,\"tollType\":null,\"callDate\":\"null\",\"callType\":\"null\",\"cellId\":null,\"cityName\":null,\"counterAreaCode\":\"null\",\"counterNumber\":\"过户\",\"favour\":38.41,\"queryMonth\":\"201703\",\"tollAdd\":0.0,\"tollFee\":1.61,\"transUseAmont\":0}
        if item['callDate'] == None or item['callDate'] == 'null':
            continue
        data['month'] = query_month
        data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data['call_cost'] = str(item['total'])
        # 以下几行为了转换时间戳
        call_time = re.findall('\d{2}', item['callDate'])
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + call_time[
            4] + ':' + call_time[5] + ':' + call_time[6]
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        data['call_time'] = call_time_timeStamp
        data['call_method'] = item['callType']
        data['call_type'] = ''
        data['call_from'] = ''
        # data['call_to'] = item['counterAreaCode']

        raw_call_to = item['counterAreaCode'].strip()
        call_to, error = self.formatarea(raw_call_to)
        if call_to:
            data['call_to'] = call_to
        else:
            self.log("crawler", "{}  {}".format(error, raw_call_to), "")
            data['call_to'] = raw_call_to

        data['call_tel'] = item['counterNumber']
        data['call_duration'] = str(item['duration'])
        records.append(data)
    return records
