# -*- coding: utf-8 -*-
import base64
import time
import re
import traceback
import sys
import random
reload(sys)
sys.setdefaultencoding("utf8")
import datetime
if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
    from crawler.china_telecom_tool import login_unity
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_unity

from common import aes_encrypt, parse_call_record
from datetime import date
from dateutil.relativedelta import relativedelta
from lxml import etree

class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)

    def need_parameters(self, **kwargs):
        return ['full_name', 'id_card', 'pin_pwd']

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def login(self, **kwargs):
        LOGIN_PARAMS_URL = "http://login.189.cn/login/ajax"
        login_params_data = {
            'm': 'checkphone',
            'phone': kwargs['tel']
        }
        code, key, resp = self.post(LOGIN_PARAMS_URL, data=login_params_data)
        if code != 0:
            return code, key
        # 这个地方 账号不存在 的话会返回空
        if not resp.text:
            self.log('user', 'invalid_tel', resp)
            return 1, 'invalid_tel'
        try:
            login_params_res = resp.json()
            if login_params_res.get('areaCode'):
                self.AreaCode = login_params_res.get('areaCode')
            else:
                self.log('crawler', 'crawl_error', resp)
                return 9, "crawl_error"
        except:
            error = traceback.format_exc()
            self.log('crawler', 'json_error:{}'.format(error), resp)
            return 9, "json_error"

        home_url = 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=01941229'
        code, key, resp = self.get(home_url)
        if code != 0:
            return code, key

        ProvinceID = '25'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        test_url = 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=01941229'
        header = {
            'Referer': 'http://www.189.cn/yn/',
            'Upgrade-Insecure-Requests': '1'
        }
        code, key, res = self.get(test_url, headers=header)
        if code != 0:
            return code, key
        if u'详单查询' in res.text:
            COOKIE_URL = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10025&toStUrl=http://yn.189.cn/service/jt/bill/qry_mainjt.jsp?SERV_NO=SHQD1&fastcode=01941229&cityCode=yn"

            code, key, cookie_req = self.get(COOKIE_URL)
            if code != 0:
                return code, key

            PROD_PARAMS_URL = "http://yn.189.cn/service/jt/bill/qry_mainjt.jsp?SERV_NO=SHQD1&fastcode=01941229&cityCode=yn"
            header = {
                'Referer': cookie_req.url
            }

            flag = True
            for retry in range(3):
                code, key, resp = self.get(PROD_PARAMS_URL, headers=header)
                if code != 0:
                    if retry == 2:
                        return code, key
                    continue

                prod_params_data = re.findall("doQuery\('(\d{11})','(\d{4})','(\d{4})','','(\d+)','(\d+)',", resp.text)
                if prod_params_data:
                    flag = False
                    break
            if flag:
                self.log('website', 'website_busy_error', resp)
                return 9, 'website_busy_error'
            try:
                self.prod_no = prod_params_data[0][2]
                self.user_id = prod_params_data[0][4]
            except:
                error = traceback.format_exc()
                self.log('crawler', 'expected_key_error:{}'.format(error), resp)
                return 9, "expected_key_error"
            LOGIN_PARAMS_URL = "http://yn.189.cn/service/jt/bill/actionjt/ifr_bill_detailslist_new.jsp"
            login_params_data = {
                "NUM": kwargs['tel'],
                "AREA_CODE": prod_params_data[0][1],
                "PROD_NO": prod_params_data[0][2],
                "USER_NAME": "",
                "ACCT_ID": prod_params_data[0][3],
                "USER_ID": prod_params_data[0][4]
            }
            header = {
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'http://yn.189.cn/service/jt/bill/qry_mainjt.jsp?SERV_NO=SHQD1&fastcode=01941229&cityCode=yn'
            }
            code, key, resp = self.post(LOGIN_PARAMS_URL, data=login_params_data, headers=header)
            if code != 0:
                return code, key
            if u'客户姓名' in resp.text:
                return 0, "success"
            else:
                self.log('crawler', 'expected_key_error', resp)
                return 9, "expected_key_error"
        else:
            if u'<title>电信账号登录</title>' in res.text or '<img src="/dqmh/errors/images/error_content_busy.png" />' in res.text:
                # error_content_busy.png 很抱歉, 目前系统繁忙, 请稍后再试
                self.log("crawler", 'website_busy_error', res)
                return 9, 'website_busy_error'
            else:
                self.log('crawler', 'html_error', res)
                return 9, 'html_error'

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片
        return
        status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
        level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
        message: unicode, 詳細的錯誤信息
        image_str: str, Captcha圖片, SMS則回空
        """
        SMS_POST_URL = "http://yn.189.cn/public/postValidCode.jsp"
        sms_post_data = {
            "NUM":kwargs['tel'],
            # "AREA_CODE": '0872',
            "AREA_CODE": '%04d' % int(self.AreaCode),
            "LOGIN_TYPE":"21",
            "OPER_TYPE":"CR0",
            "RAND_TYPE":"004"
        }
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type':'application/x-www-form-urlencoded',
            'Referer':'http://yn.189.cn/service/jt/bill/qry_mainjt.jsp?SERV_NO=SHQD1&fastcode=01941229&cityCode=yn',
            }
        code, key, resp = self.post(SMS_POST_URL, data=sms_post_data, headers=headers)
        if code != 0:
            return code, key, ''
        if '<actionFlag>0</actionFlag>' in resp.text:
            return 0, 'success', ''
        elif '<actionFlag>-196910</actionFlag>' in resp.text or '<actionFlag>-22050222</actionFlag>' in resp.text:
            self.log('user', 'send_sms_too_quick_error', resp)
            return 9, 'send_sms_too_quick_error', ''
        elif u'出现异常' in resp.text:
            self.log('user', 'website_busy_error', resp)
            return 9, 'website_busy_error', ''
        else:
            self.log('user', 'unknown_error', resp)
            return 9, "unknown_error", ''

    def verify(self, **kwargs):
        CHECK_ID_URL = "http://yn.189.cn/public/custValid.jsp"
        check_id_data = {
            "_FUNC_ID_":"WB_PAGE_PRODPASSWDQRY",
            # "NAME":kwargs['full_name'],
            # "CUSTCARDNO":kwargs['id_card'],
            "PROD_PASS":kwargs['pin_pwd'],
            "MOBILE_CODE":kwargs['sms_code'],
            "NAME":kwargs['full_name'],
            "CUSTCARDNO":kwargs['id_card']
        }
        header = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://yn.189.cn/service/jt/bill/qry_mainjt.jsp?SERV_NO=SHQD1&fastcode=01941229&cityCode=yn',
        }
        code, key, check_id_req = self.post(CHECK_ID_URL, data=check_id_data, headers=header)
        if code != 0:
            return code, key
        if '<rsFlag>1</rsFlag>' in check_id_req.text:
            CHECK_SMS_URL = "http://yn.189.cn/public/pwValid.jsp"
            check_sms_data = {
                "_FUNC_ID_":"WB_PAGE_PRODPASSWDQRY",
                "NAME":kwargs['full_name'],
                "CUSTCARDNO":kwargs['id_card'],
                "PROD_PASS":kwargs['pin_pwd'],
                "MOBILE_CODE":kwargs['sms_code'],
                "ACC_NBR":kwargs['tel'],
                "AREA_CODE": '%04d' % int(self.AreaCode),
                # "AREA_CODE": '0872',
                "LOGIN_TYPE":'21',
                "PASSWORD":kwargs['pin_pwd'],
                "MOBILE_FLAG":'1',
                "MOBILE_LOGON_NAME":kwargs['tel'],
                # "MOBILE_CODE":kwargs['sms_code'],
                "PROD_NO":self.prod_no
            }
            header = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'http://yn.189.cn/service/jt/bill/qry_mainjt.jsp?SERV_NO=SHQD1&fastcode=01941229&cityCode=yn'
            }
            code, key, check_sms_req = self.post(CHECK_SMS_URL, data=check_sms_data, headers=header)
            if code != 0:
                return code, key
            if '<rsFlag>-2</rsFlag>' in check_sms_req.text or '<rsFlag>-3</rsFlag>' in check_sms_req.text:
                return 2, "verify_error"

            # url = 'http://yn.189.cn/public/query_realnameInfo.jsp'
            # data = {
            #     'NUM': kwargs['tel'],
            #     'AREA_CODE': '',
            #     'accNbrType': '9'
            # }
            # header = {
            #     'X-Requested-With': 'XMLHttpRequest',
            #     'Referer': 'http://yn.189.cn/service/jt/bill/qry_mainjt.jsp?SERV_NO=SHQD1&fastcode=01941229&cityCode=yn'
            # }
            # code, key, req = self.get(url, params=data, headers=header)
            # if code != 0:
            #     return code, key
            # if '<actionFlag>0</actionFlag>' in req.text:
            BILL_DETAIL_URL = 'http://yn.189.cn/service/jt/bill/actionjt/ifr_bill_detailslist_new.jsp'
            bill_detail_data = {
                "NUM": kwargs['tel'],
                "AREA_CODE":  '%04d' % int(self.AreaCode),
                # "AREA_CODE": '0872',
                'PROD_NO': self.prod_no
            }
            code, key, bill_detail_req = self.post(BILL_DETAIL_URL, data=bill_detail_data)
            if code != 0:
                return code, key
            if u'<th nowrap="nowrap">查询范围</th>' in bill_detail_req.text:
                return 0, 'success'
            elif u'请输入验证信息' in bill_detail_req.text:
                self.log("user", "短信验证码错误", bill_detail_req)
                return 2, "verify_error"
            else:
                self.log('website', 'website_busy_error', bill_detail_req)
                return 9, 'website_busy_error'

            # else:
            #     self.log('crawler', 'html_error', req)
            #     return 9, 'website_busy_error'
            # elif '<rsFlag>-1</rsFlag>' in check_sms_req.text:
            #     self.log('user', 'verify_error', check_sms_req)
            #     return 2, "verify_error"
            # elif '<rsFlag>-2</rsFlag>' in check_sms_req.text:
            #     self.log('user', 'verify_error', check_sms_req)
            #     return 2, "verify_error"
            # elif '<rsFlag>-3</rsFlag>' in check_sms_req.text:
            #     self.log('user', 'verify_error', check_sms_req)
            #     return 2, "verify_error"
            # else:
            #     self.log('crawler', 'unknown_error', check_sms_req)
            #     return 9,"unknown_error"
        elif '<rsFlag></rsFlag>' in check_id_req.text:
            self.log('user', u'姓名或者身份证错误', check_id_req)
            return 2, "user_id_error"
        else:
            self.log('crawler', 'expected_key_error', check_id_req)
            return 9, "expected_key_error"

    
    def crawl_info(self, **kwargs):
        result = {}
        USER_INFO_URL = "http://yn.189.cn/service/manage/my_selfinfo.jsp"
        code, key, resp = self.get(USER_INFO_URL)
        if code != 0:
            return code, key, {}
        try:
            selector = etree.HTML(resp.text)
            result['full_name'] = selector.xpath('//td[@id="NAMEA"]/text()')[0]
            result['id_card'] = selector.xpath('//td[@id="CUSTCARDNO"]/text()')[0]
            result['address'] = selector.xpath('//input[@id="RelaAddress"]/@value')[0]
            open_date = selector.xpath('//form[@id="frmModify"]//tr[last()]/td/text()')[0]
            result['open_date'] = self.time_format(open_date)
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error:{}'.format(error), resp)
            return 9, "html_error", {}
        if result['id_card']:
            result['is_realname_register'] = True
        else:
            result['is_realname_register'] = False
        return 0, "success", result

    def time_format(self,timeoo):
        call_time = re.findall('\d{2}', timeoo)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[
            3] + ' ' + '00' + ':' + '00' + ':' + '00'
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp

    def get_year_month(self, number):
        month_list = []
        for each_month in xrange(-0, -number, -1):
            today = datetime.date.today()
            query_date = today + relativedelta(months=each_month)
            month_list.append("%d%02d" % (query_date.year, query_date.month))
        return month_list

    def crawl_call_log(self, **kwargs):
        """同一ip每天详单查询次数有上限,超过数据请求返回空"""
        missing_month_list = []
        possibly_missing_list = []
        part_missing_list = []
        crawl_num = 0
        today = date.today()
        records = []
        delta_months = [i for i in range(0, -6, -1)]
        BILL_DETAIL_URL = "http://yn.189.cn/service/jt/bill/actionjt/ifr_bill_detailslist_em_new.jsp"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://yn.189.cn/service/jt/bill/qry_mainjt.jsp?SERV_NO=SHQD1&fastcode=01941229&cityCode=yn"
        }
        for delta_month in delta_months:
            query_date = today + relativedelta(months=delta_month)
            search_month = "%d%02d" % (query_date.year, query_date.month)
            bill_detail_data = {
                "NUM": kwargs['tel'],
                "AREA_CODE": '%04d' % int(self.AreaCode),
                "CYCLE_BEGIN_DATE": "",
                "CYCLE_END_DATE": "",
                "BILLING_CYCLE": search_month,
                "QUERY_TYPE": "10"
            }
            missing_flag = False

            for retry in xrange(8):
                # IP访问有限制, 就不大量重试
                code, key, resp = self.post(BILL_DETAIL_URL, data=bill_detail_data, headers=headers)
                if code != 0:
                    missing_flag = True
                elif u'尊敬的客户，您所查询的条件内没有相应的记录' in resp.text:
                    missing_flag = False
                else:
                    break
            else:
                if missing_flag:
                    missing_month_list.append(search_month)
                else:
                    self.log('crawler', '没有详单记录', resp)
                    # 没有详单记录在可能缺失里面
                    possibly_missing_list.append(search_month)
                continue
            # with open(search_month+'.py', 'w')as f:
            #     f.write(resp.text)
            try:
                page_num = re.search(u'条记录.*?\d+\/(\d+)', resp.text, re.S)
                page_num = int(page_num.group(1)) if page_num else 1
            except:
                error = traceback.format_exc()
                self.log('crawler', 'crawl_error:{}'.format(error), '')
                missing_month_list.append(search_month)
                crawl_num += 1
                continue

            # 以下三行先把第一页的获取了
            code, key, message, data = parse_call_record(self, resp.text, search_month, kwargs['tel'])
            if code != 0:
                self.log('crawler', message, resp)
                missing_month_list.append(search_month)
                if message != 'no_body':
                    crawl_num += 1
                continue
            if data:
                records.extend(data)
            else:
                self.log("crawler", 'html_error: 值为空', resp)
                possibly_missing_list.append(search_month)

            st_time = time.time()
            et_time = st_time + 15
            rand_sleep = random.randint(3, 5)

            if page_num > 1:
                # 有多页的情况
                page_list = list(range(2, page_num + 1))
                page_and_retry = [(page, self.max_retry) for page in page_list]
                log_page_retry = []
                while page_and_retry:
                    page, retry_times = page_and_retry.pop(0)
                    log_page_retry.append((page,retry_times))
                    retry_times -= 1
                    bill_detail_data['pageno'] = page
                    # for retry in xrange(5):
                    code, key, resp = self.post(BILL_DETAIL_URL, data=bill_detail_data, headers=headers)
                    if code != 0:
                        now_time = time.time()
                        if retry_times > 0:
                            page_and_retry.append((page, retry_times))
                        elif now_time < et_time:
                            page_and_retry.append((page, retry_times))
                            time.sleep(rand_sleep)
                        else:
                            self.log("crawler", '第{}页时无数据'.format(page_num), resp)
                            part_missing_list.append(search_month)
                    else:
                        code, key, message, data = parse_call_record(self, resp.text, search_month, kwargs['tel'])
                        if code != 0:
                            self.log("crawler", message, resp)
                            if message != "no_body":
                                crawl_num += 1
                        if data:
                            records.extend(data)
                        else:
                            self.log('crawler', message, resp)
                self.log("crawler","缺页重试：{}".format(log_page_retry),"")
        part_set = set(part_missing_list)
        part_missing_list = list(part_set)
        part_missing_list.sort(reverse=True)
        self.log("crawler",
                 "缺失: {}, 可能缺失: {}, 部分缺失: {}".format(missing_month_list, possibly_missing_list, part_missing_list), "")
        if len(missing_month_list) + len(possibly_missing_list) == 6:
            if crawl_num > 0:
                self.log("crawler", '爬虫失败导致报错: 错误个数{}'.format(crawl_num), '')
                return 9, 'crawl_error', records, missing_month_list, possibly_missing_list, part_missing_list
            return 9, 'website_busy_error', records, missing_month_list, possibly_missing_list, part_missing_list
        return 0, 'success', records, missing_month_list, possibly_missing_list, part_missing_list

    def crawl_phone_bill(self, **kwargs):
        """
        bill_month      string  201612  账单月份
        bill_amount     string  10.00   账单总额
        bill_package    string  10.00   套餐及固定费
        bill_ext_calls  string  10.00   套餐外语音通信费
        bill_ext_data   string  10.00   套餐外上网费
        bill_ext_sms    string  10.00   套餐外短信费
        bill_zengzhifei string  10.00   增值业务费
        bill_daishoufei string  10.00   代收业务费
        bill_qita       string  10.00   其他费用
        #self.session.headers()
        """
        # 缺失月份
        missing_month_list = []
        crawl_num = 0
        month_fee =[]
        today = date.today()
        month_bill_url = "http://yn.189.cn/service/jt/bill/actionjt/ifr_bill_hislist_em.jsp"
        search_month = [x for x in range(-1, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d"%(query_date.year, query_date.month)
            month_bill_data = {
                "TEMPLATE_ID":'1000',
                "BILLING_CYCLE":query_month,
                "USER_ID":self.user_id,
                "NUM":kwargs['tel'],
                "AREA_CODE": '%04d' % int(self.AreaCode)
            }

            for item in xrange(self.max_retry):
                code, key, resp = self.post(month_bill_url, data = month_bill_data)
                if code != 0 or u"客户化账单查询失败，请尝试重新查询" in resp.text:
                    pass
                else:
                    break
            else:
                if code == 0:
                    self.log('crawler', '客户化账单查询失败', resp)
                missing_month_list.append(query_month)
                continue
            level, key, message, month_fee_data = self.phone_bill_get(resp, query_month)
            if level != 0:
                crawl_num += 1
                self.log('crawler', message, resp)
                missing_month_list.append(query_month)
                continue
            if month_fee_data['bill_amount'] == '0.00':
                missing_month_list.append(query_month)
                self.log('crawler', u'账单记录为空', resp)
                continue
            month_fee.append(month_fee_data)
        if len(missing_month_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', month_fee, missing_month_list
            return 9, 'website_busy_error', month_fee, missing_month_list
        return 0, "success", month_fee, missing_month_list

    def phone_bill_get(self, resp, query_month):
        month_fee_data = {}
        try:
            month_fee_data['bill_month'] = query_month
            page_text = resp.text.encode('utf-8')
            selector = etree.HTML(page_text)
            month_fee_data['bill_amount'] = selector.xpath('//font[@color="red"]/text()')[0]
            """
            # 备用
            # 获取存在所需求的信息的table, 在table中查找数据
            page_text_url_encode = etree.tostring(selector.xpath('//*[@id="custBody"]')[0])
            print page_text_url_encode
            # 由于tostring导致的汉字编码问题,使用HTMLParser().unescape()解压, 便于使用正则获取数据
            page_text = HTMLParser().unescape(page_text_url_encode).encode('utf-8')
            print page_text
            """
            package_fee = 0.00
            for i in map(float, re.findall(r'套餐月基本费.*?(\d*\.\d{2})', page_text)):
                package_fee += i
            month_fee_data['bill_package'] = str(package_fee)
            bill_ext_calls_fee = 0.00
            for i in map(float, re.findall(r'呼叫.*?(\d*\.\d{2})', page_text)):
                bill_ext_calls_fee += i
            month_fee_data['bill_ext_calls'] = str(bill_ext_calls_fee)
            bill_ext_sms_fee = 0.00
            for i in map(float, re.findall(r'短信费.*?(\d*\.\d{2})', page_text)):
                bill_ext_sms_fee += i
            month_fee_data['bill_ext_sms'] = str(bill_ext_sms_fee)
            bill_ext_data_fee = 0.00
            for i in map(float, re.findall(r'上网.*?(\d*\.\d{2})', page_text)):
                bill_ext_data_fee += i
            month_fee_data['bill_ext_data'] = str(bill_ext_data_fee)
            bill_zengzhifei_fee = 0.00
            for i in map(float, re.findall(r'增值.*?(\d*\.\d{2})', page_text)):
                bill_zengzhifei_fee += i
            month_fee_data['bill_zengzhifei'] = str(bill_zengzhifei_fee)
            bill_daishoufei_fee = 0.00
            for i in map(float, re.findall(r'代收.*?(\d*\.\d{2})', page_text)):
                bill_daishoufei_fee += i
            month_fee_data['bill_daishoufei'] = str(bill_daishoufei_fee)
            bill_qita_fee = 0.00
            for i in map(float, re.findall(r'其他费用.*?(\d*\.\d{2})', page_text)):
                bill_qita_fee += i
            month_fee_data['bill_qita'] = str(bill_qita_fee)
        except:
            error = traceback.format_exc()
            return 9, 'crawler', 'html_error : %s' % error, {}
        return 0, 'success', 'success', month_fee_data



if __name__ == '__main__':
    c = Crawler()
    USER_ID = "17387202951" 
    USER_PASSWORD = "135126"
    FULL_NAME = u"王梦思"
    ID_CARD = '411081199102158009'
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD, id_card=ID_CARD, full_name=FULL_NAME)
