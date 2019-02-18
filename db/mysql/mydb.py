import pymysql


class MyDB(object):

    def __init__(self, host, user, pwd, port, db):
        self.my_conn = pymysql.Connect(host=host,
                                       user=user,
                                       password=pwd,
                                       database=db,
                                       charset='utf8',
                                       port=port)
        self.cur = self.my_conn.cursor()

    def query(self, sql):
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def execute(self, sql):
        try:
            self.cur.execute(sql)
            self.my_conn.commit()
            return True
        except Exception as e:
            print(e)
            self.my_conn.rollback()
            return False

    def executemany(self, sql, data):
        try:
            self.cur.executemany(sql, data)
            self.my_conn.commit()
            return True
        except Exception as e:
            print(e)
            self.my_conn.rollback()
        return False

    def close(self):
        try:
            self.my_conn.close()
        except Exception as e:
            print(e)
