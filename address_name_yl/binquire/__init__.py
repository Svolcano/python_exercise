#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random

__all__ = ('QualityNameInquire', 'AddressInquire')



class ThirdPartyPool(object):

    def __init__(self):
        self.pool = set()

    def random_choice(self):
        return random.sample(self.pool, 1)[0]

    def register_api(self, api):
        self.pool.add(api)

    def remove_api(self, api):
        try:
            self.pool.remove(api)
        except KeyError:
            return False
        return True

    def __iter__(self):
        for api in self.pool:
            yield api

    def __bool__(self):
        return bool(self.pool)

    def __nonzero__(self):
        return self.__bool__()


# from .binquire import NameInquire, AddressInquire

from .name import QualityNameInquire
from .address import AddressInquire