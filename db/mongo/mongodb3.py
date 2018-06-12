# #coding:utf8

# import time
# import datetime
# import pymongo

# result = {}
# condition = {}
# telecom = ''
# province = ''
# para_start_date = ''
# para_end_date = ''
# cids_list = ['23',]
# if telecom:
#     condition['telecom'] = telecom
# if province:
#     condition['province'] = province
# if para_start_date:
#     para_date_timstamp_start = time.mktime(
#         datetime.datetime.strptime(para_start_date + "00:00:00", "%Y%m%d%H:%M:%S").timetuple())
#     condition["end_time"] = {'$gte': para_date_timstamp_start}
# if para_end_date:
#     para_date_timstamp_end = time.mktime(
#         datetime.datetime.strptime(para_end_date + "23:59:59", "%Y%m%d%H:%M:%S").timetuple())
#     if 'end_time' in condition:
#         condition['end_time']['$lte'] = para_date_timstamp_end
#     else:
#         condition["end_time"] = {'$lte': para_date_timstamp_end}
# if cids_list:
# # in tel_info cid's type is int32
#     condition["cid"] = {'$in': cids_list}
# conn = pymongo.MongoClient('172.18.19.219', 27017)
# col = conn['pwd']['tid_info']
# success_count = 0
# all_count = 0
# print condition
# con = {'end_time': 1, 'tel': 1, 'status': 1, 'cid': 1}
# all = col.find(condition, con)
# print all.count()
# for p in all:
#     print p

assert False