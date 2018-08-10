from elasticsearch import Elasticsearch
es = Elasticsearch(host='172.18.52.176')
query={
    "query" : 
    {
        "term" : 
            {
            "tels":"02075512450"
            }
    }
}
indices = es.indices
dd = indices.get_mapping()
for k, v in dd:
    print(k, v)
