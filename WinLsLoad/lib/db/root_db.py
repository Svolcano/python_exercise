
import MySQLdb
import logging

from mysql_basic_c import mysql_basic_c as database

logger = logging.getLogger(__name__)

class root_db:

    def __init__(self, host, user, passwd, db):
        self._db = database(host, user, passwd, db)

    def set_time_zone(self, timezone):
        sql = "SET GLOBAL time_zone = '%s'" % timezone
        logger.info("sql:%s",sql)
        return self._db.execute(sql)


