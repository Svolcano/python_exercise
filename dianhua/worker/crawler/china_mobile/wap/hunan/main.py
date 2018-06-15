# -*- coding:utf-8 -*-


import sys
import urllib
import re
import time
import random


from datetime import date
from dateutil.relativedelta import relativedelta

reload(sys)
sys.setdefaultencoding('utf8')

import datetime
import json
import traceback

if __name__ == '__main__':
    sys.path.append('..')
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    sys.path.append('../../../../..')
    from base_common import BaseCommon
    from crawler.base_crawler import BaseCrawler
    from exec_hunan import strEnc

else:
    from worker.crawler.china_mobile.wap.hunan.base_common import BaseCommon
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_mobile.wap.hunan.exec_hunan import strEnc


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
        # self.err = False
        # self.err_desc = "success"
        # self.err_msg = ""
        # self.err_code = 0

    # def set_err_log(self, is_err=False, err_desc="success", err_code=0, err_msg=""):
    #     self.err, self.err_desc, self.err_code, self.err_msg = is_err, err_desc, err_code, err_msg

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
        return "SMS"

    def need_parameters(self, **kwargs):
        """
        用list告訴我你需要哪些欄位
        :param kwargs:
        :return:
        list of full_name, id_card, pin_pwd, sms_verify, captcha_verify
        """
        # print('用list告訴我你需要哪些欄位')
        return ['pin_pwd', 'sms_verify']

    def ne_len_random(self):
        random_str = str(random.random()).split('.')[1]
        ne_random_str = random_str.split('e')[0]
        if len(ne_random_str) < 16:
            le = 16 - len(ne_random_str)
            xx = random.randint(int('1'.ljust(le, '1')), int('9'.ljust(le, '9')))
            random_str = '0.' + ne_random_str + str(xx)
        return random_str

    def send_login_verify_request(self, **kwargs):
        """
        2宇登陆 准备 获取验证信息
        登入時，請求發送短信，或是下載圖片，或是同時發送請求
        :param kwargs:
        :return:
            status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
            level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """

        # 登录URL http://wap.hn.10086.cn/wap/static/login/Login.html

        random_str = self.ne_len_random()
        url = "http://wap.hn.10086.cn/wap/login/getLoginInfo"
        params = {
            "undefined": "",
            "pageName": "Login.html",
            "ajaxSubmitType": "post",
            "ajax_randomcode": random_str
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://wap.hn.10086.cn/wap/static/login/Login.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, params=params, headers=headers, cookies={random_str: "0"})
        if code != 0:
            return code, key, ''

        random_str = self.ne_len_random()
        params = {
            "serialNumber": kwargs['tel'],
            "chanId": "E004",
            "operType": "SENDSMS",
            "goodsName": "发送短信验证码",
            "smsValidateCode": "",
            "loginType": "1",
            "pageName": "Login.html",
            "ajaxSubmitType": "post",
            "ajax_randomcode": random_str
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://wap.hn.10086.cn/wap/static/login/Login.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        url = "http://wap.hn.10086.cn/wap/login/sendSms"
        code, key, resp = self.post(url, headers=headers, params=params, cookies={random_str: "0"})
        if code != 0:
            return code, key, ""
        return code, key, ''

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
        # print('登陆时 提交表单 实现')
        # Building headers
        # 密码加密
        try:
            enc_pwd = strEnc(kwargs['pin_pwd'], kwargs['tel'])
        except:
            error = traceback.format_exc()
            self.log("crawler", "加密失败{}".format(error), "")
            return 9, "website_busy_error"

        random_str = self.ne_len_random()
        # TODO: 密码加密
        login_params = {
            "SERIAL_NUMBER": kwargs['tel'],
            "LOGIN_TYPE": "1",
            "USER_PASSWD": enc_pwd,
            "VALIDATE_CODE": "undefined",
            "chanId": "E004",
            "operType": "LOGIN",
            "goodsName": "服务密码登录",
            "loginType": "0",
            "USER_PASSSMS": kwargs['sms_code'],
            "pageName": "Login.html",
            "ajaxSubmitType": "post",
            "ajax_randomcode":	random_str
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://wap.hn.10086.cn/wap/static/login/Login.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        url = "http://wap.hn.10086.cn/wap/login/SSOLogin?SERIAL_NUMBER={}&LOGIN_TYPE=1&USER_PASSWD={}&" \
              "VALIDATE_CODE=undefined&chanId=E004&operType=LOGIN&goodsName=%E6%9C%8D%E5%8A%A1%E5%AF%86%E7%A0%81%E7%99%BB%E5%BD%95&" \
              "loginType=0&USER_PASSSMS={}&pageName=Login.html&ajaxSubmitType=post&ajax_randomcode={}".format(kwargs['tel'], enc_pwd, kwargs['sms_code'], random_str)
        code, key, resp = self.get(url, headers=headers, cookies={random_str: "0"})
        if code != 0:
            return code, key

        if not '登录成功' in resp.text:
            if "短信验证码错误" in resp.text:
                self.log("crawler", "短信验证码错误", resp)
                return 9, "verify_error"
            if '短信密码已经发送到您的手机，5分钟之内有效' in resp.text:
                self.log("crawler", "website_busy_error", resp)
                return 9, "website_busy_error"
            if '账户名与密码不匹配' in resp.text:
                self.log("crawler", "", resp)
                return 1, "pin_pwd_error"
            if '账号已锁定' in resp.text:
                self.log("crawler", "account_locked", resp)
                return 9, "account_locked"
            self.log("crawler", "未知原因登录失败", resp)
            if '"X_RESULTCODE":"-1"' in resp.text:
                return 9, "login_param_error"
            return 9, "unknown_error"

        timestamp = str(int(time.time())) + str(random.randint(100, 999))
        url = "https://login.10086.cn/AddUID.htm"
        try:
            result = resp.json()
            params = {
                "channelID": result.get("CHANNELID"),
                "Artifact": result.get("ARTIFACT"),
                "backUrl": "http%3A%2F%2Fwap.hn.10086.cn%2F",
                "TransactionID": timestamp
            }
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析内容错误{}".format(error), resp)
            return 9, "html_error"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://wap.hn.10086.cn/wap/static/login/Login.html",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        code, key, resp = self.get(url, params=params, headers=headers)
        if code != 0:
            return code, key
        # try:
        #
        # except:
        #     error = traceback.format_exc()
        #     return 9, "html_error"
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
        url = "http://wap.hn.10086.cn/wap/componant/initSendHattedCode"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://wap.hn.10086.cn/wap/static/doBusiness/phoneDetailBill.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        random_str = str(random.random())[:10]
        params = {
            "requestTel": "undefined",
            "pageName": "phoneDetailBill.html",
            "ajaxSubmitType": "post",
            "ajax_randomcode": random_str,
        }
        cookies = {random_str: "0"}
        code, key, resp = self.post(url, headers=headers, params=params, cookies=cookies)
        if code != 0:
            return code, key, ""
        try:
            result = resp.json()
            result_code = str(result.get("resultCode"))
            if result_code == "0":
                return 0, "success", ""
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析短信发送结果失败{}".format(error), resp)
            return 9, "json_error", ""
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
        url = "http://wap.hn.10086.cn/wap/componant/initSmsCodeAndServicePwd"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://wap.hn.10086.cn/wap/static/doBusiness/phoneDetailBill.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        random_str = str(random.random())[:10]
        params = {
            "smsCode": kwargs['sms_code'],
            "servicePwd": "NaN",
            "pageName": "phoneDetailBill.html",
            "ajaxSubmitType": "post",
            "ajax_randomcode": random_str
        }
        code, key, resp = self.get(url, params=params, headers=headers, cookies={random_str: "0"})
        if code != 0:
            return code, key
        try:
            if str(json.loads(resp.text)["resultCode"]) == "0":
                return 0, 'success'
            elif "短信密码错误" in resp.text or '短信密码已失效' in resp.text:
                self.log("crawler", "短信验证码错误", resp)
                return 2, 'verify_error'
            else:
                self.log("crawler", "unknown_error", resp)
                return 9, 'unknown_error'
        except:
            error = traceback.format_exc()
            self.log("crawler", "json_error: "+error, resp)
            return 9, 'json_error'

    def crawl_info(self, **kwargs):
        """
        WAP 没有个人信息
        """
        return 9, "unknown_error", {}

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
        message_list = []
        # def time_transform(time_str,bm='utf-8',str_format="%Y-%m-%d %H:%M:%S"):
        #     #print time_str
        #     time_type = time.strptime(time_str.encode(bm), str_format)
        #     return str(int(time.mktime(time_type)))

        def time_format(time_str, **kwargs):
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

        def structured_data(response, year_month):
            if "-997" in response.text or u'服务调用异常' in response.text or "-998" in response.text:
                # -998  BOSS.APP层出现未知情况，Head和Data均无数据返回!，请确认BOSS.APP服务是否正在重启
                return 9, "website_busy_error", "服务调用异常", []
            try:
                data = json.loads(response.text)
            except:
                error = traceback.format_exc()
                key, level, message, result = "json_error", 9, "数据解析失败{}{}".format(error, response.text), []
                return level, key, message, result
            result = []

            if data.has_key('billVoice'):
                if not data['billVoice'].has_key('result'):
                    key, level, message, result = "unknown_error", 9, "获取详单未知异常\n{}".format(response.text), []
                    return level, key, message, result

                for tr in data['billVoice']['result']:
                    # 本月有详单, 则有该字段(IMSI_NUMBER)
                    if tr.has_key('IMSI_NUMBER'):
                        raw_call_from = tr['RSRV_STR2']
                        call_from_, error = self.formatarea(raw_call_from)
                        if not call_from_:
                            call_from_ = raw_call_from
                            self.log("crawler", "{}-{}".format(error, raw_call_from), "")
                        (
                            call_method, call_from, call_cost,
                            call_duration, call_time, call_tel,
                            call_to, call_type
                        ) = (
                            tr['RSRV_STR3'], call_from_, tr['RSRV_STR8'],
                            tr['CALL_DURATION'], tr['RSRV_STR1'], tr['RSRV_STR4'],
                            "", tr['ROAM_TYPE']
                        )
                        result.append({
                            "call_method": call_method, "call_from": call_from, "call_cost": call_cost,
                            "call_duration": time_format(call_duration), "call_time": self.time_transform(call_time), "call_tel": call_tel,
                            "call_to": call_to, "call_type": call_type, "month": year_month
                        })
                    else:
                        key, level, message, result = "no_call_log", 9, "请求成功, 但返回数据为空"+response.text, []
                        return level, key, message, result
                return 0, 'success', '成功', result
            else:
                key, level, message, result = "unknown_error", 9, "获取详单未知异常\n{}".format(response.text), []
                return level, key, message, result

        temp = BaseCommon().generator_time()
        month_retrys = [(x, self.max_retry) for x in temp]
        time_fee = 0
        full_time = 40.0
        rand_time = random.randint(20, 40) / 10.0
        st_time = time.time()
        crawler_error = 0
        data_list = []
        log_for_retrys = []
        retrys_limit = -4
        while month_retrys:
            month_obj, retrys = month_retrys.pop(0)
            retrys -= 1
            year, month, beginDate, endDate, timestamp = month_obj
            year_month = year + month.zfill(2)
            if retrys < retrys_limit:
                self.log("crawler", "重试完成", "")
                miss_list.append(year_month)
                continue
            random_str = str(random.random())[:10]
            log_for_retrys.append((year_month, retrys, time_fee))
            details_params = {
                "yearMonth": year_month,
                "startDay": beginDate,
                "endDay": endDate,
                "detailBillType": "1001",
                "operType": "QUERY",
                "goodsName": "语音详单查询",
                "goodsId": "10001542",
                "pageName": "phoneDetailBill.html",
                "ajaxSubmitType": "post",
                "ajax_randomcode": random_str,
            }
            url = "http://wap.hn.10086.cn/wap/detailBillQuery/queryDetailBill"
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "Referer": "http://wap.hn.10086.cn/wap/static/doBusiness/phoneDetailBill.html",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
            }
            cookies = {random_str: "0"}

            data = []

            code, key, resp = self.get(url, params=details_params, headers=headers, cookies=cookies)
            now_month = details_params.get("yearMonth")
            if code != 0:
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                else:
                    self.log("crawler", "多次重试失败", "")
                    miss_list.append(now_month)
                continue
            try:
                level, key, message, data = structured_data(resp, year_month)
            except:
                error = traceback.format_exc()
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                else:
                    self.log("crawler", "{}".format(error), resp)
                continue

            if level != 0:
                crawler_error += 1
                if retrys >= 0:
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                elif time_fee < full_time:
                    time.sleep(rand_time)
                    time_fee = time.time() - st_time
                    month_retrys.append((month_obj, retrys))
                else:
                    self.log("crawler", "{}\n{}".format(key, message), resp)
                    if key == "no_call_log":
                        pos_miss_list.append(now_month)
                    miss_list.append(now_month)
                continue
            data_list.extend(data)

        self.log("crawler", "重试记录{}".format(log_for_retrys), "")
        if len(miss_list+pos_miss_list) == 6:

            if crawler_error == 0:
                return 9, 'website_busy_error', [], miss_list, pos_miss_list
            else:
                return 9, 'crawl_error', [], miss_list, pos_miss_list
        return 0, 'success', data_list, miss_list, pos_miss_list

    def time_transform(self, time_str, bm='utf-8', str_format="%Y-%m-%d %H:%M:%S"):
        # print time_str
        time_type = time.strptime(time_str.encode(bm), str_format)
        return str(int(time.mktime(time_type)))

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
        http://www.hn.10086.cn/service/ics/monthBillQuery/queryMonthBill?yearMonth=201703&operType=QUERY&goodsId=10001638&goodsName=%E8%B4%A6%E5%8D%95%E6%9F%A5%E8%AF%A2&ajaxSubmitType=post&ajax_randomcode=0.9345453186608987
        """
        month_fee = []
        today = date.today()
        miss_list = []
        message_list = []
        month_bill_url = "http://wap.hn.10086.cn/wap/monthBillQuery/queryMonthBill?"
        search_month = [x for x in range(0,-6,-1)]
        for each_month in search_month:
            month_fee_data = {}
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d"%(query_date.year, query_date.month)
            random_tmp = str(random.random())
            month_bill_data = {
                "yearMonth":query_month,
                "operType":"QUERY",
                "goodsId":"10001638",
                "pageName": "monthBillQuery.html",
                "goodsName":"账单查询",
                "ajaxSubmitType":"post",
                "ajax_randomcode":random_tmp
            }

            month_bill_url_tmp = month_bill_url+urllib.urlencode(month_bill_data)
            cookies = {random_tmp: "0"}
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "Referer": "http://wap.hn.10086.cn/wap/static/doBusiness/monthBillQuery.html",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            for i in range(self.max_retry):
                code, key, resp = self.post(month_bill_url_tmp, headers=headers, cookies=cookies)
                if code != 0:
                    msg = key
                    continue

                if '系统繁忙，请稍后再试' in resp.text:
                    msg = "website_busy_error"
                    continue
                try:
                    month_bill_res = resp.json()
                    call_bill_list = month_bill_res.get('monthBillList').get('result')
                    if len(call_bill_list) < 8:
                        msg = "no_data"
                        continue
                    month_fee_data = {}
                    month_fee_data['bill_amount'] = call_bill_list[0].get('NEW_DEPOSIT_SPAYFEE', '0.0')
                    month_fee_data['bill_package'] = call_bill_list[-1].get('FEE2', '0.0')
                    month_fee_data['bill_ext_calls'] = call_bill_list[-2].get('FEE2', '0.0')
                    month_fee_data['bill_ext_data'] = call_bill_list[-3].get('FEE2', '0.0')
                    month_fee_data['bill_ext_sms'] = call_bill_list[-4].get('FEE2', '0.0')
                    month_fee_data['bill_zengzhifei'] = call_bill_list[-5].get('FEE2', '0.0')
                    month_fee_data['bill_daishoufei'] = call_bill_list[-6].get('FEE2', '0.0')
                    month_fee_data['bill_qita'] = call_bill_list[-7].get('FEE2', '0.0')
                    month_fee_data = {k: str(float(v)/100) for k, v in month_fee_data.items()}
                    month_fee_data['bill_month'] = query_month
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
                miss_list.append(query_month)
                message_list.append(msg)
        now_month = datetime.datetime.now().strftime("%Y%m")
        now_month in miss_list and miss_list.remove(now_month)
        if len(miss_list) == 5:
            temp_list = map(lambda x: x.count('request_error') or x.count('website_busy_error') or x.count('success') or 0, message_list)
            if temp_list.count(0) == 0:
                return 9, 'website_busy_error', [], miss_list
        return 0, "success", month_fee, miss_list


if __name__ == "__main__":
    c = Crawler()
    USER_ID = "13507439530"
    # USER_PASSWORD = "157350"
    USER_PASSWORD = "135935"

    # self_test
    # USER_ID = "18301495516"
    # USER_PASSWORD = "332266"
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
    # c.send_login_verify_request(tel="18301495516", pin_pwd=USER_PASSWORD)
    # temp = BaseCommon().generator_time()
    # month_retrys = [(x, 3) for x in temp]
    # print month_retrys