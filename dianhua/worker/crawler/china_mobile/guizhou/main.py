#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import re
import sys
import time
import traceback
import datetime
import execjs

from dateutil.relativedelta import relativedelta
from lxml import etree
from requests.utils import add_dict_to_cookiejar

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
        self.full_name = ""

    def need_parameters(self, **kwargs):
        return ['pin_pwd']

    def get_login_verify_type(self, **kwargs):
        return ''

    def send_login_verify_request(self, **kwargs):
        # get cookies
        url = "http://www.gz.10086.cn/service/fee/xdcx.jsp"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ''

        url = "https://gz.ac.10086.cn/aicas/loginStatus"
        params = {
            "jsoncallback":	"jQuery111506838816402159038_1526368377199",
            "service": "http://www.gz.10086.cn/service/cascallback/login",
            "forceLogoutUrl": "ics_24_40001",
            "_": "1526368377200"
        }
        headers = {
            "Accept": "*/*",
            "Referer": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key, ''

        # add_dict_to_cookiejar(self.session.cookies,
        #                       {
        #                           "add_dict_to_cookiejar": "851|851",
        #                           "CmProvid": "gz"
        #                       }
        #                       )

        for i in range(self.max_retry+8):
            headers = {
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Referer": "https://gz.ac.10086.cn/aicas/?ai_param_loginIndex=9&service=http%3A%2F%2Fwww.gz.10086.cn%2Fservice%2Fcascallback%2Flogin&ai_param_loginTypes=2,1,3&forceLogoutUrl=ics_24_40001&username=",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
            }
            url = "https://gz.ac.10086.cn/aicas/createVerifyImageServlet?datetime=0.{}".format(random.randint(10000000, 99999999))
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key, ''

            # 云打码
            codetype = 3004
            key, result, cid = self._dama(resp.content, codetype)

            if key == "success" and result != "":
                captcha_code = str(result)
            else:
                self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                return 9, key, ""
            # with open("pic_{}_{}_{}.png".format(i, result, cid), 'wb') as f:
            #     f.write(resp.content)
            # 验证图片
            url = "https://gz.ac.10086.cn/aicas/verifyCodeServlet?verifyCode={}".format(captcha_code)
            headers = {
                "CONTENT-TYPE": "application/x-www-form-urlencoded;charset=UTF-8",
                "Accept": "*/*",
                "Referer": "https://gz.ac.10086.cn/aicas/?ai_param_loginIndex=9&service=http%3A%2F%2Fwww.gz.10086.cn%2Fservice%2Fcascallback%2Flogin&ai_param_loginTypes=2,1,3&forceLogoutUrl=ics_24_40001&username=",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            code, key, resp = self.post(url, headers=headers)
            if code != 0:
                return code, key, ''
            if '0000' in str(resp.text):
                self.img_code = captcha_code
                return 0, "success", ""
            else:
                code = 9
                key = "auto_captcha_code_error"
                time.sleep(1)
                self._dama_report(cid)
                continue
        else:
            return code, key, ""

    def enstr(self, pwd, key="8kd14a-3"):
        source = """function toPaddingHex(b) {
            var a = b.toString(16);
            var c = a.indexOf(".");
            if (-1 != c) {
                a = a.substr(0, c)
            }
            if (0 != (a.length % 2)) {
                a = "0" + a
            }
            return a.toUpperCase()
        }

        function userPassCipher(a, e) {
            var k = "";
            if (0 != (a.length % 2)) {
                return k
            }
            var b = ((Math.random() * 1000000) % 256);
            k = toPaddingHex(b);
            var d = 0;
            var h = e.length;
            for (var f = 0; f < a.length; ++f) {
                var c = ((a.charCodeAt(f) + b) % 255);
                var g = e.charCodeAt(d);
                var j = c ^ g;
                k += toPaddingHex(j);
                b = j;
                if (d >= h) {
                    d = 0
                } else {
                    ++d
                }
            }
            return k
        };"""
        return execjs.compile(source).call("userPassCipher", pwd, key)

    def login(self, **kwargs):
        code, key, captcha_code = self.send_login_verify_request(tel=kwargs['tel'])
        if code != 0:
            return code, key

        url = "https://gz.ac.10086.cn/aicas/UserAreaServlet"
        params = {
            "username": kwargs['tel'],
            "AGREEMENT_CHAN_CODE": "E003"
        }
        headers = {
            "CONTENT-TYPE": "application/x-www-form-urlencoded;charset=UTF-8",
            "Accept": "*/*",
            "Referer": "https://gz.ac.10086.cn/aicas/?ai_param_loginIndex=9&service=http%3A%2F%2Fwww.gz.10086.cn%2Fservice%2Fcascallback%2Flogin&ai_param_loginTypes=2,1,3&forceLogoutUrl=ics_24_40001&username=",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": "CmLocation=851|851; CmP"
        }
        code, key, resp = self.post(url, params= params, headers=headers)
        if code != 0:
            return code, key
        if "success0" not in resp.text:
            self.log("crawler", "未知异常", resp)
            return 9, "unknown_error"
        url = "https://gz.ac.10086.cn/aicas/login"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://gz.ac.10086.cn/aicas/?ai_param_loginIndex=9&service=http%3A%2F%2Fwww.gz.10086.cn%2Fservice%2Fcascallback%2Flogin&ai_param_loginTypes=2,1,3&forceLogoutUrl=ics_24_40001&username=",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        try:
            en_pwd = self.enstr(kwargs['pin_pwd'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密服务密码失败 {}".format(error), "")
            return 9, "website_busy_error"
        data = {
            "service": "http://www.gz.10086.cn/service/cascallback/login",
            "appReferer": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
            "lt": "null",
            "ai_param_loginIndex": "9",
            "ai_param_loginTypes": "2,1,3",
            "filter_rule": "/^13\d{9}$|^18\d{9}$|^15\d{9}$|^14\d{9}$|19\d{9}$/",
            "appId": "2",
            "VERIFY_CODE_FLAG": "0",
            "ENCIPHERTOOTHER_FLAG": "1",
            "forceLogoutUrl": "ics_24_40001",
            "username": kwargs['tel'],
            "loginType": "1",
            "password": en_pwd,
            "rndPassword": "",
            "verifyCode": self.img_code,
            "IS_AGREEMENT_NEED": "0",
            "AGREEMENT_CHAN_CODE": "",
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        if '登录成功插码' not in resp.text:
            self.log("crawler", "登录未成功, 需要重试", resp)
            return 9, "website_busy_error"
        try:
            et = etree.HTML(resp.text)
            form = et.xpath("//form[@id='login_form']")[0]
            url = form.xpath("@action")[0]
            data = {}
            for i in form.xpath("input"):
                name = i.xpath("@name")[0]
                value = i.xpath("@value")[0]
                data[name] = value
                if name == "Artifact":
                    self.artifact = value
            if not self.artifact:
                self.log("crawler", "未知原因导致异常", resp)
                return 9, "html_error"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            code, key, resp = self.post(url, data=data, headers=headers)
            if code != 0:
                return code, key
        except:
            error = traceback.format_exc()
            self.log("crawler", "请求跳转失败 {}".format(error), resp)
            return 9, "html_error"
        url = "http://www.gz.10086.cn/service/fee/xdcx.jsp"
        headers = {
            "Referer": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key


        # 查详单前跳转
        url = "https://login.10086.cn/AddUID.action"
        params = {
            "channelID": "00851",
            "Artifact":	self.artifact,
            "backUrl": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
            "TransactionID": datetime.datetime.now().strftime("%Y%m%d%H%M%s")[:-2]
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers, params=params)
        if kwargs['tel'] not in resp.text:
            self.log("crawler", "未知原因导致的错误", resp)
            return 9, "html_error"
        try:
            self.csrfToken = ""
            token = re.findall('TOKEN : "(.*?)"', resp.text)[0]
            self.csrfToken = token
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取token失败 {}".format(error), resp)
            return 9, "html_error"
        return 0, "success"

    def get_verify_type(self, **kwargs):
        return ''

    def get_data(self, resp, month):
        def rek(st):
            return re.sub(r"\[.*?\]", '', st)

        if "此月度范围没有返回的数据" in resp.text:
            self.log("crawler", "偶发无数据", resp)
            return 9, "poss_miss", []
        if '服务异常' in resp.text:
            self.log("website", "服务异常", resp)
            return 9, "website_busy_error", []
        if 'CSRF TOKEN 验证失败' in resp.text:
            self.log("crawler", "验证token失败", resp)
            return 9, "website_busy_error", []

        result = []
        try:
            et = etree.XML(resp.text.encode('utf8'))
            form = et.xpath("//*[@id='dataset']/text()")[0]
            if form[0] == "[" and form[-1] == "]":
                form = form[1:-1]
            form_json = json.loads(form)
            if not self.full_name:
                self.full_name = form_json.get('custName')
            data_list = form_json.get("dataList")
            all_num = form_json.get("totalRows", "条")[0]
            if all_num == "0":
                self.log("crawler", "数据条数为0", resp)
                return 0, "no_data", []
            for i in data_list:
                if 'onlyday' in i or 'isStatistics' in i:
                    continue
                data = {
                    "call_to": "",
                    "month": month.replace('-', ''),
                    "call_time": "",
                    "call_duration": "",
                    "call_type": "",
                    "call_method": "",
                    "call_tel": "",
                    "call_from": "",
                    "call_cost": "",
                }
                call_time = i.get(u"STARTTIME")
                data['call_time'] = self.time_stamp(call_time)
                call_duration = i.get(u'DURATION')
                data['call_duration'] = self.time_format(call_duration)
                call_type = rek(i.get(u'TOLLTYPE'))
                data['call_type'] = call_type
                call_method = rek(i.get(u'CALLTYPE'))
                data['call_method'] = call_method
                tel = rek(i.get(u'OPPNUMBER'))
                data['call_tel'] = tel
                raw_call_from = rek(i.get(u'HPLMN'))
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    data['call_from'] = raw_call_from
                call_cost = rek(i.get(u'CHARGE')).replace('￥', '')
                data['call_cost'] = call_cost
                result.append(data)
            if not result:
                self.log("crawler", "未知原因无数据", resp)
                return 0, "success", result
            return 0, "success", result
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析数据失败{} ".format(error), resp)
            return 9, "json_error", ""

    def crawl_call_log(self, **kwargs):
        def change_token():
            url = "https://gz.ac.10086.cn/aicas/loginStatus"
            headers = {
                "Accept": "*/*",
                "Referer": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            params = {
                "jsoncallback":	"jQuery{}_{}".format(random.randint(1000000, 9999999), int(time.time() * 1000)),
                "service": "http://www.gz.10086.cn/service/cascallback/login",
                "forceLogoutUrl": "ics_24_40001",
                "_": str(int(time.time() * 1000))
            }
            code, key, resp = self.get(url, headers=headers, params=params)
            if code != 0:
                return code, key, ""
            try:
                host_str = re.findall(r'"host":"(.*?)"', resp.text)[0]
                ticket_str = re.findall(r'"ticket":"(.*?)"', resp.text)[0]
            except:
                error = traceback.format_exc()
                self.log("crawler", "获取参数信息失败 {}".format(error), resp)
                return 9, "html_error", ""
            url = "http://www.gz.10086.cn/service/cascallback/login"
            params = {
                "ticket": ticket_str,
                "host": host_str
            }
            headers = {
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            code, key, resp = self.get(url, headers=headers, params=params)
            if code != 0:
                return code, key, ""

            url = "http://www.gz.10086.cn/service/fee/xdcx.jsp"
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key, ""
            try:
                token = re.findall('TOKEN : "(.*?)"', resp.text)[0]
                self.csrfToken = token
            except:
                error = traceback.format_exc()
                self.log("crawler", "更新token失败{}".format(error), resp)
        missing_month_list = []
        poss_missing_month_list = []
        part_missing_month_list = []

        self.crawler_error = 0

        url = "http://www.gz.10086.cn/service/app"
        params = {
            "service": "ajaxDirect/1/fee.QueryDetailBill/fee.QueryDetailBill/javascript/refreshSearchResult",
            "pagename":	"fee.QueryDetailBill",
            "eventname": "query",
            "ID": "4043",
            "csrfToken": self.csrfToken,
            "partids": "refreshSearchResult",
            "ajaxSubmitType": "post",
            "ajax_randomcode": "0.3859629529703561",
            "autoType":	"false"
        }
        headers = {
            "Accept": "application/xml, text/xml, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.gz.10086.cn/service/fee/xdcx.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        now_date = datetime.datetime.now()
        data = {
            "detailpwdQueryForm": "",
            "searchResultInfo": "",
            "isPage": "0",
            "queryMode": "queryMonth",
            "queryType": "1",
            "monthQuery": "{}".format(now_date.strftime("%Y-%m")),
            "from":	"{}-01".format(now_date.strftime("%Y-%m")),
            "to": now_date.strftime("%Y-%m-%d")
        }
        month_list = self.monthly_period(strf="%Y-%m")
        first_month = month_list[:1]
        # first_search_month = [(xx, self.max_retry) for xx in first_month]
        for i in range(self.max_retry):
            data.update({"monthQuery": datetime.datetime.now().strftime("%Y-%m")})
            params.update({"ajax_randomcode": str(random.random())})
            code, key, resp = self.post(url, headers=headers, params=params, data=data)
            if code != 0:
                continue
            else:
                if "ID=4043" in resp.text:
                    self.log("crawler", "brfore token {}".format(self.csrfToken), "")
                    change_token()
                    data.update({"csrfToken": self.csrfToken})
                    self.log("crawler", "ahter token {}".format(self.csrfToken), "")

        search_list = [(xx, self.max_retry) for xx in month_list]
        result = []
        time_limit = 40
        retry_limit = -3
        st_time = time.time()
        break_time = st_time + time_limit
        retry_logs = []
        last_logs = []
        while search_list:
            search_str, retrys = search_list.pop(0)
            retrys -= 1
            data.update({"monthQuery": search_str})
            params.update({"ajax_randomcode": str(random.random())})
            code, key, resp = self.post(url, headers=headers, params=params, data=data)
            if code == 0:
                code, key, data_list = self.get_data(resp, search_str)
                if code == 0 and data_list:
                    result.extend(data_list)
                    continue
                if key == "no_data":
                    continue
            now_time = time.time()
            if retrys >= 0:
                search_list.append((search_str, retrys))
                retry_logs.append((search_str, retrys))
            elif now_time < break_time and retrys > retry_limit:
                time.sleep(random.uniform(1, 3))
                search_list.append((search_str, retrys))

                retry_logs.append((search_str, retrys))
            else:
                last_logs.append((search_str, retrys))
                month_str = search_str.replace("-", "")
                if key == "poss_miss":
                    if month_str not in poss_missing_month_list:
                        poss_missing_month_list.append(month_str)
                else:
                    if month_str not in missing_month_list:
                        missing_month_list.append(month_str)
                continue
        miss_set = set(missing_month_list)
        missing_month_list = list(miss_set)
        self.log("crawler", "重试记录 {} 剩余记录 {}".format(retry_logs, last_logs), "")
        missing_month_list.sort(reverse=True)
        poss_missing_month_list.sort(reverse=True)
        self.log("crawler", "缺失{}, 可能缺失{}".format(missing_month_list, poss_missing_month_list), "")
        if len(missing_month_list) == 6:
            if self.crawler_error > 0:
                return 9, "crawl_error", [], [], [], []
            return 9, "website_busy_error", [], [], [], []
        return 0, "success", result, missing_month_list, poss_missing_month_list, part_missing_month_list

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

    def time_stamp(self, time_str, str_format='%Y-%m-%d %H:%M:%S'):
        today_month = datetime.date.today().month
        today_year = datetime.date.today().year
        str_month = int(time_str[:2])
        if str_month > today_month:
            str_year = today_year - 1
        else:
            str_year = today_year
        time_str = str(str_year) + "-" + time_str
        time_type = time.strptime(time_str, str_format)
        return str(int(time.mktime(time_type)))

    def crawl_info(self, **kwargs):
        data = {
            "full_name": self.full_name,
            "id_card": "",
            "address": "",
            "open_date": "",
        }
        return 0, "success", data

    def crawl_phone_bill(self, **kwargs):
        miss_list = []
        result_list = []
        error_num = 0
        message = ""
        url = "http://www.gz.10086.cn/service/fee/yzdcx.jsp"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.gz.10086.cn/service/fee/index.jsp?BusiType=telephoneCx",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, [], []
        try:
            self.csrfToken = ""
            token = re.findall('TOKEN : "(.*?)"', resp.text)[0]
            self.csrfToken = token
        except:
            error = traceback.format_exc()
            self.log("crawler", "error{}".format(error), resp)
        url = "http://www.gz.10086.cn/service/app"
        params = {
            "service": "ajaxDirect/1/fee.QueryMonthBill/fee.QueryMonthBill/javascript/",
            "pagename":	"fee.QueryMonthBill",
            "eventname": "query",
            "ID": "4047",
            "csrfToken": self.csrfToken,
            "partids": "",
            "ajaxSubmitType": "post",
            "ajax_randomcode": "0.4137878362885039",
            "autoType":	"false"
        }

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.gz.10086.cn/service/fee/yzdcx.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        for month in list(self.monthly_period())[1:]:
            for i in range(self.max_retry):
                url = "http://www.gz.10086.cn/service/app"
                data = {
                    "select_month": month
                }
                params.update({"ajax_randomcode": str(random.random())})
                code, key, resp = self.post(url, headers=headers, params=params, data=data)
                if code != 0:
                    message = "network_error"
                    continue
                try:
                    data = {
                        "bill_package": "",
                        "bill_amount": "",
                        "bill_ext_calls": "",
                        "bill_ext_data": "",
                        "bill_ext_sms": "",
                        "bill_zengzhifei": "",
                        "bill_daishoufei": "",
                        "bill_qita": "",
                    }
                    data['bill_month'] = month
                    et = etree.XML(resp.text.encode('utf8'))
                    form = et.xpath("//*[@id='dataset']/text()")[0]
                    json_dic = json.loads(form[1:-1])
                    data['bill_amount'] = json_dic.get('fee_total')
                    data_list = json_dic.get('fee_list')
                    for i in data_list:
                        fee = i.get("fee", "")
                        name = i.get("fee_name", "")

                        if u'套餐及固定费用' in name:
                            data['bill_package'] = fee
                        if u'语音通信费' in name:
                            data['bill_ext_calls'] = fee
                        if u'上网费' in name:
                            data['bill_ext_data'] = fee
                        if u'短彩信费' in name:
                            data['bill_ext_sms'] = fee
                        if u'自用增值业务费' in name:
                            data['bill_zengzhifei'] = fee
                        if u'代收费业务费用' in name:
                            data['bill_daishoufei'] = fee
                        if u'其他' in name:
                            data['bill_qita'] = fee
                    result_list.append(data)
                    break
                except:
                    error = traceback.format_exc()
                    message = u"解析账单数据失败{}".format(error)
                    self.log("crawler", message, resp)
                    continue
            else:
                if message != "network_error":
                    error_num += 1
                miss_list.append(month)
        if len(miss_list) == 5:
            if error_num > 0:
                return 9, "crawl_error", [], []
            else:
                return 9, "website_busy_error", [], []
        return 0, "success", result_list, miss_list

    def monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        monthly_period_list = []
        for month_offset in range(0, length):
            monthly_period_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return monthly_period_list


if __name__ == "__main__":
    c = Crawler()
    USER_ID = "18275130919"
    USER_PASSWORD = "678534"
    # print(c.time_stamp('04-26 10:17:44'))
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
