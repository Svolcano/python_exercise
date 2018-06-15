# -*-  coding:utf-8 -*-

import time
import socket
import inspect

if __name__ == '__main__':
    import sys
    sys.path.append('../')

from setting.api_config import ENV
from com.connection import db

"""
## `logger` 数据结构 `*` 为必填

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `*` `log_name` | stirng | state_log | 日志分类名称，比如：状态日志名称为`state_log`，爬虫为`crawler_log`，API为`api`，mrq为`mrq` |
| `*` `level` | stirng | DEBUG | `DEBUG线上不记录此级别` `ERROR` `INFO` |
| `sid` | stirng | SID384cbde729894650a8fe390e53988200 | 唯一标识符SID |
| `*` `message` | string, mixed | 记录错误信息方便debug | `traceback.format_exc()`内容，或者自定义的错误消息 |
| `state_log` | [state_log](#state_log) | 运营商返回失败 | |
| `crawler` | stirng | china_mobile.shanghai | 爬虫名称 |
| `*` `file_name` | 文件名 | /call_history_crawler/worker/state/standard_state.py | 在哪个文件出错了 |
| `*` `file_line` | 行数 | 128 | 在第几行出错了 |
| `*` `IPv4` | string | 172.18.19.219 | 创建时间 |
| `*` `created_at` | timestamp | 1498082878 | 创建时间 |
"""
def logger(log_name, level, message, **kwargs):
    log = {}

    if ENV == 'prod' and level == 'INFO':
        return log

    log['log_name'] = log_name
    log['level'] = level
    log['message'] = message
    log['created_at'] = time.time()
    log['IPv4'] = socket.gethostname()
    log['file_line'] = inspect.stack()[2][2]

    if kwargs:
        log.update(kwargs)

    for _ in xrange(3):
        res = db['log'].insert_one(log)
        if res.inserted_id:
            break
    else:
        print log
