#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .distance import jaccard_similarity

class BaseCompare(object):
    """compare object, you can init different distance algo to do your own compare
    """
    def __init__(self,distance=None):
        self.distance = distance
        pass

    def compare(self,str1,str2):
        if str1 == str2:
            return 1
        else:
            if self.distance:
                return self.distance(str1,str2)
            else:
                return 0

class JacardCaompare(BaseCompare):
    def __init__(self):
        super().__init__(distance=jaccard_similarity)

