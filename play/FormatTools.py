#!/usr/bin/python
# -*- coding: utf-8 -*
# Author: Yulore Technologies Inc.
# Version: 1.0.1
# Modified: @2018-04-19

"""This file is a set of python tools for deploying Yulore Technology products."""
"""Please use Python 2.7 as the python version."""


import datetime
import sys
import re
import time
import traceback


AREACODE_7 = ['0906', '0812', '0835', '0735', '0837', '0836', '0831', '0830', '0833', '0832', '0839',
              '0838', '0736', '0737', '0734', '0546', '0938', '0701', '0543', '0429', '0934', '0427',
              '0936', '0937', '0930', '0660', '0738', '0421', '0635', '0634', '0633', '0632', '0631',
              '0996', '0997', '0439', '0975', '0752', '0995', '0722', '0935', '0566', '0724', '0530',
              '0438', '0533', '0534', '0535', '0536', '0537', '0538', '0539', '0433', '0730', '0435',
              '0434', '0437', '0436', '0716', '0662', '0728', '0335', '0763', '0372', '0994', '0373',
              '0691', '0856', '0855', '0692', '0859', '0858', '0872', '0711', '0912', '0913', '0911',
              '0916', '0917', '0914', '0915', '0992', '0993', '0756', '0991', '0750', '0751', '0743',
              '0753', '0998', '0979', '0758', '0759', '0888', '0555', '0901', '0903', '0902', '0896',
              '0908', '0939', '0350', '0351', '0352', '0353', '0354', '0355', '0356', '0357', '0358',
              '0359', '0596', '0597', '0594', '0744', '0592', '0593', '0459', '0458', '0457', '0456',
              '0455', '0454', '0453', '0452', '0598', '0599', '0834', '0999', '0933', '0931', '0879',
              '0878', '0972', '0973', '0974', '0932', '0976', '0977', '0870', '0873', '0739', '0875',
              '0874', '0877', '0876', '0897', '0773', '0818', '0909', '0349', '0770', '0772', '0580',
              '0468', '0469', '0776', '0777', '0774', '0775', '0778', '0779', '0467', '0464', '0990',
              '0482', '0483', '0475', '0474', '0477', '0476', '0471', '0470', '0473', '0472', '0376',
              '0374', '0375', '0479', '0478', '0370', '0886', '0887', '0578', '0768', '0883', '0857',
              '0766', '0570', '0572', '0762', '0394', '0395', '0396', '0391', '0392', '0393', '0715',
              '0854', '0398', '0790', '0792', '0793', '0794', '0795', '0796', '0797', '0798', '0799',
              '0954', '0955', '0952', '0953', '0951', '0668', '0746', '0817', '0771', '0813', '0745',
              '0970', '0718', '0719', '0895', '0894', '0893', '0892', '0891', '0710', '0554', '0712',
              '0564', '0563', '0562', '0561', '0717', '0971', '0713', '0314', '0919', '0553', '0941',
              '0943', '0714', '0316', '0412', '0663', '0417', '0416', '0415', '0556', '0419', '0418',
              '0826', '0827', '0825', '0558', '0559', '0318', '0319', '0816', '0552', '0315', '0550',
              '0317', '0310', '0557', '0312', '0313']
# '0899', '0413' 现已不存在
AREACODE_8 = ['0515', '010', '0791', '0851', '0871', '0511', '0523', '0527', '0731', '0571', '0754',
              '0755', '0757', '0898', '0591', '0532', '0519', '025', '024', '027', '021', '020', '023',
              '022', '029', '028', '0531', '0411', '0577', '0518', '0379', '0431', '0377', '0514',
              '0432', '0512', '0513', '0510', '0371', '0760', '0516', '0595', '0769', '0579', '0517',
              '0574', '0575', '0576', '0551', '0311', '0451', '0573', '0899', '0413']


