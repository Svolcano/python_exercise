# -*- coding: utf-8 -*-

from worker.crawler.base_crawler import BaseCrawler

class Crawler(BaseCrawler):
    '''
     fake crawler module for no crawler supported case
    '''

    def need_parameters(self, **kwargs):
        return []

