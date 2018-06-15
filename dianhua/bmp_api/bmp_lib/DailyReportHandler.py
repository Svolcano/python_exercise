# _*_ coding:utf-8 _*_

import tornado.web
import ujson
import pymongo
import datetime
import time
import logging
from Constant import ConstantVar, SUtils

logger = logging.getLogger()

class DailyReportHandler(tornado.web.RequestHandler):
    """
    daily report handler
    has get and post method
    same logic with two way
    """
    def validate_parameter(self, d, t, n, s):
        '''
        :return: check input paramter ok or not
        d:date ,string
        t: time ,used to calculate signed string
        m: nonce not ''
        s; sign string not ''
        '''
        if not s or not n:
            return False
        if SUtils.is_date_str(d) and SUtils.is_time_str(t):
            return True
        else:
            return False

    def get(self):
        """
        http get handler
        """
        try:
            return_val = {
                'data': {},
                'status': ConstantVar.st_other,
                'msg': '',
            }
            SUtils.init()
            logger.info("\n\nget: %s", self.request.body)
            param_date = self.get_argument("date", '')
            param_channel = self.get_argument('channel', '')
            param_time = self.get_argument("t", '')
            param_nonce = self.get_argument("n", '')
            param_sign = self.get_argument('s', '')
            be_ok = self.validate_parameter(param_date, param_time, param_nonce, param_sign)
            if not be_ok:
                return_val['msg'] = ConstantVar.status_msg[ConstantVar.st_param_error]
                return_val['status'] = ConstantVar.st_param_error
                result_str = ujson.encode(return_val, ensure_ascii=False)
                self.write(result_str)
                return
            try:
                be, desc = SUtils.check_sign(param_time, param_nonce, param_sign)
                if not be:
                    return_val['msg'] = ConstantVar.status_msg[ConstantVar.st_access_deny]
                    return_val['status'] = ConstantVar.st_access_deny
                    result_str = ujson.encode(return_val, ensure_ascii=False)
                    self.write(result_str)
                    return
            except Exception as e:
                logger.error(e)
                return_val['status'] = ConstantVar.st_other
                return_val['msg'] = ConstantVar.status_msg[ConstantVar.st_other]
                result_str = ujson.encode(return_val, ensure_ascii=False)
                self.write(result_str)
                return
            logger.info(param_date)
            result = self.deal(param_date, param_channel)
            return_val['data'] = result
            return_val['status'] = ConstantVar.st_success
            result_str = ujson.encode(return_val, ensure_ascii=False)
            self.write(result_str)
        except Exception as e:
            logger.error(e)
            return_val['status'] = ConstantVar.st_other
            return_val['msg'] = ConstantVar.status_msg[ConstantVar.st_other]
            result_str = ujson.encode(return_val, ensure_ascii=False)
            self.write(result_str)

    def get_tel_num_oneday(self, mongo_handle, para_date, param_channel):
        """
        :param param_date:
        :param mongo_handle:
        :return form sid_info summary tel_num (unique)
        """
        logger.info(para_date)
        ori_sid_info = mongo_handle[ConstantVar.mongo_db_name][ConstantVar.mongo_db_ori_col]
        para_date_timstamp_start = time.mktime(
            datetime.datetime.strptime(para_date + "00:00:00", "%Y%m%d%H:%M:%S").timetuple())
        para_date_timstamp_end = time.mktime(
            datetime.datetime.strptime(para_date + "23:59:59", "%Y%m%d%H:%M:%S").timetuple())
        condition = {
            "end_time": {'$gte': para_date_timstamp_start, '$lte': para_date_timstamp_end},
        }
        if param_channel:
            condition['crawler_channel'] = param_channel
        ori_telnums_data = ori_sid_info.find(
            condition,
            {'cid': 1, 'tel': 1})
        # get realtime data from sid_info
        cid_tel_data = {}
        for k in ori_telnums_data:
            cid = k.get('cid', ConstantVar.cid_default_value)
            if cid not in cid_tel_data:
                cid_tel_data[cid] = set()
            tel = k.get('tel', ConstantVar.other_default_value)
            if isinstance(tel, dict) or isinstance(tel, list):
                # tel maybe a dict or list whick can not be add into a set
                logger.info("tel :%s is not a str", tel)
                continue
            cid_tel_data[cid].add(tel)
        return cid_tel_data

    def get_yestoday(self, today):
        """
        :param today like 20180102:
        :return yestoday like 20180101 (str):
        """
        today = datetime.datetime.strptime(today, "%Y%m%d")
        yestoday = today - datetime.timedelta(days=1)
        yestoday_str = yestoday.strftime("%Y%m%d")
        logger.info("%s, %s", today, yestoday_str)
        return yestoday_str

    def deal(self, para_date, param_channel):
        """
        :param para_date:
        :return summarize data contail key finally_require_keys
        finally_require_keys = ['cid', 'total_nums', 'authen_nums', 'crawl_nums', 'report_nums',
                    'tel_nums', 'authen_pct', 'crawl_pct', 'report_pct', 'log_loss_pct',
                    'tel_num_diff']
        """
        logger.info(para_date)
        mongo_handle = None
        try:
            # get data from mongodb
            # get summarize data from rpt table
            mongo_handle = pymongo.MongoClient(ConstantVar.mongo_db_host, ConstantVar.mongo_db_port)
            rpt_collection = mongo_handle[ConstantVar.mongo_db_name][ConstantVar.mongo_db_rpt_col]
            condition = {
                "rpt_date": para_date,
            }
            if param_channel:
                condition['crawler_channel'] = param_channel
            one_day_rpt = rpt_collection.find(condition)
            # get data realtime data from sid_info
            all_tmp_data = {}
            # maybe multi cid(every cid one result)
            # maybe multi rows return from mongo (sum them)
            for k in one_day_rpt:
                # in sid_info_data_rpt cid's type is int32, but sid_info it's type is string
                cid = k.get('cid', ConstantVar.cid_default_value)
                cid = str(cid).decode('utf8')
                if cid not in all_tmp_data:
                    all_tmp_data[cid] = {
                        'total_nums': k.get('total_nums', 0),
                        'authen_nums': k.get('authen_nums', 0),
                        'crawl_nums': k.get('crawl_nums', 0),
                        'report_nums': k.get('report_nums', 0),
                        'final_nums': k.get('final_nums', 0),
                        'call_log_intact_nums': k.get('call_log_intact_nums', 0),
                        'bill_intact_nums': k.get('bill_intact_nums', 0),
                        'cid': cid,
                        'date': para_date,
                        'tel_nums': 0,
                        'tel_num_diff': 0,
                        'log_loss_pct': 0,
                        'bill_loss_pct': 0,
                    }
                else:
                    all_tmp_data[cid]['total_nums'] += k.get('total_nums', 0)
                    all_tmp_data[cid]['authen_nums'] += k.get('authen_nums', 0)
                    all_tmp_data[cid]['crawl_nums'] += k.get('crawl_nums', 0)
                    all_tmp_data[cid]['report_nums'] += k.get('report_nums', 0)
                    all_tmp_data[cid]['call_log_intact_nums'] += k.get('call_log_intact_nums', 0)
                    all_tmp_data[cid]['bill_intact_nums'] += k.get('bill_intact_nums', 0)
                    all_tmp_data[cid]['final_nums'] += k.get('final_nums', 0)
            # calc all pct
            for k in all_tmp_data:
                v = all_tmp_data[k]
                try:
                    if v['total_nums'] == 0:
                        v['authen_pct'] = 0
                    else:
                        v['authen_pct'] = float(v['authen_nums']) / v['total_nums']

                    if v['authen_nums'] == 0:
                        v['crawl_pct'] = 0
                    else:
                        v['crawl_pct'] = float(v['crawl_nums']) / v['authen_nums']

                    if v['crawl_nums'] == 0:
                        v['report_pct'] = 0
                    else:
                        v['report_pct'] = float(v['report_nums']) / v['crawl_nums']

                    if v['final_nums'] == 0:
                        v['log_loss_pct'] = 0
                        v['bill_loss_pct'] = 0
                    else:
                        v['log_loss_pct'] = 1 - float(v['call_log_intact_nums']) / v['final_nums']
                        v['bill_loss_pct'] = 1 - float(v['bill_intact_nums']) / v['final_nums']
                except Exception as e:
                    logger.error(e)
            # get tel_num
            cid_tel_data_today = self.get_tel_num_oneday(mongo_handle, para_date, param_channel)
            logger.info(cid_tel_data_today)
            yestoday = self.get_yestoday(para_date)
            logger.info(yestoday)
            cid_tel_data_yestoday = self.get_tel_num_oneday(mongo_handle, yestoday, param_channel)
            logger.info(cid_tel_data_yestoday)
            # add tell_num data to finally result
            for k in all_tmp_data:
                today_num = len(cid_tel_data_today.get(k, set()))
                yesterday_num = len(cid_tel_data_yestoday.get(k, set()))
                all_tmp_data[k]['tel_nums'] = today_num
                all_tmp_data[k]['tel_num_diff'] = today_num - yesterday_num
        except Exception as e:
            logger.error(e)
        finally:
            if mongo_handle:
                mongo_handle.close()
        return all_tmp_data
