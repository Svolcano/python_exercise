import requests
import json

from control.db.api.account_api import DBAccountApi
from lib.tools.log_mgr import get_logger
from control.db.redis_mgr import RedisApi
from lib.tools.spider_tools import get_user_agent


class Base(object):

    mp_id = 0
    # 中文描述
    zh_name = ''
    UA = get_user_agent()
    logger = get_logger()

    def __init__(self):
        self.account = None
        self.session = None
        self.rs = RedisApi()

    def init(self, account, loop=2):
        self.account = account
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': Base.UA
        }
        self.logger.info("mp:%s, account:%s" % (account.mp_id, account.account))
        rs = RedisApi()
        key = "{}:{}:{}".format(account.uid, account.mp_id, account.id)
        r_cookies = rs.get_value(key)
        if r_cookies:
            cookies = json.loads(r_cookies.decode('utf8'))
            self.session.cookies = requests.cookies.cookiejar_from_dict(cookies)
            try:
                if not self.check_user_cookies():
                    cookies = self._login(account, loop=loop)
            except:
                cookies = self._login(account, loop=loop)
        else:
            cookies = self._login(account, loop=loop)
        if cookies:
            self.session.cookies = requests.cookies.cookiejar_from_dict(cookies)
            return True
        else:
            return False

    def _login(self, account, loop=1):
        while loop:
            key = "{}:{}:{}".format(account.uid, account.mp_id, account.id)
            try:
                cookies, nick_name = self.login(account.account, account.pswd)
            except Exception as e:
                self.logger.error(e)
                nick_name = ''
                cookies = {}
            if cookies:
                udata = dict(status=2)
                self.rs.set_value(key, json.dumps(cookies))
                db_account_api = DBAccountApi()
                if not account.nick_name:
                    udata['nick_name'] = nick_name
                db_account_api.update(udata, dict(uid=account.uid, mp_account_id=account.id))
                return cookies
            else:
                loop -= 1
        return None

    @staticmethod
    def login(user, pswd):
        pass

    def publish(self, title, content, category_id):
        pass

    def close(self):
        self.session.close()
