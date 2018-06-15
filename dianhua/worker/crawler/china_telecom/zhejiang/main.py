# -*- coding: utf-8 -*-
import time
import traceback
import re
import sys
import math
from lxml import etree
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

from datetime import date
from dateutil.relativedelta import relativedelta
import datetime

class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)

    def need_parameters(self, **kwargs):
        return ['full_name', 'id_card', 'pin_pwd', 'sms_verify']

    def login(self, **kwargs):
        start_url = 'http://www.189.cn/dqmh/my189/initMy189home.do'
        code, key, resp = self.get(url=start_url)
        if code != 0:
            return code, key

        ProvinceID = '12'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        bill_panel_url = 'http://zj.189.cn/shouji/%s/zhanghu/xiangdan/' % kwargs['tel']
        code, key, resp = self.get(url=bill_panel_url)
        if code != 0:
            return code, key
        LOGIN_URL = 'http://login.189.cn/web/login'
        if u'欢迎登录' in resp.text or resp.url == LOGIN_URL:
            self.log('user', 'login_param_error', resp)
            return 1, 'login_param_error'
        # print login_req.text
        return 0, 'success'

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def verify(self, **kwargs):
        today = date.today()
        sms_code = kwargs['sms_code']
        # query_date = today + relativedelta(months=-1)
        today = date.today()
        query_date = today + relativedelta(months=0)
        year_month = "%d%02d" % (query_date.year, query_date.month)

        data = {}
        data['flag'] = 1
        data["cdrCondition.pagenum"] = 1
        # 不要改参数，会导致无法查询数据
        data["cdrCondition.pagesize"] = 100
        data["cdrCondition.productnbr"] = kwargs['tel']
        data["cdrCondition.areaid"] = 571
        data["cdrCondition.cdrlevel"] = ""
        data["cdrCondition.productid"] = "1-G6NMt032856"
        data["cdrCondition.product_servtype"] = "18"
        data["cdrCondition.recievenbr"] = u"移动电话".encode('gbk')
        data["cdrCondition.cdrmonth"] = year_month
        data["cdrCondition.cdrtype"] = "11"
        data["cdrCondition.usernameyanzheng"] = kwargs['full_name'].encode("gbk")
        data["cdrCondition.idyanzheng"] = kwargs['id_card']
        data["cdrCondition.randpsw"] = sms_code

        # ============ PHASE 3 (GET RECORD) ===============

        call_url = 'http://zj.189.cn/zjpr/service/query/query_order.html?menuFlag=1'
        call_headers = {
            'Referer': 'http://zj.189.cn/service/queryorder/'
        }
        code, key, response = self.get(call_url, headers=call_headers)
        if code != 0:
            return code, key

        bill_detail_url = "http://zj.189.cn/zjpr/cdr/getCdrDetail.htm"
        # 验证身份证标示
        flag = True
        for i in range(3):
            code, key, resp = self.post(url=bill_detail_url, data=data)
            if code != 0:
                return code, key

            if u'清单' in resp.text or u'主叫' in resp.text or u'被叫' in resp.text:
                return 0, 'success'
            if u'随机验证码输入有误' in resp.text:
                #print(u"随机验证码输入有误")
                self.log('user', 'verify_error', resp)
                return 2, 'verify_error'

            # 请求姓名和身份证
            id_name_url = 'http://zj.189.cn/zjpr/service/query/cdr.js'
            id_headers = {
                'Referer': 'http://zj.189.cn/zjpr/service/query/query_order.html?menuFlag=1',
            }
            code, key, response = self.get(url=id_name_url, headers=id_headers)
            if code != 0:
                return code, key
            id_card = re.findall("var yzid='(.*)';", response.text)
            name = re.findall("var yzusername='(.*)';", response.text)
            if id_card and id_card[0] != kwargs['id_card']:
                return 9, 'user_id_error'
            if name and name[0] != kwargs['full_name']:
                return 9, 'user_name_error'

            # # flag = False
            # print('id_card:{}'.format(id_card))
            # print('name:{}'.format(name))

            # 如果没有从官网拿到用户姓名和身份证，出现这种情况按照官网繁忙处理。
            if '/zjpr/common/show_error.html?ErrorNo=51001' in resp.text and not name and not id_card:
                # if i == 2:
                self.log('user', u'身份证或者姓名出错', resp)
                return 9, 'user_id_error'
            continue

            # 验证身份证信息，（输入错误身份证也有可能成功，出错后再验证）
            # if flag:

            time.sleep(3)
        else:
            self.log('website', 'website_busy_error',resp)
            return 9, 'website_busy_error'

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片
        return
        status_key: str, 狀態碼金鑰，參考status_code，若無錯誤則為空字串
        level: int, 錯誤等級，一般為9，特殊狀況為1，成功為0
        message: unicode, 詳細的錯誤信息
        image_str: str, Captcha圖片, SMS則回空
        """
        # get_cookies_url = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10012&toStUrl=http://zj.189.cn/zjpr/service/query/query_order.html?menuFlag=1&fastcode=20000285&cityCode=zj"
        get_cookies_url = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10012&toStUrl=http://zj.189.cn/service/queryorder/"

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.189.cn/dqmh/my189/initMy189home.do"
        }
        code, key, resp = self.get(get_cookies_url, headers=headers)
        if code != 0:
            return code, key, ""

        headers = {
            'Referer':resp.url
        }
        # 设置cookies
        url = 'http://zj.189.cn/service/queryorder/'
        code, key, resp = self.get(get_cookies_url, headers=headers)
        if code != 0:
            return code, key, ""

        sms_url = "http://zj.189.cn/bfapp/buffalo/VCodeOperation"
        headers = {
            "Content-Type": "text/xml;charset=UTF-8",
            "Accept": "*/*",
            "Referer": "http://zj.189.cn/zjpr/service/query/query_order.html?menuFlag=1&fastcode=20000285&cityCode=zj"
        }
        data = "<buffalo-call>\n" + "<method>SendVCodeByNbr</method>\n" + "<string>{}</string>\n".format(kwargs['tel']) + "</buffalo-call>"
        code, key, resp = self.post(sms_url, data=data, headers=headers)
        if code != 0:
            return code, key, ""
        if u'成功' in resp.text:
            return 0, "success", ""
        else:
            self.log("crawler", 'unknown_error', resp)
            return 9, "unknown_error", ""


    def get_data(self, html, year_month):
        # <script>formateC("2017-07-04 11:35:00","","num1")</script>
        if "ErrorNo=51001" in html or "ErrorNo=61001" in html or "ErrorNo=61006" in html or "ErrorNo=61007" in html or "ErrorNo=61007" in html or "ErrorNo=61010" in html or "ErrorNo=61012" in html:
            # 51001 没有该月详单
            # 61001/6/7/8/10/12 系统异常; 系统繁忙; 插入本地表异常; 查询不到;
            return 0, 'success', 'no_data'

        html = html.replace("</span></td>", "</span></td><tr>")
        # print html
        et = etree.HTML(html)
        er = et.xpath("//div[@id='Pzone_details_content_2']/table/tr")
        data_list = []

        funstr1 = "def funcFmtTime(num_str):\n    return num_str\n"
        funstr2 = "def empsub(type_str):\n    return type_str\n"
        funstr3 = "def getbF(num_str):\n    num = float(num_str)\n    return num/1000\n"
        funstr4 = "def getbFlow2(stt):\n    return 'beizhu'\n"
        funstr5 = "def empsub2(emp):\n     return emp\n"
        funstr = funstr1 + funstr2 + funstr3 + funstr4 + funstr5
        
        for i in er:
            base_info_list = i.xpath("td/text()")
            js_info_list = i.xpath("td/script/text()")
            if js_info_list:
                """
                |`call_tel` | string | 18202541892 | 电话号码 |
                | `call_cost` | string | 0.00 | 通话费用 |
                | `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
                | `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
                | `call_type` | string | 本地 | 通话类型（本地, 长途） |
                | `call_from` | string | 北京市 | 本机通话地 |
                | `call_to` | string | 长沙市 | 对方归属地 |
                | `call_duration` | integer | 300 | 通话时长(秒),
                """
                call_log_data = {}
                if len(base_info_list[0]) < 3:
                    continue
                call_log_data['call_tel'] = base_info_list[0]
                call_log_data['call_method'] = base_info_list[1]
                call_log_data['call_time'] = self.time_transform(base_info_list[2])
                # call_log_data['call_from'] = base_info_list[3]

                raw_call_from = base_info_list[3].strip()
                call_from, error = self.formatarea(raw_call_from)
                if call_from:
                    call_log_data['call_from'] = call_from
                else:
                    call_log_data['call_from'] = raw_call_from

                str_list = []
                result = ""
                for k in js_info_list:
                    # print re.findall(r"\"(.*?)\"", k)
                    try:
                        exec funstr + "\nresult = " + k.strip()
                        str_list.append(result)
                    except:
                        error = traceback.format_exc()
                        return 9, "exec 执行出错!", error
                call_log_data['call_type'] = str(str_list[1])
                call_log_data['call_duration'] = str(str_list[0])
                call_log_data['call_cost'] = str(str_list[-2])
                call_log_data['call_to'] = ''
                call_log_data['month'] = year_month
                data_list.append(call_log_data)
        return 0, "success", data_list

    def time_transform(self, time_str, str_format="%Y-%m-%d %H:%M:%S"):
        time_type = time.strptime(time_str, str_format)
        return str(int(time.mktime(time_type)))

    def crawl_call_log(self, **kwargs):
        today = date.today()
        sms_code = kwargs['sms_code']
        records = []
        delta_months = [i for i in range(0, -6, -1)]

        # 缺失月份
        missing_month_list = []
        # 可能缺失月份。
        possibly_missing_list = []
        # 部分缺失列表
        part_missing_list = []
        # 爬虫错误记录
        crawl_error_num = 0

        log_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://zj.189.cn/zjpr/cdr/getCdrDetailInput.htm'
        }
        bill_detail_url = "http://zj.189.cn/zjpr/cdr/getCdrDetail.htm"
        for delta_month in delta_months:
            query_date = today + relativedelta(months=delta_month)
            year_month ="%d%02d" % (query_date.year, query_date.month)
            data = {}
            data['flag'] = 1
            data["cdrCondition.pagenum"] = 1
            # 不能改参数，改参数会导致报错
            data["cdrCondition.pagesize"] = 100
            data["cdrCondition.productnbr"] = kwargs['tel']
            data["cdrCondition.areaid"] = 571
            data["cdrCondition.cdrlevel"] = ""
            data["cdrCondition.productid"] = "1-G6NMt032856"
            data["cdrCondition.product_servtype"] = "18"
            data["cdrCondition.recievenbr"] = u"移动电话".encode('gbk')
            data["cdrCondition.cdrmonth"] = year_month
            data["cdrCondition.cdrtype"] = "11"
            data["cdrCondition.usernameyanzheng"] = kwargs['full_name'].encode("gbk")
            data["cdrCondition.idyanzheng"] = kwargs['id_card']
            data["cdrCondition.randpsw"] = sms_code

            missing_flag = False
            message = ""
            for retry in xrange(self.max_retry):
                month_data = []
                code, key, resp = self.post(url=bill_detail_url, headers=log_header, data=data)
                if code != 0:
                    missing_flag = True
                    message = "network_request_error"
                    continue
                # print resp.text
                if u'您好，您输入的证件号码信息有误！' in resp.text:
                    self.log('user', 'user_id_error', resp)
                    return 1, 'user_id_error', [], [], []
                elif u'您好，您输入的姓名信息有误！' in resp.text:
                    self.log('user', 'user_name_error', resp)
                    return 1, 'user_name_error', [], [], []
                if u'出错提示信息' in resp.text or 'location.href' in resp.text or 'window.alert' in resp.text:
                    missing_flag = False
                    # if "ErrorNo=51001" in resp.text or "ErrorNo=61001" in resp.text or "ErrorNo=61006" in resp.text or "ErrorNo=61007" in resp.text or "ErrorNo=61007" in resp.text or "ErrorNo=61010" in resp.text or "ErrorNo=61012" in resp.text:
                    #     pass
                    # else:
                    #     crawl_error_num += 1
                    continue

                # 获取第一页数据
                try:
                    code, key, call_log = self.get_data(resp.text, year_month)
                    if code != 0:
                        if call_log == 'no_data':
                            message = "no_data"
                            missing_flag = True
                            self.log("crawler", '未知原因导致无数据', resp)
                        else:
                            message = "{}{}".format(key, call_log)
                            missing_flag = True
                            self.log("crawler", '{}{}'.format(key, call_log), resp)
                        continue
                    else:
                        if call_log == 'no_data':
                            missing_flag = False
                            continue
                        if call_log:
                            month_data.extend(call_log)
                        else:
                            self.log("crawler", '未知原因导致无数据', resp)
                except:
                    error = traceback.format_exc()
                    self.log('crawler', 'html_error:{}'.format(error), resp)
                    crawl_error_num += 1
                    continue

                # 判断是否需要分页
                all_notes, one_page_note_num, now_page = 0, 0, 0
                try:
                    page_info = re.search(r'initPagenation\((\d*,\d*,\d*)\)', resp.text)
                    if page_info:
                        all_notes, one_page_note_num, now_page = map(float, page_info.group(1).split(','))
                    break
                except:
                    error = traceback.format_exc()
                    self.log("crawler", '获取页面信息错误', resp)
                    crawl_error_num += 1
                    missing_flag = False
                    continue
            else:
                if missing_flag:
                    crawl_error_num += 1
                    missing_month_list.append(year_month)
                else:
                    self.log('crawler', '没有详单记录', resp)
                    possibly_missing_list.append(year_month)
                continue

            if all_notes <= 100:
                # 获取第一页, 并无后续分页, 当前月完成
                if month_data:
                    records.extend(month_data)
                else:
                    self.log('crawler', '没有详单记录', resp)
                    possibly_missing_list.append(year_month)
                continue

            page_list = list(range(2, int(math.ceil(all_notes / one_page_note_num)) + 1))
            page_and_retry = [(page, self.max_retry) for page in page_list]

            # for i in range(2, int(math.ceil(all_notes / one_page_note_num)) + 1):
            while page_and_retry:
                page, retry_times = page_and_retry.pop(0)
                data = {
                    "cdrCondition.pagenum": "{}".format(page),
                    "cdrCondition.productnbr": kwargs['tel'],
                    "countValue": "0",
                    "tiaozhuan": "1",
                    "cdrCondition.productid": "1-G6NMt032856",
                    "cdrCondition.areaid": "571",
                    "cdrCondition.cdrtype": "11",
                    "cdrCondition.cdrmonth": year_month,
                    "cdrCondition.numtype": "2",
                    "cdrCondition.cdrlevel": "1",
                    "cdrCondition.randpsw": sms_code,
                    "cdrCondition.product_servtype": "18",
                    "cdrCondition.recievenbr": u"移动电话".encode('gbk'),
                    "username": '',
                    "idcard": '',
                    "flag": '1'
                }
                code, key, resp = self.post(bill_detail_url, data=data, headers=log_header)
                if code != 0:
                    retry_times -= 1
                    if retry_times > 0:
                        page_and_retry.append((page, retry_times))
                    else:
                        message = "network_request_error"
                        missing_flag = False
                        self.log("crawler", 'network_request_error', resp)
                    continue
                # print resp.text
                try:
                    code, key, data_list = self.get_data(resp.text, year_month)
                    if code != 0:
                        retry_times -= 1
                        if retry_times > 0:
                            page_and_retry.append((page, retry_times))
                        else:
                            self.log("crawler", "{}{}".format(key, data_list), resp)
                            crawl_error_num += 1
                            part_missing_list.append(year_month)
                            missing_flag = False
                    else:
                        if data_list == "no_data":
                            retry_times -= 1
                            if retry_times > 0:
                                page_and_retry.append((page, retry_times))
                            else:
                                missing_flag = False
                                part_missing_list.append(year_month)
                            continue
                        if data_list:
                            month_data.extend(data_list)
                        else:
                            retry_times -= 1
                            if retry_times > 0:
                                page_and_retry.append((page, retry_times))
                            else:
                                missing_flag = False
                                part_missing_list.append(year_month)
                                self.log("crawler", "未知原因导致无数据", resp)
                except:
                    error = traceback.format_exc()
                    self.log("crawler", '未知异常{}'.format(error), resp)
                    missing_flag = False
            records.extend(month_data)
            # break



        def set_miss_list(missing_month_list, possibly_missing_list, part_missing_month_list):
            part_set = set(part_missing_month_list)
            missing_set = set(missing_month_list)
            possibly_set = set(possibly_missing_list)

            possibly_set = possibly_set - part_set - missing_set
            missing_set = missing_set - part_set

            part_missing_month_list = list(part_set)
            part_missing_month_list.sort(reverse=True)

            missing_month_list = list(missing_set)
            missing_month_list.sort(reverse=True)

            possibly_missing_list = list(possibly_set)
            possibly_missing_list.sort(reverse=True)
            return missing_month_list, possibly_missing_list, part_missing_month_list

        missing_month_list, possibly_missing_list, part_missing_list = set_miss_list(missing_month_list, possibly_missing_list, part_missing_list)
        self.log("crawler", "缺失: {}, 可能缺失: {}, 部分缺失: {}".format(missing_month_list, possibly_missing_list, part_missing_list), "")
        if len(missing_month_list + possibly_missing_list) == 6:
            if crawl_error_num > 0:
                return 9, 'crawl_error', [], missing_month_list, possibly_missing_list, part_missing_list
            return 9, 'website_busy_error', [], missing_month_list, possibly_missing_list, part_missing_list
        return 0, 'success', records, missing_month_list, possibly_missing_list, part_missing_list

    def crawl_info(self, **kwargs):
        info_url = 'http://zj.189.cn/shouji/' + kwargs['tel'] + '/bangzhu/ziliaoxg/'
        headers = {'Referer': 'http://zj.189.cn/shouji/' + kwargs['tel']}
        code, key, resp = self.get(info_url, headers=headers)
        if code != 0:
            return code, key, {}
        url = "http://zj.189.cn/bfapp/buffalo/demoService"
        code, key, resp_id = self.post(url, data="<buffalo-call>\n<method>getAllProductWithCustId_D</method>\n</buffalo-call>", headers=headers)
        if code != 0:
            return code, key, {}
        name = ""
        id_card = ""
        try:
            name = re.findall(r"cust_name</string><string>(.*?)</string>", resp_id.text)[0]
            id_card = re.findall(r"cust_reg_nbr</string><string>(.*?)</string>", resp_id.text)[0]
        except:
            self.log("crawler", "获取身份信息失败", resp_id)
            pass
        try:
            selector = etree.HTML(resp.text)
            address = selector.xpath('//*[@id="saddress"]/@value')
            result = {}
            result['full_name'] = name
            result['id_card'] = id_card
            result['open_date'] = ''
            result['address'] = address[0] if address else ''
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error:{}'.format(error), resp)
            return 9, 'html_error', {}

        '''
        TODO: 没有身分证号和入网时间
        result['id_card'] = ''
        result['open_date'] = ''
        '''
        return 0, 'success', result

    def get_year_month(self, number):
        month_list = []
        for each_month in xrange(-0, -number, -1):
            today = datetime.date.today()
            query_date = today + relativedelta(months=each_month)
            month_list.append("%d%02d" % (query_date.year, query_date.month))
        return month_list

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
        http://zj.189.cn/zjpr/bill/getBillDetail.htm?pr_billDomain.bill_month=201703&pr_billDomain.product_id=12863726&pr_billDomain.query_type=1&pr_billDomain.bill_type=0&flag=htzd
        """
        # 缺失月份
        missing_month_list = []
        product_id_url = "http://zj.189.cn/zjpr/service/query/query_bill.html?menuFlag=1"
        for item in range(self.max_retry):
            code, key, resp = self.get(product_id_url)
            if code != 0 and item == self.max_retry-1:
                missing_month_list = self.get_year_month(6)
                return 9, 'website_busy_error', [], missing_month_list
            try:
                product_id = re.findall(r'tabShow\(0,\d*,(\d*),0\)', resp.text)[0]
                break
            except:
                if item == self.max_retry-1:
                    missing_month_list = self.get_year_month(6)
                    error = traceback.format_exc()
                    message = 'param_error:{}'.format(error)
                    self.log('crawler', message, resp)
                    # return 0, 'success', [], missing_month_list
                    if 'location.href' in resp.text:
                        return 9, 'website_busy_error', [], missing_month_list
                    return 9, 'crawl_error', [], missing_month_list
                else:
                    continue

        crawl_error_num = 0
        month_fee = []
        today = date.today()
        month_bill_url = "http://zj.189.cn/zjpr/bill/getBillDetail.htm"
        search_month = [x for x in range(-1, -6, -1)]
        for each_month in search_month:
            month_fee_data = {}
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            month_bill_data = {
                "pr_billDomain.bill_month": query_month,
                "pr_billDomain.product_id": product_id,
                "pr_billDomain.query_type": '1',
                "pr_billDomain.bill_type": '0',
                "flag": ''
            }
            for item in range(self.max_retry):
                code, key, resp = self.get(month_bill_url, params=month_bill_data)
                if code == 0:
                    break
            else:
                missing_month_list.append(query_month)
                continue
            try:
                month_fee_data = {}
                month_fee_data['bill_month'] = query_month
                if "location.href" in resp.text:
                    self.log('crawler', '没有账单记录', resp)
                    missing_month_list.append(query_month)
                    continue
                else:
                    # with open('test{}.py'.format(query_month), 'w') as fp:
                    #     fp.write(month_bill_req.text)
                    bill_amount = re.findall(r'本项小计.*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    if not bill_amount:
                        self.log('crawler', '没有账单记录', resp)
                        missing_month_list.append(query_month)
                        continue
                    bill_ext_calls = re.findall(r'省际漫游.*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    bill_ext_calls = bill_ext_calls[0] if bill_ext_calls else ''
                    bill_package = re.search(u'手机上网包月费.*?(\d+\.\d+)', resp.text)
                    bill_ext_sms = re.findall(r'.*短信.*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    bill_ext_sms = bill_ext_sms[0] if bill_ext_sms else ''
                    bill_zengzhifei = re.findall(r'来电显示功能费.*?(\d*\.\d{2})', resp.text.encode('utf-8'))
                    bill_zengzhifei = bill_zengzhifei[0] if bill_zengzhifei else ''
                    # bill_youhuifei = re.findall(r'上网使用费优惠.*?(\d*\.\d{2})',month_bill_req.text.encode('utf-8'))
                    # if not bill_youhuifei:
                    #     bill_youhuifei = ''
                    month_fee_data['bill_amount'] = bill_amount[0]
                    month_fee_data['bill_package'] = str(bill_package.group(1)) if bill_package else ''
                    month_fee_data['bill_ext_calls'] = bill_ext_calls
                    month_fee_data['bill_ext_data'] = ''
                    month_fee_data['bill_ext_sms'] = bill_ext_sms
                    month_fee_data['bill_zengzhifei'] = bill_zengzhifei
                    month_fee_data['bill_daishoufei'] = ''
                    month_fee_data['bill_qita'] = ''
                    month_fee.append(month_fee_data)
            except:
                error = traceback.format_exc()
                self.log('crawler', 'json_error:{}'.format(error), resp)
                crawl_error_num += 1
                missing_month_list.append(query_month)
                # return 9, "json_error", []
                continue

        if len(missing_month_list) == 6:
            if crawl_error_num > 0:
                return 9, 'crawl_error', [], missing_month_list
            return 9, 'website_busy_error', [], missing_month_list
        return 0, "success", month_fee, missing_month_list

if __name__ == '__main__':
    c = Crawler()
    USER_ID = "18167100488"
    USER_PASSWORD = "945812"
    FULL_NAME = u"毛羽建"
    # FULL_NAME = u"张紫恒0"
    ID_CARD = '330225198112260052'
    # ID_CARD = '411081199102158009'
    # self_test

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD, id_card=ID_CARD, full_name=FULL_NAME)
    # print aes_encrypt(USER_PASSWORD)