def format_telnum_BQC(tel):
    '''
    电话号码格式化的方法( 邦企查 项目使用)

    :param tel: 需要处理的电话号码
    :return: 返回处理后的号码；如果号码异常就返回error
    '''
    tel_num = tel.replace(' ', '').replace('　', '').replace(' ', '').replace('\t', '').strip()
    tel_num = tel_num.replace('(', '').replace(')', '').replace('-', '').replace('（', '')\
                        .replace('）', '').replace('——', '').replace('*', '')  # 去掉区号的符号
    # 去掉国码
    if tel_num.startswith('0+86'):
        tel_num = tel_num[4:]
    elif tel_num.startswith('0086'):
        tel_num = tel_num[4:]
    elif tel_num.startswith('+86'):
        tel_num = tel_num[3:]
    elif tel_num.startswith('086'):
        tel_num = tel_num[3:]

    result = re.match("^0{2,}", tel_num)
    if result != None:
        length = result.end() - result.start()
        tel_num = tel_num[length-1:]

    # print tel_num
    result_tel = ''
    if re.match('^\d{0,4}(4|8)00\d{7}$', tel_num) != None: # 判定为400或800电话
        if re.match("^(4|8)00\d{7}$", tel_num) != None:  # 正确的400或800的热线号码
            result_tel = tel_num
        elif re.match("^(04|08)00\d{7}$", tel_num) != None:  # 0400或0800的热线号码，去掉0
            result_tel = tel_num[1:]
        elif re.match("^0(10|2\d)(400|800)\d{7}$", tel_num) != None:  # 带有区号的400或800的热线号码，去掉区号
            result_tel = tel_num[3:]
        elif re.match("^0[3-9]\d{2}(400|800)\d{7}$", tel_num) != None:  # 带有区号的400或800的热线号码，去掉区号
            result_tel = tel_num[4:]
        else:
            result_tel = 'error'
    elif re.match('^1[3-9][\d]{9}$', tel_num) != None: # 正确的手机号码
        result_tel = tel_num
    else:
        areacode = 0
        if re.match('^0[3-9]\d{2}[\d]{7,12}$', tel_num) != None:
            areacode = tel_num[:4]
        elif re.match('^0(10|2\d)[\d]{7,12}$', tel_num) != None:
            areacode = tel_num[:3]
        if re.match('^[3-9]\d{2}[\d]{7,12}$', tel_num) != None:
            areacode = '0' + tel_num[:3]
            tel_num = '0' + tel_num
        elif re.match('^(10|2\d)[\d]{7,12}$', tel_num) != None:
            areacode = '0' + tel_num[:2]
            tel_num = '0' + tel_num
        # 开始处理区号
        if areacode != 0:
            if tel_num[:len(areacode)] in AREACODE_7:
                num = 7
            elif tel_num[:len(areacode)] in AREACODE_8:
                num = 8
            else:
                num = 0
                # print '区号错误!!!!', areacode, ',', tel
                result_tel = 'error'
            if num != 0:
                length = len(areacode) + num
                if len(tel_num) < length:
                    result_tel = 'error'
                else:
                    result_tel = tel_num[:len(areacode) + num]
        else:
            # print '错误！！！！',tel
            result_tel = 'error'
    return result_tel


def test_format_telnum_BQC():
    assert format_telnum_BQC('40088-10115') == '4008810115'
    assert format_telnum_BQC('010-40088-10115') == '4008810115'
    assert format_telnum_BQC('031540088-10115') == '4008810115'
    assert format_telnum_BQC('003-51252492-8') == '03512524928'
    assert format_telnum_BQC('075-52503013-6') == '075525030136'
    assert format_telnum_BQC('134-77261944-') == '13477261944'
    return


