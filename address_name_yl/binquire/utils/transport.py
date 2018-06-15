#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import aiohttp
import requests
from abc import ABCMeta, abstractmethod


class Connection(object,metaclass=ABCMeta):
    def __init__(self):
         pass

    @abstractmethod
    def send_request(self, method, url, params=None, json=None,
                     timeout=10, **kwargs):
        pass

class Response(object):
    """ simple http response object"""

    def __init__(self, url, status, headers, text):
        self.url = url
        self.status = status
        self.headers = headers
        self.text = text

    def json(self):
        import ujson
        return ujson.loads(self.text)

    def __repr__(self):
        return '<Response [%s]>' % (self.status)


class AsyncContextManager:
    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        pass



class RequestsHttpConnector(Connection):

    def __init__(self, limit=0, **kwargs):
        pass

    def send_request(self, method, url, params=None, json=None,
                     timeout=10, **kwargs):
        resp = requests.request(method, url=url, params=params, json=json,
                                timeout=timeout, **kwargs)

        return Response(url, resp.status_code, resp.headers, resp.text)


class AIOHttpConnector(Connection):

    def __init__(self, limit=0, **kwargs):
        if limit:
            self.semaphore = asyncio.Semaphore(limit)
        else:
            self.semaphore = AsyncContextManager()

    @staticmethod
    async def fetch(session, method, url, **kwargs):
        async with session.request(method,url, **kwargs) as resp:
            return Response(url, resp.status, resp.headers, await resp.text())
            # return resp.status, resp.headers, await resp.text()

    async def send_request(self, method, url, params=None, json=None,
                           timeout=10, **kwargs):
        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                return await self.fetch(session, method, url,
                                        params=params, json=json,
                                        timeout=timeout, **kwargs)


class Transport(object):
    """ wrapper to compatible async or sync http request
    convention::
        when you call transport you need to return it, because transport can
        return coroutine or response object
    """

    def __init__(self, connector=None, connect_limit=0, **kwargs):
        """
        :param connector: RequestsHttpConnector or AIOHttpConnector
        :param connect_limit: concurrency request limit.
            This only support AIOHTTPCONNECTOR NOW.
        """
        if connector is None:
            self.connector = AIOHttpConnector(connect_limit, **kwargs)
        else:
            self.connector = connector(connect_limit,**kwargs)

    def send_request(self, method, url, params=None, json=None, retry = 2, **kwargs):
        retry = retry if retry > 0 else 1

        while retry > 0:
            retry -= 1
            try:
                resp = self.connector.send_request(method, url,
                                                   params=params, json=json,
                                                   **kwargs)
                return resp
            except Exception as e:
                raise e

    def get(self, url, params=None, json=None, **kwargs):
        return self.send_request('get', url=url, params=params, json=json,
                                 **kwargs)

    def post(self, url, params=None, json=None, **kwargs):
        return self.send_request('post', url=url, params=params, json=json,
                                 **kwargs)
