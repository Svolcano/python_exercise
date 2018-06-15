# -*- coding: utf-8 -*-
import re
import sys
import traceback

reload(sys)
sys.setdefaultencoding("utf8")

_bill_amount_REX    = re.compile(u'合计</span></td>\s*?<td>\s*?<span class="[\S ]*?">\s*?([\S]*?)\s*?</span>'.decode('utf-8'))
_bill_package_REX   = re.compile(u'套餐及固定费用</span></td>\s*?<td>\s*?<span class="[\S ]*?">\s*?([\S]*?)\s*?</span>'.decode('utf-8'))
_bill_ext_calls_REX = re.compile(u'语音通信费</span></td>\s*?<td>\s*?<span class="[\S ]*?">\s*?([\S]*?)\s*?</span>'.decode('utf-8'))
_bill_ext_data_REX  = re.compile(u'上网费</span></td>\s*?<td>\s*?<span class="[\S ]*?">\s*?([\S]*?)\s*?</span>'.decode('utf-8'))
_bill_ext_sms_REX   = re.compile(u'短彩信费</span></td>\s*?<td>\s*?<span class="[\S ]*?">\s*?([\S]*?)\s*?</span>'.decode('utf-8'))
_bill_zengzhifei_REX = re.compile(u'自有增值业务费</span></td>\s*?<td>\s*?<span class="[\S ]*?">\s*?([\S]*?)\s*?</span>'.decode('utf-8'))
_bill_daishoufei_REX = re.compile(u'代收费业务费用</span></td>\s*?<td>\s*?<span class="[\S ]*?">\s*?([\S]*?)\s*?</span>'.decode('utf-8'))
_bill_qita_REX = re.compile(u'其他费用</span></td>\s*?<td>\s*?<span class="[\S ]*?">\s*?([\S]*?)\s*?</span>'.decode('utf-8'))

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
            return 9, 'unknown_error', '', html_data
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
        return 0, 'success', 'success', data
    except:
        error = traceback.format_exc()
        return 9, 'unknown_error', ": "+error, []