def check_tel(tel):
    # print tel
    special_call_tels = []
    result = False;
    pattern_0 = "^0[1-9]\d*$";  #可能是带有区号的座机号码
    pattern_1 = "^(4|8|04|08)00\d{7}$";  #400或800的热线号码
    pattern_2 = "^1(00|010|25|[3-9])\d*$";
    pattern_3 = "^(95|96)\d{3}$";  #95或96开头的热线号码
    pattern_6 = "^(125831|0125831|95013|095013|10193|10198)[\d]{9,12}$";  #移动副卡125831，联通的95013，10193，10198
    pattern_8 = "^(00852|\+852|00853)\d{4,8}$";  #香港电话,澳门电话
    pattern_9 = "^259\d{8}$";
    if len(tel) < 7:
        result = True;
    elif re.match(pattern_0, tel) != None:  #可能是带有区号的座机号码
        # 带区号号码
        pattern_area_1 = "^0(10|2\d)\d*$";#010或02*的区号"^\d{3}[1-9]\d{7}0$"
        pattern_area_1_1 = "^\d{3}([1-9]\d{2,7}|96\d{3,11}|95\d{3,17}|[4|8]00\d{7}|10\d*|116114)$";#96热线号码，和３大运营商
        pattern_area_1_2 = "^0101010\d{4}$";  # 北京的热线号码
        pattern_area_1_3 = "^\d{3}(125\d{9}|12590d{8})$";  # 带有区号的125号码，需要进一步处理
        pattern_area_1_4 = "^\d{3}\d{7,8}$";  # 带有区号的座机号码
        pattern_area_2 = "^0[3-9]\d{2}\d*$";  #４位的区号
        pattern_area_2_1 = "^\d{4}([1-8]\d{2,7}|96\d{3,11}|95\d{3,17}|[4|8]00\d{7}|10\d*|116114)$";  # 96、95热线号码，和３大运营商
        pattern_area_2_2 = "^\d{4}125\d{9}$";  # 带有区号的125号码
        pattern_area_2_3 = "^\d{4}\d{8}$";  # 带有区号的座机号码
        pattern_area_3 = "^012\d{9}$";  # 012+9位的号码
        pattern_area_4 = "^01259\d{7,8}$";  # 01259+9位的号码
        if re.match(pattern_area_1, tel) != None:
            if re.match(pattern_area_1_1, tel) != None:
                result = True;
            elif re.match(pattern_area_1_2, tel) != None:
                result = True;
            elif re.match(pattern_area_1_3, tel) != None:
                result = True;
            elif re.match(pattern_area_1_4, tel) != None:
                result = True;
        elif re.match(pattern_area_2, tel) != None:
            if re.match(pattern_area_2_1, tel) != None:
                result = True;
            elif re.match(pattern_area_2_2, tel) != None:
                result = True;
            elif re.match(pattern_area_2_3, tel) != None:
                result = True;
        elif re.match(pattern_area_3, tel) != None:
            result = True;
        elif re.match(pattern_area_4, tel) != None:
            result = True;
    elif re.match(pattern_1, tel) != None:  #400或800开头的热线号码
        result = True;
    elif re.match(pattern_2, tel) != None:
        # -----手机------106开头的短信平台号码------125开头的短信平台号码------1010开头的特殊号码
        if re.match("^1[3-9][\d]{9}$", tel) != None or re.match("^106[\d]{5,13}$", tel) != None \
                or re.match("^125[\d]{5,15}$", tel) != None or re.match("^179[\d]{13}$", tel) != None or re.match("^1010\d{4,8}$", tel) != None:
            result = True;
        elif re.match("^100(00|10|86)\d*$", tel) != None:
            result = True;
    elif re.match(pattern_3, tel) != None:  #95或96开头的热线号码
        result = True;
    elif re.match(pattern_6, tel) != None:  #移动副卡125831
        result = True;
    elif re.match(pattern_8, tel) != None:  #香港电话,澳门电话
        result = True;
    elif re.match(pattern_9, tel) != None:
        result = True;
    if not result:
        if tel in special_call_tels:
            result = True;
    return result


