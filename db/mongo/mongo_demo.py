#coding:utf8
import pymongo
host = '172.18.19.219'
port = 27017
db_name = 'crs'
col_name = 'sid_info'

conn = pymongo.MongoClient(host, port)
db = conn[db_name]
col = db[col_name]
cod = {}
cod['cid'] = {'$in':['3','4','5','6']}
src = col.find(cod)
for k in src:
    print (k)