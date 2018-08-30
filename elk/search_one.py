from elasticsearch import Elasticsearch
from elasticsearch import helpers
es = Elasticsearch(hosts=['172.18.52.171','172.18.52.172','172.18.52.173','172.18.52.174' ])
query={
    "query" : 
    {
        "term" : 
            {
            "tels":"10086"
            }
    }
}
scanResp= helpers.scan(client= es, query=query, scroll= "10m", timeout="10m")
for k in scanResp:
    print(k)
