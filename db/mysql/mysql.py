from mydb import MyDB
from pprint import pprint

src_host = '127.0.0.1'
src_user = 'jingmeiti'
src_pwd = 'JING$%^789jing'
src_port = 3306
src_db = 'jmedia_ali'

try:
    suffix = {}
    db = MyDB(src_host, src_user, src_pwd, src_port, src_db)

    sql = "select user_email from wp_users"

    data = db.query(sql)
    for one_row in data:
        one = one_row[0]
        s = one.split('@')[-1]
        c = suffix.get(s, 0)
        suffix[s] = c+1

    pprint(sorted(suffix.items(), key=lambda d: d[1]))

finally:
    db.close()

