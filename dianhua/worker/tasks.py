# -*- coding: utf-8 -*-
import traceback
from mrq.task import Task

from machine import Machine

class CrawlCallHistory(Task):

    def run(self, param):
        # get parameters
        runner = Machine()
        result = runner.run(param)
        return result

if __name__ == '__main__':
    task = CrawlCallHistory()
    task.run({'flow_type':'10010', 'sid':'test1', 'tel':'13041048019', 'pin_pwd':'123890', 'verify_code':'', 'website_pwd':''})
