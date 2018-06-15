# -*- coding: utf-8 -*-
import re
import sys
import traceback

reload(sys)
sys.setdefaultencoding("utf8")

_bill_amount_REX    = re.compile(u'费用合计</strong>\s*?</div>\s*?<div style="[\S\s]*?">\s*?￥\s*?([\S]*?)\s*?</div>'.decode('utf-8'))
_bill_package_REX   = re.compile(u'套餐及固定费用</strong>\s*?</div>\s*?<div style="[\S\s]*?">\s*?￥\s*?([\S]*?)\s*?</div>">([\S]*)</span>'.decode('utf-8'))
_bill_ext_calls_REX = re.compile(u'电话费\s*?</li>\s*?</div>\s*?<div style="[\S\s]*?">\s*?￥\s*?([\S]*?)\s*?</div>'.decode('utf-8'))
_bill_ext_data_REX  = re.compile(u'上网费\s*?</li>\s*?</div>\s*?<div style="[\S\s]*?">\s*?￥\s*?([\S]*?)\s*?</div>'.decode('utf-8'))
_bill_ext_sms_REX   = re.compile(u'短[\S]*?信费\s*?</li>\s*?</div>\s*?<div style="[\S\s]*?">\s*?￥\s*?([\S]*?)\s*?</div>'.decode('utf-8'))
_bill_zengzhifei_REX = re.compile(u'增值业务费</strong>\s*?</div>\s*?<div style="[\S\s]*?">\s*?￥\s*?([\S]*?)\s*?</div>'.decode('utf-8'))
_bill_daishoufei_REX = re.compile(u'代收费业务费用</strong>\s*?</div>\s*?<div style="[\S\s]*?">\s*?￥\s*?([\S]*?)\s*?</div>'.decode('utf-8'))
_bill_qita_REX = re.compile(u'其他[\S]*?</strong>\s*?</div>\s*?<div style="[\S\s]*?">\s*?￥\s*?([\S]*?)\s*?</div>'.decode('utf-8'))

def do_re(content, rex):
    result = re.findall(rex, content)
    if result:
        return result
    else:
        return ["0"]

# 账单
def phone_bill_data(html_data, searchMonth):
    try:
        bill_amount = do_re(html_data, _bill_amount_REX)
        if bill_amount[0] == '0':
            return 'unknown_error', 9, '', html_data
        data = {
            'bill_month':  searchMonth,
            'bill_amount': bill_amount[0],
            'bill_package':   do_re(html_data, _bill_package_REX)[0],
            'bill_ext_calls': do_re(html_data, _bill_ext_calls_REX)[0],
            'bill_ext_data':  do_re(html_data, _bill_ext_data_REX)[0],
            'bill_ext_sms':   do_re(html_data, _bill_ext_sms_REX)[0],
            'bill_zengzhifei': do_re(html_data, _bill_zengzhifei_REX)[0],
            'bill_daishoufei': do_re(html_data, _bill_daishoufei_REX)[0],
            'bill_qita':      do_re(html_data, _bill_qita_REX)[0]
        }
        return 'success', 0, 'success', data
    except:
        error = traceback.format_exc()
        return 'unknown_error', 9, error, []