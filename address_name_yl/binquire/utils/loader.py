#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import pathlib

import jieba
import jieba.posseg
import networkx as nx

from . import window, normalize_region, chi_to_dig

resource_path = pathlib.Path(__file__).parents[2] / "resources"
logger = logging.getLogger("binquire")
logging.getLogger('oauth2client').setLevel(logging.ERROR)

class GoogleSheetClient(object):

    def __init__(self, key="", name="", auth_file_path=None):
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        if auth_file_path is None:
            auth_file_path = str(resource_path / "auth-gspread.json")

        scope = ['https://spreadsheets.google.com/feeds']

        credentials = \
            ServiceAccountCredentials.from_json_keyfile_name(auth_file_path,
                                                             scope)
        self.gc = gspread.authorize(credentials)
        if key:
            self.sht = self.open_by_key(key)
        elif name:
            self.sht = self.open_by_name(name)

    def open_by_key(self, key):
        return self.gc.open_by_key(key)

    def open_by_name(self, name):
        return self.gc.open(name)

    def get_modified_time(self):
        return self.sht.updated

    def get_worksheet(self, name="", idx=-1):
        worksheet = None
        if name:
            worksheet = self.sht.worksheet(name)
        elif idx and idx != -1:
            worksheet = self.sht.get_worksheet(idx)

        return worksheet


class WorkSheetLoader(object):
    def __init__(self, key, worksheet_name, auth_file_path=None):
        self.client = GoogleSheetClient(key=key, auth_file_path=auth_file_path)
        self.sht = self.client.sht
        self.worksheet = None
        self.set_worksheet(worksheet_name)

    def set_worksheet(self, worksheet_name):
        self.worksheet = self.client.get_worksheet(worksheet_name)

    def get_rows(self,col):
        return self.worksheet.col_values(col)

class DictionaryGen(object):
    def __init__(self,key, tables=None, out_path=None, auth=None):
        self.worksheet = WorkSheetLoader(key, out_path,auth)
        self.resource_folder = resource_path
        if tables is None:
            self.tables = ['region_old', 'industry', 'type','x']
        else:
            self.tables = tables if tables is list else list(tables)

    def check_update(self):
        db_version_chk = self.resource_folder / "db_version_chk"
        status = False
        if not db_version_chk.exists():
            status = True
        else:
            with db_version_chk.open('r',encoding="utf-8") as f:
                version = f.readline().strip()
            if version < self.worksheet.client.get_modified_time():
                status = True
        with db_version_chk.open('w', encoding="utf-8") as f:
            f.write(self.worksheet.client.get_modified_time())
        return status

    def update(self,force=False):
        if self.check_update() or force:
            dictonary = self.resource_folder / "dictionary"
            with dictonary.open('w',encoding="utf-8") as out:
                for table in self.tables:
                    logger.info(f"Start Update table:{table}")
                    self.worksheet.set_worksheet(table)
                    _ = filter(None, self.worksheet.get_rows(1))
                    # _ = filter(lambda x: len(x) > 1, _)
                    out.write(f' 1 {table.split("_",1)[0]}\n'.join( map( chi_to_dig, _)))
                    out.write(f' 1 {table.split("_",1)[0]}\n')


class DistrictGraphGen(object):
    __shared_stats = None
    def __init__(self,level=3):
        if not DistrictGraphGen.__shared_stats:
            DistrictGraphGen.__shared_stats = self.__dict__
            self.resource_folder = resource_path
            self._graph = None
            self.__init_graph(level)
        else:
            self.__dict__ = DistrictGraphGen.__shared_stats

    def __init_graph(self,level):
        self._graph = nx.DiGraph()
        logger.debug("Init brog graph")
        district = self.resource_folder / "district2.txt"
        self._graph.add_node('中国')
        with district.open('r') as lines:
            for line in lines:
                # iter = re.sub('[市区县]', '', line.strip()).split('\t')
                iter = normalize_region(chi_to_dig(line.strip())).split(',')
                for n1, n2 in window(iter[0:level], 2):
                    # if n1 in n2:
                    #     pass
                    if n1 != n2:
                        self._graph.add_edge(n1, n2)


    def create_graph(self, graph):
        graph.add_edges_from(self._graph.edges())
        return graph

    def get_graph(self):
        return self._graph

    pass


class DistrictsLoader(object):
    __shared_stats = None

    def __init__(self):
        if not DistrictsLoader.__shared_stats:
            DistrictsLoader.__shared_stats = self.__dict__
            district = resource_path / "district2.txt"

            self._district_tokenizer = jieba.posseg.POSTokenizer()
            self._district_dict = {}

            self._district_tokenizer.add_word('上海', 1000000)

            with open(district, 'r', encoding="utf-8") as lines:
                self.__gen_data(lines)

            if (resource_path / 'patch.txt').is_file():
                patch = (resource_path / 'patch.txt')
                with open(patch, 'r', encoding="utf-8") as lines:
                    self.__gen_data(lines, 10000)

        else:
            self.__dict__ = DistrictsLoader.__shared_stats

    def __gen_data(self, file, weight=100):
        x = ['p', 'c', 'd', 't']
        for line in file:
            w = weight
            for idx, item in enumerate(line.strip().split(',')):
                self._district_dict[item] = x[idx]
                self._district_tokenizer.add_word(item, w, 'x' + x[idx])
                w -= 10


    def get_district_dict(self):
        return self._district_dict

    def get_tokenizer(self):
        return self._district_tokenizer


class DistrictsADCodeLoader(object):
    __shared_stats = None

    def __init__(self):
        if not DistrictsADCodeLoader.__shared_stats:
            from collections import defaultdict
            DistrictsADCodeLoader.__shared_stats == self.__dict__
            self.__keys = defaultdict(list)
            self.__values = defaultdict(list)
            file = resource_path / "districts_adcode.csv"

            with file.open('r',encoding="utf-8") as lines:
                for line in lines:
                    k,v = line.strip().split(',')
                    self.__keys[k].append(v)
                    self.__values[v].append(k)
        else:
            self.__dict__ = DistrictsADCodeLoader.__shared_stats

    def get_adcode(self, key:str)->list:
        return self.__keys.get(key, [])

    def get_keys(self, value:int)->list:
        return self.__values.get(value,[])

if __name__ == '__main__':
    from settings import DB_SHEET_ID
    obj = DictionaryGen(DB_SHEET_ID)
    obj.update()
    a = DistrictGraphGen()
    b = DistrictGraphGen()
    print(id(a.get_graph()) == id(b.get_graph()))
    print([*a.get_graph().neighbors('吉林')])