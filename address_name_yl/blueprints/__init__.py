#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sanic.response import json


def return_error(msg, status_code, exec_info=False):
    result = {'msg': msg, 'status_code': status_code}
    if exec_info:
        import traceback
        traceback.print_exc()
        result['debug'] = {'traceback': traceback.format_exc()}
    return json(result, 404)

status_codes ={
    1001: "input or bkwd is empty.",
    1999: 'Unknown Error.',
    1002: 'debug is not int error.',
    1003: "input or phone is empty.",
    300001: 'third party query failed.',
    0: 'success!'

}