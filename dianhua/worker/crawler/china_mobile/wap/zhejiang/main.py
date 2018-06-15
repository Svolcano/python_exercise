# -*- coding:utf-8 -*-


import sys
import re
import time
import random
import base64

from lxml import etree
from dateutil.relativedelta import relativedelta

reload(sys)
sys.setdefaultencoding('utf8')

import datetime
import traceback

if __name__ == '__main__':
    sys.path.append('..')
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    sys.path.append('../../../../..')
    from crawler.base_crawler import BaseCrawler
    from enstr import enstring
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_mobile.wap.zhejiang.enstr import enstring


class Crawler(BaseCrawler):
    """
    用装饰器,分别封装了
        1> 底层log,便于单个爬虫的bug 排查
        2> 默认异常抛出, 代码复用
    """

    def __init__(self, **kwargs):
        """
            kwargs 包含
                'tel': str,
                'pin_pwd': str,
                'user_id': str,
                'user_name': unicode,
                'sms_code': str,
                'captcha_code': str
            錯誤等級
                0: 成功
                1: 帳號密碼錯誤
                2: 認證碼錯誤
                9: 其他錯誤
        """
        super(Crawler, self).__init__(**kwargs)

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        :param kwargs:
        :return:
        list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        # print('用list告訴我你需要哪些欄位')
        return ['pin_pwd', 'sms_verify']

    def login(self, **kwargs):
        # set cookies
        login_url = "https://zj.ac.10086.cn/login?jumpurl=http://wap.zj.10086.cn/szhy/my/index.html"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        code, key, resp = self.get(login_url, headers=headers)
        if code != 0:
            return code, key
        try:
            et = etree.HTML(resp.text)
            spid = et.xpath("//form/input[@name='spid']/@value")[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取spid失败{}".format(error), resp)
            return 9, "html_error"

        codetype = 3004
        for i in range(self.max_retry):
            # 获取图片
            url = "https://zj.ac.10086.cn//common/image.jsp?r={}".format(random.randint(1000000000000, 9999999999999))
            headers = {
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Referer": login_url,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"""
            }
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key

            # 云打码
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
            # 验证
            url = "https://zj.ac.10086.cn/validImageCode?r_{}&imageCode={}".format(random.random(), captcha_code)
            headers = {
                "Referer": login_url,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest"
            }
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key
            if "1" != str(resp.text.strip()):
                self.log("crawler", "图片打码失败", resp)
                self._dama_report(cid)
                continue
            else:
                break
        else:
            self.log("crawler", "自动打码失败", "")
            return 9, "auto_captcha_code_error"
        try:
            pin_pwd = enstring(kwargs['pin_pwd'])
            tel = enstring(kwargs['tel'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "信息加密失败{}".format(error), "")
            return 9, "website_busy_error"
        data = {
            "type": "B",
            "backurl": "https://zj.ac.10086.cn/waplogin/backPage.jsp",
            "warnurl": "https://zj.ac.10086.cn/waplogin/warnPage.jsp",
            "errorurl": "https://zj.ac.10086.cn/waplogin/errorPage.jsp",
            "spid": spid,
            "RelayState": "type=B;backurl=http://wap.zj.10086.cn/servlet/assertion;nl=7;loginFromUrl=http://wap.zj.10086.cn/szhy/my/index.html;callbackurl=/servlet/assertion;islogin=true",
            "mobileNum": tel,
            "validCode": captcha_code,
            "smsValidCode": "",
            "service": "my",
            "failurl": "",
            "continue": "http%3A%2F%2Fwap.zj.10086.cn%2Fszhy%2Fmy%2Findex.html",
            "loginUserType": "1",
            "pwdType": "2",
            "billId": kwargs['tel'],
            "servicePassword": pin_pwd,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": login_url,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        url = "https://zj.ac.10086.cn/Login"
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        if resp.history:
            try:
                result_code = re.findall("code=(.*?)&", resp.url)[0]
                if result_code == "5003":
                    self.log("user", "服务密码错误", resp)
                    return 9, "pin_pwd_error"
                if result_code == "7005":
                    self.log("user", "服务密码错误", resp)
                    return 9, "pin_pwd_error"
                self.log("crawler", "其他情况登陆出现错误", resp)

                return 9, "login_param_error"

            except:
                error = traceback.format_exc()
                self.log("crawler", "解析登录结果失败 {}".format(error), resp)
                return 9, "html_error"

        try:
            et = etree.HTML(resp.text)

            url = et.xpath("//form/@action")[0]
            data = {}
            form = et.xpath("//form/input")
            for i in form:
                name = i.xpath("./@name")[0]
                value = i.xpath("./@value")[0]
                if name == "SAMLart":
                    self.samlart = value
                data[name] = value
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "https://zj.ac.10086.cn/Login",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            code, key, resp = self.post(url, headers=headers, data=data)
            if code != 0:
                return code, key
            url = "http://wap.zj.10086.cn/servlet/assertion"
            data = {
                "SAMLart": self.samlart,
                "RelayState": "type=B;backurl=http://wap.zj.10086.cn/servlet/assertion;nl=7;loginFromUrl=http://wap.zj.10086.cn/szhy/my/index.html;callbackurl=/servlet/assertion;islogin=true"
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            code, key, resp = self.post(url, headers=headers, data=data)
            if code != 0:
                return code, key
            # print(resp.text)
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取登录跳转信息失败{}".format(error), resp)
            return 9, "html_error"
        try:
            self.ul_scid = re.findall('ul_scid=(.*?)"', resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取官网随机数失败 {} ".format(error), resp)
            return 9, "html_error"
        return 0, "success"

    def get_verify_type(self, **kwargs):
        return "SMS"

    def send_verify_request(self, **kwargs):
        url = "http://wap.zj.10086.cn/new/mobileApp/client/queryUserInfoBySso.do?ul_scid={}".format(self.ul_scid)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://wap.zj.10086.cn/szhy/my/index.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, ""
        url = "http://wap.zj.10086.cn/mobileStore/details/query/queryDetails.do?r={}".format(random.random())
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://wap.zj.10086.cn/mobileStore/details/query/list.do?v=6&id=1063&nwId=wap&ul_nwid=wap&ul_scid={}".format(self.ul_scid),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {
            "listType":	"1",
            "secondPass": "",
            "type": "json",
            "id": "1063"
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key, ""

        if '验证码下发成功' in resp.text:
            return 0, "success", ""
        elif '用户查询详单验证码仍在有效期内，请继续使用' in resp.text:

            return 0, "reusable_sms", "reusable_sms"
        else:
            self.log("crawler", "下发短信验证码失败", resp)
            return 9, "send_sms_error", ""

    def verify(self, **kwargs):
        url = "http://wap.zj.10086.cn/mobileStore/details/query/queryDetails.do?r={}".format(random.random())
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://wap.zj.10086.cn/mobileStore/details/query/list.do?v=6&id=1063&nwId=wap&ul_nwid=wap&ul_scid={}".format(self.ul_scid),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {
            "listType": "1",
            "secondPass": kwargs['sms_code'],
            "type":	"json",
            "id": "1063"
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        try:
            result = resp.json()
            result_code = result.get("code")
            if result_code == "0":
                return 0, "success"
            else:
                self.log("crawler", "验证码错误", resp)
                return 9, "verify_error"
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析短信验证异常{}".format(error), resp)
            return 9, "json_error"

    def time_stamp(self, time_str, str_format='%Y-%m-%d %H:%M:%S'):
        time_type = time.strptime(time_str, str_format)
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


    def get_page_data(self, resp, month):
        et = etree.HTML(resp.text)
        xx = et.xpath("//dl")
        data_list = []
        for i in xx:
            data = {}
            call_tel = i.xpath("./dt/div[1]/span[1]/text()")
            call_cost = i.xpath("./dt/div[1]/span[2]/text()")
            call_time = i.xpath("./dt/div[2]/span[1]/text()")
            call_from = i.xpath("./dt/div[2]/span[2]/text()")
            call_method = i.xpath("./dt/div[2]/span[3]/text()")
            call_duration = i.xpath("./dt/div[2]/span[4]/text()")
            call_type = i.xpath("./dd/ul/li[2]/span[2]/text()")

            data['call_tel'] = "".join(call_tel and call_tel[0])
            data['call_cost'] = "".join(call_cost and call_cost[0])
            data['call_time'] = "".join(call_time and self.time_stamp(call_time[0]))
            raw_call_from = "".join(call_from and call_from[0])
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                data['call_from'] = call_from
            else:
                data['call_from'] = raw_call_from
            data['call_method'] = "".join(call_method and call_method[0])
            data['call_type'] = "".join(call_type and call_type[0])
            data['call_duration'] = "".join(call_duration and self.time_format(call_duration[0]))
            data['month'] = month
            data['call_to'] = ''
            data_list.append(data)
        if "点击查看更多" in resp.text:
            return 0, "has_next", data_list
        return 0, "success", data_list

    def get_next_page_data(self, resp, month):
        data_list = []
        try:
            js = resp.json()
            raw_list = js.get("list")
            for i in raw_list:
                data = {}
                info = i.get("cs")
                # print info
                if not info:
                    self.log("crawler", "异常的数据{}".format(i), resp)
                    continue
                call_tel = info[5]
                call_cost = info[0]
                call_time = info[1]
                call_from = info[7]
                call_method = info[4]
                call_duration = info[2]
                call_type = info[3]

                data['call_tel'] = call_tel
                data['call_cost'] = call_cost
                data['call_time'] = self.time_stamp(call_time)
                raw_call_from = call_from
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    data['call_from'] = call_from
                else:
                    data['call_from'] = raw_call_from
                data['call_method'] = call_method
                data['call_type'] = call_type
                data['call_duration'] = self.time_format(call_duration)
                data['call_to'] = ''
                data['month'] = month
                data_list.append(data)
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取详单未知异常{}".format(error), resp)
            return 9, "json_error", data_list
        return 0, "success", data_list


    def get_next_page(self, month, ref_url):
        data_list = []
        part_miss_list = []
        for times in range(self.max_retry):
            message = ""
            url = "http://wap.zj.10086.cn/mobileStore/details/query/queryDetails.do"
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": ref_url,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            parmas = {"r": "{}".format(random.random())}
            data = {
                "listType": "1",
                "yearMonth": month,
                "pageNum": "2",
                "type": "more",
                "id": "1063"
            }
            code, key, resp = self.post(url, headers=headers, data=data, params=parmas)
            if code != 0:
                return code, key, [], []
            message = resp
            code, key, result = self.get_next_page_data(resp, month)
            if code == 0 and result:
                data_list.extend(result)
                break
        else:
            self.log("crawler", "重试第二页失败", message)
            part_miss_list.append(month)
            return 9, "json_error", [], part_miss_list

        try:
            result = resp.json()
            totalPage = result.get("totalPage")
        except:
            error = traceback.format_exc()
            part_miss_list.append(month)
            self.log("crawler", "解析分页失败{}".format(error), resp)
            return 9, "json_error", [], part_miss_list
        # 当执行到这里时, 之前加入的部分缺失需要清空
        part_miss_list = []
        for page_num in range(3, totalPage+1):
            data['pageNum'] = page_num
            for times in range(self.max_retry):
                code, key, resp = self.post(url, headers=headers, data=data, params=parmas)
                if code != 0:
                    return code, key, [], []
                message = resp
                code, key, result = self.get_next_page_data(resp, month)
                if code == 0 and result:
                    data_list.extend(result)
                    break
            else:
                self.log("crawler", "重试第{}页失败".format(page_num), message)
                part_miss_list.append(month)
        return 0, "success", data_list, part_miss_list

    def crawl_call_log(self, **kwargs):
        miss_list = []
        pos_miss_list = []
        part_miss_list = []
        data_list = []
        month_retrys = [(x, self.max_retry) for x in self.monthly_period()]
        time_fee = 0
        full_time = 40.0
        rand_time = random.randint(20, 40) / 10.0
        st_time = time.time()
        crawler_error = 0
        result_list = []
        log_for_retrys = []
        retrys_limit = -4
        while month_retrys:
            month, retrys = month_retrys.pop(0)
            retrys -= 1
            if retrys < retrys_limit:
                self.log("crawler", "重试完成", "")
                miss_list.append(month)
                continue

            log_for_retrys.append((month, retrys, time_fee))


            url = "http://wap.zj.10086.cn/mobileStore/details/query/queryDetails.do?id=1063&listType=1&yearMonth={}&r={}".format(month, random.random())
            headers = {
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": "http://wap.zj.10086.cn/mobileStore/details/query/queryDetails.do?id=1063&listType=1",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            data = {"id": "1063"}
            code, key, resp = self.post(url, headers=headers, data=data)
            if code == 0:
                code, key, result = self.get_page_data(resp, month)
                if code == 0 and result:
                    result_list.extend(result)
                    if key == "has_next":
                        code, key, next_result, next_part_miss = self.get_next_page(month, url)
                        part_miss_list.extend(next_part_miss)
                        result_list.extend(next_result)
                    continue
            if retrys >= 0:
                time_fee = time.time() - st_time
                month_retrys.append((month, retrys))
            elif time_fee < full_time:
                time.sleep(rand_time)
                time_fee = time.time() - st_time
                month_retrys.append((month, retrys))
            else:
                self.log("crawler", "多次重试失败", "")
                miss_list.append(month)

        miss_list = list(set(miss_list))
        part_miss_list = list(set(part_miss_list))
        miss_list.sort(reverse=True)
        part_miss_list.sort(reverse=True)
        if len(miss_list) == 6:
            return 9, "website_busy_error", data_list, miss_list, pos_miss_list, part_miss_list
        return 0, "success", result_list, miss_list, pos_miss_list, part_miss_list

    def crawl_info(self, **kwargs):
        url = ""
        return 9, "unknown_error", {}

    def crawl_phone_bill(self, **kwargs):
        url = "http://wap.zj.10086.cn/"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, [], []

        url = "http://wap.zj.10086.cn/new/authentication?uid=59&chId=1&nwId=wap&ul_nwid=wap&ul_scid={}".format(self.ul_scid)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://wap.zj.10086.cn/szhy/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key, [], []
        if resp.history:
            for his in resp.history:
                self.log("crawler", "记录跳转", his)

        try:
            ref_url = resp.url
            session_str = re.findall("session=(.*?)&", ref_url)[0]
            nonce = re.findall("nonce=(.*?)&", ref_url)[0]
            encpn = re.findall("encpn=(.*?)&", ref_url)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取账单信息session_str失败{}".format(error), resp)
            return 9, "html_error", [], []

        # 用户认证
        url = "http://app.m.zj.chinamobile.com/zjweb/Authentic.do"
        params = {
            "cf": "10058",
            "nonce": nonce,
            "encpn": encpn
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }
        code, key, resp = self.post(url, headers=headers, params=params)
        if code != 0:
            return code, key, [], []

        result_list = []
        miss_list = []
        crawler_error = 0

        url = "http://app.m.zj.chinamobile.com/zjweb/Bill.do"
        params = {
            "ym": "0",
            "session": session_str,
            "num": kwargs['tel']
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": ref_url,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9c"
        }
        for month_str in self.monthly_period():
            if month_str == datetime.datetime.now().strftime("%Y%m"):
                ym = "0"
            else:
                ym = month_str
            params.update({"ym": ym})
            for i in range(self.max_retry):
                code, key, resp = self.post(url, headers=headers, params=params)
                if code == 0:
                    code, key, result = self.get_bill_data(resp, month_str)
                    if code == 0:
                        result_list.append(result)
                        break
            else:
                miss_list.append(month_str)

        if len(miss_list) == 6:
            if crawler_error > 0:
                self.log("crawler", "获取账单中有异常", "")
                return 9, "crawl_error", [], []
            return 9, "website_busy_error", result_list, miss_list
        return 0, "success", result_list, miss_list

    def get_bill_data(self, resp, month):
        try:
            js = resp.json()
            info_list = js.get('qry').get('list')
            bill_amount = js.get('qry').get('total')
            info_dict = {
                "bill_amount": bill_amount,
                "bill_month": month,
                "bill_package": "",
                "bill_ext_calls": "",
                "bill_ext_sms": "",
                "bill_ext_data": "",
                "bill_zengzhifei": "",
                "bill_daishoufei": "",
                "bill_qita": "",
            }

            for info in info_list:
                name = info['name']
                fee = info['amount']
                if name == u"套餐及固定费":
                    info_dict["bill_package"] = fee
                if name == u"语音通信费":
                    info_dict['bill_ext_calls'] = fee
                if name == u"短彩信费":
                    info_dict['bill_ext_sms'] = fee
                if name == u"上网费":
                    info_dict['bill_ext_data'] = fee
                if name == u"增值业务费":
                    info_dict['bill_zengzhifei'] = fee
                if name == u"代收费":
                    info_dict['bill_daishoufei'] = fee
            return 0, "success", info_dict
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析账单数据失败 {}".format(error), resp)
            return 9, "json_error", {}



    def monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        monthly_period_list = []
        for month_offset in range(0, length):
            monthly_period_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return monthly_period_list

if __name__ == "__main__":
    c = Crawler()
    # USER_ID = "13575702249"
    USER_ID = "13575702249"
    USER_PASSWORD = "125274"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
