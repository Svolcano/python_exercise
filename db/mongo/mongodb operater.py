import pymongo
host = '172.18.19.219'
port = 27017
db_name = 'crs'
col_name = 'sid_info'

host2 = '127.0.0.1'
db_name2 = 'test'


conn = pymongo.MongoClient(host, port)
db = conn[db_name]
col = db[col_name]


conn_target = pymongo.MongoClient(host2, port)
db_target = conn_target[db_name2]
col2 = db_target[col_name]

src = col.find({})
try:
    for k in src:
        col2.insert(k, continue_on_error=True)
except Exception as e:
    print e
    print k