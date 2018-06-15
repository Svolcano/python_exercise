# -*- coding: utf-8 -*-

from lxml import etree
from datetime import date
import traceback
import time
import sys
import re
from des_js import des_encode
# 这段代码是用于解决中文报错的问题
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
        today = date.today()
        self.this_month = "%d%02d" % (today.year, today.month)
        self.user_no = ''

        # 查询方式1，查询方式2
        self.flag = 1

    def need_parameters(self, **kwargs):
        return ['pin_pwd', 'full_name', 'id_card']

    def get_login_verify_type(self, **kwargs):
        pass

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        url = "http://gx.189.cn/public/common/control/dwr/engine.js"
        code, key, resp = self.get(url)
        if code != 0:
            return code, key
        try:
            scriptSessionId = re.findall('dwr.engine._origScriptSessionId = "([\S]+)";', resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", u'获取scriptSessionId失败:{}'.format(error), '')
            return 9, 'crawl_error'

        # 请求key 用于密码加密
        url = 'http://gx.189.cn/chaxun/iframe/user_center.jsp'
        code, key, resp = self.get(url)
        if code != 0:
            return code, key
        key1 = re.findall("var key1='(.*?)';", resp.text)
        key2 = re.findall("var key2='(.*?)';", resp.text)
        key3 = re.findall("var key3='(.*?)';", resp.text)
        try:
            pin_pwd = '__' + str(des_encode(kwargs['pin_pwd'], key1[0], key2[0], key3[0]))
        except:
            error = traceback.format_exc()
            self.log("crawler", u'加密失败:{}'.format(error), '')
            return 9, 'crawl_error'

        # 增加访问连接
        url = 'http://gx.189.cn/dwr/call/plaincall/Service.excute.dwr'
        row_data = """callCount=1
        page=/chaxun/iframe/user_center.jsp
        httpSessionId=
        scriptSessionId={}
        c0-scriptName=Service
        c0-methodName=excute
        c0-id=0
        c0-param0=string:WB_IP_ACTION_QRY
        c0-param1=boolean:true
        c0-e1=string:0.0.0.0
        c0-e2=string:24
        c0-e3=string:2
        c0-param2=Object_Object:{}
        batchId=0
        """.format(scriptSessionId, '{CUST_IP:reference:c0-e1, TIME_RANGE:reference:c0-e2, LOG_TYPE:reference:c0-e3}')
        headers = {
            'Referer': 'http://gx.189.cn/chaxun/iframe/user_center.jsp',
            'Content-Type': 'text/plain',
            'Origin': 'http://gx.189.cn',
        }

        code, key, resp = self.post(url, data=row_data.replace(' ', ''), headers=headers)
        if code != 0:
            return code, key

        login_url = "http://gx.189.cn/public/login.jsp"
        login_data = {
            'LOGIN_TYPE': '21',
            'RAND_TYPE': '001',
            'AREA_CODE': '',
            'logon_name': kwargs['tel'],
            'password_type_ra':	'1',
            'logon_passwd': pin_pwd,
            'logon_valid': '请输入验证码'
        }
        header = {'Referer': 'http://gx.189.cn/chaxun/iframe/user_center.jsp'}
        code, key, login_req = self.post(login_url, data=login_data, headers=header)
        if code != 0:
            return code, key

        if '<flag>0</flag>' in login_req.text:
            self.log('crawler', '登录返回信息', login_req)
            try:
                self.user_no = re.findall('<user_no>(.*)</user_no>', login_req.text)[0]
            except:
                error = traceback.format_exc()
                self.log('website', u'登录出错{}'.format(error), resp)
                return 9, 'website_busy_error'
            return 0, 'success'
            #密码错误时会返回： 对不起，您已经连续输错了2次密码，如连续错误达5次，您的账号将被限制登陆6小时
        elif u'验证码错误' in login_req.text:
            self.log("website", 'website_busy_error', login_req)
            return 9, 'website_busy_error'
        elif u'如连续错误达5次' in login_req.text or u'密码错误' in login_req.text:
            self.log('user', 'pin_pwd_error', login_req)
            return 1, 'pin_pwd_error'
        elif u'密码过于简单' in login_req.text:
            self.log('user', 'sample_pwd', login_req)
            return 1, 'sample_pwd'
        elif u'号码不存在' in login_req.text:
            self.log('user', 'invalid_tel', login_req)
            return 1, 'invalid_tel'
        elif u'您的账号在6小时内被限制登陆' in login_req.text:
            self.log('user', 'over_query_limit', login_req)
            return 9, 'over_query_limit'
        elif u'系统繁忙' in login_req.text or '<?xml version="1.0" encoding="utf-8" ?>' in login_req.text:
            self.log('website', 'website_busy_error', login_req)
            return 9, 'website_busy_error'
        elif u'密码锁定' in login_req.text or 'data-resultcode="9113"' in login_req.text:
            self.log('crawler', 'website_busy_error', login_req)
            return 9, 'website_busy_error'
        elif u"信息核对失败" in login_req.text:
            self.log("user", "website_busy_error", login_req)
            return 9, "website_busy_error"
        else:
            self.log('crawler', 'html_error', login_req)
            return 9, 'html_error'

    def send_verify_request(self, **kwargs):
        get_iframe_url = "http://gx.189.cn/chaxun/iframe/user_center.jsp"
        headers = {
            "Referer": "http://gx.189.cn/chaxun/iframe/user_center.jsp"
        }
        error = u'获取prod_type失败'
        for i in range(3):
            code, key, resp = self.get(get_iframe_url, headers=headers)
            if code != 0:
                return code, key, ''
            try:
                acc_nbr = re.findall(r"ACC_NBR:'(.*?)'", resp.text)[0]
                prod_type = re.findall(r"PROD_TYPE:'(.*?)'", resp.text)[0]
                break
            except:
                error = traceback.format_exc()
                data = {
                    'Logon_Name': kwargs['tel'],
                    'USER_FLAG': '001',
                    'USE_PROTOCOL': '',
                    'LOGIN_TYPE': '21',
                    'USER_NO': self.user_no,
                    'ESFlag': '8',
                    'REDIRECT_URL': '/2015/',
                }
                agree_url = 'http://gx.189.cn/public/user_protocol.jsp'
                code, key, response = self.post(agree_url, headers=headers, data=data)
                if code != 0:
                    return code, key, ''
                self.log('user', u'用户协议页面', response)
                agree_url02 = 'http://gx.189.cn/public/protocollogin.jsp'
                data = {
                    'OPEN_TYPE': '1',
                    'LOGIN_TYPE': '21',
                    'USER_NO': self.user_no,
                    'CUSTBRAND': '',
                    'ESFlag': '8',
                    'REDIRECT_URL': '/2015/',
                }
                code, key, response = self.post(agree_url02, headers=headers, data=data)
                if code != 0:
                    return code, key, ''
                self.log('user', u'用户同意页面', response)

                next_url = 'http://gx.189.cn/sales/chipmap/chipmaplogin.jsp'
                n_header = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'http://gx.189.cn/public/protocollogin.jsp',
                }
                code, key, response = self.post(next_url, headers=n_header)
                if code != 0:
                    return code, key, ''

                self.log('user', u'用户同意跳转页面', response)
                next_url02 = 'http://gx.189.cn/sales/chipmap/chipmapRecom.jsp'
                code, key, response = self.post(next_url02, headers=n_header)
                if code != 0:
                    return code, key, ''
                self.log('user', u'用户同意跳转页面02', response)
        else:
            self.log("crawler", 'html_error: {}'.format(error), resp)
            return 9, "html_error", ""

        get_post_data_url = "http://gx.189.cn/chaxun/iframe/qdcx.jsp"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://gx.189.cn/chaxun/iframe/user_center.jsp"
        }
        data = {
            "ACC_NBR": acc_nbr,
            "PROD_TYPE": prod_type
        }

        code, key, resp = self.post(get_post_data_url, headers=headers, data=data)
        if code != 0:
            return code, key, ""
        sms_data = {}
        try:
            et = etree.HTML(resp.text)
            er_name = et.xpath('//form[@id="frmGetPwd"]/input/@name')
            er_value = et.xpath('//form[@id="frmGetPwd"]/input/@value')
            for name, value in zip(er_name, er_value):
                sms_data[name] = value
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error{}".format(error), resp)
            return 9, "html_error", ""

        sms_url = 'http://gx.189.cn/service/bill/getRand.jsp'
        header = {
            'Referer': 'http://gx.189.cn/chaxun/iframe/user_center.jsp'
        }
        data = {
            'FIND_TYPE': '1031',   # 市话
            'radioQryType':	'on',  # 按月查询
            'ACCT_DATE': self.this_month,
            'ACCT_DATE_1': self.this_month,
            'PASSWORD': '',
            'CUST_NAME': '',
            'CARD_TYPE': '1',  # 使用居民身份证
            'CARD_NO': ''
        }
        data.update(sms_data)
        code, key, resp = self.post(sms_url, data=data, headers=header)
        if code != 0:
            return code, key, ''
        if '<flag>0</flag>' in resp.text:
            return 0, "success", ""
        elif u'您短时间内不能重复获取随机密码' in resp.text:
            self.log('crawler', 'send_sms_too_quick_error', resp)
            return 9, 'send_sms_too_quick_error', ''
        elif u'您输入的手机号码有误或不存在' in resp.text:
            self.log('user', 'invalid_tel', resp)
            return 1, 'invalid_tel', ''
        else:
            self.log('crawler', 'html_error', resp)
            return 9, 'html_error', ''

    def verify(self, **kwargs):
        cookie_url = 'http://gx.189.cn/public/realname/checkRealName.jsp'
        header = {
            'Referer': 'http://gx.189.cn/chaxun/iframe/user_center.jsp',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'NUM':	kwargs['tel'],
            'V_PASSWORD': kwargs['sms_code'],
            'CUST_NAME': kwargs['full_name'].encode("utf8"),
            'CARD_NO': kwargs['id_card'],
            'CARD_TYPE': '1',
            'RAND_TYPE': '002'
        }
        code, key, resp = self.post(cookie_url, data=data, headers=header)
        if code != 0:
            return code, key
        if '<PrivilegeLevel>1</PrivilegeLevel>' in resp.text:
            verify_url = 'http://gx.189.cn/chaxun/iframe/inxxall_new.jsp'
            header = {
                'Referer': 'http://gx.189.cn/chaxun/iframe/user_center.jsp',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'PRODTYPE': '2020966',
                'RAND_TYPE': '002',
                'BureauCode': '1300',
                'ACC_NBR': kwargs['tel'],
                'PROD_TYPE': '2020966',
                'PROD_PWD': '',
                'REFRESH_FLAG':	'1',
                'BEGIN_DATE': '',
                'END_DATE': '',
                'SERV_NO': '',
                'QRY_FLAG':	'1',
                'MOBILE_NAME': kwargs['tel'],
                'OPER_TYPE': 'CR1',
                'FIND_TYPE': '1041',
                'radioQryType':	'on',
                'ACCT_DATE': self.this_month,
                'ACCT_DATE_1': self.this_month,
                'PASSWORD':	kwargs['sms_code'],
                'CUST_NAME': kwargs['full_name'].encode("utf8"),
                'CARD_TYPE': '1',
                'CARD_NO': kwargs['id_card']
            }
            code, key, response = self.post(verify_url, data=data, headers=header)
            if code != 0:
                return code, key
            if 'mask_div_id' in response.text:
                if '<option value="1037"  >本地拨打异地清单</option>' in response.text:
                    self.flag = 2
                return 0, 'success'
            else:
                self.log('crawler', 'html_error', response)
                return 9, 'html_error'
        elif u'对不起,您输入的名字或证件号码不正确' in resp.text:
            self.log('user', 'user_name_error or user_id_error', resp)
            return 2, 'user_name_error'
        elif u'验证码错误' in resp.text:
            self.log('user', 'verify_error', resp)
            return 2, 'verify_error'
        elif u'系统繁忙' in resp.text:
            self.log("website", 'website_busy_error', resp)
            return 9, 'website_busy_error'
        elif u'未进行实名验证' in resp.text:
            self.log("user", u"您的号码未进行实名验证，请您携带有效证件到当地营业厅办理实名登记", resp)
            return 9, 'real_name_registration_error'
        else:
            self.log('crawler', 'html_error', resp)
            return 9, 'html_error'

    def crawl_call_log(self, **kwargs):
        missing_list = []
        possibly_missing_list = []
        website_num = 0
        crawler_num = 0
        today = date.today()
        call_log = []

        search_month = [x for x in range(0, -6, -1)]
        #这个列表 表示详单类型， 1041是漫游通话清单， 1040是长话清单，1031是市话清单，1035是国际及港澳台清单
        if self.flag == 1:
            FIND_TYPE_LIST = ['1041', '1040', '1031', '1035']
        else:
            FIND_TYPE_LIST = ['1037', '1038', '1039']

        for each_month in search_month:
            #这个变量用来统计这个月的可能缺失类型个数， 当可能缺失类型个数达到4个的时候， 加到possibly_missing
            month_type = 0
            for call_type in FIND_TYPE_LIST:
                query_date = today + relativedelta(months=each_month)
                query_month = "%d%02d" % (query_date.year, query_date.month)
                if query_month == self.this_month:
                    last_month = query_month
                else:
                    query_date = query_date + relativedelta(months=1)
                    last_month = "%d%02d" % (query_date.year, query_date.month)

                key, level, call_log_history, wrong_flag = self.deal_call_log(call_type, kwargs['tel'], query_month, last_month)
                if level == -1:
                    month_type += 1
                elif level != 0:
                    missing_list.append(query_month)
                    if wrong_flag == 'website':
                        website_num += 1
                    elif wrong_flag == 'crawler':
                        crawler_num += 1
                else:
                    if call_log_history:
                        call_log.extend(call_log_history)
                    else:
                        month_type += 1
            if month_type == 4:
                possibly_missing_list.append(query_month)
        missing_list = list(set(missing_list))
        if len(missing_list) == 6 or len(possibly_missing_list) == 6:
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        if crawler_num > 0:
            return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def deal_call_log(self, call_type, tel, query_month, last_month):
        call_log_url = 'http://gx.189.cn/chaxun/iframe/inxxall_new.jsp'
        header = {
            'Referer': 'http://gx.189.cn/chaxun/iframe/user_center.jsp'
        }
        data = {
            'ACC_NBR': tel,
            'PROD_TYPE': '2020966',
            'BEGIN_DATE': '',
            'END_DATE': '',
            'REFRESH_FLAG': '1',
            'QRY_FLAG': '1',
            'FIND_TYPE': call_type,
            'radioQryType': 'on',
            'ACCT_DATE': query_month,
            'ACCT_DATE_1': last_month
        }
        for retry in xrange(self.max_retry):
            code, key, resp = self.post(call_log_url, headers=header, data=data)
            if code != 0 or u'无记录</td>' in resp.text or u'错误日志序号' in resp.text:
                continue
            else:
                break
        else:
            if code != 0:
                return key, code, [], 'website'
            else:
                self.log('crawler', '没有查找到相关数据', resp)
                return '', -1, '', ''
        key, level, message, call_month_log = self.call_log_get(resp.text, query_month)
        if level != 0:
            self.log('crawler', message, resp)
            return "html_error", 9, [], 'crawler'
        if not call_month_log:
            self.log('website', 'no data', resp)
        return 'success', 0, call_month_log, ''

    def call_log_get(self, response, query_month):
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
            html_tree = etree.HTML(response)
            log_list = html_tree.xpath('//table[@id="list_table"]/tr')[2:-1]
            for log in log_list:
                data = {}
                row_data = log.xpath('./td/text()')
                if len(row_data) <= 1:
                    continue
                call_time = log.xpath('./td[2]/text()')[0]
                is_time = len(call_time.split(":"))
                if is_time == 3:
                    data['month'] = query_month
                    data['call_method'] = log.xpath('./td[4]/text()')[0]
                    data['call_tel'] = log.xpath('./td[5]/text()')[0] if log.xpath('./td[5]/text()') else ''
                    call_time = log.xpath('./td[2]/text()')[0]
                    data['call_time'] = self.time_format(call_time)
                    call_duration = log.xpath('./td[6]/text()')[0]
                    time_temp = call_duration.split(':')
                    data['call_duration'] = str(int(time_temp[0]) * 60 * 60 + int(time_temp[1]) * 60 + int(time_temp[2]))
                    data['call_type'] = ''
                    # data['call_from'] = log.xpath('./td[3]/text()')[0] if log.xpath('./td[3]/text()') else ''

                    raw_call_from = log.xpath('./td[3]/text()')[0] if log.xpath('./td[3]/text()') else ''
                    call_from, error = self.formatarea(raw_call_from)
                    if call_from:
                        data['call_from'] = call_from
                    else:
                        self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                        data['call_from'] = raw_call_from

                    data['call_to'] = ''
                    data['call_cost'] = log.xpath('./td[8]/text()')[0] if log.xpath('./td[8]/text()') else ''
                    call_month_log.append(data)
                else:
                    call_method = log.xpath('./td[2]/text()')[0]
                    # 目录走这个，其余会走上面
                    if call_method == u'起始时间':
                        continue

                    data['month'] = query_month
                    data['call_method'] = call_method
                    data['call_tel'] = log.xpath('./td[5]/text()')[0] if log.xpath('./td[5]/text()') else ''
                    call_time = log.xpath('./td[6]/text()')[0]
                    data['call_time'] = self.time_format(call_time)
                    data['call_duration'] = log.xpath('./td[7]/text()')[0]
                    data['call_type'] = ''
                    data['call_from'] = log.xpath('./td[3]/text()')[0] if log.xpath('./td[3]/text()') else ''
                    data['call_to'] = ''
                    data['call_cost'] = log.xpath('./td[9]/text()')[0] if log.xpath('./td[9]/text()') else ''
                    call_month_log.append(data)
        except:
            error = traceback.format_exc()
            return 'html_error', 9, 'html_error ' + error, call_month_log
        return 'success', 0, 'success', call_month_log

    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯个i他誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        info_url = 'http://gx.189.cn/service/manage/my_selfinfo.jsp'
        header = {
            'X-Requested-With': 'XMLHttpRequest',
        }
        code, key, res = self.post(info_url, headers=header)
        if code != 0:
            return code, key, {}
        full_name = re.findall(u'name="USER_NAME" value="(.*?)"', res.text)
        full_name = full_name[0] if full_name else ''

        user_info_data = {
            'full_name': full_name,
            'id_card': '',
            'open_date': '',
            'address': ''
        }
        return 0, "success", user_info_data

    def time_format(self, timeoo):
        call_time = re.findall('\d{2}', timeoo)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[
            3] + ' ' + call_time[4] + ':' + call_time[5] + ':' + call_time[6]
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        phone_bill = list()
        today = date.today()
        # 没有当月账单
        search_month = [x for x in range(-1, -6, -1)]
        bill_url = 'http://gx.189.cn/chaxun/iframe/cust_zd.jsp'
        header = {'X-Requested-With': 'XMLHttpRequest'}
        crawl_num = 0

        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            params = {
                'ACC_NBR': kwargs['tel'],
                'DATE': query_month,
                '_': int(time.time() * 1000)
            }
            for retry in xrange(self.max_retry):
                code, key, resp = self.get(bill_url, params=params, headers=header)
                if code != 0:
                    continue
                if u'错误日志序号：' in resp.text:
                    if retry == self.max_retry - 1:
                        self.log('user', '账单为空', resp)
                    continue
                code, key, message, result = self.crawl_month_bill(query_month, resp.text)
                if code != 0:
                    if retry == self.max_retry - 1:
                        crawl_num += 1
                        self.log('crawler', message, resp)
                    continue
                phone_bill.append(result)
                break
            else:
                # 访问出错不再记日志
                missing_list.append(query_month)

        if len(missing_list) == 5:
            if crawl_num > 1:
                return 9, 'crawl_error', phone_bill, missing_list
            return 9, 'website_busy_error', phone_bill, missing_list
        return 0, 'success', phone_bill, missing_list

    def crawl_month_bill(self, query_month, resp):
        month_fee_data = {}
        month_fee_data['bill_month'] = query_month
        month_fee_data['bill_amount'] = ''
        month_fee_data['bill_ext_calls'] = ''
        month_fee_data['bill_ext_data'] = ''
        month_fee_data['bill_ext_sms'] = ''
        month_fee_data['bill_zengzhifei'] = ''
        month_fee_data['bill_daishoufei'] = ''
        month_fee_data['bill_qita'] = ''
        try:
            bill_package = re.findall(u'套餐月基本费.*?x">(\d+\.\d+)<', resp, re.S)
            month_fee_data['bill_package'] = bill_package[0] if len(bill_package) else ''

            bill_ext_sms = re.findall(u'国内短信费.*?x">(\d+\.\d+)<', resp, re.S)
            month_fee_data['bill_ext_sms'] = bill_ext_sms[0] if len(bill_ext_sms) else ''

            bill_amount = re.findall(u'本期费用合计:(\d+\.\d+)元', resp, re.S)
            month_fee_data['bill_amount'] = bill_amount[0] if len(bill_amount) else ''

        except:
            error = traceback.format_exc()
            return 9, 'html_error', 'html_error'+error, {}
        return 0, 'success', 'success', month_fee_data

if __name__ == '__main__':
    c = Crawler()

    # TEL = "18076766149"
    # USER_PASSWORD = "890907"
    # ID_CARD = '14072319930902003X'
    # USER_NAME = '青培'

    # TEL = "18078454964"
    # USER_PASSWORD = "941667"
    # ID_CARD = '110229199501253824'
    # USER_NAME = '王阳'

    USER_PASSWORD = "746656"
    ID_CARD = '130981199605276614'
    USER_NAME = '韩映辉'
    TEL = "17377135156"
    # TEL = "17377135152"



    # self_test
    c.self_test(tel=TEL, pin_pwd=USER_PASSWORD, id_card=ID_CARD, full_name=USER_NAME)