def format_telnum_CSF(telephone_number):
    '''
    电话号码格式化的方法( 催收分 项目使用)

    :param telephone_number: 需要处理的电话号码
    :return: 处理后的电话号码，如果不能处理就直接返回原号码
    '''
    try:
        # print telephone_number
        telephone_number = str(telephone_number)
        if telephone_number.count('@') > 0:
            return telephone_number
        if telephone_number.count('%') > 0:
            return telephone_number
        if telephone_number.count('->') > 0:
            return telephone_number
        tel_num = telephone_number.replace(' ', '').replace('　', '').replace(' ', '').replace('\t', '').strip()
        # tel_num = tel_num.replace('+', '')  # 去掉区号的加号
        tel_num = tel_num.replace('-', '')  # 去掉区号的横线
        tel_num = tel_num.replace('(', '').replace(')', '')  # 去掉区号的小括号
        if tel_num.startswith('0+86'):
            tel_num = tel_num[4:]
        elif tel_num.startswith('0+'):
            tel_num = tel_num[2:]

        # 去除特殊的空格
        chars = {
            '\xc2\x82': ',',  # High code comma
            '\xc2\x84': ',,',  # High code double comma
            '\xc2\x85': '...',  # Tripple dot
            '\xc2\x88': '^',  # High carat
            '\xc2\x91': '\x27',  # Forward single quote
            '\xc2\x92': '\x27',  # Reverse single quote
            '\xc2\x93': '\x22',  # Forward double quote
            '\xc2\x94': '\x22',  # Reverse double quote
            '\xc2\x95': ' ',
            '\xc2\x96': '-',  # High hyphen
            '\xc2\x97': '--',  # Double hyphen
            '\xc2\x99': ' ',
            '\xc2\xa0': ' ',
            '\xc2\xa6': '|',  # Split vertical bar
            '\xc2\xab': '<<',  # Double less than
            '\xc2\xbb': '>>',  # Double greater than
            '\xc2\xbc': '1/4',  # one quarter
            '\xc2\xbd': '1/2',  # one half
            '\xc2\xbe': '3/4',  # three quarters
            '\xca\xbf': '\x27',  # c-single quote
            '\xcc\xa8': '',  # modifier - under curve
            '\xcc\xb1': ''  # modifier - under line
        }
        tel_num = re.sub('(' + '|'.join(chars.keys()) + ')', '', tel_num)


        t = re.compile('[*0-9]+')
        ret = t.search(tel_num)
        if ret != None:
            tel_num = ret.group()

        if tel_num.find('.') != -1:
            tel_num = tel_num[0:tel_num.find('.')]
        if tel_num.startswith('86') and len(tel_num) > 6:
            tel_num = tel_num[2:]
        elif tel_num.startswith('+86') and len(tel_num) > 7:
            tel_num = tel_num[3:]
        elif tel_num.startswith('086') and len(tel_num) > 7:
            tel_num = tel_num[3:]
        elif tel_num.startswith('0086') and len(tel_num) > 8:
            tel_num = tel_num[4:]
        elif tel_num.startswith('00086') and len(tel_num) > 9:
            tel_num = tel_num[5:]
        elif tel_num.startswith('+1') and len(tel_num) == 12:  # 带有＋的手机号
            tel_num = tel_num[1:]
        elif re.match('^0(10|2\d)[1-9]\d{7}0$', tel_num) != None:  # 后面多了一个0
            tel_num = tel_num[0:-1]
        elif re.match('^(04|08)00\d{7}$', tel_num) != None:  # 0400或0800的热线号码，去掉0
            tel_num = tel_num[1:]
        elif re.match('^0(10|2\d)(400|800)\d{7}$', tel_num) != None:  # 带有区号的400或800的热线号码，去掉区号
            tel_num = tel_num[3:]
        elif re.match('^0[3-9]\d{2}(400|800)\d{7}$', tel_num) != None:  # 带有区号的400或800的热线号码，去掉区号
            tel_num = tel_num[4:]
        elif tel_num.startswith('+'):  # 加号开头的号码，替换为00
            tel_num = tel_num.replace('+', '00')
        elif re.match('^125831[\d]{9,12}$', tel_num) != None:  # 移动副卡125831
            tel_num = tel_num[6:]
        elif re.match('^0125831[\d]{9,12}$', tel_num) != None:  # 移动副卡125831
            tel_num = tel_num[7:]
        elif re.match('^950136[\d]{7,12}$', tel_num) != None:  # 联通的950136，10193，10198
            tel_num = tel_num[6:]
        elif re.match('^0950136[\d]{7,12}$', tel_num) != None:  # 联通的950136，10193，10198
            tel_num = tel_num[7:]
        elif re.match('^95013[\d]{7,12}$', tel_num) != None:  # 联通的95013，10193，10198
            tel_num = tel_num[5:]
        elif re.match('^095013[\d]{7,12}$', tel_num) != None:  # 联通的95013，10193，10198
            tel_num = tel_num[6:]
        elif re.match('^0(10|2\d)950136\d*$', tel_num) != None:
            tel_num = tel_num[9:]
        elif re.match('^0[3-9]\d{2}950136\d*$', tel_num) != None:
            tel_num = tel_num[10:]
        elif re.match('^10193[\d]{9,12}$', tel_num) != None:  # 联通的95013，10193，10198
            tel_num = tel_num[5:]
        elif re.match('^10198[\d]{9,12}$', tel_num) != None:  # 联通的95013，10193，10198
            tel_num = tel_num[5:]
        elif re.match('^09990(10|2\d)[\d]{7,8}$', tel_num) != None:  # 0999 - 021 - 座机号		去0999
            tel_num = tel_num[4:]
        elif re.match('^9501361[3-9][\d]{9}$', tel_num) != None:  # 950136 - 手机号码			去950136
            tel_num = tel_num[6:]
        elif re.match('^0(10|2\d)9501361[3-9][\d]{9}$', tel_num) != None:  # 0510 - 950136 - 11位数号码,去3/4位区号和950136
            tel_num = tel_num[9:]
        elif re.match('^0[3-9]\d{2}9501361[3-9][\d]{9}$', tel_num) != None:  # 0510 - 950136 - 11位数号码,去3/4位区号和950136
            tel_num = tel_num[10:]
        elif re.match('^17951[\d]{9,12}$', tel_num) != None:  # 17951 - 09312155980 		去17951
            tel_num = tel_num[5:]
        elif re.match('^0(10|2\d)1[3-9][\d]{9}$', tel_num) != None:  # 带有区号的手机号
            tel_num = tel_num[3:]
        elif re.match('^601[3-9][\d]{9}$', tel_num) != None:  # 60开头的手机号
            tel_num = tel_num[2:]
        elif re.match('^01[3-9][\d]{9}$', tel_num) != None:  # 0开头的手机号
            tel_num = tel_num[1:]
        elif re.match('^0[3-9]\d{2}1[3-9][\d]{9}$', tel_num) != None:  # 带有区号的手机号
            tel_num = tel_num[4:]
        elif re.match('^[3-9]\d{2}1[3-9][\d]{9}$', tel_num) != None:  # 带有区号，但是没有0的手机号
            tel_num = tel_num[3:]
        elif re.match('^(10|2\d)1[3-9][\d]{9}$', tel_num) != None:  # 带有区号，但是没有0的手机号
            tel_num = tel_num[2:]
        elif re.match('^0(10|2\d)0(10|2\d)[\d]{3,8}$', tel_num) != None:  # 带有两个区号的座机号
            area_code = tel_num[0:3]
            if tel_num.startswith(area_code + area_code):
                tel_num = tel_num[3:]
        elif re.match('^0[3-9]\d{2}0[3-9]\d{2}[\d]{3,8}$', tel_num) != None:  # 带有两个区号的座机号
            area_code = tel_num[0:4]
            if tel_num.startswith(area_code + area_code):
                tel_num = tel_num[4:]
        elif re.match("^00(10|2\d)\d*$", tel_num) != None:  # 0010或002*的区号"^\d{3}[1-9]\d{7}0$"
            tel_num = tel_num[1:]
        elif re.match("^0(10|2\d)95\d{3}$", tel_num) != None: # 带有区号的95号码
            tel_num = tel_num[3:]
        elif re.match("^0[3-9]\d{2}95\d{3}$", tel_num) != None: # 带有区号的95号码
            tel_num = tel_num[4:]
        elif re.match("^095\d{3}$", tel_num) != None: # 以0开头的95号码
            tel_num = tel_num[1:]
        elif re.match('^106980095\d{3}$', tel_num) != None:#  以1069800开头的95号码
            tel_num = tel_num[7:]
        elif re.match('^106902895\d{3}$', tel_num) != None: #  以1069028开头的95号码
            tel_num = tel_num[7:]
        elif re.match('^10659021195\d{3}$', tel_num) != None: #  以106590211开头的95号码
            tel_num = tel_num[9:]
        elif re.match("^0100(86|00|10|18)\d{0,2}$", tel_num) != None:
            tel_num = tel_num[1:]
        elif re.match("^1795100861\d{10}$", tel_num) != None: # 17951+0086+手机号码 17951008615083796613
            tel_num = tel_num[9:]
        elif re.match("^[\d][>][\d][>][\d]$", tel_num) != None: # 085188417719>13936955651>12599
            tel_num = tel_num.split('>')[0]
        elif re.match('^0(10|2\d)[\d]{3,8}[*][\d]{1,7}$', tel_num) != None:  #02188005850*8888116
            tel_num = tel_num.split('*')[0]
        elif re.match('^0[3-9]\d{2}[\d]{3,8}[*][\d]{1,7}$', tel_num) != None:   #045188005850*8888116
            tel_num = tel_num.split('*')[0]

        if not check_tel(tel_num):
            if tel_num.startswith('00'):
                if not check_tel(tel_num[1:]):
                    if not check_tel(tel_num[2:]):
                        # print 'Error ! &&&&&&&&&&&&&&&&&&& telephone_number = ' + str(telephone_number)
                        pass 
                    else:
                        tel_num = tel_num[2:]
                else:
                    tel_num = tel_num[1:]
            else:
                # 有些号码可能前面少0
                tel_num_0 = '0' + tel_num
                if not check_tel(tel_num_0):
                    if len(telephone_number) == 8 or len(telephone_number) == 7:  # 不带区号的座机
                        tel_num = telephone_number
                    else:
                        print ('Error ! **************** telephone_number = ' + str(telephone_number))
                        pass
                        # tel_num = telephone_number
                        # raise Exception
                else:
                    tel_num = tel_num_0
    except:
        print(traceback.format_exc())
        tel_num = telephone_number
    return tel_num


