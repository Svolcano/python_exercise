#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import pathlib
import re
from collections import deque

import ujson as json
from elasticsearch import Elasticsearch
import elasticsearch.helpers as es_helper


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)



def get_create_index_dsl(shrads=4):
    request_body = {
        "settings": {
            "index.mapping.ignore_malformed": True,
            "number_of_shards": shrads,
            "number_of_replicas": 1,
            "analysis": {
                "analyzer": {
                    "name_analyzer": {
                        "tokenizer": "name_index"
                    },
                    "address_analyzer": {
                        "tokenizer": "address_index"
                    }
                }
            }
        },
        "mappings": {
            "shop": {
                "_all": {
                    "enabled": False
                },
                "dynamic": "false",
                "properties": {
                    "sid": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "name_analyzer",
                        "search_analyzer": "name_analyzer"
                    },
                    "address": {
                        "type": "text",
                        "analyzer": "address_analyzer",
                        "search_analyzer": "address_analyzer"
                    },
                    "tels": {
                        "type": "keyword"
                    }
                }
            }
        }
    }
    return request_body


def del_index_and_recreate(index_name,es_host):
    is_exist = es.indices.exists(index_name)
    if not is_exist:
        raise Exception(f"Index {index_name} Not Exist.")
    res = es.indices.delete(index=index_name)
    print("delete res: ",res)
    if es_host == 'production':
        shards = 4
    else:
        shards = 2
    request_body = get_create_index_dsl(shards)
    res = es.indices.create(index=index_name, body=request_body)
    print("create res: ", res)


def gen_es_del_idx(file_folder: pathlib.Path, es_index, es_type):
    for file in file_folder.glob('*/*.txt'):
        logger.debug(f'Start {file.name}')
        with file.open('r', encoding="utf-8") as lines:
            for sid in lines:
                if '*********SUCCESS********' in sid:
                    continue
                output = {'_op_type':'delete',
                          '_id': sid.strip(),
                          '_index': es_index,
                          '_type': es_type}
                yield output


def gen_es_doc(file_folder: pathlib.Path, es_index, es_type):
    _re_pure_phone = re.compile('\D+')
    pure_phone = lambda tel: _re_pure_phone.sub('', tel)

    for file in file_folder.glob('*/*.txt'):
        logger.debug(f'Start {file.name}')
        with file.open('r', encoding="utf-8") as lines:
            for line in lines:
                if '*********SUCCESS********' in line:
                    continue
                obj = json.loads(line.strip())

                source = {'sid': obj.get('sid'),
                          'name': obj.get('recommend_name', '')}
                region = obj.get('region', {})
                prov = region.get('province_name', '')
                city = region.get('city_name', '')
                dist = region.get('district_name', '')
                address: str = obj.get('recommend_address', '')
                if prov == city:
                    city = ''
                if address.startswith(dist):
                    dist = ''
                if address:
                    source['address'] = "".join([prov, city, dist, address])
                else:
                    source['address'] = None

                # source['category'] = obj.get('recommend_category_name')
                # source['category'] = source['category'][0] if source[
                #     'category'] else None
                phones = set()
                inputs = obj.get('inputs', [])
                for ele in inputs:
                    for item in ele.get('tel'):
                        phones.add(item.get('number', ''))
                source['tels'] = [*map(lambda tel: pure_phone(tel), phones)]
                output = {'_id': obj.get('sid'),
                          '_index': es_index,
                          '_type': es_type,
                          '_source':source}
                del obj
                yield output


def worker(file_folder: pathlib.Path, es_index, es_type, operation,es_host):

    raise_on_error = True

    if operation == 'delete':
        iter_action = gen_es_del_idx(file_folder,es_index,es_type)
        raise_on_error = False
    else:
        iter_action = gen_es_doc(file_folder, es_index, es_type)

    del_index_and_recreate(es_index,es_host)
    deque(es_helper.parallel_bulk(es,
                                  iter_action,
                                  thread_count=8,
                                  chunk_size=20480,
                                  raise_on_error=raise_on_error),
          maxlen=0)


def main(data_folder, es_index, es_type, oppertaion='index',es_host='production'):
    worker(data_folder,es_index,es_type,operation=oppertaion,es_host=es_host)


if __name__ == '__main__':
    import argparse

    parse = argparse.ArgumentParser()
    parse.add_argument('-s', "--src", required=True,
                       help="The merge_output or aggregate_output folder")
    parse.add_argument('-i', "--index", required=True,
                       help="Elasticsearch index name")
    parse.add_argument('-t', "--dtype", required=False, default='shop',
                       help="Elasticsearch type name")
    parse.add_argument('-op', "--operation", required=False, default='index',
                       choices=['index', 'delete'],
                       help="index or delete")
    parse.add_argument('-es', "--es_host", required=True,
                       choices=['production', 'staging'],
                       help="select es hosts")
    args = parse.parse_args()

    es_hosts = None
    if args.es_host == 'production':
        es_hosts = ['172.18.52.17' + str(i) for i in range(1, 5)]
    elif args.es_host == 'staging':
         es_hosts = ['172.18.52.17' + str(i) for i in range(6, 8)]

    es = Elasticsearch(es_hosts, timeout=180)

    main(pathlib.Path(args.src), args.index, args.dtype, args.operation, args.es_host)
