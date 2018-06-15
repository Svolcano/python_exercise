#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re

from .distance import levenshtein
from . import chi_to_dig
from .loader import DistrictsLoader
from .log import getLogger



class Address(object):
    _re_replace_parentheses = re.compile('[(（)）]')
    _re_replace_dot = re.compile('、')
    logger = getLogger(__name__)

    def __init__(self, raw_address=""):
        self.province = ""
        self.city = ""
        self.district = ""
        self.town = ""
        self.detail = ""
        self.raw_address = self._re_replace_parentheses.sub('',raw_address)
        self.raw_address = self._re_replace_dot.sub('-',self.raw_address)

    def update(self):
        raise NotImplementedError

    def __str__(self):
        return self.raw_address

    def __repr__(self):
        s = '{}/Prov,{}/City,{}/Dist,{}/Town,{}/detail'
        return s.format(self.province, self.city, self.district, self.town,
                        self.detail)


class ChinaAddress(Address):
    """
    raw address string to Chine Address Object

    Usage::
    >>> ChinaAddress('北京上海街')
    北京市/Prov,北京市/City,/Dist,/Town,上海街/detail;/Vill,/park,上海街/street,/No.,/lane,/yard,/building,/floor,/unit,/room
    
    >>> ChinaAddress("北京上海街").province
    北京市
    
    """
    province_endswith = ['省','市','自治区']
    city_endswith = ['市','地区','盟','自治洲']
    district_endswith = ['区', '市','特区', '林区', '自治旗','县']
    town_endswith = ['街道','乡','民族乡','镇','苏木','民族苏木','区公所']

    municipalitys = ['北京市', '天津市', '上海市', '重庆市']

    prov_pattern = re.compile("|".join(province_endswith))
    city_pattern = re.compile("|".join(city_endswith))
    district_pattern = re.compile("|".join(district_endswith))
    town_pattern = re.compile("|".join(town_endswith))


    not_street_pattern = re.compile('^[东西南北上中下一二三四五六七八九环]{0,3}路|^大?[道街]|村|^\d+号?')
    _re_country_pattern = re.compile('^中国')
    logger = getLogger('ChinaAddress')
    _re_remove_parentheses = re.compile('\([^(]*\)')

    def __init__(self, raw_address="",hmm=True):
        self.district_dict = DistrictsLoader().get_district_dict()
        self.d_tokenizer = DistrictsLoader().get_tokenizer()

        super().__init__(raw_address=raw_address)

        self.raw_address = self._re_country_pattern.sub('',self.raw_address)
        self.raw_address = self._re_remove_parentheses.sub('', self.raw_address)
        self.cut_address = []

        self.__vill = None
        self.__street = None
        self.__number = None
        self.__lane = None
        self.__yard = None
        self.__building = None
        self.__floor = None
        self.__unit = None
        self.__room = None
        self.__park = None
        self.__detail: str = ""
        self._hmm = hmm

        if raw_address:
            self.update()

    @property
    def village(self):
        if self.__vill is None:
            detail = self.__detail
            r = re.search('.+?村', detail)
            if r:
                self.__vill = r.group(0)
            else:
                self.__vill = ''
        return self.__vill

    @property
    def park(self):
        if self.__park is None:
            detail = self.__detail
            detail = detail.replace(self.village, '')
            r = re.search('.+(?<!办公)[园|区](?!路)', detail)
            if r and '幢' not in r.group(0):
                self.__park = r.group(0)
                # self.__detail = detail
            else:
                self.__park = ''
        return self.__park

    @property
    def street(self):
        if self.__street is None:
            detail = self.__detail
            detail = detail.replace(self.village,'').replace(self.park, '')
            r = re.search('(.*?)(?<![园区栋-])[a-zA-Z0-9-]+[号弄]([^院楼路小]|$)', detail) or \
                re.search('(^.+(路|街|道|巷|交叉|交汇)[处口]?)', detail) # [^小园]区|
            if r:
                self.__street = r.group(1)
                # self.__detail = detail
            else:
                self.__street = ''
        return self.__street


    @property
    def number(self):
        if self.__number is None:
            detail = self.__detail
            detail = detail.replace(self.village, '').replace(self.park, '').replace(self.street,'')
            r = re.search('(^[a-zA-Z]?[0-9\-]+号)([^院路楼小]|$)', detail)
            if r:
                self.__number = r.group(1)
                # self.__detail = detail
            else:
                self.__number = ''
        return self.__number

    @property
    def lane(self):
        if self.__lane is None:
            detail = self.__detail
            detail = detail.replace(self.village, '').replace(self.park, '')
            detail = detail.replace(self.street,'',1).replace(self.number,'',1)
            r = re.search('.+(胡同|弄)', detail)
            if r:
                self.__lane = r.group(0)
                # self.__detail = detail
            else:
                self.__lane = ''
        return self.__lane

    @property
    def yard(self):
        if self.__yard is None:
            detail = self.__detail
            detail = detail.replace(self.village, '').replace(self.park, '')
            detail = detail.replace(self.street,'').replace(self.number,'',1)
            detail = detail.replace(self.lane,'')
            r = re.search('^[甲乙丙丁戊己]?[0-9-]+号[院]?',detail)
            if r:
                self.__yard = r.group(0)
                # self.__detail = detail
            else:
                self.__yard = ''
        return self.__yard

    @property
    def building(self):
        if self.__building is None:
            detail = self.__detail
            detail = detail.replace(self.village, '').replace(self.park, '')
            detail = detail.replace(self.street, '').replace(self.number,'')
            detail = detail.replace(self.lane, '')
            detail = detail.replace(self.yard,'')
            r = re.search('.*([0-9]+((号楼)|[栋幢])|大楼|大厦|座|公寓|区)',detail)
            if r:
                self.__building = r.group(0)
                # self.__detail = detail
            else:
                self.__building = ''
        return self.__building

    @property
    def floor(self):
        if self.__floor is None:
            detail = self.__detail
            detail = detail.replace(self.village, '').replace(self.park, '')
            detail = detail.replace(self.street, '').replace(self.number, '')
            detail = detail.replace(self.lane, '')
            detail = detail.replace(self.yard, '').replace(self.building,'')
            r = re.search('.*[0-9、-]+[层楼Ff]', detail)
            if r:
                self.__floor = r.group(0)
                # self.__detail = detail
            else:
                self.__floor = ''
        return self.__floor

    @property
    def unit(self):
        if self.__unit is None:
            detail = self.__detail
            detail = detail.replace(self.village, '').replace(self.park, '')
            detail = detail.replace(self.street, '').replace(self.number, '')
            detail = detail.replace(self.lane, '').replace(self.yard, '')
            detail = detail.replace(self.building,'').replace(self.floor,'')
            r = re.search('([0-9]+)[甲乙丙丁戊己]?(-|单元)', detail)
            if r:
                self.__unit = r.group(0)
                # self.__detail = detail
            else:
                self.__unit = ''
        return self.__unit

    @property
    def room(self):
        if self.__room is None:
            detail = self.__detail
            detail = detail.replace(self.village, '').replace(self.park, '')
            detail = detail.replace(self.street,'').replace(self.number, '')
            detail = detail.replace(self.lane, '').replace(self.yard, '')
            detail = detail.replace(self.building,'')
            detail = detail.replace(self.floor,'').replace(self.unit,'',1)
            # print(detail)
            r = re.search('[^1-9]*([0-9-]+)(室?|号房?|$)',detail)
            if r:
                self.__room = r.group(1)
                # self.__detail = detail
            else:
                self.__room = ''
        return self.__room

    @property
    def level(self):
        """
        1 is number level, 0 is block level

        :return if the address is precision return 1 otherwise retrun 0
        :rtype int
        """

        if self.room or self.unit or self.floor or self.building :
            return 1
        else:
            return 0

    def __repr__(self):
        x = '{}/Vill,{}/park,{}/street,{}/No.,{}/lane,' \
            '{}/yard,{}/building,{}/floor,{}/unit,{}/room'
        return  super().__repr__() + ';' + x.format(self.village,
                                                    self.park,
                                                    self.street,
                                                    self.number,
                                                    self.lane,
                                                    self.yard,
                                                    self.building,
                                                    self.floor,
                                                    self.unit,
                                                    self.room)

    _re_not_number = re.compile('[^甲乙丙丁戊己\d]')

    def __eq__(self, other):
        def not_similarity_string(s1, s2, empty_compare=False):
            if ( '' != s1 or s2 != '') and \
                    levenshtein(s1, s2) > 0.2:
                return True
            return False

        def not_similarity_number(n1, n2):
            # if '' != _re_not_number.sub('', n1) != \
            #         _re_not_number.sub('', n2) != '':
            #     return True
            if self._re_not_number.sub('', n1) != self._re_not_number.sub('', n2) and \
                    ('' != n1 or n2 != ''):
                return True
            return False

        if not ( self.is_available_info() and other.is_available_info()):
            return False
        self.logger.debug(f'{self.detail},{other.detail}')
        if '' != self.room != other.room != '':
            self.logger.debug("room is not equal")
            return False
        elif not_similarity_number(self.number,other.number):
            self.logger.debug(f"number is not equal")
            return False
        elif not_similarity_number(self.unit, other.unit):
            self.logger.debug("unit is not equal")
            return False
        elif not_similarity_number(self.floor, other.floor):
            self.logger.debug("floor is not equal")
            return False
        elif not_similarity_string(self.street, other.street, True):
            self.logger.debug("street is not equal")
            return False
        elif not_similarity_string(self.building, other.building, True):
            self.logger.debug("building is not equal")
            return False
        elif not_similarity_string(self.park, other.park, True):
            self.logger.debug("park is not equal")
            return False
        elif not_similarity_number(self.yard, other.yard):
            self.logger.debug("yard is not equal")
            return False
        elif not_similarity_string(self.village, other.village):
            self.logger.debug("village is not equal")
            return False
        elif (''!=self.lane and other.lane != '') and \
                not_similarity_number(self.lane, other.lane):
            return False
        elif not self.compare_district(other):
            return False
        return True

    def compare_district(self, other):
        if ''!=self.province != other.province != '':
            self.logger.debug("province is not equal")
            return False
        elif ''!=self.city != other.city != '':
            self.logger.debug("city is not equal")
            return False
        elif '' != self.district != other.district != '':
            self.logger.debug("district is not equal")
            return False
        elif '' != self.town != other.town != '':
            self.logger.debug("town is not equal")
            return False
        return True

    def is_available_info(self):
        if not (self.village or self.park or self.street or self.building or self.floor):
            self.logger.debug(f"{self.raw_address}, detail is not available.")
            return False
        return True

    def do_cut_address(self):
        self.cut_address = self.d_tokenizer.lcut(self.raw_address,self._hmm)
        pair = self.cut_address[0]
        if pair.flag in ['ns','nz','nr'] and len(pair.word) > 2:
            if pair.flag == 'nr' and '区' == pair.word[-1]:
                return
            # need_cut = False
            # for item in set(self.province_endswith + self.city_endswith
            #                 + self.district_endswith):
            #     if item in pair.word:
            #         need_cut = True
            #         break
            # if need_cut:
            self.d_tokenizer.del_word(pair.word)
            self.cut_address = self.d_tokenizer.lcut(self.raw_address)

    def _find_province(self):
        province = self.__find_districts(self.cut_address[0].word,
                                         self.cut_address[0].flag,
                                         self.prov_pattern,
                                         self.province_endswith,
                                         'xp')
        if province:
            if len(self.cut_address) <= 1 or \
                    not self.not_street_pattern.match(self.cut_address[1].word):
                self.province = province
                if self.province in self.municipalitys:
                    self.city = self.province
                return province

    def _find_city(self):
        if self.cut_address[0].flag == 'nt':
            self.d_tokenizer.del_word(self.cut_address[0].word)
            self.do_cut_address()
            del self.cut_address[0]
        city = self.__find_districts(self.cut_address[0].word,
                                     self.cut_address[0].flag,
                                     self.city_pattern,
                                     self.city_endswith,
                                     'xc')
        if city:
            if len(self.cut_address) <= 1 or \
                    not self.not_street_pattern.match(self.cut_address[1].word):
                self.city = city
                if self.city in self.municipalitys and not self.province:
                    self.province = self.city
                return city

    def _find_district(self):
        district = self.__find_districts(self.cut_address[0].word,
                                         self.cut_address[0].flag,
                                         self.district_pattern,
                                         self.district_endswith,
                                         'xd')
        if district:
            if len(self.cut_address) <= 1 or \
                    not self.not_street_pattern.match(self.cut_address[1].word):
                self.district = district
                return district

    def _find_town(self):
        # if self.cut_address[0].flag == 'xt':
        #     self.town = self.cut_address[0].word
        town = self.__find_districts(self.cut_address[0].word,
                                     self.cut_address[0].flag,
                                     self.town_pattern,
                                     self.town_endswith,
                                     'xt')
        if town:
            if len(self.cut_address) <= 1 or \
                    not self.not_street_pattern.match(self.cut_address[1].word):
                self.town = town
                return town

    def __find_districts(self, candidate, flag, find_pattern,
                         level_endswith, level_flag):

        if find_pattern.search(candidate):
            if flag == level_flag:
                return candidate
        elif len(candidate) > 1 and flag[0] != 'x' or flag == level_flag:
            for miss_word in level_endswith:
                pair = self.d_tokenizer.lcut(candidate+miss_word)[0]
                if pair.flag == level_flag:
                    return candidate + miss_word

    def update(self,raw_address=""):
        if raw_address:
            self.raw_address = raw_address
            self.province = self.city = self.district = self.town = ''

            self.__park = self.__street = self.__number = self.__lane = \
                self.__yard = self.__building = self.__floor = self.__unit = \
                self.__room = None

        self.do_cut_address()

        for func in [self._find_province, self._find_city, self._find_district,
                     self._find_town]:
            r = func()
            if r:
                del self.cut_address[0]
                if not self.cut_address:
                    break

        self.detail = "".join(map(lambda x: x.word,self.cut_address))
        self.__detail = chi_to_dig(self.detail)
        return self
