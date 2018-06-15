#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sanic import Blueprint,response

from blueprints import status_codes, return_error
from binquire.name import NameResultCode

bp = Blueprint('FuzzyName', '/fuzzyname')

def get_params(request):
    try:
        name = request.args.get('name', '').strip()
        region = request.args.get('region', '').strip()
        if not( name or region):
            raise Exception("name or region is empty")
    except Exception as e:
        raise e
    return name, region


@bp.get('')
async def fuzzyname(request):
    try:
        name, region = get_params(request)
    except:
        return return_error(status_codes[1003], 1003)

    fuzzyname = request.app.fuzzyname

    names = await fuzzyname.async_search_all(name)
    similarity_name = ''
    max_similarity = 0
    for ele in names:
        if fuzzyname.check_region(ele, region):
            curr_similarity = fuzzyname.get_key_word_similarity(name,ele)
            if max_similarity < curr_similarity:
                max_similarity = curr_similarity
                similarity_name = ele
    info = {'keyword_similarity': max_similarity,
            'match_result': NameResultCode.IGNORE,
            'name': similarity_name,
            'status': 0,
            'msg': status_codes[0]}
    return response.json(info)