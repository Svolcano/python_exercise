from elasticsearch import Elasticsearch
from elasticsearch import helpers

hosts = ['172.18.52.171', '172.18.52.172','172.18.52.173' ,'172.18.52.174']
es = Elasticsearch('172.18.52.171')
query={"query" : {"match_all" : {}}}
scanResp= helpers.scan(client= es, query=query, scroll= "10m", timeout="10m")
ts = set()
for resp in scanResp:
    try:
        tels = resp['_source']['tels']
        for t in tels:
            ts.add(t)
        if len(ts) == 1000000:
            break
    except:
        pass
ts = list(ts)
with open("tel.txt", 'w') as wh:
    wh.write('\n'.join(ts))