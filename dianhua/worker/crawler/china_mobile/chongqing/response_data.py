# -*- coding: utf-8 -*-
import json
import sys
import traceback
from lxml import etree

reload(sys)
sys.setdefaultencoding("utf8")


# 账单
def phone_bill_data(html_data, searchMonth):
    try:
        root = etree.fromstring(html_data.encode('utf-8'))
        json_string = root.xpath('//*[@id="dataset"]')
        try:
            bill_json = json.loads(json_string[0].text)[0]
        except:
            error = traceback.format_exc()
            return 9, 'bill_json_error', error, []
        phone_bill_json = {}
        for FEE_DETAIL in bill_json['FEE_DETAIL']:
            phone_bill_json[FEE_DETAIL['FEENAME']] = FEE_DETAIL['FEE']
        data = {
            'bill_month':  searchMonth,
            # 'bill_amount': phone_bill_json[u'手机话费消费合计'],
            'bill_amount': phone_bill_json.get(u'消费合计', ""),
            'bill_package': phone_bill_json.get(u'套餐及固定费', ""),
            'bill_ext_calls': phone_bill_json.get(u'套餐外语音通信费', ""),
            'bill_ext_data': phone_bill_json.get(u'套餐外上网费', ""),
            'bill_ext_sms': phone_bill_json.get(u'套餐外短彩信费', ""),
            'bill_zengzhifei': phone_bill_json.get(u'增值业务费', ""),
            'bill_daishoufei': phone_bill_json.get(u'代收费', ""),
            'bill_qita': phone_bill_json.get(u'其他费用', "")
        }
        return 0, 'success', 'success', data
    except:
        error = traceback.format_exc()
        return 9, 'unknown_error', error, []