def test_format_telnum_CSF():
    assert format_telnum_CSF('+8618515977837') == '18515977837'
    assert format_telnum_CSF('+8601053186044') == '01053186044'
    assert format_telnum_CSF('0+8618515977837') == '18515977837'
    assert format_telnum_CSF('0+8601053186044') == '01053186044'
    assert format_telnum_CSF('8618515977837') == '18515977837'
    assert format_telnum_CSF('8601053186044') == '01053186044'
    assert format_telnum_CSF('0+18515977837') == '18515977837'
    assert format_telnum_CSF('0+01053186044') == '01053186044'
    assert format_telnum_CSF('08618515977837') == '18515977837'
    assert format_telnum_CSF('08601053186044') == '01053186044'
    assert format_telnum_CSF('008618515977837') == '18515977837'
    assert format_telnum_CSF('008601053186044') == '01053186044'
    assert format_telnum_CSF('+18515977837') == '18515977837'
    assert format_telnum_CSF('+01053186044') == '01053186044'
    assert format_telnum_CSF('Â 8615985868359') == '15985868359'
    assert format_telnum_CSF('010-086') == '10086'
    assert format_telnum_CSF('010-08611') == '1008611'
    assert format_telnum_CSF('04000618800') == '4000618800'
    assert format_telnum_CSF('075513825201200') == '13825201200'
    assert format_telnum_CSF('01001053186044') == '01053186044'
    assert format_telnum_CSF('1053186044') == '01053186044'
    assert format_telnum_CSF('75513825201200') == '13825201200'
    assert format_telnum_CSF('1013825201200') == '13825201200'
    assert format_telnum_CSF('013007997284') == '13007997284'
    assert format_telnum_CSF('0013007997284') == '13007997284'
    assert format_telnum_CSF('6018633199337') == '18633199337'
    assert format_telnum_CSF('001053186044') == '01053186044'
    assert format_telnum_CSF('075595511') == '95511'
    assert format_telnum_CSF('095511') == '95511'
    assert format_telnum_CSF('106980095533') == '95533'
    assert format_telnum_CSF('106902895577') == '95577'
    assert format_telnum_CSF('10659021195528') == '95528'
    assert format_telnum_CSF('12583118633199337') == '18633199337'
    assert format_telnum_CSF('012583118633199337') == '18633199337'
    assert format_telnum_CSF('95013618633199337') == '18633199337'
    assert format_telnum_CSF('095013618633199337') == '18633199337'
    assert format_telnum_CSF('1019318633199337') == '18633199337'
    assert format_telnum_CSF('1019818633199337') == '18633199337'
    assert format_telnum_CSF('1795118633199337') == '18633199337'
    assert format_telnum_CSF('17951008618633199337') == '18633199337'
    assert format_telnum_CSF('9516715151') == '09516715151'
    assert format_telnum_CSF('85291343060') == '085291343060'
    assert format_telnum_CSF('053110086') == '053110086'
    assert format_telnum_CSF('01010086') == '01010086'
    assert format_telnum_CSF('1069005501') == '01069005501'
    assert format_telnum_CSF('0271008611') == '0271008611'
    assert format_telnum_CSF('01053186044') == '01053186044'
    assert format_telnum_CSF('00861053186044') == '01053186044'
    assert format_telnum_CSF('861053186044') == '01053186044'
    assert format_telnum_CSF('+861053186044') == '01053186044'
    assert format_telnum_CSF('0+8675510086') == '075510086'
    assert format_telnum_CSF('051395075401') == '051395075401'
    assert format_telnum_CSF('085188417719>13936955651>12599') == '085188417719'
    assert format_telnum_CSF('02188005850*8888116') == '02188005850'
    assert format_telnum_CSF('045188005850*8888116') == '045188005850'
    print ("format_telnum_CSF() tested successfully.")
    return


