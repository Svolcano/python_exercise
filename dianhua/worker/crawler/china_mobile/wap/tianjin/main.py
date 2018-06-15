# -*- coding:utf-8 -*-


import sys
import re
import time
import random
import base64

from lxml import etree
from dateutil.relativedelta import relativedelta
from requests.utils import add_dict_to_cookiejar
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
    from enstr import enstr
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_mobile.wap.tianjin.enstr import enstr

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
        self.token = None
        self.random_str = ""

    def get_login_verify_type(self, **kwargs):
        """
        1登陆时验证方法类型
        :param kwargs:
        :return:
        return
            '': 不需驗證(繼承後默認)
            'SMS': 短信隨機碼
            'Captcha': 圖形驗證碼
            'SMSCaptcha': 短信隨機碼+圖形驗證碼
        """
        # print('登陆时验证方法类型')
        return ""

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
        """
        3登陆时 提交表单 实现
        :param kwargs:
            'tel': str,
            'pin_pwd': str,
            'user_id': str,
            'user_name': unicode,
            'sms_code': str,
            'captcha_code': str
        :return:
        登入時，請求發送短信，或是下載圖片，或是同時發送請求
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        # 获取cookies
        url = "http://wap.tj.10086.cn/"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key

        # 生成一个长18的随机16进制字符串
        hex_str_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        random_hex_str = '2'+''.join([random.choice(hex_str_list) for i in range(18)]) # 2 是固定开头, 不在18的长度内
        time_str = "{}".format(int(time.time()*10))
        params_str = random_hex_str+time_str
        cookies_dict = {"WT_FPC": "id={rand}:lv={timestr}:ss={timestr}".format(rand=params_str, timestr=time_str)}

        url = "http://service.tj.10086.cn:7070/app/webtrends/dcs.gif?WT.branch=wap&dcssip=wap.tj.10086.cn&WT.host=wap.tj.10086.cn&dcsuri=%2Findex.action&WT.es=http%3A%2F%2Fwap.tj.10086.cn%2Findex.action&WT.sr=1920x1080&WT.ti=%E6%8E%8C%E4%B8%8A%E8%90%A5%E4%B8%9A%E5%8E%85-%E5%A4%A9%E6%B4%A5%E7%A7%BB%E5%8A%A8&WT.mobile=&WT.co_f={}&dcsdat={}".format(params_str, int(time.time()*10))
        headers = {
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "http://wap.tj.10086.cn/index.action",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key

        # 获取token
        login_url = "https://tj.ac.10086.cn/login.htm?appKey=201703157622&display=mobile&redirectUrl=http%3A%2F%2Fwap.tj.10086.cn&sign=448D261865EBDD381A7B0CEBE31CB03B6F508B46"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(login_url, headers=headers)
        if code != 0:
            return code, key
        try:
            et = etree.HTML(resp.text)
            self.token = et.xpath("//input[@id='token']/@value")
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取登录信息失败{}".format(error), resp)
            return 9, "html_error"

        for i in range(self.max_retry):
            # 获取图片
            url = "https://tj.ac.10086.cn/captcha.htm"
            params = {
                "token": self.token,
                "_": "{}".format(random.random())
            }
            headers = {
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": login_url,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            code, key, resp = self.get(url, headers=headers, params=params)
            if code != 0:
                return code, key
            # 云打码
            if "data:image/png;base64," not in resp.text:
                self.log("crawler", "返回的图片格式发生变化或返回错误", resp)
                return 9, "html_error"

            pic = re.sub("data:image/png;base64,", "", resp.text)
            codetype = 3004
            key, result, cid = self._dama(base64.b64decode(pic), codetype)
            if key == "success" and result != "":
                captcha_code = str(result)
            else:
                self.log("website", "website_busy_error: 云打码失败{}".format(result), '')
                return 9, key
            # with open("{}_{}.png".format(i, captcha_code), "wb")as f:
            #     f.write(base64.b64decode(pic))
            # 验证图片
            url = "https://tj.ac.10086.cn/login.json"
            headers = {
                "Pragma": "no-cache",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": login_url,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            data = {
                "token": self.token,
                "mp": kwargs['tel'],
                "loginPwd": kwargs['pin_pwd'],
                "captcha": captcha_code,
                "action": "passwd",
                "appKey": "201703157622",
                "redirectUrl": "http://wap.tj.10086.cn",
                "_": "{}".format(random.random())
            }
            add_dict_to_cookiejar(self.session.cookies, cookies_dict)
            code, key, resp = self.post(url, headers=headers, data=data)
            if code != 0:
                return code, key
            if '服务密码不正确' in resp.text:
                self.log("crawler", "服务密码不正确", resp)
                return 1, "pin_pwd_error"
            if '验证码输入不正确' in resp.text:
                self.log("crawler", "验证码不正确", resp)
                self._dama_report(cid)
                continue
            if '登录成功' in resp.text:
                break
            else:
                self.log("crawler", "未知原因登录失败", resp)
                return 9, "unknown_error"
        else:
            self.log("crawler", "打码全部失败", "")
            return 9, "auto_captcha_code_error"
        url = "http://wap.tj.10086.cn/"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key
        try:
            self.random_str = re.findall('random=(.*?)">', resp.text)[0]
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取random值失败{}".format(error), resp)
            return 9, "html_error"
        return 0, "success"

    def get_verify_type(self, **kwargs):
        """
        4二次验证方法类型
        :param kwargs:
        :return:
        """
        return "SMS"

    def send_verify_request(self, **kwargs):
        """
        5欲 二次验证  获取信息
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """
        # print('二次验证,获取信息')
        zhongjian_url = "http://wap.tj.10086.cn/query.action?call=zhongjianye&random={}".format(self.random_str)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://wap.tj.10086.cn/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(zhongjian_url, headers=headers)
        if code != 0:
            return code, key, ""
        try:
            self.random_str = ''.join(
                filter(lambda x: 'a' < x < 'z' or 'A' < x < 'Z', re.findall('random=(.*?)">', resp.text)[0]))
        except:
            error = traceback.format_exc()
            self.log("crawler", "更新random值失败{}".format(error), resp)
            return 9, "html_error", ""

        url = "http://wap.tj.10086.cn/qdcx.action"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": zhongjian_url
        }
        params = {
            "call": "processqdcx",
            "action": "view",
            "random": self.random_str
        }
        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key, ""
        try:
            # self.log("crawler", "保存值", resp)
            # et = etree.HTML(resp.text)
            # self.modulus = et.xpath("//input[@id='hid_modulus']/@value")[0]
            # self.exponent = et.xpath("//input[@id='hid_exponent']/@value")[0]
            self.modulus = "00bed06e918ea4807ae0fdbc8388416a95e9697d8398c0231ab79e42c110969f8d1fa78a25011436333c8fbda36114990c61e6359ebdfe221e37318eef04b74f0d2c43e1a1a4a22f6b80865599cee2e0737f2da10a17223173aaa758619a93cd9e148a078a647e5e6cddda620ac571fc793a38fd06985b79291fd88eb7e2d71d3d"
            self.exponent = "010001"
            self.pwd = enstr(self.modulus, self.exponent, kwargs['pin_pwd'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析短信发送结果失败{}".format(error), resp)
            return 9, "json_error", ""
        url = "http://wap.tj.10086.cn/qdcx.action"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://wap.tj.10086.cn/qdcx.action?call=processqdcx&action=view&random={}".format(self.random_str),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {
            "call": "loginNub",
            "fwmm": self.pwd
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key, ""
        resp_strip_text = resp.text.strip()
        if "is" == resp_strip_text:
            return 0, "success", ""
        if 'dj' == resp_strip_text:
            self.log("crawler", "DJ", resp)
            return 9, "over_query_limit", ''
        if 'notsend' == resp_strip_text:
            self.log("crawler", "NOTSEND", resp)
            return 9, "resp_strip_text", ""
        if 'no' == resp_strip_text:
            self.log("crawler", "NO", resp)
            return 9, "website_busy_error", ""
        if "fwmmerror" == resp_strip_text:
            self.log("crawler", "服务密码错, 怎么会有这个??", resp)
            return 9, "pin_pwd_error", ""
        self.log("crawler", "未知原因错误", resp)
        return 9, "unknown_error", ""

    def verify(self, **kwargs):
        """
        6二次登陆 提交 实现
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """
        url = "http://wap.tj.10086.cn/qdcx.action"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://wap.tj.10086.cn/qdcx.action?call=processqdcx&action=view&random={}".format(self.random_str),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        try:
            sms = enstr(self.modulus, self.exponent, kwargs['sms_code'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密短信验证码失败{}".format(error), "")
            return 9, "website_busy_error"
        data = {
            "dxpwd": sms,
            "fwmm": self.pwd,
            "call": "processqdcx",
            "action": "query"
        }
        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        if resp.history:
            for his in resp.history:
                self.log("crawler", "记录跳转", his)

        if "当月" in resp.text:
            return 0, "success"
        else:
            if "验证码错误" in resp.text or "验证码已过期" in resp.text:
                self.log("crawler", "验证码错误", resp)
                return 9, "verify_error"
            self.log("crawler", "未知原因出错", resp)
            return 9, "unknown_error"

    def crawl_info(self, **kwargs):
        url = "http://wap.tj.10086.cn/grxxProc.action"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://wap.tj.10086.cn/query.action?call=zhongjianye&random=",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        params = {
            "call":	"grxxcx",
            "random": "Ay41U"
        }
        code, key, resp = self.get(url, headers=headers, params=params)
        if code != 0:
            return code, key, {}
        try:
            full_name = re.findall(u"客户名称：</b>(.*?)<", resp.text)[0]
            open_date = re.findall(u"入网时间：</b>(.*?)<", resp.text)[0]
            address = re.findall(u"证件地址：</b>(.*?)<", resp.text)[0]
            open_date = self.time_stamp(open_date)
            info_data = {
                "full_name": full_name,
                "id_card": "",
                "address": address,
                "open_date": open_date
            }
            return 0, "success", info_data
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析个人信息失败  {}".format(error), resp)
            return 9, "json_error", {}

    def time_stamp(self, time_str, str_format='%Y-%m-%d %H:%M:%S'):
        xx = re.findall("\d{2,4}", time_str)
        if len(xx) == 3:
            time_str += " 00:00:00"
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
        xc = et.xpath("//*[@class='tables']")

        data_list = []
        for i in xc:
            dat = dict()
            xx = i.xpath("tr/td[2]/text()")

            dat['call_tel'] = xx[3]
            dat['call_cost'] = xx[7]
            call_time = xx[0]
            call_time_str = re.findall("\d{2,4}", call_time)
            if len(call_time_str) == 3:
                self.log("crawler", "{}".format(call_time), "")
                continue
            dat['call_time'] = self.time_stamp(call_time)
            dat['call_method'] = xx[2]
            dat['call_type'] = xx[5]
            raw_call_from = xx[1]
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                dat['call_from'] = call_from
            else:
                dat['call_from'] = raw_call_from
            dat['call_from'] = xx[1]
            dat['call_to'] = ""
            call_duration = self.time_format(xx[4])
            dat['call_duration'] = call_duration
            dat['month'] = month
            data_list.append(dat)
        return 0, "success", data_list

    def crawl_call_log(self, **kwargs):
        """
        获取详单历史
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        # print('获取详单历史')
        pos_miss_list = []
        miss_list = []

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
            url = "http://wap.tj.10086.cn/qdcx.action"
            data = {
                "biltype": "1001",
                "month": month,
                "call":	"processqdcx",
                "action": "querytwo"
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "http://wap.tj.10086.cn/qdcx.action",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            code, key, resp = self.post(url, headers=headers, data=data)
            if code == 0:
                code, key, data_list = self.get_page_data(resp, month)
                if code == 0 and data_list:
                    result_list.extend(data_list)
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

        self.log("crawler", "重试记录{}".format(log_for_retrys), "")
        if len(miss_list+pos_miss_list) == 6:

            if crawler_error == 0:
                return 9, 'website_busy_error', [], miss_list, pos_miss_list
            else:
                return 9, 'crawl_error', [], miss_list, pos_miss_list
        return 0, 'success', result_list, miss_list, pos_miss_list

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
        bill_url = "http://wap.tj.10086.cn/query.action?call=zhongjianye&random={}".format(self.random_str)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://wap.tj.10086.cn/qdcx.action",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        code, key, resp = self.get(bill_url, headers=headers)
        if code != 0:
            self.log("crawler", "获取cookies失败", resp)
            return code, key, [], []
        try:
            self.random_str = ''.join(
                filter(lambda x: 'a' < x < 'z' or 'A' < x < 'Z', re.findall('random=(.*?)">', resp.text)[0]))
        except:
            error = traceback.format_exc()
            self.log("crawler", "账单更新random失败 {}".format(error), resp)
            return 9, "html_error", [], []

        month_fee = []
        miss_list = []
        message_list = []
        month_bill_url = "http://wap.tj.10086.cn/hfcxProc.action"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": bill_url
        }
        # 先使用self.random_str 请求一次账单
        params = {
            "call":	"querymonthbill",
            "random": self.random_str
        }
        coed, key, resp = self.get(month_bill_url, headers=headers, params=params)
        if code != 0:
            return code, key, [], []
        for each_month in self.monthly_period():
            params = {
                "call":	"querymonthbill",
                "month": each_month
            }
            for i in range(self.max_retry):
                code, key, resp = self.get(month_bill_url, headers=headers, params=params)
                if code != 0:
                    msg = key
                    continue

                if '系统繁忙，请稍后再试' in resp.text:
                    msg = "website_busy_error"
                    continue
                try:
                    month_fee_data = {}
                    bill_amount = re.findall(u"账单总额.*?(\d{1,}\.\d{2})", resp.text)
                    bill_package = re.findall(u"套餐及固定费.*?(\d{1,}\.\d{2})", resp.text)
                    bill_ext_calls = re.findall(u"语音通信费.*?(\d{1,}\.\d{2})", resp.text)
                    bill_ext_data = re.findall(u"上网超套餐流量费.*?(\d{1,}\.\d{2})", resp.text)
                    bill_ext_sms = re.findall(u"短彩信费.*?(\d{1,}\.\d{2})", resp.text)
                    bill_zengzhifei = re.findall(u"自有增值业务.*?(\d{1,}\.\d{2})", resp.text)
                    bill_daishoufei = re.findall(u"代收费业务费用.*?(\d{1,}\.\d{2})", resp.text)
                    bill_qita = re.findall(u"其它.*?(\d{1,}\.\d{2})", resp.text)

                    month_fee_data['bill_amount'] = "".join(bill_amount and bill_amount[0])
                    month_fee_data['bill_package'] = "".join(bill_package and bill_package[0])
                    month_fee_data['bill_ext_calls'] = "".join(bill_ext_calls and bill_ext_calls[0])
                    month_fee_data['bill_ext_data'] = "".join(bill_ext_data and bill_ext_data[0])
                    month_fee_data['bill_ext_sms'] = "".join(bill_ext_sms and bill_ext_sms[0])
                    month_fee_data['bill_zengzhifei'] = "".join(bill_zengzhifei and bill_zengzhifei[0])
                    month_fee_data['bill_daishoufei'] = "".join(bill_daishoufei and bill_daishoufei[0])
                    month_fee_data['bill_qita'] = "".join(bill_qita and bill_qita[0])
                    month_fee_data['bill_month'] = each_month
                    # 如果都为空则不添加到集合
                    if month_fee_data['bill_amount'] == '0.0':
                        break
                    month_fee.append(month_fee_data)
                    break
                except:
                    error = traceback.format_exc()
                    msg = "json_error: " + error
                    continue
            else:
                if msg == "website_busy_error":
                    self.log("website", msg, resp)
                else:
                    self.log("crawler", msg, resp)
                miss_list.append(each_month)
                message_list.append(msg)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], miss_list
        return 0, "success", month_fee, miss_list

    def monthly_period(self, length=6, strf='%Y%m'):
        current_time = datetime.datetime.now()
        monthly_period_list = []
        for month_offset in range(0, length):
            monthly_period_list.append((current_time - relativedelta(months=month_offset)).strftime(strf))
        return monthly_period_list

if __name__ == "__main__":
    c = Crawler()
    USER_ID = "18202541892"
    # USER_PASSWORD = "157350"
    USER_PASSWORD = "806402"

    # self_test
    # USER_ID = "18301495516"
    # USER_PASSWORD = "332266"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # c.send_login_verify_request(tel="18301495516", pin_pwd=USER_PASSWORD)
    # temp = BaseCommon().generator_time()
    # month_retrys = [(x, 3) for x in temp]
    # print month_retrys