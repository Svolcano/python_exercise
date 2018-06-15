#!/user/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/28 15:05
# @Author  : zhangjun
# Title    :

import random
import re
import traceback
import datetime
import sys
from lxml import etree

reload(sys)
sys.setdefaultencoding("utf8")

import base64
from des_js import des_encode
from fake_useragent import UserAgent
from datetime import date,datetime
import time
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    sys.path.append('../../..')
    sys.path.append('../../../..')
    sys.path.append('../../../../..')
    from worker.crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


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
        self.session.headers.update({'User-Agent': UserAgent().safari})

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        start_url = 'http://waphn.189.cn'
        code, key, resp = self.get(start_url)
        if code != 0:
            return code, key

        # 获取加密所需参数
        url = 'http://waphn.189.cn/js/RSA/RSA.js'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key
        try:
            module = re.findall('this.m = biFromHex\("(\S+)"\);', resp.text)[0]
            pwd = des_encode('10001', module, kwargs['pin_pwd'])
            tel = base64.b64encode(kwargs['tel'])
        except:
            error = traceback.format_exc()
            self.log('crawler', '加密出错：{}'.format(error), resp)
            return 9, 'crawler_failed'

        form_data = {
            'loginModel': '',
            'reUrl': '/selfservice/usercenter/index.do',
            'accountType': '2000004',
            'pwdType': '1',
            'phoneNum': tel,
            'areaCode': '0731',
            'phoneNum1': kwargs['tel'],
            'phoneNum2': '',
            'phoneNum3': '',
            'servicePwd': pwd,
            'vicode': '',
        }

        # 4位数字
        codetype = 1004
        for i in range(self.max_retry):
            url = 'http://waphn.189.cn/common/Verification/patchca.do?code=loginCode&rand='
            headers = {"Referer": "http://waphn.189.cn/user/login/toLogin.do?reUrl=/selfservice/usercenter/index.do"}
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key
            try:
                key, result, cid = self._dama(resp.content, codetype)
            except:
                msg = traceback.format_exc()
                self.log('crawler', u'打码失败:{}'.format(msg), '')
                continue
            if key == "success" and result != "":
                form_data['vicode'] = str(result).lower()
            else:
                continue

            header = {
                'Referer': 'http://waphn.189.cn/user/login/toLogin.do?reUrl=/selfservice/usercenter/index.do',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            LOGIN_URL = 'http://waphn.189.cn/user/login/userLogin.action'
            code, key, login_req = self.post(url=LOGIN_URL, data=form_data, headers=header)
            if code != 0:
                return code, key
            # 在网页中搜索msg_p 查看错误原因
            if 'id="msg_p"' not in login_req.text:
                return 0, 'success'
            if u'验证码错误!' in login_req.text:
                self.log('user', 'verify_error', login_req)
                self._dama_report(cid)
                continue
            if u'登录失败，账号或密码错误' in login_req.text:
                self.log('user', u'账号或密码错误', login_req)
                return 1, 'pin_pwd_error'
            if u'密码过于简单' in login_req.text:
                self.log('user', u'密码过于简单', login_req)
                return 1, 'sample_pwd'

            self.log('crawler', u'未知错误', login_req)
            return 9, 'crawler_failed'

        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error'

    def send_verify_request(self, **kwargs):
        # return 0, 'success', ''
        # 详单验证页面
        url = 'http://waphn.189.cn/hnselfservice/billquery/queryBillList.action?patitype=2'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, ''

            # 4位数字
        codetype = 1004
        for i in range(self.max_retry):
            url = 'http://waphn.189.cn/common/Verification/patchca.do?code=busiRand'
            headers = {
                "Referer": "http://waphn.189.cn/hnselfservice/billquery/queryBillList.action?patitype=2"}
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key
            try:
                key, result, cid = self._dama(resp.content, codetype)
            except:
                msg = traceback.format_exc()
                self.log('crawler', u'打码失败:{}'.format(msg), '')
                continue
            if key == "success" and result != "":
                vicode = str(result).lower()
            else:
                continue

            header = {
                'Referer': 'http://waphn.189.cn/user/login/toLogin.do?reUrl=/selfservice/usercenter/index.do',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            data = {
                'vicode': vicode
            }
            url = 'http://waphn.189.cn/hnselfservice/billquery/queryBilly.action'
            code, key, resp = self.post(url=url, data=data, headers=header)
            if code != 0:
                return code, key, ''

            if 'success' in resp.text:
                return 0, 'success', ''
            if 'randfailed' in resp.text:
                self.log('user', 'verify_error', resp)
                self._dama_report(cid)
                continue
            self.log('crawler', u'未知错误', login_req)
            return 9, 'crawler_failed', ''

        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error', ''

    def verify(self, **kwargs):
        today = date.today()
        query_date = today + relativedelta(months=0)
        begDate = "%d-%02d" % (query_date.year, query_date.month)

        data = {
            'tabIndex': '2',
            'queryMonth': begDate,
            'patitype': '2',
            'code': kwargs['sms_code'],
        }
        url = 'http://waphn.189.cn/hnselfservice/billquery/queryBillListx.action'
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key
        if u'查询结果' in resp.text or u'总通话记录数' in resp.text:
            return 0, 'success'
        if u'验证码错误' in resp.text:
            self.log('user', u'验证码错误', resp)
            return 2, 'verify_error'
        self.log('crawler', u'未知错误', resp)
        return 9, 'crawler_failed'

    def crawl_call_log(self, **kwargs):
        # return 0, 'success',[],[],[]
        missing_list = []
        possibly_missing_list = []
        call_log = []
        crawl_num = 0
        today = date.today()
        page_and_retry = []

        url = 'http://waphn.189.cn/hnselfservice/billquery/queryBillListx.action'
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            queryMonth = "%d-%02d" % (query_date.year, query_date.month)
            page_and_retry.append((queryMonth,self.max_retry))

        st_time = time.time()
        et_time = st_time + 20
        log_for_retry_request = []

        while page_and_retry:
            queryMonth, m_retry_times = page_and_retry.pop(0)
            month = queryMonth.replace('-', '')
            log_for_retry_request.append((month, m_retry_times))
            m_retry_times -= 1
            result = []
            msg = ''
            data = {
                'tabIndex':'2',
                'queryMonth':queryMonth,
                'patitype':'2',
                'code':'',
            }
            code, key, resp = self.post(url, data=data)
            if code == 0:
                try:
                    result = self.call_log_get(resp)
                    if result:
                        call_log.extend(result)
                        continue
                except:
                    msg = traceback.format_exc()
                    crawl_num += 1

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((queryMonth, m_retry_times))
                continue
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((queryMonth, m_retry_times))
                    time.sleep(rand_sleep)
                    continue
            if code == 0 and not result:
                possibly_missing_list.append(month)
            else:
                missing_list.append(month)
            self.log('website', u'未找到指定数据:{}'.format(msg), resp)

        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        # print('missing_list:{}'.format(missing_list))
        # print('possibly_missing_list:{}'.format(possibly_missing_list))
        if len(missing_list) + len(possibly_missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

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

    def call_log_get(self, response):
        records = []
        htmltree = etree.HTML(response.text)
        divs = htmltree.xpath('//*[@class="brs-04 inp-01 brb"]')
        for div in divs:
            tel = div.xpath('label/text()')
            if not tel:
                continue
            data = {}
            month = div.xpath('div/text()')
            if not month:
                continue
            data['month'] = month[0].strip().replace('-', '')[:6]
            data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data['call_method'] = div.xpath('label/p/text()')[0].strip()
            data['call_duration'] = self.time_format_second(div.xpath('label/p/span/text()')[0].strip())
            data['call_cost'] = div.xpath('div/p/span/text()')[0].strip()
            data['call_tel'] = tel[0].strip()
            timeArray = time.strptime(div.xpath('div/text()')[0].strip(), "%Y-%m-%d %H:%M:%S")
            call_time_timeStamp = str(int(time.mktime(timeArray)))
            data['call_time'] = call_time_timeStamp
            data['call_from'] = ''
            data['call_to'] = ''
            data['call_type'] = ''
            records.append(data)
        return records

    def crawl_info(self, **kwargs):
        user_info = {}
        url = 'http://waphn.189.cn/selfservice/cust/custInfo.action'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, {}
        try:
            user_info['full_name'] = re.findall(u'<li>客户姓名：(\S+)</li>', resp.text)[0]
            user_info['id_card'] = re.findall(u'<li>证件号码：(\S+)</li>', resp.text)[0]
            user_info['address'] = ''
            user_info['open_date'] = ""
            user_info['is_realname_register'] = True
            return 0, 'success', user_info
        except:
            msg = traceback.format_exc()
            self.log('user', u'解析用户信息出错{}'.format(msg),resp)
            return 9, 'crawler_failed', user_info

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        missing_list = []
        crawl_num = 0

        url = 'http://waphn.189.cn/hnselfservice/billquery/queryBillDetailQuery.do'
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            data = {
                'queryNumType':'',
                'accNbrType':'',
                'queryMonth': searchMonth,
                'queryNum': kwargs['tel'],
                'queryFlag':'2',
            }
            code, key, resp = self.post(url, data=data)
            if code != 0:
                missing_list.append(searchMonth)
                continue
            try:
                result = self.get_phone_bill(resp, searchMonth, **kwargs)
                phone_bill.append(result)
            except:
                msg = traceback.format_exc()
                self.log('crawler', msg, resp)
                missing_list.append(searchMonth)
                continue

        if len(missing_list) == 5:
            if crawl_num > 0:
                return 9, 'crawl_error', phone_bill, missing_list
            return 9, 'website_busy_error', phone_bill, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, 'success', phone_bill, missing_list

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.now()
        for month_offset in range(1, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

    def get_phone_bill(self, resp, month, **kwargs):

        htmltree = etree.HTML(resp.text)
        divs = htmltree.xpath('//*[@class="qudao-taocan-con"]/dl')
        result_div = ''
        for div in divs:
            if kwargs['tel'] in div.xpath('dt/span/text()')[0]:
                result_div = div
                break
        bill_data = {
            'bill_month': month,
            'bill_amount': '0',
            'bill_package': '',
            'bill_ext_calls': '',
            'bill_ext_data': '',
            'bill_ext_sms': '',
            'bill_zengzhifei': '',
            'bill_daishoufei': '',
            'bill_qita': '',
        }
        for li in result_div.xpath('div/ul/li'):
            b_name = li.xpath('label/b/text()')
            la_name = li.xpath('label/text()')
            num = li.xpath('span/text()')[0].replace(u'元', '')
            if b_name:
                if b_name[0] == u'套餐月基本费':
                    bill_data['bill_amount'] = str(float(bill_data['bill_amount']) + float(num))
                    bill_data['bill_package'] = num
                if b_name[0] == u'套餐超出费用':
                    bill_data['bill_amount'] = str(float(bill_data['bill_amount']) + float(num))
                continue
            if la_name:
                if la_name[0] == u'短信费':
                    bill_data['bill_ext_sms'] = num
                if la_name[0] == u'语音通信费' or la_name[0] == u'国内通话费':
                    bill_data['bill_ext_calls'] = num
                if la_name[0] == u'上网及数据通信费' or la_name[0] == u'手机上网费':
                    bill_data['bill_ext_data'] = num
                if la_name[0] == u'代收费':
                    bill_data['bill_daishoufei'] = num
                if la_name[0] == u'CDMA代收-SP费':
                    bill_data['bill_qita'] = num
        return bill_data

if __name__ == '__main__':
    crawle = Crawler()
    tel = '18907307267'
    pwd = '762703'

    crawle.self_test(tel=tel, pin_pwd=pwd)


