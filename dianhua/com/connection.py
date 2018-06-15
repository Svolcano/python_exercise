# -*-  coding:utf-8 -*-
import pymongo
from setting.db_config import DB_CONFIG
from mongo_proxy import MongoProxy
class MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_db_conn()

    def set_db_conn(self):
        mongo_config=DB_CONFIG["base"]
        safe_conn = MongoProxy(pymongo.MongoClient(mongo_config['host'], mongo_config['port'], connect=False))
        self.conn = safe_conn[mongo_config['db']]

    def get_db_conn(self):
        db = self.conn
        return db

db_conn = MongodbConnection().get_db_conn()
db = {
    'user_info': db_conn[DB_CONFIG["user_info"]["collection"]],
    'call_log': db_conn[DB_CONFIG["call_log"]["collection"]],
    'sid_info': db_conn[DB_CONFIG["sid_info"]["collection"]],
    'report': db_conn[DB_CONFIG["report"]["collection"]],
    'state': db_conn[DB_CONFIG["state"]["collection"]],
    'params': db_conn[DB_CONFIG["params"]["collection"]],
    'phone_bill': db_conn[DB_CONFIG["phone_bill"]["collection"]],
    'state_log': db_conn[DB_CONFIG["state_log"]["collection"]],
    'log': db_conn[DB_CONFIG["log"]["collection"]],
    'call_log_details': db_conn[DB_CONFIG["call_log_details"]["collection"]],
    'dama_cfg': db_conn[DB_CONFIG["dama_cfg"]["collection"]],
    'other_call_log': db_conn[DB_CONFIG["other_call_log"]["collection"]],
    'phone_bill_cache': db_conn[DB_CONFIG["phone_bill_cache"]["collection"]],
    'other_phone_bill': db_conn[DB_CONFIG["other_phone_bill"]["collection"]]
    }
