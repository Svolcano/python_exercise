
import re

class TelFormater():   
    
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
    
    @staticmethod
    def format(tel):
        # 去掉区号的符号
        if '*' in tel:
            tel = tel[:tel.index('*')]
        tel = list(tel)
        tel = [i for i in tel if i.isdigit() or i == '+']
        tel_num = ''.join(tel)
        # 去掉国码
        tel_num = re.sub("^[0|+][0|+]?86", '', tel_num, 1)
    
        #remove prefix 0 which more than 2
        tel_num = re.sub("^0{2,}", '', tel_num, 1)
        areacode = ''
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
        elif re.match('^1[3-9][\d]{9}$', tel_num) != None: # 正确的手机号码
            result_tel = tel_num
        else:
            if re.match('^0[3-9]\d{2}[\d]{7,12}$', tel_num) != None:
                areacode = tel_num[:4]
            elif re.match('^0(10|2\d)[\d]{7,12}$', tel_num) != None:
                areacode = tel_num[:3]
            elif re.match('^[3-9]\d{2}[\d]{7,12}$', tel_num) != None:
                areacode = '0' + tel_num[:3]
                tel_num = '0' + tel_num
            elif re.match('^(10|2\d)[\d]{7,12}$', tel_num) != None:
                areacode = '0' + tel_num[:2]
                tel_num = '0' + tel_num
            # 开始处理区号
            if areacode:
                lc = len(areacode)
                t_code = tel_num[:lc]
                num = 0
                if t_code in TelFormater.AREACODE_7:
                    num = 7
                elif t_code in TelFormater.AREACODE_8:
                    num = 8
                if num != 0:
                    length = lc + num
                    if len(tel_num) >= length:
                        result_tel = tel_num[:lc] + '-' + tel_num[lc:length]
        return result_tel, areacode

    @staticmethod
    def get_tels(src):
        """
        :param src: input string
        :return: company name in input
        """
        res = []
        if not src:
            return res
        mobile_pattern = '(13[0-9]\d{8}|14[579]\d{8}|15[0-3,5-9]\d{8}|16[6]\d{8}|17[0135678]\d{8}|18[0-9]\d{8}|19[89]\d{8})'
        all_mobile = re.findall(mobile_pattern, src)
        res.extend(all_mobile)
        fix_pattern = "0[0-9]{2,3}-?[2-9][0-9]{6,8}"
        all_fixed = re.findall(fix_pattern, src)
        res.extend(all_fixed)
        return res


if __name__ == "__main__":
    tel = '010-56215826'
    a = TelFormater.format(tel)
    print(a)




