# -*- coding: utf-8 -*-
import hashlib
from lxml import etree

from Crypto.Cipher import AES
import base64
import time

import traceback
import re
import sys
import random
reload(sys)
sys.setdefaultencoding("utf8")
if __name__ == '__main__':
    import sys
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

class Crawler(BaseCrawler):

    def __init__(self, **kwargs):
        super(Crawler,self).__init__(**kwargs)

    def need_parameters(self, **kwargs):
        # return ['pin_pwd', 'captcha_verify']
        return ['pin_pwd']

    def login(self, **kwargs):

        ProvinceID = '10'
        code, key = login_unity(self, ProvinceID, **kwargs)
        if code != 0:
            return code, key

        url = 'http://www.189.cn/dqmh/my189/checkMy189Session.do'
        data = {
            'fastcode': '20000846'
        }
        code, key, resp = self.post(url, data=data)
        if code != 0:
            return code, key

        headers = {
            'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do',
        }
        url = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10010&toStUrl=http://hl.189.cn/service/zzfw.do?method=ywsl&id=10&fastcode=20000846&cityCode=hl'
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key

        final_url = 'http://hl.189.cn/service/zzfw.do?method=ywsl&id=10&fastcode=20000846&cityCode=hl'
        for retry in xrange(self.max_retry):
            code, key, resp = self.get(final_url)
            if code != 0:
                return code, key
            if u'发送随机短信密码' in resp.text:
                return 0, "success"
            else:
                pass
        else:
            self.log('crawler', 'request_error', resp)
            return 9, 'website_busy_error'

    def get_verify_type(self, **kwargs):
        return 'SMS'

    def send_verify_request(self, **kwargs):
        """
        請求發送短信，或是下載圖片，或是同時發送請求
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            image_str: str, Captcha圖片的base64字串, SMS則回空
        """

        send_sms_url = 'http://hl.189.cn/service/userCheck.do'
        params = {'method': 'sendMsg'}
        code, key, resp = self.post(send_sms_url, params=params)
        if code != 0:
            return code, key, ''
        if resp.text == '1':
            return 0, "success", ""
        else:
            self.log('crawler', 'request_error', resp)
            return 9, "request_error", ""

    def verify(self, **kwargs):
        """
        執行二次驗證
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
        """

        check_sms_url = 'http://hl.189.cn/service/zzfw.do'
        check_sms_data = {
            'method': 'checkDX',
            'yzm': kwargs['sms_code']
        }
        code, key, resp = self.post(check_sms_url, data=check_sms_data)
        if code != 0:
            return code, key
        if u'点击取消弹出' in resp.text:
            return 0, "success"
        elif u'验证码错误' in resp.text:
            self.log('crawler', 'verify_error', resp)
            return 2, 'verify_error'
        else:
            self.log("crawler", "unknown_error", resp)
            return 9, "unknown_error"


    def crawl_info(self, **kwargs):
        result = {}
        tel_info_url = 'http://hl.189.cn/service/crm_cust_info_show.do?funcName=custSupport&canAdd2Tool=canAdd2Tool'
        code, key, resp = self.get(tel_info_url)
        if code != 0:
            return code, key, {}
        try:
            selector = etree.HTML(resp.text)
            full_name = selector.xpath('//div[@class="fe-yu-ku"]/table/tr[2]/td[2]/text()')
            if full_name:
                result['full_name'] = full_name[0]
            else:
                result['full_name'] = ""
            result['id_card'] = ''
            address = selector.xpath('//div[@class="fe-yu-ku"]/table/tr[8]/td[2]/span[1]/input/@value')
            if address:
                result['address'] = address[0]
            else:
                result['address'] = ""
            result['open_date'] = ''
        except:
            error = traceback.format_exc()
            self.log('crawler', 'html_error %s' % error, resp)
            return 9, "html_error", {}

        return 0, "success", result

    def crawl_call_log(self, **kwargs):
        """
        爬取詳單
        return
            status_key: str, 狀態碼金鑰，參考status_code
            level: int, 錯誤等級
            message: unicode, 詳細的錯誤信息
            call_log: list, 通信詳單，參考詳單格式
        """
        missing_list = []
        possibly_missing_list = []
        website_num = 0
        crawler_num = 0
        call_log = []
        today = date.today()
        search_month = [x for x in range(-1, -6, -1)]
        this_month = "%d%02d" % (today.year, today.month)

        st_time = time.time()
        et_time = st_time + 3
        end_time = st_time+ 12

        first_page_retry_times  = self.max_retry
        rand_time = random.randint(2,3)

        while True:
            first_page_retry_times -=1
            #查询当月的详单
            key, level, call_log_month, wrong_flag = self.deal_call_log('2', kwargs['tel'], this_month)
            now_time = time.time()
            if level == -1:
                possibly_missing_list.append(this_month)
                break
            elif level != 0:
                if first_page_retry_times >0 :
                    continue
                elif now_time < et_time:
                    time.sleep(random.randint(1,2))
                else:
                    missing_list.append(this_month)
                    if wrong_flag == 'website':
                        website_num += 1
                    elif wrong_flag == 'crawler':
                        crawler_num += 1
                    break
            else:
                call_log.extend(call_log_month)
                break

        # 查询历史详单
        for each_month in search_month:
            month_missing = 0
            query_date = today + relativedelta(months=each_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)

            senc_page_retry_times = self.max_retry
            while True:
                senc_page_retry_times -= 1
                key, level, call_log_history, wrong_flag = self.deal_call_log('1', kwargs['tel'], query_month)
                if level == -1:
                    month_missing += 1
                    possibly_missing_list.append(query_month)
                    break
                elif level != 0:
                    now_time = time.time()
                    if senc_page_retry_times >0:
                        continue
                    elif now_time<end_time:
                        time.sleep(rand_time)
                    else:
                        missing_list.append(query_month)
                        if wrong_flag == 'website':
                            website_num += 1
                        elif wrong_flag == 'crawler':
                            crawler_num += 1
                        break
                else:
                    call_log.extend(call_log_history)
                    break
        missing_list = list(set(missing_list))

        if len(possibly_missing_list + missing_list) == 6:
            if crawler_num > 0:
                return 9, 'crawl_error', call_log, missing_list, possibly_missing_list
            return 9, 'website_busy_error', call_log, missing_list, possibly_missing_list
        return 0, "success", call_log, missing_list, possibly_missing_list

    def deal_call_log(self, selectType, tel, query_month):
        call_log_url = 'http://hl.189.cn/service/cqd/queryDetailList.do?'
        # selectType 为1 表示历史详单，  为2表示当月详单
        call_log_data = {
            'isMobile': '0',
            'seledType': '9',
            'queryType': "",
            'pageSize': '9999',
            'pageNo': '1',
            'flag': '',
            'pflag': '',
            'accountNum': tel + ':2000004',
            'callType': '3',
            'selectType': selectType,
            'detailType': '9',
            'selectedDate': query_month,
            'method': 'queryCQDMain'
        }
        headers = {
            'Referer': 'http://hl.189.cn/service/cqd/detailQueryCondition.do',
        }
        for retry in xrange(self.max_retry):
            code, key, resp = self.get(call_log_url, params=call_log_data, headers=headers)
            if code != 0:
                pass
            else:
                break
        else:
            return key, code, [], 'website'
        if u'没有查找到相关数据' in resp.text:
            self.log('crawler', '没有查找到相关数据', resp)
            return '', -1, '', ''
        else:
            try:
                call_month_log = self.call_log_get(resp.text, query_month)
            except:
                error = traceback.format_exc()
                self.log('crawler', 'html_error : %s' % error, resp)
                return "html_error", 9, [], 'crawler'
            return 'success', 0, call_month_log, ''

    def call_log_get(self, response, query_month):
        call_month_log = []
        selector = etree.HTML(response)
        rows = selector.xpath('//*[@id="tb1"]//tr')
        for i, row in enumerate(rows):
            call_log = {}
            call_log['month'] = query_month
            # 费用
            cost = row.xpath('.//script')
            if len(cost) <= 0:
                continue
            cost = cost[0]
            cost = cost.xpath('string(.)')
            call_cost = int(re.findall('var thMoney = new String\((\d+)\);', cost)[0])
            # 转换单位（元）
            if call_cost % 100 == 0:
                call_cost = call_cost / 100
            else:
                call_cost = round(call_cost / 100, 2)
            call_log['call_cost'] = str(call_cost)
            call_log['call_tel'] = row.xpath('.//td[5]/text()')[0]
            call_log['call_method'] = row.xpath('.//td[4]/text()')[0]
            call_log['call_type'] = row.xpath('.//td[7]/text()')[0]
            # call_log['call_from'] = row.xpath('.//td[3]/text()')[0]

            raw_call_from = row.xpath('.//td[3]/text()')[0].strip()
            call_from, error = self.formatarea(raw_call_from)
            if call_from:
                call_log['call_from'] = call_from
            else:
                # self.log("crawler", "{}  {}".format(error, raw_call_from), "")
                call_log['call_from'] = raw_call_from

            call_duration = row.xpath('.//td[6]/text()')[0]
            time_list = call_duration.split(':')
            call_log['call_duration'] = str(int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2]))
            call_log['call_to'] = ''
            call_time = row.xpath('./td[2]/text()')[0]
            timeArray = time.strptime(call_time, "%Y%m%d%H%M%S")
            call_time_timeStamp = str(int(time.mktime(timeArray)))
            call_log['call_time'] = call_time_timeStamp
            call_month_log.append(call_log)
        return call_month_log

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
        """
        month_fee = []
        missing_list = []
        today = date.today()
        crawler_num = 0
        search_month = [x for x in range(0, -6, -1)]
        month_bill_url = 'http://hl.189.cn/service/billDateChoiceNew.do'
        for query_month in search_month:
            month_fee_data = {}
            query_date = today + relativedelta(months=query_month)
            query_month = "%d%02d" % (query_date.year, query_date.month)
            month_bill_data = {
                'method': 'doSearch',
                'selectDate': query_month
            }
            for retry in xrange(self.max_retry):
                code, key, resp = self.post(month_bill_url, data=month_bill_data)
                if code != 0:
                    pass
                else:
                    break
            else:
                missing_list.append(query_month)
                continue
            if u'对不起，系统忙，请稍后再试！' in resp.text:
                missing_list.append(query_month)
                self.log('website', u'官网繁忙或没有本月账单', resp)
                continue
            try:
                # with open('bill.py','w')as f:
                #     f.write(resp.text)
                month_fee_data['bill_month'] = "%d%02d" % (query_date.year, query_date.month)
                bill_amount = re.findall(r'本期费用合计：(\d*\.?\d+\.\d+)', resp.text.encode('utf8'))
                if not bill_amount:
                    missing_list.append(query_month)
                    continue
                else:
                    month_fee_data['bill_amount'] = bill_amount[0]
                bill_package = str(float(re.findall(r'基本月租费\s+</td>\s+<td class="td5">[\D]+(\d+\.\d+)',
                                    resp.text.encode('utf8'))[0]))

                # 改版前，2017-12-11
                #  bill_package = str(float(re.findall(r'基本月租费\s+</td>\s+<td class="td5">[\D]+(\d+\.\d+)',
                #                                     resp.text.encode('utf8'))[0]) +
                #                                      float(re.findall(r'手机上网月功能费业务可选包\s+</td>\s+<td class="td5">[\D]+(\d+\.\d+)',
                #                                      resp.text.encode('utf8'))[0]))

                month_fee_data['bill_package'] = bill_package
                bill_ext_calls = re.findall(r'国内通话费\s+</td>\s+<td class="td5">\s+(\d+\.\d+)', resp.text.encode('utf8'))
                month_fee_data['bill_ext_calls'] = bill_ext_calls[0] if bill_ext_calls else ''
                bill_ext_data = re.findall(r'手机国内上网费\s+</td>\s+<td class="td5">\s+(\d+\.\d+)',resp.text.encode('utf8'))
                month_fee_data['bill_ext_data'] = bill_ext_data[0] if bill_ext_data else ''
                bill_ext_sms = re.findall(r'短信通信费.*?(\d+\.\d+)',resp.text.encode('utf8'),re.S)
                month_fee_data['bill_ext_sms'] = bill_ext_sms[0] if bill_ext_sms else ''
                month_fee_data['bill_zengzhifei'] = ''
                month_fee_data['bill_daishoufei'] = ''
                month_fee_data['bill_qita'] = ''
            except:
                error = traceback.format_exc()
                self.log('crawler', 'html_error : %s' % error, resp)
                missing_list.append(query_month)
                crawler_num += 1
                continue
            month_fee.append(month_fee_data)
        if len(missing_list) == 6:
            if crawler_num > 0:
                return 9, 'crawl_error', month_fee, missing_list
            return 9, 'website_busy_error', month_fee, missing_list
        today = date.today()
        today_month = "%d%02d" % (today.year, today.month)
        if today_month in missing_list:
            missing_list.remove(today_month)
        return 0, "success", month_fee, missing_list



if __name__ == '__main__':
    c = Crawler()

    # USER_ID = "18182842719"
    # USER_PASSWORD = "917248"
    USER_ID = "15304542694"
    USER_PASSWORD = "133081"

    c.self_test(tel=USER_ID, pin_pwd=USER_PASSWORD)
