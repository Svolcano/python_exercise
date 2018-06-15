# -*- coding: utf-8 -*-

import sys
import datetime
import time
import re
import calendar
from datetime import date
import traceback
import urllib
from lxml import etree
from dateutil.relativedelta import relativedelta
from HTMLParser import HTMLParser
from collections import OrderedDict
from functools import reduce

from scrapy.selector import Selector as sel
import random

reload(sys)
sys.setdefaultencoding("utf8")

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
        super(Crawler, self).__init__(**kwargs)
        self.pin_pwd_error_times = 0
        self.today_year = datetime.date.today().year
        self.today_month = datetime.date.today().month
        self.today_day = datetime.date.today().day

    def get_msg(self, res):
        msg = ""
        req_url = "request_url" + str(res.request.url)
        res_url = "response_url" + str(res.url)

        if res.request.method == "POST":
            msg = req_url + "\n" + res_url + "\n" + str(res.request.headers) + "\n" + str(
                res.request.body) + "\n" + str(res.headers) + "\n" + str(res.text)
        if res.request.method == "GET":
            msg = req_url + "\n" + res_url + "\n" + str(res.request.headers) + "\n" + str(res.headers) + "\n" + str(
                res.text)
        return msg

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        return
            list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        return ['full_name', 'id_card', 'pin_pwd']

    def get_verify_type(self, **kwargs):
        """
        告訴我二次驗證用什麼驗證
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        return 'SMS'

    def login(self, **kwargs):
        ProvinceID = '19'
        code, key = login_unity(self, ProvinceID, **kwargs)
        return code, key

    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式

            {'full_name': full_name,
            'id_card': id_card,
            'is_realname_register': is_realname_register,
            'open_date': open_date}
        """
        lis_msg = []
        msg_dict = {}
        msg_dict["open_date"] = ""
        msg_dict["id_card"] = ""
        msg_dict["address"] = ""
        msg_dict['full_name'] = ""
        user_info_url = "http://www.189.cn/dqmh/userCenter/userInfo.do?method=editUserInfo_new&fastcode=&cityCode=hn"

        code, key, resp = self.get(user_info_url)
        if code != 0:
            return code, key, {}
        lis_msg.append("crawl_info1")
        lis_msg.append(self.get_msg(resp))
        try:
            et = etree.HTML(resp.text.encode('utf-8'), parser=etree.HTMLParser(encoding='utf-8'))
            user_name = et.xpath('//*[@name="realName"]')[0]
            msg_dict['full_name'] = user_name.get("value")
            card_num = et.xpath('//input[@name="certificateNumber"]')[0].get("value")
            msg_dict["id_card"] = card_num
            xx_address = et.xpath('//textarea')[0]
            msg_dict["address"] = xx_address.text
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error : %s' % error, resp)
            return 9, 'html_error', {}
        return 0, "success", msg_dict

    def get_verify_picture(self):
        random_code = random.random()
        url = 'http://hn.189.cn/webportal-wt/common/Verification/patchca.do?code=randQuery&rand=' + str(random_code)
        code, key, resp = self.get(url)
        if code != 0:
            return code, key, ''
        return 0, 'success', resp.content

    def send_verify_request(self, **kwargs):
        """
            請求發送短信，或是下載圖片，或是同時發送請求
            return
                status_key: str, 狀態碼金鑰，參考status_code
                level: int, 錯誤等級
                message: unicode, 詳細的錯誤信息
                image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        first_url = "http://hn.189.cn/grouplogin?rUrl=http://hn.189.cn/webportal-wt/hnselfservice/billquery/bill-query!queryBill.action&fastcode=10000280&cityCode=hn"
        code, key, resp = self.get(first_url)
        if code != 0:
            return code, key, ''

        post_user_info_data = {
            "reUrl": "/webportal-wt/hnselfservice/billquery/bill-query!queryBill.action",
            "checkType": "2",
            "cardId": kwargs["id_card"],
            "userName": kwargs["full_name"]
        }
        post_user_info_url = "http://hn.189.cn/webportal-wt/hnselfservice/customerInfo/customer-info!checkCustInfo.do"
        code, key, resp = self.post(post_user_info_url, data=post_user_info_data)
        if code != 0:
            return code, key, ''
        if '校验失败，请重新输入您的实名信息提交校验' in resp.text:
            self.log("user", "实名制信息填写错误", resp)
            return 9, 'user_id_error', ''
        if '对不起您的号码未通过实名校验，请先完成实名核对' in resp.text or '根据国家对手机号码实名制要求' in resp.text or '/*实名制跳转*/' in resp.text:
            self.log('user', 'real_name_registration_error', resp)
            return 9, 'real_name_registration_error', ""
        code, key, captcha_str = self.get_verify_picture()
        if code != 0:
            return code, key, ''
        key = "website_busy_error"
        for retry in xrange(self.max_retry):
            # 查看data/yundama_type.py 获得
            codetype = '1004'
            error_message = ''
            key, result, cid = self._dama(captcha_str, codetype)
            if key == "success" and result != "":
                captcha_code = result
            else:
                self.log("website", "云打码异常{}".format(result), '')
                error_message = "YDM"
                continue
            get_sms_url = "http://hn.189.cn/webportal-wt/hnselfservice/billquery/bill-query!queryBilly.action"
            phone_num = {
                "number": kwargs["tel"],
                'randQuery': captcha_code
            }
            code, key, resp = self.post(get_sms_url, data=phone_num)
            if code != 0:
                return code, key, ''
            if resp.text == 'success':
                return 0, "success", ""
            else:
                if 'a padding to disable MSIE and Chrome friendly crawler page' in resp.text:
                    self.log('website', 'website_busy_error', resp)
                    return 9, 'website_busy_error', ''
                elif 'randFailed' in resp.text:
                    try:
                        self._dama_report(cid)
                    except:
                        self.log("website", "发送打码失败信息失败", "")
                        return 9, 'send_sms_error', ''
                    self.log("website", 'send_sms_error: 第{}次打码失败'.format(retry + 1), resp)
                    error_message = ""
                    continue
                else:
                    self.log('crawler', 'unknown_error', resp)
                    return 9, 'unknown_error', ''
        else:
            if error_message == "YDM":
                self.log("website", "云打码异常website_busy_error", resp)
                return 9, key, ""
            self.log('crawler', 'send_sms_error', resp)
            return 9, 'send_sms_error', ''

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
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

    def get_six_year_month(self):
        # "默认时间起点为当前时间 返回值[(年, 月), (年, 月)...]"
        time_list = []
        for n in range(6):
            if (self.today_month - n) > 0:
                mon = (self.today_month - n)
                yea = self.today_year
            else:
                mon = 12 + (self.today_month - n)
                yea = self.today_year - 1
            time_list.append((yea, mon))
        return time_list

    def make_get_call_log_url_list(self, call_type="", **kwargs):
        # "构造爬取详单的URL"
        get_call_log_url_list = []
        time_list = self.get_six_year_month()
        for n in time_list:
            yea = n[0]
            mon = n[1]
            time_now, time_apm, month_end = self.change_time_for_data()

            verify_params = OrderedDict([
                ("tabIndex", "2"),
                ("queryMonth", str(yea) + "-" + str(mon).rjust(2, "0")),
                ("patitype", "2"),
                ("startDay", "1"),
                ("endDay", month_end),
                ("code", kwargs['sms_code']),
                ("accNbr", "")
            ])

            tm_value = str(self.today_year + self.today_month + self.today_day - 1)
            tm = urllib.urlencode({"tm": tm_value + time_apm})
            verify_params = urllib.urlencode(verify_params)
            call_verify_url = "http://hn.189.cn/webportal-wt/hnselfservice/billquery/bill-query!queryBillx.action?" + tm + time_now + "&" + verify_params

            log_params = OrderedDict([
                ("tabIndex", "2"),
                ("queryMonth", str(yea) + "-" + str(mon).rjust(2, "0")),
                ("patitype", "2"),
                ("startDay", "1"),
                ("endDay", month_end),
                ("pageNo", "1"),
                ("valicode", "undefined"),
                ("accNbr", "")
            ])
            log_params = urllib.urlencode(log_params)
            call_log_url = "http://hn.189.cn/webportal-wt/hnselfservice/billquery/bill-query!queryBillx.action?" + tm + time_now + "&" + log_params
            if call_type == "verify":
                return call_verify_url
            else:
                get_call_log_url_list.append(call_log_url)
        return get_call_log_url_list

    def change_time_for_data(self):
        time_now = time.strftime("%X", time.localtime(time.time()))
        year_month = time.strftime("%Y-%m", time.localtime(time.time()))
        time_apm = int(time_now.split(":")[0])
        if time_apm <= 12:
            time_apm = u"上午" + str(time_apm)
        else:
            time_apm = u"下午" + str(time_apm - 12)
        time_now = time_now.split(":")[1:]
        time_now.insert(1, ":")
        time_now.insert(0, ":")
        time_now = reduce(lambda x, y: x + y, time_now)
        temp, month_end = calendar.monthrange(int(year_month.split("-")[0]), int(year_month.split("-")[1]))

        return time_now, time_apm, month_end

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        try:
            url = self.make_get_call_log_url_list(call_type="verify", **kwargs)
        except:
            error = traceback.format_exc()
            self.log('crawler', 'unknown_error : %s' % error, '')
            return 9, "unknown_error"
        code, key, resp = self.get(url)
        if code != 0:
            return code, key
        if '<label id="fail">验证码错误!</label>' in resp.text:
            self.log("crawler", "验证码错误", resp)
            return 2, "verify_error"
        return 0, "success"

    def random_sleep(self, tm, page=1, modulus=3):
        time.sleep(random.uniform(tm / page / modulus / 1.5, 1.5 * tm / page / modulus))

    def crawl_call_log(self, **kwargs):
        """
        | `call_tel` | string | 电话号码 |
        | `call_cost` | string | 爬取费用 |
        | `call_time` | string | 通话起始时间 |
        | `call_method` | string | 呼叫类型（主叫, 被叫） |
        | `call_type` | string | 通话类型（本地, 长途）  |
        | `call_from` | string | 本机通话地 |
        | `call_to` | string | 对方归属地 |
        | `call_duration` | string | 通话时长 |
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        missing_list = []
        possibly_missing_list = []
        part_missing_list = []
        log_list = []
        crawle_num = 0
        today = date.today()
        try:
            url_list = self.make_get_call_log_url_list(**kwargs)
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error : %s' % error, '')
            return 9, "crawler", log_list, missing_list, possibly_missing_list, part_missing_list
        for num, url in enumerate(url_list):
            query_date = today + relativedelta(months=num * -1)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            missing_flag = True
            start_time = time.time()
            end_time = start_time + 5
            aid_time_dict = dict()
            retry_times = self.max_retry
            log_for_retry = []
            while 1:
                log_for_retry.append((1, retry_times))
                retry_times -= 1
                code, key, resp = self.get(url)
                if code != 0:
                    missing_flag = True
                if '对不起您的号码未通过实名校验，请先完成实名核对' in resp.text or '根据国家对手机号码实名制要求' in resp.text or '/*实名制跳转*/' in resp.text:
                    self.log('user', 'real_name_registration_error', resp)
                    return 9, 'real_name_registration_error', log_list, missing_list, possibly_missing_list
                elif u"没有查询到相关数据" in resp.text:
                    missing_flag = False
                else:
                    flag = True
                    break
                # now_time = time.time()
                if retry_times >= 0:
                    aid_time_dict.update({retry_times: time.time()})
                # elif now_time < end_time:
                #     # loop_time = aid_time_dict.get(0, time.time())
                #     # left_time = end_time - loop_time
                #     # self.random_sleep(left_time)
                #     pass
                else:
                    flag = False
                    if missing_flag:
                        missing_list.append(query_month)
                    else:
                        possibly_missing_list.append(query_month)
                    break
            if not flag:
                self.log('crawler', '{}重试记录{}'.format(query_month, log_for_retry), '')
                continue
            # for retry in range(self.max_retry):
            #     code, key, resp = self.get(url)
            #     if code != 0:
            #         missing_flag = True
            #     elif u"没有查询到相关数据" in resp.text:
            #         missing_flag = False
            #     else:
            #         break
            # else:
            #     if missing_flag:
            #         missing_list.append(query_month)
            #     else:
            #         self.log('crawler', '未查询到您的详单信息', resp)
            #         possibly_missing_list.append(query_month)
            #     continue
            # if '对不起您的号码未通过实名校验，请先完成实名核对' in resp.text or '根据国家对手机号码实名制要求' in resp.text or '/*实名制跳转*/' in resp.text:
            #     self.log('user', 'real_name_registration_error', resp)
            #     return 9, 'real_name_registration_error', log_list, missing_list, possibly_missing_list
            html = resp.text
            miss = False
            sig_data = []
            try:
                month_data = self.get_month_call(html, query_month)
                if month_data:
                    sig_data.extend(month_data)
                else:
                    miss = True
                    self.log("crawler", 'no_data', resp)
                    possibly_missing_list.append(query_month)
                total_page = int(re.findall(ur'总页数：(.*?) 当前页', html)[0])
                if total_page > 1:
                    page_and_retry = [(page, self.max_retry) for page in range(2, total_page + 1)]
                    while page_and_retry:
                        page, retry_times = page_and_retry.pop(0)
                        log_for_retry.append((page, retry_times))
                        retry_times -= 1
                        url = url.split("pageNo=")[0] + "pageNo=" + str(page) + "&valicode=undefined&accNbr="

                        code, key, res1 = self.get(url)
                        if not code:
                            html = res1.text
                            month_log = self.get_month_call(html, query_month)
                            if len(month_log) != 0:
                                sig_data.extend(month_log)
                                continue
                        now_time = time.time()
                        if retry_times >= 0:
                            page_and_retry.append((page, retry_times))
                            aid_time_dict.update({retry_times: time.time()})
                        elif now_time < end_time:
                            page_and_retry.append((page, retry_times))
                        else:
                            part_missing_list.append(query_month)
                    log_list.extend(sig_data)
                else:
                    log_list.extend(sig_data)
            except:
                error = traceback.format_exc()
                self.log('crawler', 'request_error : %s' % error, resp)
                missing_list.append(query_month)
                crawle_num += 1
            self.log('crawler', '{}重试记录{}'.format(query_month, log_for_retry), '')

            #     while(True):
            #         next_page = re.findall(u'<a style="cursor: pointer;" onclick="qdPageQuery\(\'(.*?)\'\)">下一页</a>', html)
            #         if len(next_page) == 0:
            #             break
            #         next_page = int(next_page[0])
            #         url = url.split("pageNo=")[0] + "pageNo=" + str(next_page) + "&valicode=undefined&accNbr="
            #         code, key, res1 = self.get(url)
            #         if code != 0:
            #             self.log('crawler', 'request_error', res1)
            #             missing_list.append(query_month)
            #             continue
            #         html = res1.text
            #         month_log = self.get_month_call(res1.text, query_month)
            #         if len(month_log) == 0:
            #             self.log("crawler", 'no_data: 或许有缺页', res1)
            #             miss = True
            #             if query_date not in part_missing_list:
            #                 part_missing_list.append(query_month)
            #             continue
            #         sig_data.extend(month_log)
            #     log_list.extend(sig_data)
            # except:
            #     error = traceback.format_exc()
            #     self.log('crawler', 'request_error : %s' % error, resp)
            #     missing_list.append(query_month)
            #     crawle_num += 1
            #     continue
        self.log("crawler", "缺失: {}, 可能缺失: {}, 部分缺失{}".format(missing_list, possibly_missing_list, part_missing_list),
                 "")
        if len(missing_list + possibly_missing_list) == 6:
            if crawle_num > 0:
                return 9, 'crawl_error', log_list, missing_list, possibly_missing_list, part_missing_list
            return 9, 'website_busy_error', log_list, missing_list, possibly_missing_list, part_missing_list
        return 0, "success", log_list, missing_list, possibly_missing_list, part_missing_list

    def get_month_call(self, html, query_month):
        log_list = []
        tr_list = sel(text=html).xpath('//*[@id="tab_cont_box"]/div[2]/table/tr')
        for i in tr_list:
            # 不论第几页, 记录从第四行开始
            xuhao = "yyyy-mm-dd"
            if i.xpath('.//td[1]/text()').extract():
                xuhao = i.xpath('.//td[1]/text()').extract()[0].strip()
            if len(xuhao.strip()) == len("yyyy-mm-dd"):
                continue
            month_phone_log = {}
            month_phone_log['month'] = query_month
            month_phone_log['call_time'] = self.time_transform(i.xpath('.//td[2]/text()').extract()[0].strip())
            month_phone_log['call_method'] = u"被叫" if u"被叫" in i.xpath('.//td[3]/text()').extract()[
                0].strip() else u"主叫"
            month_phone_log['call_duration'] = self.time_format(i.xpath('.//td[5]/text()').extract()[0].strip())

            raw_call_from = i.xpath('.//td[6]/text()').extract()[0].strip()
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                month_phone_log['call_from'] = call_from
            else:
                # self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                month_phone_log['call_from'] = raw_call_from

            month_phone_log['call_cost'] = i.xpath('.//td[7]/text()').extract()[0].strip()
            month_phone_log['call_to'] = ''
            # month_phone_log['call_type'] = u"长途" if  u"漫游" in i.xpath('.//td[8]/text()').extract()[0].strip() else u"本地"
            if i.xpath('.//td[8]/text()'):
                month_phone_log['call_type'] = u"长途" if u"漫游" in i.xpath('.//td[8]/text()').extract()[
                    0].strip() else u"本地"
            else:
                month_phone_log['call_type'] = ''
            month_phone_log['call_tel'] = i.xpath('.//td[4]/text()').extract()[0].strip()
            log_list.append(month_phone_log)
        return log_list

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
        """
        missing_list = []
        crawle_num = 0
        today = date.today()
        # 请求这个网页进行安全验证,获取关键cookies
        seccend_url = "http://hn.189.cn/grouplogin?rUrl=http://hn.189.cn/webportal-wt/hnselfservice/billquery/bill-query!queryBanlance.action&fastcode=10000278&cityCode=hn"
        code, key, resp = self.get(seccend_url)
        if code != 0:
            return 9, "website_busy_error", [], missing_list
        url = "http://hn.189.cn/webportal-wt/hnselfservice/billquery/bill-query!queryUserBillDetail.action?"
        six_mon_fee_list = []
        time_list = self.get_six_year_month()
        for num, n in enumerate(time_list):
            query_date = today + relativedelta(months=num * -1)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            yea = n[0]
            mon = n[1]
            params = OrderedDict([
                ("chargeType", ""),
                ("queryMonth", str(yea) + "-" + str(mon).rjust(2, "0")),
                ("productId", kwargs['tel'])
            ])
            for retry in xrange(self.max_retry):
                code, key, resp = self.get(url, params=params)
                if u"系统出错了" in resp.text:
                    self.log('network', 'website_busy_error', resp)
                else:
                    break
            else:
                missing_list.append(query_month)
                continue
            html = resp.text.encode("utf-8")
            if "查不到相应月份的账户级账单" in html:
                missing_list.append(query_month)
                continue
            fee_dict = {}
            fee_dict["bill_month"] = str(yea) + str(mon).rjust(2, "0")
            try:
                fee_dict['bill_amount'] = re.findall(r"本期费用合计.*?(\d*\.\d*)", html, re.S)[0]
            except:
                error = traceback.format_exc()
                self.log('crawler', 'html_error : %s' % error, resp)
                missing_list.append(query_month)
                crawle_num += 1
                continue
            try:
                et = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
                fee_list = et.xpath("//*[@id='Table4']/tr")
            except:
                error = traceback.format_exc()
                self.log('crawler', 'html_error : %s' % error, resp)
                missing_list.append(query_month)
                crawle_num += 1
                continue
            if len(fee_list) == 0:
                missing_list.append(query_month)
                continue
            else:
                lm_text = etree.tostring(fee_list[2])
            try:
                bm_text = HTMLParser().unescape(lm_text).encode('utf-8')
                fee_dict['bill_package'] = self.add_all(re.findall(r'月基本费.*?(\d*\.\d{1,2})', bm_text, re.S))
                fee_dict['bill_ext_calls'] = self.add_all(re.findall(r'语音.*?(\d*\.\d{1,2})', bm_text, re.S))
                fee_dict['bill_ext_data'] = self.add_all(re.findall(r'上网.*?(\d*\.\d{1,2})', bm_text, re.S))
                fee_dict['bill_ext_sms'] = self.add_all(re.findall(r'短信.*?(\d*\.\d{1,2})', bm_text, re.S))
                fee_dict['bill_zengzhifei'] = self.add_all(re.findall(r'增值.*?(\d*\.\d{1,2})', bm_text, re.S))
                fee_dict['bill_daishoufei'] = self.add_all(re.findall(r'代收.*?(\d*\.\d{1,2})', bm_text, re.S))
                fee_dict['bill_qita'] = self.add_all(re.findall(r'其他.*?(\d*\.\d{1,2})', bm_text, re.S))
            except:
                error = traceback.format_exc()
                self.log('crawler', 'html_error : %s' % error, resp)
                missing_list.append(query_month)
                crawle_num += 1
                continue
            six_mon_fee_list.append(fee_dict)
        if crawle_num > 0:
            return 9, 'crawl_error', six_mon_fee_list, missing_list
        if len(missing_list) == 6:
            return 9, 'website_busy_error', six_mon_fee_list, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, "success", six_mon_fee_list, missing_list

    def add_all(self, num_list):
        if len(num_list) == 0:
            return ""
        else:
            return str(reduce(lambda x, y: x + y, map(float, num_list)))


if __name__ == '__main__':
    crawle = Crawler()
    id_card = "430602198704155628"
    full_name = u"刘放"
    crawle.self_test(tel='18907307267', pin_pwd='762703', id_card=id_card, full_name=full_name)