from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
nd = datetime.now()
yesterday = (nd + timedelta(days=-1)).strftime("%Y.%m.%d")
print(yesterday)
filter_yesterday = (nd + timedelta(days=-1)).strftime("%Y-%m-%d")
print (filter_yesterday)
before_yesterday = (nd + timedelta(days=-2)).strftime("%Y.%m.%d")
print(before_yesterday )


url = 'http://192.168.9.228:9200'

es = Elasticsearch(url, timeout=120)
a = es.info()
print(es.indices)