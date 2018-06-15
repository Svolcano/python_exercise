#_*_coding:utf-8 _*_

import datetime
import time
import hashlib
import re
import configparser


class ConstantVar(object):
    """
    store constant var in this class
    all var store here
    """
    # mongo_db setting
    mongo_db_host = '172.18.19.219'
    mongo_db_port = 27017
    mongo_db_name = 'crs'
    mongo_db_ori_col = 'sid_info'
    mongo_db_rpt_col = 'sid_info_data_rpt'
    mongo_db_pwd_name = 'pwd'
    mongo_db_pwd_col = 'tid_info'

    # tornado server setting
    tornado_port = 18000

    # default value
    cid_default_value = -1
    other_default_value = 'miss'

    # api return value
    # success: 0
    # fail : !0
    st_success = 0
    st_other = 7777
    st_param_error = 7778
    st_access_deny = 7779
    status_msg = {
        st_success: '',
        st_other: 'unknown errors.',
        st_param_error: 'parameters error.',
        st_access_deny: 'access deny.',
    }

    # pwd reset retry status
    pwd_reset_success = 0

    # jianquan key
    api_key = '0aa2cb33d0eaedc4abe412348045dc8'
    api_secret = '0b178ed2d1d049e46472711d8f92bf4'
    jq_timeout = 300#  5min


class SUtils(object):
    """
    all static function defined here
    """
    @staticmethod
    def fill_day_with_time(begin, end=None):
        """
        :param begin: like 20190101
        :param end: like 20190201
        :return: if end is None  end - begin
        return begin000000, begin235959
        else:begin000000,end235959
        finally turn then to seconds
        return
        """
        ss = time.mktime(
            datetime.datetime.strptime(begin + "00:00:00", "%Y%m%d%H:%M:%S").timetuple())
        if end:
            begin = end
        es = time.mktime(
            datetime.datetime.strptime(begin + "23:59:59", "%Y%m%d%H:%M:%S").timetuple())
        return ss, es

    @staticmethod
    def check_sign(time_v, nonce, php_v, api_key=ConstantVar.api_key, api_secret=ConstantVar.api_secret):
        now_t = int(time.time())
        time_v_i = int(time_v)
        if now_t - time_v_i > ConstantVar.jq_timeout:
            return False, "timeout"
        in_p = [api_key, api_secret, time_v, nonce]
        in_p.sort()
        in_str = ''.join(in_p)
        m = hashlib.md5()
        m.update(in_str)
        v1 = m.hexdigest()
        m2 = hashlib.md5()
        m2.update(v1)
        python_result = m2.hexdigest()
        # php_v, python_result
        # print  python_result == php_v
        equal = (python_result == php_v)
        if equal:
            return True, ''
        else:
            return False, 'not equal'

    @staticmethod
    def is_date_str(d):
        """
        check d is like 20180101
        :param d: date str like 20180101
        :return: True or False
        """
        dr = re.compile(r'^\d{8}$')
        a = dr.match(d)
        if a:
            try:
                datetime.datetime.strptime(d, '%Y%m%d')
                return True
            except Exception as e:
                return False
        else:
            return False

    @staticmethod
    def is_time_str(d):
        """
        check d is like 20180101
        :param d: date str like 20180101
        :return: True or False
        """
        dr = re.compile(r'^\d{10}$')
        a = dr.match(d)
        if a:
            try:
                datetime.datetime.fromtimestamp(int(d))
                return True
            except Exception as e:
                return False
        else:
            return False

    @staticmethod
    def init():
        """
        read config from inni and set value to ConstantVar
        :return:
        """
        try:
            ret, result = SUtils.parse_config('config.ini')
            if ret:
                ConstantVar.mongo_db_host = result['mongo_db_host']
                ConstantVar.mongo_db_port = result['mongo_db_port']
                ConstantVar.tornado_port = result['server_port']
                ConstantVar.api_secret = result['api_secret']
                ConstantVar.api_key = result['api_key']
                ConstantVar.jq_timeout = result['timeout']
        except Exception as e:
            print(e)


    @staticmethod
    def parse_config(file_name='../config.ini'):
        try:
            cfg_read = configparser.ConfigParser()
            cfg_read.read(file_name, encoding='ascii')
            obj = {}
            obj['mongo_db_host'] = cfg_read['mongo']['host']
            obj['mongo_db_port'] = int(cfg_read['mongo']['port'])
            obj['server_port'] = int(cfg_read['server']['port'])
            obj['api_key'] = cfg_read['key']['api_key']
            obj['api_secret'] = cfg_read['key']['api_secret']
            obj['timeout'] = int(cfg_read['key']['timeout'])
            return True, obj
        except Exception as e:
            return False, None





if __name__ == "__main__":
    print SUtils.parse_config()


