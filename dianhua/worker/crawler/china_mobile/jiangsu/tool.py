# -*- coding: utf-8 -*-
import json
import re
import time
import traceback
# from com.format_callfrom import formatArea
import lxml.html
# from Crypto.Cipher import AES

kv_mapping = {
    'call_duration': 'callDuration',
    'call_from': 'visitArear',
    'call_tel': 'otherParty',
    'call_time': 'startTime'
}


def time_transform(time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
    is_time_str = r".*?(\d{2,4})"
    is_time = re.findall(is_time_str, time_str)
    if is_time:
        time_type = time.strptime(time_str.encode(bm), str_format)
        return str(int(time.mktime(time_type)))
    else:
        return ""


def time_format(time_str, **kwargs):
    exec_type = 1
    time_str = time_str.encode('utf-8')
    if 'exec_type' in kwargs:
        exec_type = kwargs['exec_type']
    if (exec_type == 1):
        xx = re.match(r'(.*时)?(.*分)?(.*秒)?', time_str)
        h, m, s = 0, 0, 0
        if xx.group(1):
            hh = re.findall('\d+', xx.group(1))[0]
            h = int(hh)
        if xx.group(2):
            mm = re.findall('\d+', xx.group(2))[0]
            m = int(mm)
        if xx.group(3):
            ss = re.findall('\d+', xx.group(3))[0]
            s = int(ss)
        real_time = h*60*60 + m*60 + s
    if (exec_type == 2):
        if not time_str:
            h, m, s = 0, 0, 0
            return 9, "success", "返回的时间为空{}".format(time_str), ""
        else:
            xx = re.findall(r'\d+', time_str)
            if len(xx) == 3:
                h, m, s = map(int, xx)
            else:
                # 在官网返回的数据中会夹杂异常数据, 并且无法恢复成正常数据, 跳过, 
                h, m, s = 0, 0, 0
                return 0, "website_error", "msg:unexpect time type 返回时间解析失败{}".format(time_str), ""
        real_time = h*60*60 + m*60 + s
    return 0, "succes", "", str(real_time)


def parse_call_record_short(html, query_month, **kwargs):
    result_list = []
    try:
        da_dict = json.loads(html)
    except:
        error = traceback.format_exc()
        return 9, "json_error", error, []

    if 'resultObj' not in da_dict or da_dict['resultObj'] is None:
        return 9, "unknown_error", "msg:unknown_error get call_log faile{}".format(html), []

    short_data = da_dict['resultObj']['qryResult']['vpmnBillDetail']
    self_obj = kwargs['self_obj']
    if len(short_data) <= 1:
        return 9, "no_data", "未发现需要的数据, 源文件为: {}".format(html), []
    for i in short_data[1:]:
        data = {}
        data['call_month'] = query_month
        data['call_to'] = ""
        raw_call_from = i.get("visitArear", "")
        call_from, error = self_obj.formatarea(raw_call_from)
        # call_from, error = formatArea(raw_call_from)
        if not call_from:
            call_from = raw_call_from
            # print call_from
            self_obj.log("crawler", "{}-{}".format(error, raw_call_from), "")
        data['call_from'] = call_from
        data['call_cost'] = i.get("chFee", "0.0")
        raw_call_duration = i.get("callDuration", "00:00:00")
        level, key, message, value = time_format(raw_call_duration, exec_type=2)
        if level != 0:
            return level, key, message, []
        data['call_duration'] = value
        raw_call_time = i.get("cdrStartDate", "")
        data['call_time'] = time_transform(raw_call_time)
        data['call_tel'] = i.get("otherParty", "")
        data['call_method'] = i.get("statusType", "")
        data['call_type'] = ""
        result_list.append(data)
    return 0, "success", "", result_list


def parse_call_record(html, query_month, **kwargs):
    records = []
    try:
        obj = json.loads(html)
        # 本月无账单, 同样会有resultObj
        if 'resultObj' not in obj or obj['resultObj'] is None:
            return 9, "unknown_error", "msg:unknown_error get call_log faile{}".format(html), []
        # 当本月无详单时obj['resultObj']['qryResult']['gsmBillDetail'][1:] 长度为0
        data_of_call_log = obj['resultObj']['qryResult']['gsmBillDetail'][1:]
        if len(data_of_call_log) == 0:
            return 9, "no_data", "未发现需要的数据, 源文件为: {}".format(html), []
        for record_element in data_of_call_log:
            level, key, message, get_parse_record = parse_record_element(record_element, query_month, self_obj=kwargs['self_obj'])
            if level == 0:
                if key == 'website_error':
                    continue
                record = get_parse_record
            else:
                return level, key, message, get_parse_record
            records.append(record)
    except:
        error = traceback.format_exc()
        return 9, 'json_error', error, []
    return 0, "success", "", records


def parse_record_element(record_element, query_month, **kwargs):
    record = {}
    for k, v in kv_mapping.items():
        if k == 'call_duration':
            level, key, message, value = time_format(record_element[v], exec_type=2)
            if level != 0:
                return level, key, message, []
            else:
                record[k] = value
        elif k == 'call_time':
            record[k] = time_transform(record_element[v])
        else:
            record[k] = record_element[v]

    # call_to
    record['call_to'] = u''
    self_obj = kwargs['self_obj']
    raw_call_from = record['call_from']
    call_from, error = self_obj.formatarea(raw_call_from)
    if not call_from:
        call_from = raw_call_from
        self_obj.log("crawler", "{}-{}".format(error, raw_call_from), "")
    record['call_from'] = call_from
    # call_cost
    total_fee = record_element.get('realCfee', 0.0) + record_element.get('realLfee', 0.0)
    record['call_cost'] = str(total_fee)

    # call_method
    record['call_method'] = record_element['roamType']

    # call_type
    if u'本地' in record_element['roamType']:
        record['call_type'] = u'本地'
    elif u'长途' in record_element['roamType']:
        record['call_type'] = u'长途'
    else:
        record['call_type'] = u'国内漫游'

    record['month'] = query_month
    return 0, 'success', '', record


if __name__ == '__main__':
    data = """{"resultMsg":"系统忙，请稍候再试！","logicCode":"0","ELst":[],"systemCode":"","resultCode":"0","success":true,"resultObj":{"startTime":"20171101","qryResult":{"errorMessage":"成功","mpmusicBillDetail":[],"ac121BillDetail":[],"montnetBillDetail":[],"smsBillDetail":[],"gsmMagaBillDetail":[],"cdrsPointBillDetail":[],"wlanBillDetail":[],"cdrsBillDetail":[],"meetBillDetail":[],"accessId":"S0012018030615232610173947310.32.229.106:10012","is_end":"","bossCode":"","ineSmsBillDetail":[],"gprsBillDetail":[],"resultCode":"0","contentList":[{"nameData":"通信方式~对方号码~集团短号~起始时间~通话时长~通信地点~国内话费(元)~国际及港澳台话费(元)~应收其他话费(元)~小计(元)~套餐费(元)~套餐信息~使用者~高清","keyV":"8:1005:-1","isEnd":"1","ddbNextno":"0","lengthData":"30~24~6~14~6~40~12~12~12~12~12~256~11~4"}],"key":"","mmsBillDetail":[],"cmnetBillDetail":[],"gsmVideoBillDetail":[],"gsmBillDetail":[],"ispBillDetail":[],"ipcarBillDetail":[],"ussdBillDetail":[],"personalBroBill":[],"errorCode":"0","isp2BillDetail":[],"vpmnBillDetail":[{"callDuration":"6","statusType":"30","otherFee":12,"realCfee":0,"cdrStartDate":"14","payFlag":"","startTime":"","chFee":12,"realLfee":0,"visitArear":"40","totalFee":12,"interGATFee":12,"shortNum":"6","feeItem01":12,"serviceCode":"","tpRemark":"256","user":"11","otherParty":"24","highDefinition":"4"},{"callDuration":"00:00:38","statusType":"主叫","otherFee":0,"realCfee":0,"cdrStartDate":"2017-11-01 15:16:54","payFlag":"","startTime":"","chFee":0,"realLfee":0,"visitArear":"苏州","totalFee":0,"interGATFee":0,"shortNum":"","feeItem01":0,"serviceCode":"","tpRemark":"5元包家庭500分钟和网内国内主叫100分钟（2014版，58元月最低消费，不足需补齐）","user":"13862553775","otherParty":"15995792212","highDefinition":"否"}],"lbsBillDetail":[]},"qryInterval":"2017-11-01 至 2017-11-30","query_ym":["201710","201711","201712","201801","201802","201803"],"realMobile":"13862553775","endTime":"20171130","user":{"agentLevel":"","ssoSMSCookieStr":"","userCounty":0,"isOpenSXZPlan":1,"tempMobile":"","tel":"","score":"","userType":"1","userState":0,"newSsoCookieStr":"","surveyStatus":"","balance":"","loginSource":1,"musicInfo":null,"mpoint":"","needJJKUserInfo":0,"city_jbNum":"SZDQ","userId":"","userName":"于宙","userpayMode":"","ebBalance":"","userBrandNum":"","agentCustomId":"","custIcNo":"","agentUserId":"","brand_jbNum":"QQT","userApplyDate":"","email":"","sessionId":"","contactName":"","city_busiNum":"","activeTime":"","emailInfo":null,"mobile":"13862553775","userDetail":0,"isorder4gprod":"","vipUserHgreade":0,"userAreaNum":"11","contactAddr":"","userAreaName":"","contactTel":"","brand_busiNum":"","agentPwd":"","lastSsoActiveTime":0,"isHost":0,"bossCode":"","mobilePwd":"","brand_jbNum_name":"全球通","brand_busiNum_name":"全球通","custIcType":0,"email_139":"","contactEmail":"","encryptInfo":"","postCode":"","userCountyName":"","jjkUserSchool":"","ssoCookieStr":""}}}"""
    
    class A(object):
        def __init__(self):
            self.error_msg = ""
            self.suc_err = "success"
            self.error_code = 9
            self.error_desc = ""
            self.error_msg = ""
            self.run_times = 2

    a = A()
    d = parse_call_record_short(data, '201712', self_obj=None)
    print d
    print len(d)
