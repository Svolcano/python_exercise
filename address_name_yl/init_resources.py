#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from binquire.utils.loader import  DictionaryGen
from binquire.settings import  db_sheet_id
obj = DictionaryGen(db_sheet_id)
obj.update(force=True)