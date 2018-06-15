# -*- coding: utf-8 -*-
import re
import sys
import traceback
from lxml import etree
reload(sys)
sys.setdefaultencoding("utf8")


# 账单
def phone_bill_data(self, html, searchMonth):
    try:
        html_data = html.text
        all_fee = re.findall(ur'费用总计.*?(\d+\.?\d*)', html_data, re.S)
        if not all_fee:
            return 'no_data', 9, 'phone_bill_data not find amount', {}
        bill_package = re.findall(ur'月基本费.*?">(\d+\.?\d*)', html_data, re.S)
        bill_package = bill_package or ['']
        bill_daishoufri = re.findall(ur'代收.*?">(\d+\.?\d*)', html_data, re.S)
        bill_daishoufri = bill_daishoufri or ['']
        bill_ext_sms = re.findall(ur'综合信息服务费.*?">(\d+\.?\d*)', html_data, re.S)
        bill_ext_sms = bill_ext_sms or ['']
        bill_ext_calls = re.findall(ur'语音通话费.*?">(\d+\.?\d*)', html_data, re.S)
        bill_ext_calls = bill_ext_calls or ['']

        data = {
            'bill_month':  searchMonth,
            'bill_amount': all_fee[0],
            'bill_package':   bill_package[0],
            'bill_ext_calls': bill_ext_calls[0],
            'bill_ext_data':  "",
            'bill_ext_sms':   bill_ext_sms[0],
            'bill_zengzhifei': '',
            'bill_daishoufei': bill_daishoufri[0],
            'bill_qita':      ''
        }
        et = etree.HTML(html_data)
        length = len(et.xpath("//table[@class='table']/tr"))
        if length > 8:
            self.log("crawler", "记录内容以获得其他信息", html)
        return 'success', 0, 'success', data
    except:
        error = traceback.format_exc()
        return 'unknown_error', 9, u'phone_bill_data Exception: %s' % (error), {}