def time_to_second(time_str):
    '''
    对通话时长进行格式化，转化成秒

    :param time_str: 通话时长字符串
    :return: 转换成秒
    '''
    result = 0
    tmp_time_str = str(time_str)
    if tmp_time_str == '':
        result = 0
    else:
        # 如果有汉字就将时间格式转化为 01:02:03 的格式
        tmp_time_str = tmp_time_str.replace('小时', ':')
        tmp_time_str = tmp_time_str.replace('时', ':')
        tmp_time_str = tmp_time_str.replace('分钟', ':')
        tmp_time_str = tmp_time_str.replace('分', ':')
        tmp_time_str = tmp_time_str.replace('秒', '')
        # 根据时间格式计算出通话时长为多少秒
        if tmp_time_str.find(':'):
            time_array = tmp_time_str.split(':')
            length = len(time_array)
            if length == 3:
                hour = int(time_array[0])
                minute = int(time_array[1])
                result = int(time_array[2]) + 60*minute + 60*60*hour
            elif length == 2:
                minute = int(time_array[0])
                if time_array[1] == '':
                    result = 60 * minute
                else:
                    result = int(time_array[1]) + 60 * minute
            elif length == 1:
                try:
                    result = int(float(time_array[0]))
                except ValueError:
                    result = 0
            else:
                raise Exception
        else:
            result = int(tmp_time_str)
    return result


