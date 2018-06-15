# -*- coding: utf-8 -*-

import datetime

DATE_DICT = {'1':('01-01', '01-31'),
             '2-1':('02-01', '02-28'),
             '2-2':('02-01', '02-29'),
             '3':('03-01', '03-31'),
             '4':('04-01', '04-30'),
             '5':('05-01', '05-31'),
             '6':('06-01', '06-30'),
             '7':('07-01', '07-31'),
             '8':('08-01', '08-31'),
             '9':('09-01', '09-30'),
             '10':('10-01', '10-31'),
             '11':('11-01', '11-30'),
             '12':('12-01', '12-31')}

def generate_dates(months=5):
    results = []
    today = datetime.datetime.now()
    if today.month == 2:
        if today.year % 4 == 0:
            target = '2-2'
        else:
            target = '2-1'
    else:
        target = str(today.month)
    target_tup = DATE_DICT[target]
    target_start = '{}-{}'.format(today.year, target_tup[0])
    target_end = '{}-{:02d}-{:02d}'.format(today.year, today.month, today.day)
    results.append((target_start, target_end))
    for i in xrange(1, months+1):
        tmp_year = today.year
        tmp_month = today.month - i
        if tmp_month == 2:
            if tmp_year % 4 == 0:
                target = '2-2'
            else:
                target = '2-1'
        elif tmp_month <= 0:
            tmp_month = tmp_month + 12
            tmp_year -= 1
            target = str(tmp_month)
        else:
            target = str(tmp_month)
        target_tup = DATE_DICT[target]
        target_start = '{}-{}'.format(tmp_year, target_tup[0])
        target_end = '{}-{}'.format(tmp_year, target_tup[1])
        results.append((target_start, target_end))
        
    return results

if __name__ == '__main__':
    print generate_dates() 
