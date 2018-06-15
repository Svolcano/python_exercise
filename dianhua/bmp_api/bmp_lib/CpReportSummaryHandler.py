# _*_ coding:utf-8 _*_

import tornado.web
import ujson
import pymongo
import datetime
import time
import logging
from Constant import ConstantVar, SUtils

logger = logging.getLogger()

class CpReportSummaryHandler(tornado.web.RequestHandler):
    """
    daily report handler
    post method
    """
    def validate_parameter(self, st, et, t, cids, n, s):
        """
        :param st: start date
        :param et: end date
        :param t:  time len is 10
        :param cids: [123,12] list string
        :param n: nonce
        :param s: signed string
        :return: True or False
        """
        if not n or not s:
            return False
        if not SUtils.is_time_str(t):
            return False
        if st:
            if not SUtils.is_date_str(st):
                return False
        if et:
            if not SUtils.is_date_str(et):
                return False
        if cids:
            try:
                tl = eval(cids)
                if not isinstance(tl, list):
                    return False
            except Exception as e:
                return False
        return True

    def post(self):
        """
        : http post handler:
        """
        try:
            SUtils.init()
            return_val = {
                'data': {},
                'status': ConstantVar.st_other,
                'msg': '',
            }
            logger.info("\n\npost: %s", self.request.body)
            param_time = self.get_argument("t", '')
            param_nonce = self.get_argument("n", '')
            param_sign = self.get_argument('s', '')
            para_start_date = self.get_argument('start_date', '')
            para_end_date = self.get_argument('end_date', '')
            cids_list = self.get_argument('cids', '')
            crawler_channel = self.get_argument('crawler_channel', '')
            telecom = self.get_argument('telecom', '')
            province = self.get_argument('province', '')
            be_ok = self.validate_parameter(para_start_date, para_end_date, param_time, cids_list, param_nonce,
                                            param_sign)
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
            if cids_list:
                cids_list = eval(cids_list)
            # deal
            result = self.deal(para_start_date, para_end_date, cids_list, telecom, province, crawler_channel)
            # json obj 2 str
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

    def get_tel_num(self, mongo_handle, condition):
        """
        :param param_date:
        :param mongo_handle:
        :return form sid_info summary tel_num (unique)
        """
        logger.info(condition)
        ori_sid_info = mongo_handle[ConstantVar.mongo_db_name][ConstantVar.mongo_db_ori_col]
        if 'rpt_date' in condition:
            v = condition['rpt_date']
            if '$gte' in v:
                para_date_timstamp_start = time.mktime(
                    datetime.datetime.strptime(v['$gte'] + "00:00:00", "%Y%m%d%H:%M:%S").timetuple())
                v['$gte'] = para_date_timstamp_start
            if '$lte' in v:
                para_date_timstamp_end = time.mktime(
                    datetime.datetime.strptime(v['$lte'] + "23:59:59", "%Y%m%d%H:%M:%S").timetuple())
                v['$lte'] = para_date_timstamp_end
            condition['end_time'] = v
            del condition['rpt_date']
        if 'cid' in condition:
            # in [sid_info]  cid is a string , should be utf8 string
            v = condition['cid']
            condition['cid'] = [str(i).decode('utf8') for i in v]
        logger.info(condition)
        ori_telnums_data = ori_sid_info.find(condition, {'cid': 1, 'tel': 1})
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

    def get_pwd_reset_data(self, data, province, telecom, cids_list, para_start_date, para_end_date):
        """
        data like {cid:tel_set}
        :return:{} like {cid:(pwd_reset_success, pwd_reset_total, pwd_rt_success_pct)}
        """
        logger.info("")
        result = {}
        condition = {}
        if telecom:
            condition['telecom'] = telecom
        if province:
            condition['province'] = province
        if para_start_date:
            para_date_timstamp_start = str(time.mktime(
                datetime.datetime.strptime(para_start_date + "00:00:00", "%Y%m%d%H:%M:%S").timetuple()))
            condition["end_time"] = {'$gte': para_date_timstamp_start}
        if para_end_date:
            para_date_timstamp_end = str(time.mktime(
                datetime.datetime.strptime(para_end_date + "23:59:59", "%Y%m%d%H:%M:%S").timetuple()))
            if 'end_time' in condition:
                condition['end_time']['$lte'] = para_date_timstamp_end
            else:
                condition["end_time"] = {'$lte': para_date_timstamp_end}
        if cids_list:
            # in tel_info cid's type is int32
            condition["cid"] = {'$in': [str(i) for i in cids_list]}
        logger.info(condition)
        conn = None
        try:
            conn = pymongo.MongoClient(ConstantVar.mongo_db_host, ConstantVar.mongo_db_port)
            col = conn[ConstantVar.mongo_db_pwd_name][ConstantVar.mongo_db_pwd_col]
            success_count = 0
            all_count = 0
            all = col.find(condition, {'end_time': 1, 'tel': 1, 'status': 1, 'cid': 1})
            logger.info(all.count())
            for p in all:
                try:
                    status = p['status']
                    tel = p['tel']
                    cid = p['cid']
                    if not (tel in data.get(cid, set())):
                        continue
                    if status == 0:
                        success_count += 1
                    all_count += 1
                    if all_count != 0:
                        result[cid] = [success_count, all_count, float(success_count)/all_count]
                except Exception as e:
                    logger.error("error: %s, data: %s", e, p)
            return result
        finally:
            if conn:
                conn.close()

    def deal(self, para_start_date, para_end_date, cids_list, telecom, province, crawler_channel):
        """
        :param para_date:
        :return summarize data contail key finally_require_keys
        finally_require_keys = ['cid', 'total_nums', 'authen_nums', 'crawl_nums', 'report_nums',
                    'tel_nums', 'authen_pct', 'crawl_pct', 'report_pct', 'log_loss_pct',
                    'tel_num_diff']
        """
        logger.info('')
        mongo_handle = None
        try:
            # get data from mongodb
            # get summarize data from rpt table
            mongo_handle = pymongo.MongoClient(ConstantVar.mongo_db_host, ConstantVar.mongo_db_port)
            rpt_collection = mongo_handle[ConstantVar.mongo_db_name][ConstantVar.mongo_db_rpt_col]
            condition = {}
            if telecom:
                condition['telecom'] = telecom
            if province:
                condition['province'] = province
            if crawler_channel:
                condition['crawler_channel'] = crawler_channel
            if para_start_date:
                condition["rpt_date"] = {'$gte': para_start_date}
            if para_end_date:
                if 'rpt_date' in condition:
                    condition['rpt_date']['$lte'] = para_end_date
                else:
                    condition["rpt_date"] = {'$lte': para_end_date}
            if cids_list:
               #in sid_info_data_rpt cid's type is int32
                cids_list = [int(k) for k in cids_list]
                condition["cid"] = {'$in': cids_list}
            logger.info(condition)
            one_day_rpt = rpt_collection.find(condition)
           #get data realtime data from sid_info
            all_tmp_data = {}
            # maybe multi cid(every cid one result)
            # maybe multi rows return from mongo (sum them)
            for k in one_day_rpt:
                # change int to string
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
                        'cid':cid,
                        'log_loss_pct': 0,
                        'bill_loss_pct': 0,
                        'tel_num': 0,
                        'pwd_rt_success': 0,
                        'pwd_rt_total': 0,
                        'pwd_rt_pct': 0,
                    }
                else:
                    all_tmp_data[cid]['total_nums'] += k.get('total_nums', 0)
                    all_tmp_data[cid]['authen_nums'] += k.get('authen_nums', 0)
                    all_tmp_data[cid]['crawl_nums'] += k.get('crawl_nums', 0)
                    all_tmp_data[cid]['report_nums'] += k.get('report_nums', 0)
                    all_tmp_data[cid]['call_log_intact_nums'] += k.get('call_log_intact_nums', 0)
                    all_tmp_data[cid]['bill_intact_nums'] += k.get('bill_intact_nums', 0)
                    all_tmp_data[cid]['final_nums'] += k.get('final_nums', 0)
            # get all tel num
            all_tel_num_data = self.get_tel_num(mongo_handle, condition)
            pwd_result = self.get_pwd_reset_data(all_tel_num_data, province, telecom, cids_list, para_start_date, para_end_date)
            # calc all pct
            for cid in all_tmp_data:
                v = all_tmp_data[cid]
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
                    v['tel_num'] = len(all_tel_num_data.get(cid, set()))
                    pwd_data = pwd_result.get(cid, [0, 0, 0])
                    v['pwd_rt_success'], v['pwd_rt_total'], v['pwd_rt_pct'] = pwd_data
                except Exception as e:
                    logger.error(e)
        except Exception as e:
            logger.error(e)
        finally:
            if mongo_handle:
                mongo_handle.close()
        return all_tmp_data