def timestamp_to_datetime(time_st, date_format='%Y-%m-%d %H:%M:%S'):
    '''
    将时间戳转化为时间格式的字符串

    :param time_st: 要转换的时间戳，以秒为单位
    :param date_format: 传递进来的date_st是什么格式的，默认为：%Y-%m-%d %H:%M:%S
    :return: 转换好的日期格式字符串
    '''
    timestamp = int(time_st)
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    dt = time.strftime(date_format, time_local)
    return dt


def datetime_to_timestamp(date_st, date_format='%Y-%m-%d %H:%M:%S'):
    '''
    将时间格式的字符串转换为时间戳

    :param date_st: 要转换的时间字符串
    :param date_format: 传递进来的date_st是什么格式的，默认为：%Y-%m-%d %H:%M:%S
    :return: 时间戳，以秒为单位
    '''
    timeArray = time.strptime(date_st, date_format)
    timestamp = time.mktime(timeArray)
    return timestamp


def test_format_datatime():
    assert format_datatime('22OCT2017:12:49:30.000') == '2017-10-22 12:49:30'
    assert format_datatime('2016-08-31 15:50:00') == '2016-08-31 15:50:00'
    assert format_datatime('20160831155000') == '2016-08-31 15:50:00'
    assert format_datatime('2016-08-31 15:50') == '2016-08-31 15:50:00'
    assert format_datatime('2016-08-31/15:50:00') == '2016-08-31 15:50:00'
    assert format_datatime('08-31 15:50:00') == '2016-08-31 15:50:00'
    print ("test_format_datatime() tested successfully.")
    return


