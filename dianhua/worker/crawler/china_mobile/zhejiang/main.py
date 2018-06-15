# -*- coding: utf-8 -*-

from lxml import etree

from scrapy.selector import Selector
import re
import time
import datetime
import traceback
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
from datetime import date
import sys
from js_encryption import get_enString
import random
reload(sys)
sys.setdefaultencoding("utf8")
if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from crawler.base_crawler import BaseCrawler
else:
    from worker.crawler.base_crawler import BaseCrawler


class Crawler(BaseCrawler):
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
        self.pos_miss_list = []
        self.part_miss_list = []
        self.miss_list = []

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def need_parameters(self, **kwargs):
        return ['pin_pwd']

    # 获取登录参数
    def get_login_data(self, html, en_tel, en_pwd, **kwargs):
        htmltree = etree.HTML(html.decode('utf-8'))
        loginType = htmltree.xpath('//*[@id="loginType"]/@value')[0]
        backurl = htmltree.xpath('//*[@name="backurl"]/@value')[0]
        warnurl = htmltree.xpath('//*[@id="warnurl"]/@value')[0]
        errorurl = htmltree.xpath('//*[@id="errorurl"]/@value')[0]
        spid = htmltree.xpath('//*[@id="spid"]/@value')[0]
        RelayState = htmltree.xpath('//*[@id="RelayState"]/@value')[0]
        mobileNum = en_tel
        # validCode = kwargs['captcha_code']
        servicePassword = en_pwd

        login_data = {
            'type': loginType,
            'backurl': backurl,
            'warnurl': warnurl,
            'errorurl': errorurl,
            'spid': spid,
            'RelayState': RelayState,
            'mobileNum': mobileNum,
            'loginmodel': '',
            'validCode': "",
            'smsValidCode': '',
            'servicePassword': servicePassword,
        }
        return login_data

    def get_back_data(self, html):
        htmltree = etree.HTML(html.decode('utf-8'))
        SAMLart = htmltree.xpath('//*[@name="SAMLart"]/@value')[0]
        isEncodePassword = htmltree.xpath('//*[@name="isEncodePassword"]/@value')[0]
        displayPic = htmltree.xpath('//*[@name="displayPic"]/@value')[0]
        RelayState = htmltree.xpath('//*[@name="RelayState"]/@value')[0]
        isEncodeMobile = htmltree.xpath('//*[@name="isEncodeMobile"]/@value')[0]
        displayPics = htmltree.xpath('//*[@name="displayPics"]/@value')[0]

        back_data = {
            'SAMLart': SAMLart,
            'isEncodePassword': isEncodePassword,
            'displayPic': displayPic,
            'RelayState': RelayState,
            'isEncodeMobile': isEncodeMobile,
            'displayPics': displayPics,
        }
        return back_data

    def login(self, **kwargs):
        """
        Login process
            1. Check Validate Code
            2. Check ID/PW
            3. Request Login
            4. Request Set Uid Cookie
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        top_url = 'https://zj.ac.10086.cn/login'
        code, key, resp = self.get(top_url)
        if code != 0:
            return code, key

        next_url = re.findall(r"location.replace\('(.*)'\)", resp.text)
        login_type = False
        if next_url:
            login_type = True
            headers = {"Referer": "https://zj.ac.10086.cn/login"}
            code, key, resp = self.get(next_url[0], headers=headers)
            if code != 0:
                return code, key
        try:
            en_tel = get_enString(kwargs['tel'])
            en_pwd = get_enString(kwargs['pin_pwd'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密失败 {}".format(error), resp)
            return 9, "website_busy_error"
        try:
            self.data = self.get_login_data(resp.text, en_tel, en_pwd, **kwargs)
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error{}".format(error), resp)
            return 9, "html_error"

        # 数字字母
        codetype = 2004
        for i in range(self.max_retry+3):
            captcha_url = "https://zj.ac.10086.cn/common/image.jsp"
            headers = {'Referer': 'https://zj.ac.10086.cn/login'}
            code, key, resp = self.get(captcha_url, headers=headers)
            if code != 0:
                return code, key
            try:
                key, result, cid = self._dama(resp.content, codetype)
            except:
                msg = traceback.format_exc()
                self.log('crawler', u'打码失败:{}'.format(msg), '')
                continue
            if key == "success" and result != "":
                captcha_code = str(result).lower()
            else:
                continue
            url = "https://zj.ac.10086.cn/validImageCode"
            params = {
                str(random.random()): "",
                "imageCode": captcha_code,
            }
            code, key, resp = self.get(url, params=params)
            if code != 0:
                return code, key
            if "1" not in str(resp.text):
                self.log("crawler", "图片打码失败", resp)
                self._dama_report(cid)
                continue
            url = "https://zj.ac.10086.cn/Login"
            self.data["validCode"] = captcha_code
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "https://zj.ac.10086.cn/login"
            }
            code, key, resp = self.post(url, data=self.data, headers=headers)
            if code != 0:
                if isinstance(resp, str):
                    pass
                elif resp.status_code == 302:
                    return 2, 'login_param_error'
                return code, key

            if 'SAMLart' in resp.text:
                # back_data = self.get_back_data(resp.text)
                break
            elif u'用户名或密码错误' in resp.text:
                self.log("user", 'invalid_tel', resp)
                return 1, 'invalid_tel'
            elif u'密码有误' in resp.text:
                self.log("user", 'pin_pwd_error', resp)
                return 1, 'pin_pwd_error'
            elif u'验证码错误' in resp.text or u'验证码已失效' in resp.text:
                self.log("user", 'verify_error', resp)
                # return 2, 'verify_error'
                self._dama_report(cid)
                continue
            elif u'账户已被锁定' in resp.text:
                self.log("user", 'over_query_limit', resp)
                return 2, 'over_query_limit'
            else:
                #  u'登陆第一次跳转错误{}'.format(resp.text)
                self.log("crawler", 'login_param_error', resp)
                return 2, 'login_param_error'
        else:
            self.log('crawler', u'两次打码都失败', '')
            return 9, 'auto_captcha_code_error'

        if login_type:
            try:
                next_url = re.findall(r"location.replace\(\'(.*?)\'\)", resp.text)[0]
            except:
                error = traceback.format_exc()
                self.log("crawler", "html_error{}".format(error), resp)
                return 9, "html_error"

            code, key, resp = self.get(next_url)
            if code != 0:
                return code, key
            # headers = {
            #     "Referer": "https://zj.ac.10086.cn/Login",
            # }
        else:
            try:
                et = etree.HTML(resp.text)
                next_url = et.xpath("//form/@action")[0]

                data = {}
                form = et.xpath("//form")[0]
                name = form.xpath("input/@name")
                value = form.xpath("input/@value")

                for i in zip(name, value):
                    data[i[0]] = i[1]
            except:
                error = traceback.format_exc()
                self.log("crawler", "获取跳转信息失败{}".format(error), resp)
                return 9, "html_error"
            headers = {"Referer": "https://zj.ac.10086.cn/Login"}
            code, key, resp = self.post(next_url, headers=headers, data=data)
            if code != 0:
                return code, key
        try:
            if resp.text.strip() == '':
                self.log('website', 'website_busy_error', resp)
                return 9, 'website_busy_error'
            SAMLart = re.findall(r"Login.callAssert\('(.*?)'\)", resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "html_error{}".format(error), resp)
            return 9, "html_error"
        ass_data = {
            'SAMLart': SAMLart,
            'RelayState': 'type=B;backurl=http://www.zj.10086.cn/my/servlet/assertion;nl=6;loginFromUrl=http://www.zj.10086.cn/my/index.do;callbackurl=/servlet/assertion;islogin=true'
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        url = 'http://www.zj.10086.cn/my/servlet/assertion'
        code, key, resp = self.post(url, headers=headers, data=ass_data)
        if code != 0:
            return code, key
        return 0, 'success'

    def send_verify_request(self, **kwargs):
        """
        Send SMS verify code
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        for retry in xrange(self.max_retry):
            send_verify_request_url = "http://service.zj.10086.cn/yw/detail/secondPassCheck.do"
            send_verify_request_data = {
                'validateCode': '',
                'bid': 'BC5CC0A69BC10482E044001635842132',
            }
            headers = {'Referer': 'http://service.zj.10086.cn/yw/detail/queryHisDetailBill.do?menuId=13009'}
            code, key, resp = self.post(send_verify_request_url, data=send_verify_request_data, headers=headers)
            if code != 0:
                return code, key, ""
            if resp.text == '1':
                #  u'短信验证码30分钟内有效，请继续使用'
                self.log("crawler", 'reusable_sms', resp)
                return 0, 'success', ''
            elif 'SAMLRequest' in resp.text:
                if retry == self.max_retry - 1:
                    self.log("crawler", "尝试发送短信失败", resp)
                    return 9, 'website_busy_error', ''
                try:
                    htmltree = etree.HTML(resp.text)
                    SAMLRequest = htmltree.xpath('//*[@name="SAMLRequest"]/@value')[0]
                    RelayState = htmltree.xpath('//*[@name="RelayState"]/@value')[0]
                    data = {
                        'SAMLRequest': SAMLRequest,
                        'RelayState': RelayState,
                    }
                except:
                    error = traceback.format_exc()
                    self.log("crawler", 'html_error: ' + error, resp)
                    return 9, "html_error", ""

                url = 'https://zj.ac.10086.cn/POST'
                code, key, resp = self.post(url, data=data)
                if code != 0:
                    return code, key, ""
                try:
                    data = self.get_back_data(resp.text)
                except:
                    error = traceback.format_exc()
                    if u'系统忙，请您稍后重试' in resp.text:
                        self.log('website', 'website_busy_error', resp)
                        # return 9, 'website_busy_error', ''
                        continue
                    self.log("crawler", 'html_error: ' + error, resp)
                    return 9, "html_error", ""

                url = 'http://service.zj.10086.cn/servlet/assertion'
                code, key, resp = self.post(url, data=data)
                if code != 0:
                    return code, key, ""
            else:
                self.log("crawler", "website_busy_error", resp)
                return 9, 'website_busy_error', ''

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        verify_url = "http://service.zj.10086.cn/yw/detail/secondPassCheck.do"
        verify_data = {
            'validateCode': kwargs['sms_code'],
            'bid': 'BC5CC0A69BC10482E044001635842132',
        }
        code, key, resp = self.post(verify_url, data=verify_data)
        if code != 0:
            return code, key
        if resp.text == u'12' or resp.text == '':
            return 0, 'success'
        else:
            self.log("crawler", "验证码错误", resp)
            return 2, 'verify_error'

    def crawl_info(self, **kwargs):
        """
        Crawl user's personal info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        # Get Personal Info
        info_url = "http://www.zj.10086.cn/my/userinfo/queryUserYdInfo.do"
        info_data = {
            'secPwd': kwargs['sms_code'],
            'fromFlag': '',
        }
        headers = {
            'Referer': 'http://www.zj.10086.cn/my/userinfo/userYdinfoFirst.jsp',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4,ja;q=0.2,zh-CN;q=0.2'
        }
        code, key, resp = self.post(info_url, data=info_data, headers=headers)
        if code != 0:
            return code, key, {}
        if re.search(u'验证码验证失败', resp.text):
            self.log("user", 'verify_error', resp)
            return 9, 'verify_error', {}
        else:
            is_ok, data = self.get_info(resp.text)
            if is_ok:
                return 0, 'success', data
            else:
                self.log("crawler", "html_error: "+data, resp)
                return 9, 'html_error', {}

    def get_info(self, response_text):
        try:
            full_name = Selector(text=response_text).xpath('//table[@class="persoydtable"]//tr[1]/td[1]/text()').extract()
            id_card = ''
            is_realname_register = Selector(text=response_text).xpath(
                '//table[@class="persoydtable"]//tr[3]/td[2]/text()').extract()
            open_date = Selector(text=response_text).xpath('//table[@class="persoydtable"]//tr[3]/td[1]/text()').extract()
            address = ""
            open_date = ''.join(open_date).strip()
            if open_date:
                open_date = self.time_transform(''.join(open_date).strip(), str_format="%Y-%m-%d")

            return True, {
                    'full_name': ''.join(full_name).strip(),
                    'id_card': id_card,
                    'is_realname_register': u'已实名' in ''.join(is_realname_register),
                    'open_date': open_date,
                    'address': address,
                    }
        except:
            error = traceback.format_exc()
            return False, error

    def crawl_call_log(self, **kwargs):
        """
        Crawl user's detail bill info
            1. Get Current Month Detail Info
            2. Get Past Month Detail Info
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        self.pos_miss_list = []
        self.miss_list = []
        self.part_miss_list = []
        crawl_error_num = 0
        all_data = []
        today = datetime.date.today()
        previous_datetime_retrys = [(x, self.max_retry) for x in list(rrule(MONTHLY,count=6,bymonthday=1,dtstart=today + relativedelta(months=-6)))]
        while previous_datetime_retrys:
            previous_datetime, retrys = previous_datetime_retrys.pop(0)
            code, key, message, data, response = self.request_single_month_first_page(previous_datetime)
            all_data.extend(data)
            if key != 'success':
                crawl_error_num += 1

        part_set = set(self.part_miss_list)
        miss_set = set(self.miss_list)
        pos_set = set(self.pos_miss_list)

        self.pos_miss_list = list(pos_set - part_set)
        self.miss_list = list(miss_set - part_set)

        self.pos_miss_list.sort(reverse=True)
        self.miss_list.sort(reverse=True)
        self.part_miss_list.sort(reverse=True)

        if len(self.miss_list + self.pos_miss_list) == 6 or not all_data:
            if crawl_error_num > 0:
                return 9, 'crawl_error', all_data, self.miss_list, self.pos_miss_list, self.part_miss_list
            return 9, 'website_busy_error', all_data, self.miss_list, self.pos_miss_list, self.part_miss_list
        self.log("crawler", "缺失月份: {}, 可能缺失月份: {}, 部分缺失月份: {}".format(
                     self.miss_list, self.pos_miss_list, self.part_miss_list), "")
        return 0, 'success', all_data, self.miss_list, self.pos_miss_list, self.part_miss_list

    def request_single_month_first_page(self, previous_datetime):
        call_params = {
            'bid': '',
            'menuId': '13009',
            'listtype': '1',
            'month': '{0}-{1}'.format(str(previous_datetime.month).zfill(2), previous_datetime.year),
        }
        call_url = "http://service.zj.10086.cn/yw/detail/queryHisDetailBill.do"
        headers = {'Referer': 'http://service.zj.10086.cn/yw/detail/queryHisDetailBill.do?menuId=13009'}
        single_month_data = []
        log_for_retrys = []
        log_for_part_retrys = []
        local_st_time = time.time()
        local_full_time = 4.0
        local_time_fee = 0
        rand_time = random.randint(20, 40) / 10.0
        local_retrys = self.max_retry
        total_pages = None
        while True:
        # for item in range(self.max_retry):
            local_retrys -= 1
            log_for_retrys.append((local_retrys, local_time_fee))
            code, key, resp = self.get(call_url, params=call_params, headers=headers)
            if code != 0:
                if local_retrys >= 0:
                    local_time_fee = time.time() - local_st_time
                elif local_time_fee < local_full_time:
                    time.sleep(rand_time)
                    local_time_fee = time.time() - local_st_time
                else:
                    self.log("crawler", "多次尝试仍失败", "")
                    # code, key, message, data, response
                    break
                continue
            if u'开户日期' in resp.text or u'输入的月份超出可查询范围' in resp.text:
                # key, level, msg = 'success', 0, 'open_date'
                self.log('user', 'websiter_prohibited_error', resp)
                break
            elif u'用户详单信息查询失败：详单查询接口:该月详单尚未开放查询' in resp.text:
                code, key, msg = 9, 'website_maintaining_error', '该月详单尚未开放查询'
                self.log("crawler", "website_maintaining_error 该月详单尚未开放查询", resp)
                break
            elif u'用户详单信息查询失败' in resp.text:
                code, key, msg = 9, 'crawl_error', 'response_text:{}'.format(resp.text)
                if local_retrys >= 0:
                    local_time_fee = time.time() - local_st_time
                elif local_time_fee < local_full_time:
                    time.sleep(rand_time)
                    local_time_fee = time.time() - local_st_time
                else:
                    self.log("crawler", "用户详单信息查询 多次尝试仍失败", "")
                    break
                continue
            elif u'服务总线系统错误[调用业务服务超时]，请联系系统维护人员!' in resp.text \
                    or 'Cannot get a connection, pool error Timeout waiting for idle object' in resp.text :
                code, key, msg = 9, 'website_busy_error', u'服务总线系统错误[调用业务服务超时]，请联系系统维护人员!'
                if local_retrys >= 0:
                    local_time_fee = time.time() - local_st_time
                elif local_time_fee < local_full_time:
                    time.sleep(rand_time)
                    local_time_fee = time.time() - local_st_time
                else:
                    self.log("crawler", "运营商官网错误 多次尝试仍失败", "")
                    break
                continue
            else:
                #  账单为空时，没有页数
                pages = re.search(u'总共(\d+)页', resp.text)
                if pages == None:
                    # self.log('ERROR', 'crawl_error', r.text, r)
                    code, key, msg = 0, 'success', 'no_data'
                    if local_retrys >= 0:
                        local_time_fee = time.time() - local_st_time
                    elif local_time_fee < local_full_time:
                        time.sleep(rand_time)
                        local_time_fee = time.time() - local_st_time
                    else:
                        self.log("crawler", "未查到页码信息", "")
                        self.pos_miss_list.append("%d%02d" % (previous_datetime.year, previous_datetime.month))
                        break
                    continue

                total_pages = int(pages.group(1))
                year_month = "%d%02d" % (previous_datetime.year, previous_datetime.month)
                code, key, data = self.get_call(resp.text, year_month)
                if code != 0:
                    msg = data
                    if local_retrys >= 0:
                        local_time_fee = time.time() - local_st_time
                    elif local_time_fee < local_full_time:
                        time.sleep(rand_time)
                        local_time_fee = time.time() - local_st_time
                    else:
                        self.log("crawler", "解析获取到的数据多次报错", "")
                        self.miss_list.append("%d%02d" % (previous_datetime.year, previous_datetime.month))
                        break
                    continue
                # 如果两次为空，直接返回
                if not data:
                    code, key, msg = 0, 'success', 'no_data'
                    if local_retrys >= 0:
                        local_time_fee = time.time() - local_st_time
                    elif local_time_fee < local_full_time:
                        time.sleep(rand_time)
                        local_time_fee = time.time() - local_st_time
                    else:
                        self.log("crawler", "多次为空值", "")
                        self.pos_miss_list.append("%d%02d" % (previous_datetime.year, previous_datetime.month))
                        break
                    continue
                single_month_data.extend(data)
                break

        if total_pages:
            part_time_fee = 0
            part_time_full = 6.0
            part_rand_time = random.randint(20, 30) / 10.0
            part_st_time = time.time()

            pages = [(x, self.max_retry) for x in range(2, total_pages+1)]

            # while total_pages > 1:
            while pages:
                total_pages, part_retrys = pages.pop(0)
                part_retrys -= 1
                code, key, message, data, resp = self.request_single_month_other_page(previous_datetime, total_pages)
                log_for_part_retrys.append((total_pages, part_retrys, part_time_fee))
                if code != 0:
                    if part_retrys >= 0:
                        part_time_fee = time.time() - part_st_time
                        pages.append((total_pages, part_retrys))
                    elif part_time_fee < part_time_full:
                        time.sleep(part_rand_time)
                        part_time_fee = time.time() - part_st_time
                        pages.append((total_pages, part_retrys))
                    else:
                        self.log("crawler", "多次为空值", "")
                        self.part_miss_list.append("%d%02d" % (previous_datetime.year, previous_datetime.month))
                        if message != "network_request_error":
                            self.log("crawler", "{}{}".format(key, message), resp)
                        break
                    continue
                    # return code, key, message, single_month_data, resp
                single_month_data.extend(data)
        if not single_month_data:
            self.log("crawler", '数据为空', resp)

                # return 0, 'success', '', single_month_data, resp
        self.log("crawler", "首页重试记录: {}".format(log_for_retrys), "")
        self.log("crawler", "缺页重试记录: {}".format(log_for_part_retrys), "")
        return 0, 'success', '', single_month_data, resp

    def request_single_month_other_page(self, previous_datetime, page):
        call_params = {
            'bid': '',
            'firstPageFlag': 'N',
            'listtype': '1',
            'pageindex': page,
            'month': '{0}-{1}'.format(str(previous_datetime.month).zfill(2), previous_datetime.year),
        }
        call_url = "http://service.zj.10086.cn/yw/detail/queryNowDetailBill.do"
        headers = {'Referer': 'http://service.zj.10086.cn/yw/detail/queryHisDetailBill.do?bid=&menuId=13009'}

        for item in range(self.max_retry):
            code, key, resp = self.get(call_url, params=call_params, headers=headers)
            if code != 0:
                message = "network_request_error"
                continue
            if u'用户详单信息查询失败' in resp.text:
                code, key, message = 9, 'crawl_error', ' response_text:{}'.format(resp.text)
                continue
            else:
                year_month = "%d%02d" % (previous_datetime.year, previous_datetime.month)
                code, key,  result = self.get_call(resp.text, year_month)
                if code != 0:
                    continue
                else:
                    call_data = result
                # 如果两次为空，直接返回
                if not call_data:
                    code, key, message = 0, 'success', ''
                    continue
                # self.record_list.extend(call_data)
                return 0, 'success', '', call_data, resp
        else:
            return code, key, "", [], resp

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        if str_format == "%Y-%m-%d":
            time_str += " 12:00:00"

        str_format = "%Y-%m-%d %H:%M:%S"
        time_type = time.strptime(time_str.encode(bm), str_format)
        return str(int(time.mktime(time_type)))

    def time_format(self, time_str, **kwargs):
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
            real_time = h * 60 * 60 + m * 60 + s
        if (exec_type == 2):
            xx = re.findall(r'\d*', time_str)
            h, m, s = map(int, xx[::2])
            real_time = h * 60 * 60 + m * 60 + s
        return str(real_time)

    def get_call(self, response_text, year_month):
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
        try:
            call_log = list()
            html_etree = etree.HTML(response_text.decode('utf-8'))
            # 找到listtitle 父节点 并遍历所有tr。
            html_tr = html_etree.xpath("//*[@class='listtitle']/../tr[@class='content2']")
            for item in html_tr:
                record = {}
                call_time = item.xpath('./td/text()')[1]
                record['call_time'] = self.time_transform(call_time.strip())
                record['call_duration'] = self.time_format(item.xpath('./td/text()')[2])
                record['call_type'] = item.xpath('./td/text()')[3].strip()
                record['call_method'] = item.xpath('./td/text()')[4].strip()
                record['call_tel'] = item.xpath('./td/text()')[5].strip()
                raw_call_from = item.xpath('./td/text()')[7].strip()
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    record['call_from'] = call_from
                else:
                    record['call_from'] = raw_call_from
                record['call_cost'] = item.xpath('./td/text()')[12].strip()
                record['month'] = year_month
                record['call_to'] = ''
                call_log.append(record)
            return 0, "success", call_log
        except:
            error = traceback.format_exc()
            return 9, 'xml_error', '解析详单失败{}, {}'.format(error, response_text)

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
        http://service.zj.10086.cn/yw/bill/billDetail.do?menuId=13003&bid=&month=01-2017
        """
        month_fee = []
        miss_list = []
        crawl_error_num = 0
        today = date.today()
        month_bill_url = "http://service.zj.10086.cn/yw/bill/billDetail.do"
        search_month = [x for x in range(-1, -6, -1)]
        for each_month in search_month:
            month_fee_data = {}
            query_date = today + relativedelta(months=each_month)
            query_month = "%02d-%d" % (query_date.month, query_date.year)
            bill_month = "%d%02d" % (query_date.year, query_date.month)
            month_bill_data = {
                "menuId": '13003',
                "bid": '',
                "month": query_month
            }
            for i in range(self.max_retry):
                code, key, resp = self.get(month_bill_url, params=month_bill_data)
                if code != 0:
                    message = "network_request_error"
                    continue
                try:
                    key = "crawl_phone_bill"
                    month_fee_data = {}
                    month_fee_data['bill_month'] = bill_month
                    bill_package = re.findall(r'套餐及固定费[\s\S]*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_package:
                        bill_package = ["0.00"]
                    bill_ext_calls = re.findall(r'语音通信费[\s\S]*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_ext_calls:
                        bill_ext_calls = ["0.00"]
                    bill_ext_data = re.findall(r'上网费[\s\S]*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_ext_data:
                        bill_ext_data = ["0.00"]
                    bill_ext_sms = re.findall(r'短彩信费[\s\S]*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_ext_sms:
                        bill_ext_sms = ["0.00"]
                    bill_zengzhifei = re.findall(r'增值业务费[\s\S]*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_zengzhifei:
                        bill_zengzhifei = ["0.00"]
                    bill_daishoufei = re.findall(r'代收费[\s\S]*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_daishoufei:
                        bill_daishoufei = ["0.00"]
                    bill_youhuifei = re.findall(r'优惠费[\s\S]*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_youhuifei:
                        bill_youhuifei = ["0.00"]
                    bill_amount = re.findall(r'合计[\s\S]*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_amount:
                        # bill_amount = ["0.00"]
                        message = "success"
                        continue
                    # bill_amount = str(float(bill_amount_tmp[0]) + float(bill_youhuifei[0]))
                    month_fee_data['bill_amount'] = bill_amount[0]
                    month_fee_data['bill_package'] = bill_package[0]
                    month_fee_data['bill_ext_calls'] = bill_ext_calls[0]
                    month_fee_data['bill_ext_data'] = bill_ext_data[0]
                    month_fee_data['bill_ext_sms'] = bill_ext_sms[0]
                    month_fee_data['bill_zengzhifei'] = bill_zengzhifei[0]
                    month_fee_data['bill_daishoufei'] = bill_daishoufei[0]
                    # month_fee_data['bill_qita'] = "{:.2f}".format(abs(float(month_fee_data['bill_amount'])-float(month_fee_data['bill_package'])-float(month_fee_data['bill_ext_calls'])-float(month_fee_data['bill_ext_data'])-float(month_fee_data['bill_ext_sms'])-float(month_fee_data['bill_daishoufei'])-float(month_fee_data['bill_zengzhifei'])))
                    month_fee_data['bill_qita'] = "0.00"
                    month_fee.append(month_fee_data)
                    break
                except:
                    error = traceback.format_exc()
                    key = "html_error"
                    message = error
                    continue
            else:
                if message != "network_request_error":
                    self.log("crawler", "{}{}".format(key, message), resp)
                    crawl_error_num += 1
                miss_list.append(bill_month)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5:
            if crawl_error_num > 0:
                return 9, 'crawl_error', month_fee, miss_list
            return 9, 'website_busy_error', month_fee, miss_list
        return 0, "success", month_fee, miss_list


if __name__ == '__main__':
    # from worker.crawler.main import *
    c = Crawler()
    USER_ID = "13575702249"
    USER_PASSWORD = "135126"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    """
    # unit test
    pprint(c.send_login_verify_request())

    validate_code = ""
    pprint(c.login(tel=USER_ID, pin_pwd=USER_PASSWORD, captcha_code=validate_code))

    pprint(c.send_verify_request(tel=USER_ID))

    validate_code = ""
    pprint(c.verify(tel=USER_ID, sms_code=validate_code))

    pprint(c.crawl_info())
    pprint(c.crawl_call_log())
    """
