# import pymongo


# host = '127.0.0.1'
# port = 27017
# db_name = 'test'
# col_name = "sid_info"

# conn = pymongo.MongoClient(host, port)
# db = conn[db_name]
# col = db[col_name]
# all = col.find({'tel':'15903551769'}).count()
# print all

# fun = '''
# function(obj, prev){
#     prev.count ++
# }
# '''
# all_doc = col.group(["tel"], None, {"count":0}, fun)
# for k in all_doc:
#     print k

# all = col.distinct('tel')
# print len(all)

import sys
a = sys.getsizeof(u'18506903527')
print a
num = 1*1024*1024*1024 // a
print num