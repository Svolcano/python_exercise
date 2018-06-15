# -*- coding: utf-8 -*-
import traceback
import re
import json
import time

def info(result_obj):
    status = True
    final_result = {}

    try:
        if not result_obj['result'].has_key('MyDetail'):
            return False, 'website_busy_error , no result[MyDetail]: %s'% result_obj

        final_result['full_name'] = \
            result_obj['result']['MyDetail'].get('custname', '')
        final_result['id_card'] = \
            result_obj['result']['MyDetail'].get('certnum', '')
        final_result['address'] = \
            result_obj['result']['MyDetail'].get('certaddr', '')
        final_result['open_date'] = \
            time_transform(result_obj['result']['MyDetail'].get('opendate', ''), str_format="%Y-%m-%d")
        final_result['product_name'] = \
            result_obj['result']['MyDetail'].get('productname', '')
        final_result['pukcode'] = result_obj['result'].get('pukcode', '')

        if not final_result['id_card'] or final_result['id_card'] == u'无':
            final_result['is_realname_register'] = False
        else:
            final_result['is_realname_register'] = True
    except:
        error = traceback.format_exc()
        return False,'%s'%error
    return status, final_result

def time_transform(time_str,bm='utf-8',str_format="%Y-%m-%d %H:%M:%S"):
    #print time_str
    if time_str == '':
        return time_str
    time_str = time_str.encode(bm)
    #下面一行的转换是因为吉林联通出现了 2017-03-31 20:17:-0  这样的数据
    time_str = time_str.replace(':-', ':0')
    if str_format == "%Y-%m-%d":
        time_str = reduce(lambda x,y: x+"-"+y,re.findall(r'(\d{1,4})', time_str)) + " 12:00:00"
    str_format="%Y-%m-%d %H:%M:%S"
    time_type = time.strptime(time_str, str_format)
    return str(int(time.mktime(time_type)))


def time_format(time_str,**kwargs):
    exec_type=1
    time_str = time_str.encode('utf-8')
    
    if 'exec_type' in kwargs:
        exec_type = kwargs['exec_type']
    if (exec_type == 1):
        xx = re.match(r'(.*时)?(.*分)?(.*秒)?',time_str)
        h,m,s = 0,0,0
        if  xx.group(1):
            hh = re.findall('\d+', xx.group(1))[0]
            h = int(hh)
        if  xx.group(2):
            mm = re.findall('\d+', xx.group(2))[0]
            m = int(mm)
        if  xx.group(3):
            ss = re.findall('\d+', xx.group(3))[0]
            s = int(ss)
        real_time = h*60*60 + m*60 +s
    if (exec_type == 2):
        xx = re.findall(r'\d*', time_str)
        h, m, s = map(int,xx[::2])
        real_time = h*60*60 + m*60 +s
    
    return str(real_time)

def call_log(self, result_obj, year_month):
    """
        | `call_tel` | string | 18202541892 | 电话号码 |
        | `call_cost` | string | 0.00 | 通话费用 |
        | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
        | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
        | `call_type` | string | 本地 | 通话类型（本地, 长途） |
        | `call_from` | string | 北京市 | 本机通话地 |
        | `call_to` | string | 长沙市 | 对方归属地 |
        | `call_duration` | integer | 300 | 通话时长(秒)

    """
    final_result = []
    for record in result_obj:
        try:
            tmp_result = {}
            if record.has_key('calldateformat'):
                # 湖北联通的改版后格式
                date_time = '{} {}'.format(record.get('calldateformat',''), record.get('calltimeformat',''))
                tmp_result['call_time'] = time_transform(date_time)
                tmp_result['call_tel'] = record.get('othernumber', '')
                #  已经转换成秒了
                tmp_result['call_duration'] = record.get('calllonghour', '')
                # tmp_result['call_from'] = record.get('eparchyname', '')

                raw_call_from = record.get('eparchyname', '')
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    tmp_result['call_from'] = call_from
                else:
                    tmp_result['call_from'] = raw_call_from

                tmp_result['call_type'] = record.get('voicetype', '')
                tmp_result['call_method'] = record.get('calltypename', '').replace('-', '')
            else:
                date_time = '{} {}'.format(record.get('calldate', ''), record.get('calltime', ''))
                tmp_result['call_time'] = time_transform(date_time)
                tmp_result['call_duration'] = time_format(record.get('calllonghour',''))
                tmp_result['call_tel'] = record.get('othernum', '')
                # tmp_result['call_from'] = record.get('homeareaName', '')

                raw_call_from = record.get('homeareaName', '')
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    tmp_result['call_from'] = call_from
                else:
                    # self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                    tmp_result['call_from'] = raw_call_from

                tmp_result['call_type'] = record.get('landtype','')
                tmp_result['call_method'] = record.get('calltypeName', '')

            tmp_result['call_cost'] = record.get('totalfee', '')
            # tmp_result['call_to'] = record.get('calledhome', '')

            raw_call_to = record.get('calledhome', '')
            call_to, error = self.formatarea(raw_call_to)
            if call_to:
                tmp_result['call_to'] = call_to
            else:
                # self.log("crawler", "{}  {}".format(error, raw_call_to), "")
                tmp_result['call_to'] = raw_call_to

            tmp_result['month'] = year_month
            # if u'\ufffd' in tmp_result['call_from'] or \
            #    u'\ufffd' in tmp_result['call_to']  or \
            #    u'\ufffd' in tmp_result['call_method'] or \
            #    u'\ufffd' in tmp_result['call_type']:
            #     # TODO:: add loggging
            #     assert False, '\ufffd char appear!!!'
            final_result.append(tmp_result)
        except:
            # TODO: add logging
            error = traceback.format_exc()
            # status = False
            return False,'%s'%error
    return True, final_result


