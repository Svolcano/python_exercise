#!/user/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/30 13:56
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

    def get_login_verify_type(self, **kwargs):
        return 'SMS'

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def send_login_verify_request(self, **kwargs):
        start_url = 'http://wap.yn.ct10000.com/index.do'
        code, key, resp = self.get(start_url)
        if code != 0:
            return code, key, ''

        url = 'http://wap.yn.ct10000.com/sendSms.do'
        data = {
            'accNbr': kwargs['tel'],
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, ''
        if u'发送成功' in resp.text:
            return 0, 'success', ''
        if u'太过频繁' in resp.text:
            self.log('user', u'操作过于频繁', resp)
            return 9, 'send_sms_too_quick_error', ''

        self.log('crawler', u'短信发送失败', resp)
        return 9, 'send_sms_error', ''

    def login(self, **kwargs):
        try:
            enAccNbr = des_encode(kwargs['tel'], 'wap_accnbr_2016')
            enPassword = des_encode(kwargs['sms_code'], 'wap_password_2016')
        except:
            msg = traceback.format_exc()
            self.log('crawler', u'加密失败:{}'.format(msg), )
            return 9, 'crawler_failed'

        form_data = {
            'loginPwdType': 'B',
            'nodeId': '72',
            'mode': 'other',
            'enAccNbr': enAccNbr,
            'enPassword': enPassword,
            'valid': '',
        }

        # 4位数字
        codetype = 1004
        for i in range(self.max_retry):
            image_url = 'http://wap.yn.ct10000.com/vcImage.do?vvv='
            code, key, resp = self.get(image_url)
            if code != 0:
                return code, key
            try:
                key, result, cid = self._dama(resp.content, codetype)
            except:
                msg = traceback.format_exc()
                self.log('crawler', u'打码失败:{}'.format(msg), '')
                continue
            if key == "success" and result != "":
                form_data['valid'] = str(result).lower()
            else:
                continue

            header = {
                'Referer': 'http://wap.yn.ct10000.com/initLogin.do',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            LOGIN_URL = 'http://wap.yn.ct10000.com/loginValidate.do'
            code, key, resp = self.post(url=LOGIN_URL, data=form_data, headers=header)
            if code != 0:
                return code, key

            # 短信错误：
            if 'valcellphoneLoginFormMsgId' not in resp.text:
                return 0, 'success'
            if u'随机验证码有误' in resp.text or u'您的随机验证码已经失效' in resp.text:
                self.log('user', u'短信输入有误', resp)
                return 9, 'verify_error'
            if u'验证码不正确' in resp.text:
                self.log('user', 'verify_error', resp)
                self._dama_report(cid)
                continue
            self.log('crawler', u'登录未知错误', resp)
            return 9, 'crawl_error'
        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error'

    def send_verify_request(self, **kwargs):
        # return 0, 'success', ''
        # 详单验证页面
        url = 'http://wap.yn.ct10000.com/self/fee/sendSms.do'
        data = {
            'accNbr': '',
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, ''
        if u'随机码发送成功' in resp.text:
            return 0, 'success', ''
        self.log('crawler', u'二次短信未知错误', resp)
        return 9, 'crawl_error', ''

    def verify(self, **kwargs):
        today = date.today()
        query_date = today + relativedelta(months=0)
        begDate = "%d%02d" % (query_date.year, query_date.month)

        data = {
            'cdrtype': '10',
            'date': begDate,
            'deailsms': kwargs['sms_code'],
            'nodeId': '86',
        }
        url = 'http://wap.yn.ct10000.com/self/fee/detailRecord.do'
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key
        if u'您输入的随机码有误' in resp.text:
            self.log('crawler', u'二次短信验证错误', resp)
            return 9, 'verify_error'
        if u'所有语音详单如下' in resp.text or u'没有相应的记录' in resp.text:
            return 0, 'success'
        self.log('crawler', u'二次短信验证未知错误', resp)
        return 9, 'verify_error'

    def crawl_call_log(self, **kwargs):
        # return 0, 'success',[],[],[]
        missing_list = []
        possibly_missing_list = []
        call_log = []
        crawl_num = 0
        today = date.today()
        page_and_retry = []

        url = 'http://wap.yn.ct10000.com/self/fee/detailRecord.do'
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            queryMonth = "%d%02d" % (query_date.year, query_date.month)
            page_and_retry.append((queryMonth, self.max_retry))

        st_time = time.time()
        et_time = st_time + 20
        log_for_retry_request = []

        while page_and_retry:
            queryMonth, m_retry_times = page_and_retry.pop(0)
            # month = queryMonth.replace('-', '')
            log_for_retry_request.append((queryMonth, m_retry_times))
            m_retry_times -= 1
            result = []
            msg = ''
            data = {
                'cdrtype': '10',
                'date': queryMonth,
                'deailsms': kwargs['sms_code'],
                'nodeId': '86',
            }
            code, key, resp = self.post(url, data=data)
            if code == 0:
                try:
                    result = self.call_log_get(resp, queryMonth, kwargs['tel'])
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
                possibly_missing_list.append(queryMonth)
            else:
                missing_list.append(queryMonth)
            self.log('website', u'未找到指定数据:{}'.format(msg), resp)

        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        # print('missing_list:{}'.format(missing_list))
        # print('possibly_missing_list:{}'.format(possibly_missing_list))
        if len(missing_list) + len(possibly_missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def call_log_get(self, response, month, tel):
        records = []
        if u'没有相应的记录' in response.text:
            return records
        htmltree = etree.HTML(response.text)
        divs = htmltree.xpath('//*[@class="body-content"]/div')
        update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for div in divs:
            data = {
                'update_time': update_time,
                'call_tel': '',
                'call_cost': '',
                'call_time': '',
                'call_method': '',
                'call_type': '',
                'call_from': '',
                'call_to': '',
                'call_duration': '',
                'month': month,
            }
            all_p = div.xpath('p')
            for p in all_p:
                name = p.xpath('span/text()')[0]
                value = p.xpath('text()')
                if u'通话类型' in name and value:
                    data['call_type'] = value[0]
                elif u'呼叫类型' in name and value:
                    data['call_method'] = value[0]
                elif u'主叫号码' in name and value and tel not in value[0]:
                    data['call_tel'] = value[0]
                elif u'被叫号码' in name and value and tel not in value[0]:
                    data['call_tel'] = value[0]
                elif u'主叫位置' in name and value:
                    data['call_from'] = value[0]
                elif u'被叫位置' in name and value:
                    data['call_to'] = value[0]
                elif u'通话开始时间' in name and value:
                    timeArray = time.strptime(value[0].strip(), "%Y-%m-%d-%H:%M:%S")
                    call_time_timeStamp = str(int(time.mktime(timeArray)))
                    data['call_time'] = call_time_timeStamp
                elif u'通话时长' in name and value:
                    data['call_duration'] = value[0]
                elif u'基本/漫游费' in name and value:
                    data['call_cost'] = value[0]
            records.append(data)
        return records


    def crawl_info(self, **kwargs):
        user_info = {}
        url = 'http://wap.yn.ct10000.com/self/info/custInfo.do?nodeId=319'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, {}
        try:
            user_info['full_name'] = re.findall(u'客户姓名：(\S+)<br/>', resp.text)[0]
            user_info['id_card'] = re.findall(u"证件号码：(\S+)<br/>", resp.text)[0]
            user_info['address'] = re.findall(u"联系地址：(\S+)<br/>", resp.text)[0]
            user_info['open_date'] = re.findall(u"开通时间：(\S+)<br/>", resp.text)[0].replace('-', '')
            user_info['is_realname_register'] = True
            return 0, 'success', user_info
        except:
            msg = traceback.format_exc()
            self.log('user', u'解析用户信息出错{}'.format(msg),resp)
            return 9, 'crawler_failed', user_info

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.now()
        for month_offset in range(1, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        missing_list = []
        crawl_num = 0


        for searchMonth in self.__monthly_period(6, '%Y%m'):
            url = 'http://wap.yn.ct10000.com/self/fee/historyItemQuery.do?nodeId=84&billingCycleId={}'.format(searchMonth)
            code, key, resp = self.get(url)
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

    def get_phone_bill(self, resp, month, **kwargs):
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

        bill_amount = re.findall(u'账单费用合计为：([0-9\.]+)元，', resp.text)
        if bill_amount:
            bill_data['bill_amount'] = bill_amount[0]
        bill_package = re.findall(u'月基本费 ([0-9\.]+)元', resp.text)
        if bill_package:
            bill_data['bill_package'] = bill_package[0]
        bill_ext_sms = re.findall(u'短信费 ([0-9\.]+)元', resp.text)
        if bill_ext_sms:
            bill_data['bill_ext_sms'] = bill_ext_sms[0]
        bill_ext_data = re.findall(u'上网费 ([0-9\.]+)元', resp.text)
        if bill_ext_data:
            bill_data['bill_ext_data'] = bill_ext_data[0]

        return bill_data

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17387202951"
    # USER_ID = "17387202959"
    USER_PASSWORD = "135126"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)

