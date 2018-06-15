# -*- coding: utf-8 -*-
import json
import pandas as pd
import StringIO
from lxml import etree

from datetime import date
import traceback
import calendar
import time
import sys
import base64
import re
import random
# 这段代码是用于解决中文报错的问题

reload(sys)
sys.setdefaultencoding("utf8")

from dateutil.relativedelta import relativedelta


if __name__ == '__main__':
    sys.path.append('../..')
    sys.path.append('../../..')
    sys.path.append('../../../..')
    from base_crawler import BaseCrawler
    from crawler.china_telecom_tool import login_unity
else:
    from worker.crawler.base_crawler import BaseCrawler
    from worker.crawler.china_telecom_tool import login_unity

from com.yundama import yundama
from setting.yundama_config import YUNDAMA_CODE


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

    def need_parameters(self, **kwargs):
        return ['pin_pwd']

    def get_verify_type(self, **kwargs):
        return ""

    def login(self, **kwargs):
        ProvinceID = '03'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        cookie_url = "http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=02251361"
        code, key, cookie_req = self.get(cookie_url)
        if code != 0:
            return code, key
        # 域名跳转url
        jump_url = 'http://www.189.cn/login/sso/ecs.do?method=linkTo&platNo=10002&toStUrl=http://tj.189.cn/tj/service/bill/feeQueryIndex.action?tab=6&fastcode=02251361&cityCode=tj'
        code, key, resp = self.get(jump_url)
        if code != 0:
            return code, key
        if "window.location='http://tj.189.cn/tj/service/bill/feeQueryIndex.action" in resp.text:
            return 0, "success"

        else:
            self.log('crawler', 'html_error', resp)
            return 9, 'html_error'

    def send_verify_request(self, **kwargs):
        # 开始云打码
        codetype = 1004
        for i in range(self.max_retry):
            url = "http://tj.189.cn/tj/authImg?{}".format(random.random())
            headers = {"Referer": "http://tj.189.cn/tj/service/bill/detailBillQuery2.action"}
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key, ''
            try:
                cid, result = yundama.decode(resp.content, codetype)
            except:
                error = traceback.format_exc()
                self.log("website", "unknown_error云打码异常: " + error, resp)
                return 9, 'website_busy_error', ""
            if cid > 0 and result != "":
                captcha_code = str(result)
            else:
                message = YUNDAMA_CODE.get(str(cid), '').decode('utf-8')
                self.log("website", "website_busy_error:{}".format(message), '')
                return 9, 'website_busy_error', ""
            # 验证打码是否正确
            url = "http://tj.189.cn/tj/checkrand/checkRand.action"
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://tj.189.cn/tj/service/bill/detailBillQuery2.action",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
            data = {"randValue": captcha_code}
            code, key, resp = self.post(url, headers=headers, data=data)
            if code != 0:
                return code, key, ''
            try:
                result = resp.json()
                if result.get('ret') != 0:
                    self.log("crawler", "云打码失败", resp)
                    continue
                break
            except:
                error = traceback.format_exc()
                self.log("crawler", "获取图片验证结果失败".format(error), resp)
        else:
            self.log("crawler", "云打码全部失败", "")
            return 9, "website_busy_error", ""
        verify_type = kwargs.get('verify_type', '')
        if verify_type in ['', 'sms']:
            # 获取短信验证码
            url = "http://tj.189.cn/tj/service/bill/sendRandomSmscode.action"
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": "http://tj.189.cn/tj/service/bill/detailBillQuery2.action"
            }
            data = {
                "randomMode": "2",
                "funcType":	"detail",
                "checkCode": captcha_code
            }
            code, key, resp = self.post(url, headers=headers, data=data)
            if code != 0:
                return code, key, ""
            try:
                result = resp.json()
                flg = result.get("requestFlag", "")
                if flg != "success":
                    self.log("crawler", "获取短信失败", resp)
                    return 9, "send_sms_error", ""
            except:
                error = traceback.format_exc()
                self.log("crawler", "获取短信发送信息失败{}".format(error), resp)
                return 9, "html_error", ""
        image_str = ''
        # 获取图片
        if verify_type in ['', 'captcha']:
            url = "http://tj.189.cn/tj/authImg?{}".format(random.random())
            headers = {"Referer": "http://tj.189.cn/tj/service/bill/detailBillQuery2.action"}
            code, key, resp = self.get(url, headers=headers)
            if code != 0:
                return code, key, ''
            image_str = base64.b64encode(resp.content)
        return 0, 'success', image_str


    def verify(self, **kwargs):
        # 验证图片
        url= "http://tj.189.cn/tj/checkrand/checkRand.action"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://tj.189.cn/tj/service/bill/detailBillQuery2.action"
        }
        data = {"randValue": kwargs['captcha_code']}

        code, key, resp = self.post(url, headers=headers, data=data)
        if code != 0:
            return code, key
        try:
            result = resp.json()
            flg = result.get("ret", "")
            if flg != 0:
                self.log("crawler", "图形验证码不正确", resp)
                return 2, "verify_error"
        except:
            error = traceback.format_exc()
            self.log("crawler", "解析图片验证结果失败{}".format(error), resp)
            return 9, "json_error"

        # 验证短信
        url = "http://tj.189.cn/tj/service/bill/validateRandomcode.action"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://tj.189.cn/tj/service/bill/detailBillQuery2.action"
        }
        data = {
            "sRandomCode": kwargs['sms_code'],
            "randomMode": "1",
            "funcType":	"detail"
        }
        code, key, resp = self.post(url, headers=headers, params=data)
        if code != 0:
            return code, key
        try:
            result = resp.json()
            flg = result.get("requestFlag", "")
            if flg == "success":
                return 0, "success"
            else:
                self.log("crawler", "短信验证码错误", resp)
                return 9, "verify_error"
        except:
            error = traceback.format_exc()
            self.log("crawler", "获取短信验证信息失败{}".format(error), resp)
            return 9, "json_error"

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """

        call_log = []
        crawl_num = 0
        missing_list, possibly_missing_list = [], []
        today = date.today()

        url = 'http://tj.189.cn/tj/exportToExcel'
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://tj.189.cn/tj/service/bill/detailBillQuery2.action"
        }
        page_and_retry = []
        search_month = [x for x in range(0, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year,query_date.month)
            BEGIN_DATE = "%d-%02d-" % (query_date.year, query_date.month) + '01'
            END_DATE = "%d-%02d-" % (query_date.year, query_date.month) + \
                       str(calendar.monthrange(query_date.year, query_date.month)[1])
            params = {
                "pageNo": "-1",
                "pageRecords": "-1",
                "billDetailType": "1",
                "beginTime": BEGIN_DATE,
                "endTime": END_DATE,
                "cardType": "",
                "exporttxttype": "1"
            }
            page_and_retry.append((params, query_month, self.max_retry))

        st_time = time.time()
        et_time = st_time + 30
        log_for_retry_request = []
        while page_and_retry:
            params, m_query_month, m_retry_times = page_and_retry.pop(0)
            log_for_retry_request.append((m_query_month, m_retry_times))
            m_retry_times -= 1
            level = 0
            message = '----'
            code, key, resp = self.get(url, params=params, headers=headers)
            if code == 0:
                if u'抱歉，您没有权限访问此功能或您尚未登录' in resp.text:
                    self.log('webiste', u'抱歉，您没有权限访问此功能或您尚未登录', resp)
                    return 9, "website_busy_error", [], [], []
                key, level, message, result = self.call_log_get(resp, m_query_month, self_tel=kwargs['tel'])
                if level == 0 and result:
                    call_log.extend(result)
                    continue

            now_time = time.time()
            if m_retry_times > 0:
                page_and_retry.append((params, m_query_month, m_retry_times))
                continue
            elif now_time < et_time:
                rand_sleep = random.randint(2, 4)
                if m_retry_times > -10:
                    page_and_retry.append((params, m_query_month, m_retry_times))
                    time.sleep(rand_sleep)
                    continue
            if code == 0 and (level == -1 or not result):
                resp.encoding = 'utf-8'
                self.log('crawler', u'详单为空或未查询到您的详单信息 : 请求的body为excel.', '')
                possibly_missing_list.append(m_query_month)
            else:
                missing_list.append(query_month)
                crawl_num += 1
                # if "NOT_NOTES" != message:
                self.log('crawler', message, '')

        missing_list = list(set(missing_list))
        possibly_missing_list = list(set(possibly_missing_list))
        missing_list.sort(reverse=True)
        possibly_missing_list.sort(reverse=True)
        #
        # print('missing_list:', missing_list)
        # print('possibly_missing_list:', possibly_missing_list)
        # print('call_log:', len(call_log))
        self.log("crawler", "重试记录: {}".format(log_for_retry_request), "")
        if len(missing_list + possibly_missing_list) == 6:
            if crawl_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def call_log_get(self, response, query_month, self_tel):
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
        result = []
        try:
            xls = StringIO.StringIO(response.content)
        except:
            error = traceback.format_exc()
            return 'html_error', 9, '装入buffer失败 ' + error, result
        err = None
        try:
            pd_data = pd.read_excel(xls)
        except:
            error = traceback.format_exc()
            err = True
        finally:
            xls.close()
        if err:
            return 'html_error', 9, '读取Excel失败 ' + error, result
        try:
            for index in pd_data.index[:-1]:
                value_list = pd_data.loc[index].values
                timeArray = time.strptime(value_list[-4], "%Y-%m-%d %H:%M:%S")
                call_time_timeStamp = str(int(time.mktime(timeArray)))
                call_method = value_list[2]
                if call_method == u"主叫":
                    call_tel = str(int(value_list[1]))
                elif call_method == u"被叫":
                    call_tel = str(int(value_list[0]))
                else:
                    self.log("crawler", "意外的呼叫方式  {}".format(call_method), "")
                    call_tel_z = str(int(value_list[1]))
                    call_tel_b = str(int(value_list[0]))
                    call_tel = ''
                    if call_tel_z != self_tel:
                        call_tel = call_tel_z.strip()
                    if call_tel_b != self_tel:
                        call_tel = call_tel_b.strip()
                    if not call_tel:
                        all_info = self.get_all_info(pd_data)
                        self.log("crawler", "无法获取的call_tel: {}".format(all_info), "")
                        # 当发生自己与自己的通话记录, 或者自己与空的通话记录, 都跳过
                        continue

                # raw_call_from = value_list[3].strip()
                raw_call_from = str(value_list[3])
                if raw_call_from =='nan':
                    call_from = ''
                else:
                    call_from, error = self.formatarea(raw_call_from.strip())
                    if not call_from:
                        call_from = raw_call_from
                da = {
                    "call_tel": call_tel,
                    "call_cost": value_list[-1],
                    "call_time": call_time_timeStamp,
                    "call_method": call_method,
                    "call_type": "",
                    "call_from": call_from,
                    "call_to": "",
                    "call_duration": str(int(value_list[-3])),
                    "month": query_month
                }
                result.append(da)
        except:
            error = traceback.format_exc()
            all_info = self.get_all_info(pd_data)
            self.log("crawler", error+all_info, "")
            # 因为在这时, 进行记录没有任何意义, 因为内容被意外编码, 转义, 导致的日志内容无法恢复
            return 'html_error', 9, 'NOT_NOTES', result
        return 'success', 0, 'success', result

    def get_all_info(self, xls):
        try:
            strr_list = []
            for i in xls.iloc[:-1].values:
                # 函数原型: 请由内至外, 由右至左阅读
                # [].append(reduce(exec, map(exec, raw_list)))
                strr_list.append(reduce(lambda x, y: x + "  " + y + "  ",
                                        (map(lambda x: x if isinstance(x, unicode) else str(int(x)), i))))
        except:
            error = traceback.format_exc()
            return "无法按照预期获取数据!!!!!{}".format(error)
        return "\n".join(strr_list)

    def crawl_info(self, **kwargs):
        """
        爬取帳戶資訊
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯个i他誤等級
            message: unicode, 詳細的錯誤信息
            info: dict, 帳戶信息，參考帳戶信息格式
        """
        info_url = 'http://tj.189.cn/tj/service/manage/modifyUserInfo.action?fastcode=02241349&amp;cityCode=tj'
        code, key, response = self.get(info_url)
        if code != 0:
            return code, key, {}
        try:
            html_tree = etree.HTML(response.text)
            full_name = html_tree.xpath('//*[@id="box-1"]/table/tbody/tr[1]/td[1]/text()')
            full_name = full_name[0] if full_name else ''
            id_card = html_tree.xpath('//*[@id="box-1"]/table/tbody/tr[2]/td[1]/text()')
            id_card = id_card[0] if id_card else ''
            open_date = html_tree.xpath('//*[@id="box-1"]/table/tbody/tr[2]/td[2]/text()')
            open_date = open_date[0] if open_date else ''
            address = html_tree.xpath('//*[@id="box-1"]/table/tbody/tr[3]/td[2]/text()')
            address = address[0] if address else ''

            user_info_data = {
                'full_name': full_name,
                'id_card': id_card.strip(),
                'open_date': self.time_format(open_date.strip()),
                'address': address.strip(),
            }
            return 0, "success", user_info_data
        except:
            self.log("crawler", "unknown_error", response)
            return 9, "unknown_error", {}


    def time_format(self, timeoo):
        call_time = re.findall('\d{2}', timeoo)
        call_time_change = call_time[0] + call_time[1] + '-' + call_time[2] + '-' + call_time[
            3] + ' ' + call_time[4] + ':' + call_time[5] + ':' + call_time[6]
        timeArray = time.strptime(call_time_change, "%Y-%m-%d %H:%M:%S")
        call_time_timeStamp = str(int(time.mktime(timeArray)))
        return call_time_timeStamp


    def crawl_phone_bill(self, **kwargs):
        missing_list = []
        crawl_num = 0
        phone_bill = list()
        today = date.today()
        month_bill_url = 'http://tj.189.cn/tj/service/bill/queryBillInfo.action'
        search_month = [x for x in range(-1, -6, -1)]
        for each_month in search_month:
            query_date = today + relativedelta(months=each_month)
            query_month = "%d年%02d月" % (query_date.year, query_date.month)
            month = "%d%02d" % (query_date.year, query_date.month)
            post_data = {
                'billingCycle1': query_month,
                'dataCode': '009'
            }
            for retry in xrange(self.max_retry):
                code, key, resp = self.post(month_bill_url, data=post_data)
                if code != 0:
                    pass
                else:
                    break
            else:
                missing_list.append(month)
                continue
            # with open(missing_month+'.py', 'w')as f:
            #     f.write(resp.text)
            code, key, message, result = self.crawl_month_bill(month, resp.text)
            if code != 0:
                self.log('crawler', message, resp)
                crawl_num += 1
                missing_list.append(month)
                continue
            phone_bill.append(result)
        missing_list = list(set(missing_list))
        missing_list.sort(reverse=True)
        if crawl_num > 0:
            return 9, 'crawl_error', phone_bill, missing_list
        if len(missing_list) == 5:
            return 9, 'website_busy_error', phone_bill, missing_list
        return 0, 'success', phone_bill, missing_list


    def crawl_month_bill(self, query_month, resp):
        month_fee_data = {}
        month_fee_data['bill_month'] = query_month
        month_fee_data['bill_amount'] = ''
        month_fee_data['bill_package'] = ''
        month_fee_data['bill_ext_calls'] = ''
        month_fee_data['bill_ext_data'] = ''
        month_fee_data['bill_ext_sms'] = ''
        month_fee_data['bill_zengzhifei'] = ''
        month_fee_data['bill_daishoufei'] = ''
        month_fee_data['bill_qita'] = ''
        try:
            bill_data = json.loads(resp)
        except:
            error = traceback.format_exc()
            return 9, 'json_error', 'json_error'+error, {}
        try:
            bill_list = bill_data["retInfo"]['list'][0]['acctItems']
            for bill in bill_list:
                if bill['acctItemName'] == '国内语音通信费':
                    month_fee_data['bill_ext_calls'] = bill['acctItemFee']
                elif bill['acctItemName'] == '月基本费':
                    month_fee_data['bill_package'] = bill['acctItemFee']
                elif bill['acctItemName'] == '短信彩信费':
                    month_fee_data['bill_ext_sms'] = bill['acctItemFee']
                else:
                    month_fee_data['bill_qita'] = bill['acctItemFee']
            month_fee_data['bill_amount'] = bill_data["retInfo"]['list'][0]['billFee']
        except:
            error = traceback.format_exc()
            return 9, 'html_error', 'html_error'+error, {}
        return 0, 'success', 'success', month_fee_data




if __name__ == '__main__':
    c = Crawler()

    USER_ID = "18920425979"
    # USER_PASSWORD = "979524"
    USER_PASSWORD = "582414"

    # self_test
    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
