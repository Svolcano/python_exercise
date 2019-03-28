import pymysql
import requests
import logging

logger = logging.getLogger(__name__)

db = pymysql.Connect(host='jzsq.jingmeiti.com',
                     user='root',
                     password='$%^789Jing',
                     database='jzsq',
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor
                     )
try:
    with db.cursor() as cursor:
        sql = '''
            select cover 
            from media
        '''
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
        for p in result:
            cover = p['cover']
            strip_c = cover.strip()
            if strip_c:
                resp = requests.get('%s?x-oss-process=image/info' % (strip_c), timeout=30)
                if resp.status_code == 200:
                    rj = resp.json()
                    c_h = float(rj['ImageHeight']['value'])
                    c_w = float(rj['ImageWidth']['value'])
                    tsql = '''
                    update media
                    set c_w=%s, c_h=%s
                    where cover='%s'
                    ''' % (c_w, c_h, cover)
                    cursor.execute(tsql)
    db.commit()
except Exception as e:
    logger.info(e)
db.close()