# -*- coding: utf-8 -*-
import base64
import traceback
import datetime
import time
import sys
import re
from lxml import etree

import request_params
from datetime import date

import des_js
import random

# 这段代码是用于解决中文报错的问题
reload(sys)
sys.setdefaultencoding("utf8")

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from crawler.china_telecom_tool import login_unity
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
        初始化
        """
        super(Crawler, self).__init__(**kwargs)
        self.pin_pwd_error_times = 0

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):

        ProvinceID = '14'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        url = 'http://www.189.cn/login/sso/ecs.do?method=linkTo&platNo=10014&toStUrl=http://fj.189.cn/newcmsweb/commonIframe.jsp?URLPATH=/service/bill/index.jsp?TYPE=detail&fastcode=01420651&cityCode=fj'
        code, key, response = self.get(url)
        if code != 0:
            return code, key
        return 0, "success"

    def send_verify_request(self, **kwargs):

        data = """
            <buffalo-call>
            <method>getCDMASmsCode</method>
            <map>
            <type>java.util.HashMap</type>
            <string>PHONENUM</string>
            <string>{}</string>
            <string>PRODUCTID</string>
            <string>50</string>
            <string>CITYCODE</string>
            <string></string>
            <string>I_ISLIMIT</string>
            <string>1</string>
            <string>QUERYTYPE</string>
            <string>BILL</string>
            </map>

            </buffalo-call>
        """.format(kwargs['tel'])

        url = 'http://fj.189.cn/BUFFALO/buffalo/QueryAllAjax'
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, ''

        if u'短信随机密码已经发到您的手机' in resp.text:
            return 0, 'success', ''
        elif u'系统升级公告' in resp.text:
            return 9, 'website_maintaining_error', ''
        elif u'短信随机码过于频繁' in resp.text:
            self.log('user', u'短信随机码过于频繁', resp)
            return 9, 'send_sms_too_quick_error', ''
        else:
            self.log('crawler', 'send_sms_error', resp)
            return 9, 'send_sms_error', ''

    def verify(self, **kwargs):

        url = 'http://fj.189.cn/service/bill/tanChu.jsp'
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        params = {
            'PRODNO': kwargs['tel'],
            'PRODTYPE': '50',
            'CITYCODE': '',
            'MONTH': today_month,
            'SELTYPE': '1',
        }
        headers = {
            'Referer': 'http://fj.189.cn/service/bill/detail.jsp'
        }
        code, key, resp = self.get(url, params=params, headers=headers)
        if code != 0:
            return code, key
        try:
            dom = etree.HTML(resp.text)
            data = {}
            data['PRODNO'] = dom.xpath('//*[@id="PRODNO"]/@value')[0]
            data['PRODTYPE'] = dom.xpath('//*[@id="PRODTYPE"]/@value')[0]
            data['CITYCODE'] = dom.xpath('//*[@id="CITYCODE"]/@value')[0]
            data['SELTYPE'] = dom.xpath('//*[@id="SELTYPE"]/@value')[0]
            data['MONTH'] = dom.xpath('//*[@id="MONTH"]/@value')[0]
            data['PURID'] = dom.xpath('//*[@id="PURID"]/@value')[0]
            data['email_empoent'] = dom.xpath('//*[@id="email_empoent"]/@value')[0]
            data['email_module'] = dom.xpath('//*[@id="email_module"]/@value')[0]
            data['randomPwd'] = kwargs['sms_code']
            data['serPwd50'] = des_js.get_pwd(data['email_empoent'], data['email_module'], kwargs['pin_pwd'])
        except:
            err_msg = traceback.format_exc()
            self.log('crawler', 'html_error:{}'.format(err_msg), resp)
            return 9, 'html_error'

        url = "http://fj.189.cn/service/bill/trans.jsp"
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key
        if u'手机通话清单' in resp.text:
            return 0, 'success'

        if u'短信随机码不正确或已失效' in resp.text:
            self.log('user', 'verify_error', resp)
            return 2, 'verify_error'
        elif u'系统忙，请稍后再试' in resp.text:
            self.log("website", 'website_busy_error', resp)
            return 9, 'website_busy_error'
        elif u'密码验证错误' in resp.text:
            self.log('user', 'pin_pwd_error', resp)
            return 1, 'pin_pwd_error'
        elif u'该号码还没实名' in resp.text:
            self.log("user", u"号码未实名", resp)
            return 9, "real_name_registration_error"
        elif u'不能办理业务' in resp.text:
            self.log("user", u"未知原因不能办理业务", resp)
            return 9, "crawl_error"
        else:
            if 'location' in resp.text:
                url = re.findall(u"location='(.*?)'", resp.text)
                url = 'http://www.189.cn' + url[0]
                code, key, resp = self.get(url)
                return code, key
            self.log('crawler', 'unknown_error', resp)
            return 9, 'unknown_error'

    def crawl_info(self, **kwargs):
        return 9, 'unknown_error', {}

    def crawl_call_log(self, **kwargs):

        crawler_error_num = 0
        missing_list = []
        possibly_missing_list = []
        headers = {
            'Referer': 'http://fj.189.cn/service/bill/trans.jsp',
        }
        call_log = []
        search_month = [x for x in range(0, -6, -1)]
        call_log_url = 'http://fj.189.cn/service/bill/result/mobile/mobile_call_result.jsp'
        today = date.today()
        search_month_retrys = [(x, self.max_retry) for x in search_month]
        st_time = time.time()
        full_time = 50.0
        time_fee = 0
        rand_time = random.randint(23, 45) / 10.0
        log_for_retry = []
        while search_month_retrys:
            each_month, retrys = search_month_retrys.pop(0)
            retrys -= 1
            query_date = today + relativedelta(months=each_month)
            call_month = "%d%02d" % (query_date.year, query_date.month)
            call_log_data = request_params.call_log_data(each_month, **kwargs)
            log_for_retry.append((call_month, retrys, time_fee))
            # for retry in xrange(self.max_retry):
            code, key, resp = self.get(call_log_url, params=call_log_data, headers=headers)
            if code != 0:
                if retrys >= 0:
                    time_fee += time.time() - st_time
                    search_month_retrys.append((each_month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee += time.time() - st_time
                    search_month_retrys.append((each_month, retrys))
                else:
                    missing_list.append(call_month)
                    self.log('crawler', '详单查询失败', resp)
                continue
            else:
                if u'对不起，暂无您所查询的数据清单' in resp.text :
                    possibly_missing_list.append(call_month)
                    self.log('crawler', '详单为空', resp)
                    continue
                elif u'您输入的产品号无法正确查询' in resp.text:
                    # 改code值 为了记录到缺失列表
                    possibly_missing_list.append(call_month)
                    self.log('crawler', '详单为空', resp)
                    continue

            # 开始解析详单
            code, key, message, call_month_log = self.call_log_get(resp, call_month)
            if code != 0:
                if retrys >= 0:
                    time_fee += time.time() - st_time
                    search_month_retrys.append((each_month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee += time.time() - st_time
                    search_month_retrys.append((each_month, retrys))
                else:
                    missing_list.append(call_month)
                    self.log('crawler', '详单查询失败', resp)
                continue
            if call_month_log:
                call_log.extend(call_month_log)
                continue
            else:
                if retrys >= 0:
                    time_fee += time.time() - st_time
                    search_month_retrys.append((each_month, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee += time.time() - st_time
                    search_month_retrys.append((each_month, retrys))
                else:
                    self.log('crawler', '详单为空', resp)
                    possibly_missing_list.append(call_month)

        possibly_missing_list.sort(reverse=True)
        missing_list.sort(reverse=True)
        self.log("crawler", "重试记录: {}".format(log_for_retry), "")
        # print 'missing_list:', missing_list
        # print 'possibly_missing_list:', possibly_missing_list
        if len(missing_list+possibly_missing_list) == 6:
            if crawler_error_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success",  call_log, missing_list, possibly_missing_list

    def call_log_get(self, response, call_month):
        """
        `call_tel` | string | 18202541892 | 电话号码 |
        | `call_cost` | string | 0.00 | 通话费用 |
        | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
        | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
        | `call_type` | string | 本地 | 通话类型（本地, 长途） |
        | `call_from` | string | 北京市 | 本机通话地 |
        | `call_to` | string | 长沙市 | 对方归属地 |
        | `call_duration` | integer | 300 | 通话时长(秒),
        """
        call_month_log = []
        try:
            html_tree = etree.HTML(response.text)
            trs = html_tree.xpath('//*[@class="jtqd_table2"]/table/tr')
            for item in trs:
                data = {}
                tds = item.xpath('./td/text()')
                if len(tds) == 7:
                    data['month'] = call_month
                    data['call_time'] = self.time_format(tds[1])
                    data['call_duration'] = self.time_format_second(tds[2])
                    data['call_method'] = tds[3]
                    # data['call_from'] = tds[4]

                    raw_call_from = tds[4].strip()
                    call_from, error = self.formatarea(raw_call_from)
                    if call_from:
                        data['call_from'] = call_from
                    else:
                        # self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                        data['call_from'] = raw_call_from

                    data['call_tel'] = tds[5]
                    data['call_cost'] = tds[6]
                    data['call_to'] = ''
                    data['call_type'] = ''
                    call_month_log.append(data)
        except:
            error = traceback.format_exc()
            return 9, 'html_error', 'html_error : %s' % error, []
        return 0, 'success', 'success', call_month_log

    # 将通话起始时间转换为时间戳
    def time_format(self, timeoo):
        call_time = re.findall('\d{2}', timeoo)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[
            3] + ' ' + call_time[4] + ':' + call_time[5] + ':' + call_time[6]
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

    # 将通话时长转换为秒
    def time_format_second(self, time_str):
        time_str = time_str.encode('utf-8')
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
        real_time = h * 60 * 60 + m * 60 + s
        return str(real_time)

    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        crawler_num = 0
        phone_bill = list()
        headers = {
            'Referer': 'http://fj.189.cn/service/bill/bill.jsp'
        }
        month_bill_url = 'http://fj.189.cn/service/bill/custbill.jsp'
        # 查不到当月账单
        for month in self.__monthly_period(5, '%Y%m'):
            post_data = request_params.month_bill_data(month, **kwargs)
            for retry in range(self.max_retry):
                code, key, resp = self.post(month_bill_url, data=post_data, headers=headers)
                if code != 0:
                    continue
                else:
                    break
            else:
                missing_list.append(month)
                continue
            # 开卡前的账单缺失不加入缺失列表
            if u'没有找到对应的产权客户' in resp.text:
                continue
            bill_amount = re.findall(u'<li><span class="fw_b">本期费用合计：(.*?)元</span></li>', resp.text)
            bill_package = re.findall(u'<div class="fyxx_bot_a">\s+<span class="fr">\s+<span>\s+(.*?)\s+</span>\s+'
                                      u'</span>\s+<span class="leftk">&nbsp;&nbsp;&nbsp;&nbsp;套餐月基本费</span>', resp.text)
            month_bill = {
                'bill_month': month,
                'bill_amount': bill_amount[0] if len(bill_amount) > 0 else '',
                'bill_package': bill_package[0] if len(bill_package) > 0 else '',
                'bill_ext_calls': '',
                'bill_ext_data': '',
                'bill_ext_sms': '',
                'bill_zengzhifei': '',
                'bill_daishoufei': '',
                'bill_qita': ''
            }
            if month_bill['bill_amount'] == '' or month_bill['bill_amount'] == '0.00':
                missing_list.append(month)
                crawler_num += 1
                self.log('crawler', '月度账单为空', resp)
            else:
                phone_bill.append(month_bill)

        # print 'missing_list:', missing_list
        if len(missing_list) == 5:
            if crawler_num > 0:
                return 9, 'crawl_error', phone_bill, missing_list
            return 9, 'website_busy_error', phone_bill, missing_list
        return 0, 'success', phone_bill, missing_list

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset + 1)).strftime(strf)


if __name__ == '__main__':
    c = Crawler()

    USER_ID = "17750213608"
    USER_PASSWORD = "003802"
    # full_name = "青培"
    # id_card = "14072319930902003X"


    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
