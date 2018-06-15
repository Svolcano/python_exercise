# -*- coding:utf-8 -*-

"""
@version: v1.0
@author: xuelong.liu
@license: Apache Licence 
@contact: xuelong.liu@yulore.com
@software: PyCharm
@file: base_common.py
@time: 12/21/16 7:10 PM
"""
import calendar
import functools
import datetime
import time


class BaseCommon(object):

    """
    逻辑装饰器, 通用方法
    """

    @classmethod
    def check_flag(cls, func):
        """
        检查状态
        :param func:
        :return:
        """

    @staticmethod
    def get_YMD():
        dtime = datetime.datetime.now().strftime('%Y-%m-%d').split('-')
        return int(dtime[0]), int(dtime[1]), int(dtime[2])

    def generator_time(self, test_month=None):
        year, month, today = self.get_YMD()
        # month = month + 1 if month != 12 else 12
        if test_month:
            month = test_month
        month += 1
        mt = [m for m in xrange(1, 13)]
        mtt = [m for m in xrange(1, 14)]
        sm_i = mtt.index(month)
        em_i = mtt.index(month)-6
        if em_i < 0:
            all_month = map(lambda x: str(x), mt[em_i:]+mt[:sm_i])
            old_year = len(mt[em_i:])
        else:
            old_year = 0
            all_month = [str(m) for m in xrange(mt[em_i], month)]

        all_month_day = [str(calendar.monthrange(year, int(m))[1]) for m in all_month]
        begin_day_list = ["1"] * len(all_month)
        all_year = [str(year-1)] * old_year + [str(year)] * (len(all_month) - old_year)

        timestamp_list = [str(time.time())] * len(all_month)

        temp = zip(all_year, all_month, begin_day_list, all_month_day, timestamp_list)
        temp.append((str(year), str(month), "1", str(today), str(time.time())))
        return temp[:-1]

if __name__ == "__main__":
    b = BaseCommon()
    for i in range(1, 13):
        print b.generator_time(i)
    # a = b.generator_time()
    # for i in a:
    #     print i[0] + i[1].rjust(2, '0')

