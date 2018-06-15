# -*- coding: utf-8 -*-
import random
import traceback
from dateutil.rrule import MONTHLY, rrule
import time
import re

import sys
reload(sys)
sys.setdefaultencoding("utf8")

from datetime import date
import datetime
from lxml import etree
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_unity
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_unity

class Crawler(BaseCrawler):
    """
    kwargs 包含
        'tel': str,
        'pin_pwd': str,
        'id_card': str,
        'full_name': unicode,
        'sms_code': str,
        'captcha_code': str
    錯誤等級
        0: 成功
        1: 帳號密碼錯誤
        2: 認證碼錯誤
        9: 其他錯誤
    """

    def __init__(self, **kwargs):
        """
        初始化  详单页：http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000776
        """
        super(Crawler, self).__init__(**kwargs)
        self.today = datetime.date.today()

    def need_parameters(self, **kwargs):
        return['pin_pwd']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        ProvinceID = '30'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        index_url = 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000776'
        for _ in range(3):
            code, key, resp = self.get(index_url)
            if code != 0:
                continue

            if kwargs['tel'][:3] in resp.text and kwargs['tel'][3:7] in resp.text and kwargs['tel'][7:] in resp.text:
                return 0, "success"
            else:
                self.log("crawler", "website_busy_error", resp)
                return 9, "website_busy_error"
        else:
            self.log("crawler", "website_busy_error:网络请求错误", resp)
            return 9, "website_busy_error"

    def send_verify_request(self, **kwargs):
        url = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10009&toStUrl=http://nx.189.cn/jt/bill/xd/?fastcode=20000776&cityCode=nx'
        header = {'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000776'}
        code, key, resp = self.get(url,headers= header)
        if code != 0:
            return code, key, ""

        areacode_url = 'http://nx.189.cn/jt/bill/xd/?fastcode=20000776&cityCode=nx'
        header = {
            'Host': 'nx.189.cn',
            'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000776',
            'Connection':'keep-alive'
        }

        code, key, resp = self.get(areacode_url,headers=header)
        if code != 0:
            return code, key, ""
        if kwargs['tel'] in resp.text and "详单查询结果" in resp.text:
            try:
                areacode = re.findall(r'areaCode" value="(.*?)"',resp.text)[0]
            except:
                error = traceback.format_exc()
                self.log("crawler", "html_error:{}".format(error), resp)
                return 9, "html_error", ""
        else:
            self.log("website", "个人数据返回为空", resp)
            return 9, "website_busy_error", ""

        get_num_url = 'http://nx.189.cn/bfapp/buffalo/CtQryService'
        data = """
                <buffalo-call>
                <method>getSelectedFeeProdNum</method>
                <string>{}</string>
                <string>{}</string>
                <string>2</string>
                </buffalo-call>
                """.format(areacode, kwargs['tel'])   #0951  areaCode
        header = {'Referer':'http://nx.189.cn/jt/bill/xd/?fastcode=20000776&cityCode=nx'}
        code, key, resp = self.post(get_num_url, data=data,headers=header)
        if code != 0:
            return code, key, ""
        if resp.text.strip() != "<buffalo-reply><string></string></buffalo-reply>":
            self.log("crawler", "登录超时", resp)
            return 9, "website_busy_error", ""

        check_sms_url = "http://nx.189.cn/bfapp/buffalo/CtQryService"
        data = """
                <buffalo-call>
                <method>checkIsBillSMSShow</method>
                </buffalo-call>
                """
        code, key, resp = self.post(check_sms_url, data=data)
        if code != 0:
            return code, key, ""
        if "需要验证" in resp.text:
            sendsms_url = 'http://nx.189.cn/bfapp/buffalo/CtSubmitService'
            data = '''
                    <buffalo-call>
                    <method>sendDXYzmForBill</method>
                    </buffalo-call>
                    '''
            # headers = {'Referer':'http://nx.189.cn/jt/bill/xd/?fastcode=10000501&cityCode=nx'}
            code, key, resp = self.post(sendsms_url, data=data)
            if code != 0:
                return code, key, ""
            if"短信已发送至" in resp.text and "base.Success" in resp.text:
                return 0, "success", ""
            else:
                self.log("crawler", "send_sms_error", resp)
                return 9, "send_sms_error", ""
        else:
            self.log("crawler", "unknown_error", resp)
            return 9, "unknown_error", ""

    def verify(self, **kwargs):
        verify_url = 'http://nx.189.cn/bfapp/buffalo/CtQryService'
        data = """
            <buffalo-call>
            <method>validBillSMS</method>
            <string>{}</string>
            <string>{}</string>
            </buffalo-call>
        """.format(kwargs['tel'], kwargs['sms_code'])
        code, key, resp = self.post(verify_url, data = data)
        if code != 0:
            return code, key
        if "base.Error" in resp.text and "验证失败" in resp.text:
            self.log("user", "短信验证码错误", resp)
            return 2, "verify_error"
        elif "base.Success" in resp.text and "验证成功" in resp.text:
            return 0, "success"
        else:
            self.log("crawler", "二次验证未知错误", resp)
            return 9, "unknown_error"

    def crawl_info(self, **kwargs):
        user_info = {}
        checkmy_url = 'http://www.189.cn/dqmh/my189/checkMy189Session.do'
        data = {'fastcode':'10000523'}
        headers = {'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000776'}
        code, key, resp = self.post(checkmy_url,data = data,headers=headers)
        if code != 0:
            return code, key
        if 'status":"2' in resp.text and 'msg":null' in resp.text:
            info_url = 'http://nx.189.cn/bfapp/buffalo/CtQryService'
            data = """
                    <buffalo-call>
                    <method>getCustAndContInfo</method>
                    <string>1</string>
                    </buffalo-call>
                    """
            headers = {'Referer': 'http://nx.189.cn/jt/zl/wdzl/?fastcode=10000523&cityCode=nx'}
            code, key, resp = self.post(info_url,data=data,headers = headers)
            if code != 0:
                return code, key
            try:
                xml = etree.HTML(resp.text)
                mapa = xml.xpath('//buffalo-reply/map/map')[1]
                for every_map in mapa:
                    user_info['full_name'] = every_map.xpath('//string/text()')[6]
                    open_date_str = every_map.xpath('//string/text()')[24]  #20180521
                    opendate = "{}/{}/{} 00:00:00".format(open_date_str[:4],open_date_str[4:6],open_date_str[6:8])
                    open_date = self.time_stamp(opendate)
                    if open_date[0]:
                        user_info['open_date'] = str(open_date[1])
                    else:
                        user_info['open_date'] = ""
                user_info['id_card'] = xml.xpath('//buffalo-reply/map/map[3]/string[2]/text()')[0]
                user_info['address'] = ""
            except:
                error = traceback.format_exc()
                self.log("crawler", "解析用户数据失败：{}".format(error), resp)
                return 9, "html_error", {}
            return 0, "success", user_info
        else:
            self.log("crawler", "未知原因导致获取个人信息失败", resp)
            return 9, "html_error", {}


    def crawl_call_log(self, **kwargs):
        call_logs, miss_list, pos_miss_list = [], [], []
        message, response = "", ""
        error_num = 0
        log_for_retrys = []
        retrys_limit = 4
        full_time = 60.0
        st_time = time.time()
        time_fee = 0
        rand_time = random.randint(20, 40) / 10.0
        month_list = list(
            rrule(MONTHLY,
                  count=5,
                  bymonthday=-1,
                  dtstart=self.today + relativedelta(months=-5)))
        month_list.append(self.today)
        month_retry_list = [("{}{:0>2}".format(i.year, i.month), '{:0>2}'.format(i.day),self.max_retry) for i in month_list]
        while month_retry_list:
            month, day, retrys = month_retry_list.pop(0)
            retrys -= 1
            # if retrys < -retrys_limit:
            #     self.log("crawler", "重试次数完毕", "")
            #     miss_list.append(month)
            #     continue
            log_for_retrys.append((month, retrys, time_fee))
            #请求详单
            call_log_url = 'http://nx.189.cn/bfapp/buffalo/CtQryService'
            data = """
                    <buffalo-call>
                    <method>qry_sj_yuyinfeiqingdan</method>
                    <string>{}{}01</string>  
                    <string>{}{}{:0>2}</string>
                    </buffalo-call>
                    """.format(month[:4],month[4:7],month[:4],month[4:7], day)
            headers = {'Referer': 'http://nx.189.cn/jt/bill/xd/?fastcode=10000501&cityCode=nx'}
            code, key, resp = self.post(call_log_url, data=data,headers=headers)
            if code != 0:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                else:
                    self.log("crawler", "获取详单失败{}".format(key), resp)
                    miss_list.append(month)
                continue
            code, key, msg, result = self.call_log_get(resp.text, month)
            if code == 0:
                if result:
                    call_logs.extend(result)
                else:
                    if retrys >= 0:
                        time_fee = time.time() - st_time
                        month_retry_list.append((month, day, retrys))
                    elif time_fee < full_time:
                        time.sleep(rand_time)
                        time_fee = time.time() - st_time
                        month_retry_list.append((month, day, retrys))
                    else:
                        self.log("crawler", "详单或许缺失", resp)
                        pos_miss_list.append(month)
                continue
            else:
                message, response = key, resp
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retry_list.append((month, day, retrys))
                else:
                    self.log("crawler", u"获取详单失败{}".format(key), resp)
                    miss_list.append(month)
        if message == "html_error":
            self.log("crawler", message, response)
            error_num += 1
        self.log("crawler", "重试记录：{}".format(log_for_retrys), "")
        self.log("crawler", "缺失: {}, 可能缺失: {}, 部分缺失: {}".format(miss_list, pos_miss_list, []), "")
        if len(pos_miss_list) + len(miss_list) == 6:
            if error_num > 0:
                return 9, "crawl_error", [], [], []
            else:
                return 9, "website_busy_error", [], [], []
        return 0, "success", call_logs, miss_list, pos_miss_list


    def call_log_get(self,resp_text,month):
        """
        `call_tel` | string | 18202541892 | 电话号码 |
       | `call_cost` | string | 0.00 | 通话费用 |
       | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
       | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
       | `call_type` | string | 本地 | 通话类型（本地, 长途） |
       | `call_from` | string | 北京市 | 本机通话地 |
       | `call_to` | string | 长沙市 | 对方归属地 |
       | `call_duration` | integer | 300 | 通话时长(秒),
       :param resp:
       :param month:
       :return:
        """
        call_log = []
        if "allCount</string><int>0" in resp_text and "成功" in resp_text:
            return 0, "success", "", []

        elif "成功" in resp_text and "allCount" in resp_text:
            try:
                xml = etree.HTML(resp_text)
                maps = xml.xpath('//buffalo-reply/map/list/map')
                for i in range(1, len(maps)+1):
                    call = {}
                    maps = xml.xpath('//buffalo-reply/map/list/map[{}]/string/text()'.format(i))
                    call['call_tel'] = maps[7]
                    call_time = (str(month[:4])+'-'+maps[3]).replace("-", "/")
                    result, call_time = self.time_stamp(call_time)
                    if not result:
                        self.log("crawler", "时间转换失败{}{}".format(call_time, resp_text), "")
                        return 9, 'html_error', 'html_error when transform call_time to time_stamp : %s' % call_time, []
                    call['call_time'] = call_time
                    call_from, error = self.formatarea(maps[13])
                    if not call_from:
                        call_from = maps[13]
                    call['call_from'] = call_from
                    call['call_method'] = maps[9]
                    call['call_duration'] = str(self.split_time(maps[11]))
                    call['call_cost'] = '%.2f' %(float(maps[15])/100)
                    call['call_type'] = maps[17]
                    call_to, error = self.formatarea(maps[5])
                    if not call_to:
                        call_to = maps[5]
                    call['call_to'] = call_to
                    call['month'] = month
                    call_log.append(call)
            except:
                error = traceback.format_exc()
                self.log("crawler", "获取xpath失败{}".format(error), resp_text)
                return 9, "html_error"
        else:
            self.log("crawler", "website_busy_error:unknown_error", resp_text)
            return 9, "website_busy_error", "", []
        return 0, "success", "成功", call_log

    def split_time(self,time_str):
        line = time_str.split(":")
        seconds = int(line[0]) * 3600 + int(line[1]) * 60 + int(line[2])
        return seconds

    def time_stamp(self, time_str):
        try:
            timeArray = time.strptime(time_str, "%Y/%m/%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            return True, str(timeStamp)
        except:
            error = traceback.format_exc()
            return False, error

    def crawl_phone_bill(self, **kwargs):
        """
        bill_month	    string	201612	账单月份
        bill_amount     string	10.00	账单总额
        bill_package	string	10.00	套餐及固定费
        bill_ext_calls	string	10.00	套餐外语音通信费
        bill_ext_data	string	10.00	套餐外上网费
        bill_ext_sms	string	10.00	套餐外短信费
        bill_zengzhifei	string	10.00	增值业务费
        bill_daishoufei	string	10.00	代收业务费
        bill_qita       string	10.00	其他费用
        :param kwargs:
        :return:
        """
        data_list, miss_list = [], []
        today = date.today()
        message = ""
        error_num= 0
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            url = 'http://www.189.cn/dqmh/homogeneity/balanceOutDetailQuery.do'
            data = {
                'billingcycle':query_month,
            }
            headers = {'Referer': 'http://www.189.cn/dqmh/homogeneity/initCost.do?menuType=balanceoutquery&fastcode=20000779&cityCode=nx'}
            for _ in range(self.max_retry):
                code, key, resp = self.post(url, data=data, headers=headers)
                if code != 0:
                    message = "network_request_error"
                    continue
                self.log("crawler","线上记录账单内容", resp)
                try:
                    b = re.sub(r'\s+', '', resp.text)
                    bill_fee = {}
                    set_key = set(['bill_month', 'bill_amount', 'bill_package', 'bill_ext_calls', 'bill_ext_data',
                                   'bill_ext_sms','bill_zengzhifei', 'bill_daishoufei', 'bill_qita'])
                    bill_fee['bill_month'] = query_month
                    bill_fee['bill_amount'] = '%.2f' % float((re.findall(r'<spanclass="fs24">(.*?)<em>', b)[0]))  # 1.59
                    if u"套餐月使用费" in b:
                        bill_fee['bill_package'] = '%.2f' % float((re.findall(ur'套餐月使用费<span>(.*?)元', b)[0]))  # 1.29
                    if u"语音通信费" in b:
                        bill_fee['bill_ext_calls'] = '%.2f' % float((re.findall(ur'语音通信费<span>(.*?)元</span>', b)[0]))  # 0.10
                    if u"短信彩信费" in b:
                        bill_fee['bill_ext_sms'] = '%.2f' % float((re.findall(ur'短信彩信费<span>(.*?)元</span>', b)[0]))  # 0.20
                    for extra_keys in list(set_key - set(bill_fee.keys())):
                        bill_fee[extra_keys] = "0.00"
                    data_list.append(bill_fee)
                    break
                except:
                    message = traceback.format_exc()
                    continue
            else:
                if message != "network_request_error":
                    self.log("crawler", "html_error:{}".format(message), "")
                    error_num += 1
                miss_list.append(query_month)
                break
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5 and error_num > 0:
            return 9, "crawl_error", [], miss_list
        return 0, "success", data_list, miss_list

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "15378996764"
    USER_PASSWORD = "850295"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
