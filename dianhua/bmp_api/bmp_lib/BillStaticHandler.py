# _*_ coding:utf-8 _*_

import tornado.web
import ujson
import pymongo
import datetime
import logging
from Constant import ConstantVar, SUtils

logger = logging.getLogger()


class BillStaticHandler(tornado.web.RequestHandler):
    """
    daily report handler
    has get and post method
    same logic with two way
    """
    def validate_parameter(self, d, t, n, s):
        """
        check param ok or not
        :param d: date string like 20180101
        :param t: time string int(time.time()), len is 10
        :param n:nonce not empty
        :param s:sign string not empty
        :return:
        """
        if not n or not s:
            return False
        if SUtils.is_time_str(t) and SUtils.is_date_str(d):
            return True
        else:
            return False


    def get(self):
        """
        http get handler
        """
        try:
            SUtils.init()
            return_val = {
                'data': {},
                'status': ConstantVar.st_other,
                'msg': '',
            }
            logger.info("\n\nget %s", self.request.body)
            param_date = self.get_argument("date", '')
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
                return_val['msg'] = ConstantVar.status_msg[ConstantVar.st_other]
                return_val['status'] = ConstantVar.st_other
                result_str = ujson.encode(return_val, ensure_ascii=False)
                self.write(result_str)
                return
            result = self.deal(param_date)
            return_val['data'] = result
            return_val['status'] = ConstantVar.st_success
            result_str = ujson.encode(return_val, ensure_ascii=False)
            # logger.info("result_str:%s", result_str)
            self.write(result_str)
        except Exception, e:
            logger.error(e)
            return_val['msg'] = ConstantVar.status_msg[ConstantVar.st_other]
            return_val['status'] = ConstantVar.st_other
            result_str = ujson.encode(return_val, ensure_ascii=False)
            self.write(result_str)

    def get_days_before_param(self, para_date):
        """
        :param para_date:
        :return:
        False: first day of month
        True; first day , and yestoday

        """
        logger.info(para_date)
        para_date_obj = datetime.datetime.strptime(para_date, "%Y%m%d")
        first_day = datetime.datetime.strptime("%s01" % (para_date[:-2]), "%Y%m%d")
        yestoday = para_date_obj - datetime.timedelta(days=1)
        if first_day >= yestoday:
            return False, None
        else:
            return True, (first_day.strftime("%Y%m%d"), yestoday.strftime("%Y%m%d"))

    def get_tel_num(self, mongo_handle, para_date):
        """
        :param param_date:
        :param mongo_handle:
        :return form sid_info summary tel_num (unique)
        """
        logger.info(para_date)
        ori_sid_info = mongo_handle[ConstantVar.mongo_db_name][ConstantVar.mongo_db_ori_col]
        ss, es = SUtils.fill_day_with_time(para_date)
        logger.info("%s,%s" , ss, es)
        ori_telnums_data = ori_sid_info.find(
            {"end_time": {'$gte': ss, '$lte': es}},
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

        # get total month before today
        should_deal, dd = self.get_days_before_param(para_date)
        logger.info('%s, %s', should_deal, dd)
        # first day , return
        if not should_deal:
            return cid_tel_data
        first, yestoday = dd
        ss, es = SUtils.fill_day_with_time(first, yestoday)
        ori_telnums_data_dd = ori_sid_info.find(
            {"end_time": {'$gte': ss, '$lte': es}},
            {'cid': 1, 'tel': 1})
        cid_tel_data_dd = {}
        for k in ori_telnums_data_dd:
            cid = k.get('cid', ConstantVar.cid_default_value)
            if cid not in cid_tel_data_dd:
                cid_tel_data_dd[cid] = set()
            tel = k.get('tel', ConstantVar.other_default_value)
            if isinstance(tel, dict) or isinstance(tel, list):
                # tel maybe a dict or list whick can not be add into a set
                logger.info("tel :%s is not a str", tel)
                continue
            cid_tel_data_dd[cid].add(tel)
        for k in cid_tel_data:
            para_date_tel = cid_tel_data[k]
            before_date_tel = cid_tel_data_dd.get(k, set())
            cid_tel_data[k] = para_date_tel - before_date_tel
        return cid_tel_data

    def deal(self, para_date):
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
            one_day_rpt = rpt_collection.find({"rpt_date": para_date})
            # get data realtime data from sid_info
            all_tmp_data = {}
            # maybe multi cid(every cid one result)
            # maybe multi rows return from mongo (sum them)
            for k in one_day_rpt:
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
                        'new_tel_nums': 0,
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
            cid_tel_data_today = self.get_tel_num(mongo_handle, para_date)
            # add tell_num data to finally result
            for k in all_tmp_data:
                all_tmp_data[k]['new_tel_nums'] = len(cid_tel_data_today.get(k, set()))
        except Exception as e:
            logger.error(e)
        finally:
            if mongo_handle:
                mongo_handle.close()
        return all_tmp_data
