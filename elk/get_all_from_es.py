from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch(config['es_server'])

index_v="teacher-center-single_question_count"
doc_type_v="single_question_count"

query={"query" : {"match_all" : {}}}

scanResp= helpers.scan(client= es, query=query, scroll= "10m", index= index_v , doc_type=doc_type_v , timeout="10m")

for resp in scanResp:
    qid = resp['_id']