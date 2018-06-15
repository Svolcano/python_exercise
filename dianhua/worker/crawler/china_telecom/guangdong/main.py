# -*- coding: utf-8 -*-
import json
import traceback
import time
import sys
import re
# 这段代码是用于解决中文报错的问题
from lxml import etree
import datetime
from datetime import date
import calendar
reload(sys)
sys.setdefaultencoding("utf8")

from dateutil.relativedelta import relativedelta


if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
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
        self.pin_pwd_error_times = 0

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'sms_verify']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        url = 'https://gd.189.cn/common/getLoginUserNameJt.jsp?'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, ""

        befor_login_url = 'https://gd.189.cn/common/newLogin/newLogin/login.htm?v=3&SSOArea=0000&SSOAccount=&SSOProType=&SSORetryTimes=&SSOError=&uamError=&SSOCustType=0&loginOldUri=&SSOOldAccount=&SSOProTypePre='
        code, key, resp = self.get(befor_login_url)
        if code != 0:
            return code, key, ""

        codetype = 3004
        for i in range(self.max_retry):
            url = 'https://gd.189.cn/nCheckCode?1521699235615'
            code, key, resp = self.get(url)
            if code != 0:
                return code, key, ""
            try:
                key, result, cid = self._dama(resp.content, codetype)
            except:
                msg = traceback.format_exc()
                self.log('crawler', u'打码失败:{}'.format(msg), '')
                continue
            if key == "success" and result != "":
                kwargs['captcha_code'] = str(result).lower()
            else:
                continue

            url = "https://gd.189.cn/dwr/exec/newLoginDwr.goLogin.dwr"
            row_data = """callCount=1
            c0-scriptName=newLoginDwr
            c0-methodName=goLogin
            c0-id=8067_1521699284106
            c0-param0=boolean:false
            c0-param1=boolean:false
            c0-param2=string:{}
            c0-param3=string:
            c0-param4=string:2000004
            c0-param5=string:{}
            c0-param6=string:00
            c0-param7=string:{}
            c0-param8=string:
            c0-param9=string:sysType%3DNewLogin
            xml=true
            """.format(kwargs['captcha_code'], kwargs['tel'], kwargs['pin_pwd'])

            headers = {
                'Referer': befor_login_url,
                'Content-Type': 'text/plain',
                'Origin': 'https://gd.189.cn',
            }

            code, key, resp = self.post(url, data=row_data.replace(' ',''), headers=headers)
            if code != 0:
                return code, key

            # '验证码错误'
            if '\u9A8C\u8BC1\u7801\u9519\u8BEF' in resp.text:
                self.log('user', 'verify_error', resp)
                # return 2, 'verify_error'
                self._dama_report(cid)
                continue
            SSORequestXML = re.findall(u'var s4="(.*?)";s0\[3\]=s4;', resp.text)
            if not SSORequestXML:
                self.log('website', 'website_busy_error', resp)
                return 9, 'website_busy_error'

            self.log('crawler', u'登录第一步', resp)
            break
        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error'
        SSORequestXML = SSORequestXML[0]

        form_data = {
            'area': '',
            'accountType': '2000004',
            'passwordType': '00',
            'loginOldUri': '/service/home/',
            'IFdebug': 'null',
            'errorMsgType': '',
            'SSORequestXML': SSORequestXML,
            'sysType': '2',
            'from': 'new',
            'isShowLoginRand': 'Y',
            'areaSel': '020',
            'accountTypeSel': '2000001',
            'account': kwargs['tel'],
            'passtype': 'custPassword',
            'loginCodeRand': kwargs['captcha_code'],
        }

        headers = {
            'Referer': befor_login_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        url = 'https://uam.gd.ct10000.com/portal/SSOLoginForWT.do'
        code, key, resp = self.post(url, data=form_data, headers=headers)
        if code != 0:
            return code, key

        if u'登录失败！号码不存在' in resp.text:
            self.log('user', 'invalid_tel', resp)
            return 1, 'invalid_tel'
        if u'密码不正确' in resp.text:
            self.log('user', 'pin_pwd_error', resp)
            return 1, 'pin_pwd_error'
        if u'该号码今天的登陆失败次数已经超过限制' in resp.text:
            self.log('user', 'account_locked', resp)
            return 9, 'account_locked'
        # 操作过频
        if 'https://gd.189.cn/receiveUATiecket.do?sysType=NewLogin&UATicket=-2' in resp.text:
            self.log('user', 'over_query_limit', resp)
            return 9, 'over_query_limit'
        try:
            htmltree = etree.HTML(resp.text)
            redirectForm = htmltree.xpath(u'//*[@id="redirectForm"]/@action')
            if not redirectForm:
                self.log('website', 'website_busy_error', resp)
                return 9, 'website_busy_error'
            url = redirectForm[0]
            self.log('crawler', u'登录第二步', resp)
        except:
            self.log('crawler', 'html_error', resp)
            return 9, 'html_error'

        code, key, resp = self.get(url)
        if code != 0:
            return code, key

        SESSIONID = re.findall(u'var sessionId = "(.*?)";', resp.text)
        if not SESSIONID:
            self.log('crawler', 'website_busy_error', resp)
            return 9, 'website_busy_error'

        SESSIONID = SESSIONID[0]
        data = {
            'loginRedirect': 'true',
        }
        login_url = 'https://gd.189.cn/service/home/?SESSIONID={}'.format(SESSIONID)
        code, key, resp = self.post(login_url, data=data)
        if code != 0:
            return code, key
        self.log('crawler', u'登录第三步', resp)

        url = 'https://gd.189.cn/common/getLoginUserNameJt.jsp?'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key
        self.log('crawler', u'登录第四步', resp)

        jsp_url = 'https://gd.189.cn/common/getCustInfo.jsp?'
        code, key, resp = self.get(jsp_url)
        if code != 0:
            return code, key
        # 返回结果如：custCode=2662369735860000&&loginNum=18124880858
        # print('jsp 设置cooke')
        # print(resp.text)

        self.log('crawler', u'登录第五步', resp)
        # 设置cookie
        url = 'https://gd.189.cn/J/J10006.j'
        data = {
            'a.c': '0',
            'a.u': 'user',
            'a.p': 'pass',
            'a.s': 'ECSS',
            'd.payType': '',
            'd.numberTypeCode': '',
        }

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': login_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        msg = ''
        for retry in range(3):
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                return code, key
            # print('调用顺序0')
            # print(resp.text)

            try:
                numJSON = json.loads(resp.text)
                numStr = numJSON['r']['numberList'][0]['numType']
                self.area_code = str(numStr).split('-')[0]
                self.log('crawler', u'登录第六步', resp)
                break
            except:
                err = traceback.format_exc()
                # self.log('crawler', 'json_error:{}'.format(err), resp)
                # return 9, 'json_error'
                msg = err
                time.sleep(2)
        else:
            self.log('website', u'请求cookles失败:{}'.format(msg), resp)
            return 9, 'website_busy_error'

        url = 'https://gd.189.cn/J/J10007.j'
        data = {
            'a.c': '0',
            'a.u': 'user',
            'a.p': 'pass',
            'a.s': 'ECSS',
            'd.numStr': numStr,
        }

        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key, ''
        # print(resp.text)
        try:
            result = json.loads(resp.text)
            if result['b']['m'] == u'成功':
                self.log('crawler', u'登录第七步', resp)
                return 0, 'success'
            self.log('crawler', 'crawl_error', resp)
            return 9, 'crawl_error'
        except:
            self.log('crawler', 'json_error', resp)
            return 9, 'json_error'

    def send_verify_request(self, **kwargs):
        # return 9, 'crawl_error', ''
        url = 'https://gd.189.cn/J/J10008.j'
        data = {
            'a.c': '0',
            'a.u': 'user',
            'a.p': 'pass',
            'a.s': 'ECSS',
            '': '',
        }
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://gd.189.cn/service/home/query/xd_index.html',
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key, ''
        # print(u'调用顺序6')
        # print(resp.text)
        self.log('crawler', u'发送短信第一步', resp)

        # 开始发送短信
        data = {
            'number': kwargs['tel'],
            'latnId': self.area_code,
            'typeCode': 'LIST_QRY',
        }
        url = 'https://gd.189.cn/volidate/validateSendMsg.action'
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, ''
        # print('短信发送1')
        if u'允许发送短信' not in resp.text:
            if u'您的号码发送短信超过限制次数，请明天再试' in resp.text:
                self.log('user', 'over_max_sms_error', resp)
                return 9, 'over_max_sms_error', ''
            if u'您的短信发送过于频繁，请稍后再试' in resp.text:
                self.log('user', 'send_sms_too_quick_error', resp)
                return 9, 'send_sms_too_quick_error', ''

            self.log('crawler', 'send_sms_error', resp)
            return 9, 'send_sms_error', ''
        # print(resp.text)
        self.log('crawler', u'发送短信第二步', resp)
        url = 'https://gd.189.cn/volidate/insertSendSmg.action'
        data = {
            'validaterResult':'0',
            'resultmsg':u'允许发送短信',
            'YXBS':'LIST_QRY',
            'number': kwargs['tel'],
            'latnId': self.area_code,
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key, ''
        # print('短信发送2')
        # print(resp.text)
        if u'保存信息成功' not in resp.text:
            self.log('crawler', 'send_sms_error', resp)
            return 9, 'send_sms_error', ''
        self.log('crawler', u'发送短信第三步', resp)
        return 0, 'success', ''

    def verify(self, **kwargs):
        # return 0, 'success'

        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        end_day = "%d%02d%02d" % (today.year, today.month, today.day)
        url = 'https://gd.189.cn/J/J10009.j'
        data = {
            'a.c': '0',
            'a.u': 'user',
            'a.p': 'pass',
            'a.s': 'ECSS',
            'c.n': u'语音清单',
            'c.t': '02',
            'c.i': '02-005-04',
            'd.d01': 'call',
            'd.d02': today_month,
            'd.d03': '{}01'.format(today_month),
            'd.d04': end_day,
            'd.d05': '20',
            'd.d06': '1',
            'd.d07': kwargs['sms_code'],
            'd.d08': '1',
        }

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://gd.189.cn/service/home/query/xd_index.html',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        key = 'verify_error'
        for i in range(3):
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                return code, key
            # 偶发
            if u"用户未进行实名登记" in resp.text:
                continue

            try:
                result = json.loads(resp.text)
                if u'验证码不正确' in resp.text:
                    self.log('crawler', u'短信验证失败', resp)
                    # return 9, 'verify_error'
                    continue
                if result['b']['m'] == u'成功':
                    return 0, 'success'
                self.log('crawler', 'verify_error1', resp)
                continue
            except:
                self.log('crawler', 'json_error', resp)
                return 9, 'json_error'
        else:
            self.log('website', 'website_busy_error', resp)
            return 9, key


    def crawl_info(self, **kwargs):

        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯个i他誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        user_info_dict = {}
        # 开始请求登记信息
        url = 'https://gd.189.cn/transaction/operApply1.jsp?operCode=ChangeCustInfoNew&in_cmpid=khzy-zcdh-yhzx-grxx-wdzl'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, {}

        try:
            htmltree = etree.HTML(resp.text)
            operCode = htmltree.xpath('//*[@name="operCode"]/@value')
            operCode = operCode[0] if operCode else ''
            latnID = htmltree.xpath('//*[@name="latn_id"]/@value')
            latnID = latnID[0] if latnID else ''
            number = htmltree.xpath('//*[@name="number"]/@value')
            number = number[0] if number else ''
            ApplyId = htmltree.xpath('//*[@name="ApplyId"]/@value')
            ApplyId = ApplyId[0] if ApplyId else ''

        except:
            err_msg = traceback.format_exc()
            self.log('crawler', 'html_error:{}'.format(err_msg), resp)
            return 9, 'html_error', {}

        data = {
            'operCode': operCode,
            'divId': 'null',
            'university': 'null',
            'custCode': '',
            'oldEmail': '',
            'latn_id': latnID,
            'ApplyId': ApplyId,
            'number': number,
            'fromPage': 'first',
            'toPage': 'second',
            'targetChk': 'targetChk',
        }
        url = 'https://gd.189.cn/OperationInitAction2.do?OperCode=ChangeCustInfoNew&Latn_id={}'.format(latnID)

        code, key, resp = self.post(url,data=data)
        if code != 0:
            return code, key, {}

        try:
            htmltree = etree.HTML(resp.text)
            name = htmltree.xpath('//*[@id="cust_name_id"]/@value')
            id_card = htmltree.xpath('//*[@id="id_num_id"]/@value')
            addr = htmltree.xpath('//*[@id="id_addr_id"]/@value')
            user_info_dict['address'] = addr[0] if addr else ''
            user_info_dict['full_name'] = name[0] if name else ''
            if id_card:
                user_info_dict['id_card'] = id_card[0]
                user_info_dict['is_realname_register'] = True
            else:
                user_info_dict['id_card'] = ""
                user_info_dict['is_realname_register'] = False

            user_info_dict['open_date'] = ""
        except:
            error = traceback.format_exc()
            self.log('crawler', 'request_error : %s' % error, resp)
            return 9, "request_error", {}
        return 0, "success", user_info_dict

    def crawl_call_log(self, **kwargs):

        crawler_error_num = 0
        missing_list = []
        possibly_missing_list = []
        part_missing_list = []

        call_log = []
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://gd.189.cn/service/home/query/xd_index.html',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'a.c': '0',
            'a.u': 'user',
            'a.p': 'pass',
            'a.s': 'ECSS',
            'c.n': '语音清单',
            'c.t': '02',
            'c.i': '02-005-04',
            'd.d01': 'call',
            'd.d02': 'endDate',
            'd.d03': 'start_month',
            'd.d04': 'end_month',
            'd.d05': '20',
            'd.d06': '1',
            'd.d07': kwargs['sms_code'],
            'd.d08': '1',
        }
        today = date.today()
        call_log_url = 'https://gd.189.cn/J/J10009.j'
        search_month = [x for x in range(-0, -6, -1)]

        for each_month in search_month:
            # 从第一页开始
            data['d.d06'] = 1
            query_date = today + relativedelta(months=each_month)
            call_month = "%d%02d" % (query_date.year, query_date.month)
            endDate = calendar.monthrange(query_date.year, query_date.month)[1]
            start_month = call_month + '01'

            # 当月查到今天
            if each_month == 0:
                end_month = "%d%02d%02d" % (today.year, today.month, today.day)
            else:
                end_month = "{}{}".format(call_month, endDate)
            data['d.d02'] = call_month
            data['d.d03'] = start_month
            data['d.d04'] = end_month
            # print(data)
            for i in range(3):
                code, key, call_log_response = self.post(call_log_url, data=data, headers=headers)
                # print('详单数据：\n')
                # print(call_log_response.text)
                # 偶发异常
                if u'用户未进行实名登记' in call_log_response.text:
                   continue
                break
            else:
                self.log('website', u'数据返回异常', call_log_response)
                continue

            if code != 0:
                missing_list.append(call_month)
                continue

            code, call_month_log, pages = self.call_log_get(call_log_response, call_month)
            if code != 0:
                crawler_error_num += 1
                if call_month_log:
                    part_missing_list.append(call_month)
                    call_log.extend(call_month_log)
                else:
                    missing_list.append(call_month)
                if pages < 1:
                    continue
            else:
                if not call_month_log:
                    self.log('website', u'没有数据', call_log_response)
                    possibly_missing_list.append(call_month)
                else:
                    call_log.extend(call_month_log)

            # 查询剩余页
            for page in range(2, pages + 1):
                # print(u'翻页==========================')
                # print(page)
                data['d.d06'] = page
                code, key, call_log_response = self.post(call_log_url, data=data, headers=headers)
                if code != 0:
                    missing_list.append(call_month)
                    continue
                code, call_month_log, pages = self.call_log_get(call_log_response, call_month)
                if code != 0:
                    crawler_error_num += 1
                    if call_month_log:
                        #
                        call_log.extend(call_month_log)
                    # 已经查到第二页了，所以记录部分缺失
                    part_missing_list.append(call_month)
                    # if pages < 1:
                        # continue
                else:
                    if not call_month_log:
                        self.log('website', u'没有数据', call_log_response)
                        possibly_missing_list.append(call_month)
                    else:
                        call_log.extend(call_month_log)
                    # call_log.extend(call_month_log)

        # 月份去重
        part_set = set(part_missing_list)
        missing_set = set(missing_list)
        possibly_set = set(possibly_missing_list)

        possibly_set = possibly_set - part_set - missing_set
        missing_set = missing_set - part_set

        part_missing_list = list(part_set)
        part_missing_list.sort(reverse=True)

        missing_list = list(missing_set)
        missing_list.sort(reverse=True)

        possibly_missing_list = list(possibly_set)
        possibly_missing_list.sort(reverse=True)
        self.log("crawler",
                 "记录缺失列表:\n 缺失:{}\n可能缺失:{}\n部分缺失:{}".format(
                     missing_list,
                     possibly_missing_list,
                     part_missing_list
                 ), "")


        if len(missing_list + possibly_missing_list) == 6:
            if crawler_error_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list, part_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list, part_missing_list
        return 0, "success",  call_log, missing_list, possibly_missing_list, part_missing_list

    def call_log_get(self, response, call_month):
        """
        | `call_tel` | string | 18202541892 | 电话号码 |
        | `call_cost` | string | 0.00 | 通话费用 |
        | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
        | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
        | `call_type` | string | 本地 | 通话类型（本地, 长途） |
        | `call_from` | string | 北京市 | 本机通话地 |
        | `call_to` | string | 长沙市 | 对方归属地 |
        | `call_duration` | integer | 300 | 通话时长(秒),
        """
        call_month_log = []
        pages = 0
        try:
            row_json = json.loads(response.text)
            if u'成功' != row_json['b']['m']:
                self.log('website', 'website_busy_error', response)
                return 9, call_month_log, pages

            # 页数
            pages = int(row_json['r']['r05'])
            for item in row_json['r']['r03']:
                call_data = {}
                call_data['month'] = call_month
                call_data['call_tel'] = item[1]
                call_data['call_type'] = item[0]
                call_data['call_method'] = item[5]
                call_data['call_cost'] = item[4]
                # call_data['call_from'] = item[6]
                call_from, error = self.formatarea(item[6])
                if call_from:
                    call_data['call_from'] = call_from
                else:
                    # self.log("crawler", "{}  {}".format(error, item[6]), "")
                    call_data['call_from'] = item[6]
                call_data['call_duration'] = self.time_format_second(item[3])
                call_data['call_time'] = self.time_format(item[2])
                call_data['call_to'] = ''
                call_month_log.append(call_data)
        except:
            error = traceback.format_exc()
            self.log('crawler', 'json_error:= {}'.format(error), response)
            return 9,  call_month_log, pages
        return 0, call_month_log, pages

    def time_format(self, timeoo):
        timeArray = time.strptime(timeoo, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

    # 将通话时长转换为秒
    def time_format_second(self, time_str):
        tis = time_str.split(':')
        real_time = int(tis[0]) * 3600 + int(tis[1]) * 60 + int(tis[2])
        return str(real_time)

    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        phone_bill = []

        headers = {
            'Referer': 'https://gd.189.cn/service/home/query/xf_zd.html?in_cmpid=khzy-zcdh-fycx-wdxf-zdcx',
        }
        # 设置cookie
        url = 'https://gd.189.cn/J/J10032.j'
        data = {
            'a.c': '0',
            'a.u': 'user',
            'a.p': 'pass',
            'a.s': 'ECSS',
        }
        code, key, resp = self.post(url, data=data, headers=headers)
        if code != 0:
            return code, key, [], []
        # print(resp.text)

        url = 'https://gd.189.cn/J/J10053.j'
        data = {
            'a.c': '0',
            'a.u': 'user',
            'a.p': 'pass',
            'a.s': 'ECSS',
            'c.n': '账单查询',
            'c.t': '02',
            'c.i': '02-004',
            'd.d01': '  ',
            'd.d02': '1',
            'd.d03': '',
            'd.d04': '',
        }
        for month in self.__monthly_period():
            data['d.d01'] = month
            for i in range(3):
                code, key, resp = self.post(url, data=data, headers=headers)
                if code != 0:
                    continue
                if u'查询失败' in resp.text:
                    time.sleep(1)
                    continue
                if u'客户帐单' in resp.text:
                    break
            else:
                self.log('website', 'website_busy_error', resp)
                missing_list.append(month)
                continue
            month_bill = {
                'bill_month': month,
                'bill_amount': '0.00',
                'bill_package': '',
                'bill_ext_calls': '',
                'bill_ext_data': '',
                'bill_ext_sms': '',
                'bill_zengzhifei': '',
                'bill_daishoufei': '',
                'bill_qita': ''
            }
            try:
                row_json = resp.json()
                bill_data = row_json['r']['r03']['r0302']
                if bill_data:
                    bill_amount = bill_data[0]['r030203']
                    bill_package = bill_data[0]['r030208'][0]['r03020802'][0]['r0302080202']
                    month_bill['bill_amount'] = bill_amount
                    month_bill['bill_package'] = bill_package
                    phone_bill.append(month_bill)
                else:
                    missing_list.append(month)
                    self.log('website', u'未查到指定数据', resp)
            except:
                err = traceback.format_exc()
                self.log('crawler', 'html_error:={}'.format(err), resp)
                missing_list.append(month)
        if len(missing_list) == 6:
            self.log('website', u'没有查到账单信息', '')
            return 9, 'website_busy_error', phone_bill, missing_list

        # print('缺失月份{}'.format(missing_list))
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, 'success', phone_bill, missing_list

    def __monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        for month_offset in range(0, length):
            yield (current_time - relativedelta(months=month_offset+1)).strftime(strf)

if __name__ == '__main__':
    c = Crawler()

    USER_ID = "18198858921"
    USER_PASSWORD = "741963"

    # USER_ID = "18938837174"
    # # USER_ID = "18938837173"
    # USER_PASSWORD = "786756"

    # USER_ID = "13318136767"
    # USER_PASSWORD = "329996"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
