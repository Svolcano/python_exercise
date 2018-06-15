# -*- coding: utf-8 -*-
import hashlib
import re
import traceback

from Crypto.Cipher import AES
import base64
import time
import sys
reload(sys)
sys.setdefaultencoding("utf8")

from lxml import etree

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

def parse_call_record(self, log_data, search_month, tel):
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
    try:
        if u"没有相应的记录" in log_data:
            return 9, "html_error", "no_body", []
        selector = etree.HTML(log_data)
        items = selector.xpath('//table[@id="details_table"]/tr')[1:-1]

        body = selector.xpath('//body')
        if not body:
            return 9, "html_error", "no_body", []

        if not items:
            return 9, "html_error", "html_error", []
    except:

        error = traceback.format_exc()
        return 9, "html_error", "html_error:{}".format(error), []
    for item in items:
        data = {}
        try:
            data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data['call_cost'] = str(float(item.xpath('./td[7]/text()')[0]) + float(item.xpath('./td[8]/text()')[0]))
            #以下几行为了解决时间戳问题
            call_time = re.findall('\d{2}', item.xpath('./td[5]/text()')[0])
            call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[3] + ' ' + call_time[
                4] + ':' + call_time[5] + ':' + call_time[6]
            timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
            call_time_timeStamp = str(int(time.mktime(timeArray)))
            data['call_time'] = call_time_timeStamp

            data['call_method'] = item.xpath('./td[9]/text()')[0][:2]
            data['call_type'] = ''
            call_from = item.xpath('./td[2]/text()')
            if call_from:
                raw_call_from = call_from[0].strip()
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    data['call_from'] = raw_call_from
            else:
                data['call_from'] = ''

            data['call_to'] = ''
            data['call_tel'] = item.xpath('./td[4]/text()')[0]
            if tel in data['call_tel']:
                data['call_tel'] = item.xpath('./td[3]/text()')[0]

            durations = item.xpath('./td[6]/text()')[0].split(':')
            duration = int(durations[0]) * 3600 + int(durations[1]) * 60 + int(durations[2])
            data['call_duration'] = str(duration)
            data['month'] = str(search_month)

            records.append(data)
        except:
            error = traceback.format_exc()
            return 9, 'json_error',  'json_error:{}'.format(error), records
    return 0, 'success', 'success', records
