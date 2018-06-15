#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import json
from settings import REDIS_EXPIRE


class LRUCache(collections.OrderedDict):

    def __init__(self, size=5):
        self.size = size,
        self.cache = collections.OrderedDict()

    def get(self, key):
        if key in self.cache:
            val = self.cache.pop(key)
            self.cache[key] = val
        else:
            val = None

        return val

    def set(self, key, val, time=None):
        if key in self.cache:
            val = self.cache.pop(key)
            self.cache[key] = val
        else:
            if len(self.cache) == self.size:
                self.cache.popitem(last=False)
                self.cache[key] = val
            else:
                self.cache[key] = val


def lru_cache(cache, prefix, func, *args, **kwargs):
    if len(args):
        key = f'{prefix}:{"".join(map(str,args))}'
    else:
        key = f'{prefix}:{func.__name__}'
    is_cache = True
    result = cache.get(key)
    if result is None:
        is_cache = False
        result = func(*args, **kwargs)
        cache.set(key, json.dumps(result))
    else:
        result = json.loads(result)

    return is_cache, result


async def a_lru_cache(cache, prefix, coroutine, *args, **kwargs):
    if len(args):
        key = f'{prefix}:{"".join(map(str,args))}'
    else:
        key = f'{prefix}:{coroutine.__name__}'
    is_cache = True
    result = cache.get(key)
    if result is None:
        is_cache = False
        result = await coroutine(*args, **kwargs)
        cache.set(key, json.dumps(result))
    else:
        result = json.loads(result)

    return is_cache, result


async def a_third_party_cache(cache, db, api, *args):
    """
    cache third party and save to mongo

    :param cache: thee cache object maybe redis or LRUCache
    :param db: pymongo db object
    :param api: third_party_api object
    :param args: search_name string to api search function
    :return: response a dict, key is ( api_name, resp_name, resp_address )
    """
    if len(args):
        key = f'third_party:{"".join(map(str,args))}'

    if isinstance(cache, LRUCache):
        result = cache.get(key)
    else:
        result = await cache.get(key)

    if result is None:
        result = {}
        resp = (await api.search(*args)).json()
        result['api_name'] = api.name
        result['resp_name'] = api.decode_name(resp)
        result['resp_address'] = api.decode_address(resp)

        if isinstance(cache, LRUCache):
            cache.set(key, json.dumps(result))
        else:
            try:
                await cache.set(key, json.dumps(result), expire=REDIS_EXPIRE)
                if db and result['resp_name']:
                    await db[api.name].insert_one(resp)
            except Exception as e:
                import traceback
                traceback.print_exc()
                pass
    else:
        result = json.loads(result)

    return result