def parse_call_bill(result_req, query_month):
    month_fee_data = {}
    month_bill_res = json.loads(result_req)
    # with open('test{}.json'.format(query_month), 'w') as fp:
    #     fp.write(result_req)
    month_fee_data['bill_ext_calls'] = "0.00"
    month_fee_data['bill_ext_data'] = "0.00"
    month_fee_data['bill_ext_sms'] = "0.00"
    month_fee_data['bill_zengzhifei'] = "0.00"
    month_fee_data['bill_daishoufei'] = "0.00"
    month_fee_data['bill_qita'] = "0.00"
    try:
        result_list = month_bill_res['historyResultList']
        month_fee_data['bill_month'] = query_month
        month_fee_data['bill_amount'] = month_bill_res.get('nowFee', '0.00').replace(' ','')
        if month_fee_data['bill_amount'] in ['0.00', '0']:
            return False
        month_fee_data['bill_package'] = result_list[0].get('value', '0.00').replace(' ','')
        if month_bill_res.get('userInfo',{}).get('provincecode','') == "086":
            bill_package = re.findall(u'"name":".*月固定费","value":"(.*?)"',result_req)
            if bill_package:
                month_fee_data['bill_package'] = bill_package[0].replace(' ','')
        if month_bill_res.get('userInfo',{}).get('provincecode','') == "010":
            bill_package = re.findall(u'"name":".*炫铃功能费","value":"(.*?)"',result_req)
            if bill_package:
                month_fee_data['bill_package'] = bill_package[0].replace(' ','')
        bill_ext_calls = re.findall(u'"name":".*通话费","value":"(.*?)"',result_req)
        if bill_ext_calls:
            month_fee_data['bill_ext_calls'] = bill_ext_calls[0].replace(' ','')
        bill_ext_data = re.findall(u'"name":".*上网费","value":"(.*?)"',result_req)
        if bill_ext_data:
            month_fee_data['bill_ext_data'] = bill_ext_data[0].replace(' ','')
        bill_ext_sms = re.findall(u'"name":".*短信.*?费","value":"(.*?)"',result_req)
        if bill_ext_sms:
            month_fee_data['bill_ext_sms'] = bill_ext_sms[0].replace(' ','')
        bill_zengzhifei = re.findall(u'"name":".*增值业务费","value":"(.*?)"',result_req)
        if bill_zengzhifei:
            month_fee_data['bill_zengzhifei'] = bill_zengzhifei[0].replace(' ','')
        bill_daishoufei = re.findall(u'"name":".*代收费(信息费)","value":"(.*?)"',result_req)
        if bill_daishoufei:
            month_fee_data['bill_daishoufei'] = bill_daishoufei[0].replace(' ','')
        bill_qita = re.findall(u'"name":".*其他.*","value":"(.*?)"',result_req)
        if bill_qita:
            month_fee_data['bill_qita'] = bill_qita[0].replace(' ','')
    except:
        result_list = month_bill_res.get('result',{}).get('billinfo',[])
        month_fee_data['bill_month'] = query_month
        month_fee_data['bill_amount'] = month_bill_res.get('result', {}).get('allfee','0.00')
        if month_fee_data['bill_amount'] == '0.00':
            return False
        month_fee_data['bill_package'] = result_list[0].get('fee', '0.00')
        bill_ext_calls = re.findall(u'"fee":"(\d*.\d{2})","integrateitem":"语音通话费"',result_req)
        if bill_ext_calls:
            month_fee_data['bill_ext_calls'] = bill_ext_calls[0]
        bill_ext_data = re.findall(u'"fee":"(\d*.\d{2})","integrateitem":"上网费"',result_req)
        if bill_ext_data:
            month_fee_data['bill_ext_data'] = bill_ext_data[0]
        bill_ext_sms = re.findall(u'"fee":"(\d*.\d{2})","integrateitem":"短信通信费"',result_req)
        if bill_ext_sms:
            month_fee_data['bill_ext_sms'] = bill_ext_sms[0]
        bill_zengzhifei = re.findall(u'"fee":"(\d*.\d{2})","integrateitem":"增值业务费"',result_req)
        if bill_zengzhifei:
            month_fee_data['bill_zengzhifei'] = bill_zengzhifei[0]
        bill_daishoufei = re.findall(u'"fee":"(\d*.\d{2})","integrateitem":"代收费(信息费)"',result_req)
        if bill_daishoufei:
            month_fee_data['bill_daishoufei'] = bill_daishoufei[0]
        bill_qita = re.findall(u'"fee":"(\d*.\d{2})","integrateitem":".*其他.*"',result_req)
        if bill_qita:
            month_fee_data['bill_qita'] = bill_qita[0]
    return month_fee_data


