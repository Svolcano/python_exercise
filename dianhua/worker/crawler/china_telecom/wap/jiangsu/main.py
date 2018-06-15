#!/user/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/4/23 10:15

import calendar
import json
import random
import traceback
import datetime
import sys
reload(sys)
sys.setdefaultencoding("utf8")

from fake_useragent import UserAgent
from datetime import date
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
        self.pubToken = ''
        self.areaCode = ''

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify', 'full_name', 'id_card']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        url = 'http://wapjs.189.cn/tysh/pages/main/home.html'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key

        # # 登录
        url = 'http://wapjs.189.cn/tysh/interface/doAjax.do'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://wapjs.189.cn/tysh/pages/main/home.html',
            'Origin': 'http://wapjs.189.cn',
        }
        self.session.headers.update(headers)

        data = {
            'para': 'accNbr={};password={};accNbrType=2000004;PWDType=-1;areaCode=;actionCode=login037;channelCode_common=100003;pubAreaCode=025;pushUserId=jszt_804723162833;coachUser=;userLogAccNbrType=;userLogAccNbr=;userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken=undefined;'.format(kwargs['tel'],kwargs['pin_pwd']),
            'url': 'http://61.160.137.141/jszt/rest/login2User',
        }

        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key

        if u'服务密码错误' in resp.text or u'您已连续输错2次!' in resp.text or '密码被限制使用' in resp.text or u'已输错三次验证码' in resp.text:
            self.log('user', u'服务密码错误', resp)
            return 1, 'pin_pwd_error'
        if u'您的账号已被锁定' in resp.text:
            self.log('user', '账号已被锁定', resp)
            return 9, 'account_locked'
        try:
            resp_json = eval(resp.text.replace('null', ''))
            areaCode = resp_json['areaCode']
            token = resp_json['token']
            self.pubToken = token
            self.areaCode = areaCode
            para_str = """accNbr={};accNbrType=2000004;PWDType=-1;areaCode={};actionCode=yw013;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_804723162833;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={}""".format(kwargs['tel'], areaCode, areaCode, kwargs['tel'], token)
        except:
            if u'用户的产品状态不允许登录' in resp.text:
                self.log('user', u'用户的产品状态不允许登录', resp)
                return 9, 'websiter_prohibited_error'
            msg = traceback.format_exc()
            if u'密码未激活' in resp.text:
                self.log('user', u'密码未激活', resp)
                return 1, 'pin_pwd_error'
            if u'帐号不存在' in resp.text:
                self.log('user', u'帐号不存在', resp)
                return 9, 'invalid_tel'
            self.log('crawler', msg, resp)
            return 9, 'json_error'

        data = {
            'para': para_str,
            'url': 'http://61.160.137.141/jszt/rest/login2UserInfo',
        }
        code, key, resp1 = self.post(url, data=data)
        if code != 0:
            return code, key

        # 个人信息
        self.user_info = {
            'full_name': '',
            'id_card': '',
            'is_realname_register': '',
            'open_date': '',
            'address': ''
        }
        try:
            user_msg = eval(resp.text.replace('null', ''))
            self.user_info['full_name'] = user_msg['customerName'].decode('utf-8')
            self.user_info['id_card'] = user_msg['indentNbr']
            self.user_info['open_date'] = user_msg['broadbandInfo'][0]['startTime']
            self.user_info['address'] = user_msg['broadbandInfo'][0]['address'].decode('utf-8')
            if self.user_info['id_card']:
                self.user_info['is_realname_register'] = True
        except:
            msg = traceback.format_exc()
            self.log('crawler', msg, resp)

        # 登录跳转2
        para_str = 'accNbr={};dccDestinationAttr=2;areaCode={};actionCode=jsztActionCode_uniformitysearchCallBalanceReqWithCache;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_804723162833;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={}'.format(
            kwargs['tel'], areaCode, areaCode, kwargs['tel'], token)

        data = {
            'para': para_str,
            'url': 'http://61.160.137.141/jszt/uniformity/searchCallBalanceReqWithCache',
        }
        code, key, resp2 = self.post(url, data=data)
        if code != 0:
            return code, key

        # 登录跳转3
        para_str = 'accNbr={};areaCode={};family=2;actionCode=jsztActionCode_restaccnbrscore;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_804723162833;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={};'.format(kwargs['tel'], areaCode, areaCode, kwargs['tel'], token)

        data = {
            'para': para_str,
            'url': 'http://61.160.137.141/jszt/rest/accnbrscore',
        }
        code, key, resp3 = self.post(url, data=data)
        if code != 0:
            return code, key

        # 登录跳转4
        para_str = 'accNbr={};areaCode={};family=2;actionCode=jsztActionCode_uniformitysearchCurrAcuReqWithCache;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_804723162833;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={};'.format(
            kwargs['tel'], areaCode, areaCode, kwargs['tel'], token)

        data = {
            'para': para_str,
            'url': 'http://61.160.137.141/jszt/uniformity/searchCurrAcuReqWithCache',
        }
        code, key, resp4 = self.post(url, data=data)
        if code != 0:
            return code, key

        # 登录跳转5
        para_str = 'recommendAreaMark=100;limit=21;areaCode={};actionCode=jsztActionCode_flowflowrestgetFocusPic;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_804723162833;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={};'.format(
            areaCode, areaCode, kwargs['tel'], token)

        data = {
            'para': para_str,
            'url': 'http://221.228.39.34/ZtFlowOrder/jszt/flow/flowrest/getFocusPic',
        }
        code, key, resp5 = self.post(url, data=data)
        if code != 0:
            return code, key

        try:
            resp_json = json.loads(resp5.text)
            if resp_json['TSR_MSG'] == '成功':
                return 0, 'success'
            if u'繁忙，请稍后再试' in resp5.text :
                self.log('website', u'1:{}\n 2:{}\n 3:{}\n 4:{}\n 5:{}\n'.
                         format(resp.text,resp1.text, resp2.text, resp3.text, resp4.text), resp5)
                return 9, 'website_busy_error'
            # self.log('crawler', u'未知错误', resp5)
            self.log('crawler', u'未知错误1:{}\n 2:{}\n 3:{}\n 4:{}\n 5:{}\n'.
                     format(resp.text, resp1.text, resp2.text, resp3.text, resp4.text), resp5)
            return 9, 'crawl_error'
        except:
            msg = traceback.format_exc()
            self.log('crawler', msg, resp5)
            return 9, 'json_error'

    def send_verify_request(self, **kwargs):
        url = 'http://wapjs.189.cn/tysh/interface/doAjax.do'
        para_str = 'accNbr={};actionCode=auth_smscode_001;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_553072141649;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={};'.format(
            kwargs['tel'], self.areaCode, kwargs['tel'], self.pubToken)

        data = {
            'para': para_str,
            'url': 'http://61.160.137.141/jszt/ztauth/getAuthCode',
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, ''

        try:
            resp_json = eval(resp.text.replace('null', ''))
            if resp_json['TSR_MSG'] == '成功':
                return 0, 'success', ''
            if u'操作太频繁啦' in resp.text:
                self.log('user', 'send_sms_too_quick_error', resp)
                return 9, 'send_sms_too_quick_error', ''
            self.log('crawler', 'send_sms_error', resp)
            return 9, 'send_sms_error', ''
        except:
            msg = traceback.format_exc()
            self.log('crawler', msg, resp)
            return 9, 'json_error', ''


    def verify(self, **kwargs):
        # return 0, 'success'
        url = 'http://wapjs.189.cn/tysh/interface/doAjax.do'
        para_str = 'accNbr={};family=2;code={};idcard={};name={};actionCode=jsztActionCode_ztauthverifyIdentity;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_553072141649;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={};'.format(
            kwargs['tel'], kwargs['sms_code'], kwargs['id_card'], kwargs['full_name'], self.areaCode, kwargs['tel'],self.pubToken)
        data = {
            'para': para_str,
            'url': 'http://61.160.137.141/jszt/ztauth/verifyIdentity',
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key
        if u'"TSR_MSG":"成功"' in resp.text or u'"TSR_MSG":"成功!"' in resp.text or 'accNbr' in resp.text:
            return 0, 'success'
        if u'验证码错误或者失效' in resp.text:
            self.log('user', 'verify_error', resp)
            return 2, 'verify_error'
        if u'姓名验证失败' in resp.text:
            self.log('user', 'user_name_error', resp)
            return 2, 'user_name_error'
        if u'身份证验证失败' in resp.text:
            self.log('user', 'user_id_error', resp)
            return 2, 'user_id_error'
        if u'系统繁忙' in resp.text:
            self.log('website', 'website_busy_error', resp)
            return 9, 'website_busy_error'

        self.log('crawler', u'未知错误', resp)
        return 9, 'crawl_error'

    def crawl_info(self, **kwargs):
        return 0, "success", self.user_info

    def crawl_call_log(self, **kwargs):
        missing_list = []
        possibly_missing_list = []
        call_log = []
        crawl_num = 0
        today = date.today()
        page_and_retry = []
        url = 'http://wapjs.189.cn/tysh/interface/doAjax.do'
        #  pageSize 3000
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            begDate = "%d%02d01" % (query_date.year, query_date.month)
            endDay = calendar.monthrange(query_date.year, query_date.month)[1]
            endDate = "%d%02d%s" % (query_date.year, query_date.month, endDay)
            para = 'accNbr={}; acctName={};begDate={};endDate={};areaCode={};productId=2;family=2;auth=auth;curPage=1;pageSize=3000;getFlag=1;actionCode=jsztActionCode_restvoiceticket;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_553072141649;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={};'
            para = para.format(kwargs['tel'], kwargs['tel'], begDate, endDate, self.areaCode, self.areaCode,
                               kwargs['tel'], self.pubToken)
            data = {
                'url': 'http://61.160.137.141/jszt/rest/voiceticket',
                'para': para
            }
            page_and_retry.append((data, begDate[:6], self.max_retry))

        st_time = time.time()
        et_time = st_time + 20
        log_for_retry_request = []

        while page_and_retry:
            call_log_data, m_query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            result = []
            msg = ''
            code, key, resp = self.post(url, data=call_log_data)
            if code == 0:
                try:
                    result = self.call_log_get(resp.text)
                    if result:
                        call_log.extend(result)
                        continue
                except:
                    msg = traceback.format_exc()
                    crawl_num += 1

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((call_log_data, m_query_month, m_retry_times))
                continue
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((call_log_data, m_query_month, m_retry_times))
                    time.sleep(rand_sleep)
                    continue
            if code == 0 and not result:
                possibly_missing_list.append(m_query_month)
            else:
                missing_list.append(m_query_month)
            self.log('website', u'未找到指定数据:{}'.format(msg), resp)

        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        # print('missing_list:{}'.format(missing_list))
        # print('possibly_missing_list:{}'.format(possibly_missing_list))
        if len(missing_list) + len(possibly_missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def call_log_get(self, response):
        """
        | `update_time` | string | 更新时间戳 |
        | `call_cost` | string | 爬取费用 |
        | `call_time` | string | 通话起始时间 |
        | `call_method` | string | 呼叫类型（主叫, 被叫） |
        | `call_type` | string | 通话类型（本地, 长途）  |
        | `call_from` | string | 本机通话地 |
        | `call_to` | string | 对方归属地 |
        | `call_duration` | string | 通话时长 |
        """
        records = []
        resp_json = eval(response.replace('null', ''))
        if not resp_json.has_key('items'):
            return []
        items = resp_json['items']
        if not isinstance(items, list):
            items1 = []
            items1.append(items)
            items = items1

        for item in items:
            data = {}
            data['month'] = item['startDateNew'].replace('-', '')[:6]
            data['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data['call_cost'] = item['ticketChargeCh']

            timeArray = time.strptime('{} {}'.format(item['startDateNew'], item['startTimeNew']), "%Y-%m-%d %H:%M:%S")
            call_time_timeStamp = str(int(time.mktime(timeArray)))
            data['call_time'] = call_time_timeStamp
            data['call_method'] = item['ticketTypeNew'].decode('utf-8')
            data['call_type'] = item['durationType'].decode('utf-8')
            raw_call_from = item['areaCode'].strip()
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                data['call_from'] = call_from
            else:
                data['call_from'] = raw_call_from
            data['call_to'] = ''
            if 'nbr' in item:
                data['call_tel'] = item['nbr']
            else:
                data['call_tel'] = item['accNbr']
            if 'duartionCh' in item:
                duration = item['duartionCh']
            else:
                duration = item['durationCh']

            call_durations = duration.split(':')
            call_duration = int(call_durations[0]) * 3600 + int(call_durations[1]) * 60 + int(call_durations[2])
            data['call_duration'] = str(call_duration)

            records.append(data)
        return records

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset)).strftime(strf)

    def crawl_phone_bill(self, **kwargs):
        phone_bill = list()
        missing_list = []
        crawl_num = 0
        data = {
            'para':'',
            'url':'http://61.160.137.141/jszt/rest/bill',
        }
        url = 'http://wapjs.189.cn/tysh/interface/doAjax.do'
        for searchMonth in self.__monthly_period(6, '%Y%m'):
            para = 'accNbr={};areaCode={};productId=2;billingCycleId={};auth=auth;queryFlag=0;actionCode=fy002;channelCode_common=100003;pubAreaCode={};pushUserId=jszt_307261426672;coachUser=;userLogAccNbrType=2;userLogAccNbr={};userTokenAccNbrType=2;ztVersion=3.1.0;ztInterSource=100003;pubToken={};'.format(kwargs['tel'], self.areaCode, searchMonth,self.areaCode,kwargs['tel'], self.pubToken)
            data['para'] = para
            code, key, resp = self.post(url, data=data)
            if code != 0:
                # return code, key
                missing_list.append(searchMonth)
                continue
            try:
                result = self.get_phone_bill(resp, searchMonth)
                phone_bill.append(result)
            except:
                if u'鉴权不通过，请重新登录' in resp.text:
                    self.log('website', u'鉴权不通过，请重新登录', resp)
                    return 9, 'website_busy_error', phone_bill, missing_list
                msg = traceback.format_exc()
                self.log('crawler', msg, resp)
                missing_list.append(searchMonth)
                continue

        if len(missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', phone_bill, missing_list
            return 9, 'website_busy_error', phone_bill, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, 'success', phone_bill, missing_list


    def get_phone_bill(self, resp, month):
        phone_bill = eval(resp.text.replace('null', ''))
        bill_list = phone_bill['CustBillQuery'][1]['ProductBillTree'][0]
        bill_data = {
            'bill_month': month,
            'bill_amount': '',
            'bill_package': '',
            'bill_ext_calls': '',
            'bill_ext_data': '',
            'bill_ext_sms': '',
            'bill_zengzhifei': '',
            'bill_daishoufei': '',
            'bill_qita': '',
        }
        for bill in bill_list:
            if bill['BillItemName'] == u'手机':
                bill_data['bill_amount'] = bill['BillItemAmount']
            if bill['BillItemName'] == u'套餐费优惠':
                bill_data['bill_package'] = bill['BillItemAmount']
            if bill['BillItemName'] == u'国内短信费':
                bill_data['bill_ext_sms'] = bill['BillItemAmount']
            if bill['BillItemName'] == u'语音通信费':
                bill_data['bill_ext_calls'] = bill['BillItemAmount']
        return bill_data

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17368357716"
    USER_PASSWORD = "488496"
    full_name = '应朝晖'
    id_card = '33010219680525123X'
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD, full_name=full_name, id_card=id_card)