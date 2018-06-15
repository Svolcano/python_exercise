# -*- coding: utf-8 -*-
import sys
import traceback

reload(sys)
sys.setdefaultencoding("utf8")

def get_amount(content):
    try:
        if int(content) > 0:
            return '{}.{}'.format(content[:-2],content[-2:])
    except Exception as e:
        return '0'


# 账单
def phone_bill_data(html_json, searchMonth):
    try:
        if not html_json:
            return 'website_busy_error', 9, 'website_busy_error', []
        html_data = {
            u'手机': '0',
            u'套餐费优惠': '0',
            u'语音通信费': '0',
            u'国内短信费': '0',
            u'短信彩信费': '0',
        }
        for html_custBillInfoList in html_json['custBillInfoList']:
            html_data[html_custBillInfoList['itemName']] = get_amount(html_custBillInfoList['itemCharge'])
        try:
            if html_json['newStatisticalList'][0]['itemName'] == '语音通信费':
                bill_ext_calls = html_json['newStatisticalList'][0]['itemCharge']
            else:
                bill_ext_calls = ''
        except:
            bill_ext_calls = ''
        data = {
            'bill_month':  searchMonth,
            'bill_amount': html_data[u'手机'],
            'bill_package':html_data[u'套餐费优惠'],
            'bill_ext_calls': bill_ext_calls,
            'bill_ext_data':  '', #html_data[u'套餐费优惠'],
            'bill_ext_sms':   str(float(html_data[u'国内短信费']) + float(html_data[u'短信彩信费'])),
            'bill_zengzhifei': '', #html_data[u'套餐费优惠'],
            'bill_daishoufei': '', #html_data[u'套餐费优惠'],
            'bill_qita': '', #html_data[u'套餐费优惠']
        }
        return 'success', 0, 'success', data
    except:
        error = traceback.format_exc()
        return 'unknown_error', 9, 'html_error %s' % error, []