def format_datatime(time_str):
    '''
    对通话时间和爬取时间进行格式化

    :param time_str: 传进来的时间字符串
    :return: 输出的格式为‘2016-08-31　15:50:08’
    '''
    result_time_str = None
    # print time_str
    if re.match('^[0-9]*$', time_str) != None: # 全部都是数字
        if re.match('^\d{10}$', time_str) != None:  # 时间戳的格式
            result_time_str = timestamp_to_datetime(time_str)
        elif re.match('^\d{13}$', time_str) != None:  # 时间戳的格式
            time_str_new = int(time_str) / 1000
            result_time_str = timestamp_to_datetime(time_str_new)
        elif re.match('^\d{14}$', time_str) != None: # 如:20170117215641
            timeArray = time.strptime(time_str, "%Y%m%d%H%M%S")
            result_time_str = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        else:
            print ('1. Error Time : ' + time_str)
            raise Exception
    else: # 有特殊符号
        time_str = time_str.replace('年', '-').replace('月', '-').replace('日', '')
        if re.match('^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$', time_str) != None:  # 正确的格式
            result_time_str = time_str
        elif re.match('^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3,7}$', time_str) != None:  # 2017-06-02 13:51:07:007
            result_time_str = time_str[:19]
        elif re.match('^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:-0$', time_str) != None:  # 2017-04-30 20:17:-0
            result_time_str = time_str[:-2] + '00'
        elif re.match('^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3,7}$', time_str) != None:  # 22017-06-25 13:28:58.0000000
            result_time_str = time_str[:19]
        elif re.match('^\d{4} \d{2}-\d{1,2} \d{1,2}:\d{2}:\d{2}$', time_str) != None:# 如2017 08-31 15:50:08
            result_time_str = time_str.replace(' ', '-', 1)
        elif re.match('^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$', time_str) != None:# 如2016/08/31 15:50:08
            result_time_str = time_str.replace('/', '-')
        elif re.match('^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$', time_str) != None:# 如2016/08/31 15:50
            result_time_str = time_str.replace('/', '-') + ':00'
        elif re.match('^\d{4}-\d{1,2}-\d{1,2}/\d{1,2}:\d{2}:\d{2}$', time_str) != None:# 如2016-08-31/15:50:08
            result_time_str = time_str.replace('/', ' ')
        elif re.match('^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{2}$', time_str) != None:# 如2016-08-31 9:50
            result_time_str = time_str + ':00'
        elif re.match('^\d{2}-\d{2} \d{1,2}:\d{2}:\d{2}$', time_str) != None:# 如08-31 15:50:08
            if re.match('^(0[7-9]|1[0-2])-.*$', time_str):
                time_str_new = '2016-' + time_str
            elif re.match('^0[1-6]-.*$', time_str):
                time_str_new = '2017-' + time_str
            else:
                print ('2. Error Time : ' + time_str)
                raise Exception
            result_time_str = time_str_new
        elif re.match('^\d{2}[A-Za-z]{3}\d{4}:\d{2}:\d{2}:\d{2}$', time_str) != None:# 如 02JUN2017:07:59:06
            timeArray = time.strptime(time_str, '%d%b%Y:%H:%M:%S')
            result_time_str = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
        elif re.match('^\d{2}[A-Za-z]{3}\d{2}:\d{2}:\d{2}:\d{2}$', time_str) != None:# 如 02JUN17:07:59:06
            timeArray = time.strptime(time_str, '%d%b%y:%H:%M:%S')
            result_time_str = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
        elif re.match('^\d{2}[A-Za-z]{3}\d{4}:\d{2}:\d{2}:\d{2}.0{1,3}$', time_str) != None:# 如 22OCT2017:12:49:30.000
            timeArray = time.strptime(time_str.split('.')[0], '%d%b%Y:%H:%M:%S')
            result_time_str = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
        elif re.match('^\d{4}-\d{1,2}-\d{1,2}$', time_str) != None:# 如2016-08-31
            result_time_str = time_str + ' 23:59:59'
        else:
            print ('3. Error Time : ' + time_str)
            raise Exception
    return result_time_str


def test_all():
    test_format_telnum_CSF()
    test_format_telnum_BQC()
    test_format_datatime()
    print ("********  All test Finished !!!!!!   ********")


if __name__ == "__main__":
        l = ['6156509927',
'13621754242',
'3118741185',
'4326464317',
'7576325086',
'30178091789',
'5748471782',
'7315782238',
'05537250058/13635533203',
'7918452868',
'30178384368',
'797718038',
'72786651872',
'0.127722901',
]
for ll in l :
    print(ll, "===", format_telnum_BQC(ll))



