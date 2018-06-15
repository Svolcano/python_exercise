#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import re
import traceback

AREA_CODE = {
    "00852": {
        "province": "香港",
        "city": "香港"
    },
    "00853": {
        "province": "澳门",
        "city": "澳门"
    },
    "00886": {
        "province": "台湾",
        "city": "台湾"
    },
    "010": {
        "province": "北京",
        "city": ""
    },
    "0834": {
        "province": "四川",
        "city": "凉山"
    },
    "0837": {
        "province": "四川",
        "city": "阿坝"
    },
    "0836": {
        "province": "四川",
        "city": "甘孜"
    },
    "0831": {
        "province": "四川",
        "city": "宜宾"
    },
    "0830": {
        "province": "四川",
        "city": "泸州"
    },
    "0833": {
        "province": "四川",
        "city": "乐山"
    },
    "0832": {
        "province": "四川",
        "city": "内江"
    },
    "0429": {
        "province": "辽宁",
        "city": "葫芦岛"
    },
    "0839": {
        "province": "四川",
        "city": "广元"
    },
    "0838": {
        "province": "四川",
        "city": "德阳"
    },
    "0736": {
        "province": "湖南",
        "city": "常德"
    },
    "0737": {
        "province": "湖南",
        "city": "益阳"
    },
    "0734": {
        "province": "湖南",
        "city": "衡阳"
    },
    "0546": {
        "province": "山东",
        "city": "东营"
    },
    "0938": {
        "province": "甘肃",
        "city": "天水"
    },
    "0939": {
        "province": "甘肃",
        "city": "陇南"
    },
    "0543": {
        "province": "山东",
        "city": "滨州"
    },
    "0731": {
        "province": "湖南",
        "city": "长沙"
    },
    "0934": {
        "province": "甘肃",
        "city": "庆阳"
    },
    "0312": {
        "province": "河北",
        "city": "保定"
    },
    "0936": {
        "province": "甘肃",
        "city": "张掖"
    },
    "0937": {
        "province": "甘肃",
        "city": "酒泉"
    },
    "0930": {
        "province": "甘肃",
        "city": "临夏"
    },
    "0931": {
        "province": "甘肃",
        "city": "兰州"
    },
    "0738": {
        "province": "湖南",
        "city": "娄底"
    },
    "0739": {
        "province": "湖南",
        "city": "邵阳"
    },
    "0635": {
        "province": "山东",
        "city": "聊城"
    },
    "0634": {
        "province": "山东",
        "city": "莱芜"
    },
    "0633": {
        "province": "山东",
        "city": "日照"
    },
    "0632": {
        "province": "山东",
        "city": "枣庄"
    },
    "0631": {
        "province": "山东",
        "city": "威海"
    },
    "0996": {
        "province": "新疆",
        "city": "库尔勒"
    },
    "0870": {
        "province": "云南",
        "city": "昭通"
    },
    "0457": {
        "province": "黑龙江",
        "city": "大兴安岭"
    },
    "0997": {
        "province": "新疆",
        "city": "阿克苏"
    },
    "0439": {
        "province": "吉林",
        "city": "白山"
    },
    "0975": {
        "province": "青海",
        "city": "果洛"
    },
    "0994": {
        "province": "新疆",
        "city": "昌吉"
    },
    "0438": {
        "province": "吉林",
        "city": "松原"
    },
    "0995": {
        "province": "新疆",
        "city": "吐鲁番"
    },
    "025": {
        "province": "江苏",
        "city": "南京"
    },
    "024": {
        "province": "辽宁",
        "city": "沈阳"
    },
    "027": {
        "province": "湖北",
        "city": "江汉"
    },
    "0722": {
        "province": "湖北",
        "city": "随州"
    },
    "021": {
        "province": "上海",
        "city": ""
    },
    "020": {
        "province": "广东",
        "city": "广州"
    },
    "023": {
        "province": "重庆",
        "city": ""
    },
    "022": {
        "province": "天津",
        "city": ""
    },
    "029": {
        "province": "陕西",
        "city": "西安"
    },
    "028": {
        "province": "四川",
        "city": "眉山"
    },
    "0535": {
        "province": "山东",
        "city": "烟台"
    },
    "0530": {
        "province": "山东",
        "city": "菏泽"
    },
    "0531": {
        "province": "山东",
        "city": "济南"
    },
    "0532": {
        "province": "山东",
        "city": "青岛"
    },
    "0533": {
        "province": "山东",
        "city": "淄博"
    },
    "0534": {
        "province": "山东",
        "city": "德州"
    },
    "0724": {
        "province": "湖北",
        "city": "荆门"
    },
    "0536": {
        "province": "山东",
        "city": "潍坊"
    },
    "0537": {
        "province": "山东",
        "city": "济宁"
    },
    "0431": {
        "province": "吉林",
        "city": "长春"
    },
    "0539": {
        "province": "山东",
        "city": "临沂"
    },
    "0433": {
        "province": "吉林",
        "city": "延边"
    },
    "0379": {
        "province": "河南",
        "city": "洛阳"
    },
    "0435": {
        "province": "吉林",
        "city": "通化"
    },
    "0434": {
        "province": "吉林",
        "city": "四平"
    },
    "0437": {
        "province": "吉林",
        "city": "辽源"
    },
    "0436": {
        "province": "吉林",
        "city": "白城"
    },
    "0538": {
        "province": "山东",
        "city": "泰安"
    },
    "0896": {
        "province": "西藏",
        "city": "那曲"
    },
    "0716": {
        "province": "湖北",
        "city": "荆州"
    },
    "0757": {
        "province": "广东",
        "city": "佛山"
    },
    "0728": {
        "province": "湖北",
        "city": "仙桃"
    },
    "0872": {
        "province": "云南",
        "city": "大理"
    },
    "0455": {
        "province": "黑龙江",
        "city": "绥化"
    },
    "0717": {
        "province": "湖北",
        "city": "宜昌"
    },
    "0470": {
        "province": "内蒙古",
        "city": "呼伦贝尔"
    },
    "0335": {
        "province": "河北",
        "city": "秦皇岛"
    },
    "0432": {
        "province": "吉林",
        "city": "吉林"
    },
    "0763": {
        "province": "广东",
        "city": "清远"
    },
    "0663": {
        "province": "广东",
        "city": "揭阳"
    },
    "0479": {
        "province": "内蒙古",
        "city": "锡林郭勒盟"
    },
    "0478": {
        "province": "内蒙古",
        "city": "巴彦淖尔"
    },
    "0853": {
        "province": "贵州",
        "city": "安顺"
    },
    "0852": {
        "province": "贵州",
        "city": "遵义"
    },
    "0851": {
        "province": "贵州",
        "city": "贵阳"
    },
    "0857": {
        "province": "贵州",
        "city": "毕节"
    },
    "0856": {
        "province": "贵州",
        "city": "铜仁"
    },
    "0855": {
        "province": "贵州",
        "city": "黔东南"
    },
    "0854": {
        "province": "贵州",
        "city": "黔南"
    },
    "0859": {
        "province": "贵州",
        "city": "黔西南"
    },
    "0858": {
        "province": "贵州",
        "city": "六盘水"
    },
    "0523": {
        "province": "江苏",
        "city": "泰州"
    },
    "0762": {
        "province": "广东",
        "city": "河源"
    },
    "0527": {
        "province": "江苏",
        "city": "宿迁"
    },
    "0912": {
        "province": "陕西",
        "city": "榆林"
    },
    "0913": {
        "province": "陕西",
        "city": "渭南"
    },
    "0911": {
        "province": "陕西",
        "city": "延安"
    },
    "0916": {
        "province": "陕西",
        "city": "汉中"
    },
    "0917": {
        "province": "陕西",
        "city": "宝鸡"
    },
    "0914": {
        "province": "陕西",
        "city": "商洛"
    },
    "0915": {
        "province": "陕西",
        "city": "安康"
    },
    "0754": {
        "province": "广东",
        "city": "汕头"
    },
    "0755": {
        "province": "广东",
        "city": "深圳"
    },
    "0756": {
        "province": "广东",
        "city": "珠海"
    },
    "0991": {
        "province": "新疆",
        "city": "乌鲁木齐"
    },
    "0750": {
        "province": "广东",
        "city": "江门"
    },
    "0751": {
        "province": "广东",
        "city": "韶关"
    },
    "0752": {
        "province": "广东",
        "city": "惠州"
    },
    "0753": {
        "province": "广东",
        "city": "梅州"
    },
    "0769": {
        "province": "广东",
        "city": "东莞"
    },
    "0998": {
        "province": "新疆",
        "city": "喀什"
    },
    "0999": {
        "province": "新疆",
        "city": "伊犁"
    },
    "0758": {
        "province": "广东",
        "city": "肇庆"
    },
    "0759": {
        "province": "广东",
        "city": "湛江"
    },
    "0768": {
        "province": "广东",
        "city": "潮州"
    },
    "0888": {
        "province": "云南",
        "city": "丽江"
    },
    "0883": {
        "province": "云南",
        "city": "临沧"
    },
    "0735": {
        "province": "湖南",
        "city": "郴州"
    },
    "0901": {
        "province": "新疆",
        "city": "塔城"
    },
    "0903": {
        "province": "新疆",
        "city": "和田"
    },
    "0902": {
        "province": "新疆",
        "city": "哈密"
    },
    "0909": {
        "province": "新疆",
        "city": "博乐"
    },
    "0908": {
        "province": "新疆",
        "city": "克州"
    },
    "0350": {
        "province": "山西",
        "city": "忻州"
    },
    "0351": {
        "province": "山西",
        "city": "太原"
    },
    "0352": {
        "province": "山西",
        "city": "大同"
    },
    "0766": {
        "province": "广东",
        "city": "云浮"
    },
    "0354": {
        "province": "山西",
        "city": "晋中"
    },
    "0730": {
        "province": "湖南",
        "city": "岳阳"
    },
    "0518": {
        "province": "江苏",
        "city": "连云港"
    },
    "0519": {
        "province": "江苏",
        "city": "常州"
    },
    "0516": {
        "province": "江苏",
        "city": "徐州"
    },
    "0517": {
        "province": "江苏",
        "city": "淮安"
    },
    "0514": {
        "province": "江苏",
        "city": "扬州"
    },
    "0515": {
        "province": "江苏",
        "city": "盐城"
    },
    "0512": {
        "province": "江苏",
        "city": "苏州"
    },
    "0513": {
        "province": "江苏",
        "city": "南通"
    },
    "0510": {
        "province": "江苏",
        "city": "无锡"
    },
    "0511": {
        "province": "江苏",
        "city": "镇江"
    },
    "0596": {
        "province": "福建",
        "city": "漳州"
    },
    "0597": {
        "province": "福建",
        "city": "龙岩"
    },
    "0594": {
        "province": "福建",
        "city": "莆田"
    },
    "0595": {
        "province": "福建",
        "city": "泉州"
    },
    "0592": {
        "province": "福建",
        "city": "厦门"
    },
    "0593": {
        "province": "福建",
        "city": "宁德"
    },
    "0459": {
        "province": "黑龙江",
        "city": "大庆"
    },
    "0591": {
        "province": "福建",
        "city": "福州"
    },
    "0660": {
        "province": "广东",
        "city": "汕尾"
    },
    "0456": {
        "province": "黑龙江",
        "city": "黑河"
    },
    "0662": {
        "province": "广东",
        "city": "阳江"
    },
    "0454": {
        "province": "黑龙江",
        "city": "佳木斯"
    },
    "0453": {
        "province": "黑龙江",
        "city": "牡丹江"
    },
    "0452": {
        "province": "黑龙江",
        "city": "齐齐哈尔"
    },
    "0451": {
        "province": "黑龙江",
        "city": "哈尔滨"
    },
    "0599": {
        "province": "福建",
        "city": "南平"
    },
    "0358": {
        "province": "山西",
        "city": "吕梁"
    },
    "0835": {
        "province": "四川",
        "city": "雅安"
    },
    "0933": {
        "province": "甘肃",
        "city": "平凉"
    },
    "0906": {
        "province": "新疆",
        "city": "阿勒泰"
    },
    "0970": {
        "province": "青海",
        "city": "海北"
    },
    "0971": {
        "province": "青海",
        "city": "西宁"
    },
    "0972": {
        "province": "青海",
        "city": "海东"
    },
    "0973": {
        "province": "青海",
        "city": "黄南"
    },
    "0974": {
        "province": "青海",
        "city": "海南"
    },
    "0932": {
        "province": "甘肃",
        "city": "定西"
    },
    "0976": {
        "province": "青海",
        "city": "玉树"
    },
    "0977": {
        "province": "青海",
        "city": "德令哈"
    },
    "0871": {
        "province": "云南",
        "city": "昆明"
    },
    "0979": {
        "province": "青海",
        "city": "格尔木"
    },
    "0873": {
        "province": "云南",
        "city": "红河"
    },
    "0421": {
        "province": "辽宁",
        "city": "朝阳"
    },
    "0875": {
        "province": "云南",
        "city": "保山"
    },
    "0874": {
        "province": "云南",
        "city": "曲靖"
    },
    "0877": {
        "province": "云南",
        "city": "玉溪"
    },
    "0876": {
        "province": "云南",
        "city": "文山"
    },
    "0897": {
        "province": "西藏",
        "city": "阿里"
    },
    "0773": {
        "province": "广西",
        "city": "桂林"
    },
    "0349": {
        "province": "山西",
        "city": "朔州"
    },
    "0879": {
        "province": "云南",
        "city": "普洱"
    },
    "0772": {
        "province": "广西",
        "city": "来宾"
    },
    "0580": {
        "province": "浙江",
        "city": "舟山"
    },
    "0770": {
        "province": "广西",
        "city": "防城港"
    },
    "0771": {
        "province": "广西",
        "city": "南宁"
    },
    "0776": {
        "province": "广西",
        "city": "百色"
    },
    "0777": {
        "province": "广西",
        "city": "钦州"
    },
    "0774": {
        "province": "广西",
        "city": "梧州"
    },
    "0775": {
        "province": "广西",
        "city": "贵港"
    },
    "0778": {
        "province": "广西",
        "city": "河池"
    },
    "0779": {
        "province": "广西",
        "city": "北海"
    },
    "0467": {
        "province": "黑龙江",
        "city": "鸡西"
    },
    "0464": {
        "province": "黑龙江",
        "city": "七台河"
    },
    "0550": {
        "province": "安徽",
        "city": "滁州"
    },
    "0353": {
        "province": "山西",
        "city": "阳泉"
    },
    "0711": {
        "province": "湖北",
        "city": "鄂州"
    },
    "0482": {
        "province": "内蒙古",
        "city": "兴安盟"
    },
    "0483": {
        "province": "内蒙古",
        "city": "阿拉善盟"
    },
    "0878": {
        "province": "云南",
        "city": "楚雄"
    },
    "0894": {
        "province": "西藏",
        "city": "林芝"
    },
    "0746": {
        "province": "湖南",
        "city": "永州"
    },
    "0760": {
        "province": "广东",
        "city": "中山"
    },
    "0410": {
        "province": "辽宁",
        "city": "铁岭"
    },
    "0941": {
        "province": "甘肃",
        "city": "甘南"
    },
    "0899": {
        "province": "海南",
        "city": "三亚"
    },
    "0375": {
        "province": "河南",
        "city": "平顶山"
    },
    "0691": {
        "province": "云南",
        "city": "西双版纳"
    },
    "0355": {
        "province": "山西",
        "city": "长治"
    },
    "0475": {
        "province": "内蒙古",
        "city": "通辽"
    },
    "0474": {
        "province": "内蒙古",
        "city": "乌兰察布"
    },
    "0477": {
        "province": "内蒙古",
        "city": "鄂尔多斯"
    },
    "0476": {
        "province": "内蒙古",
        "city": "赤峰"
    },
    "0471": {
        "province": "内蒙古",
        "city": "呼和浩特"
    },
    "0356": {
        "province": "山西",
        "city": "晋城"
    },
    "0473": {
        "province": "内蒙古",
        "city": "乌海"
    },
    "0472": {
        "province": "内蒙古",
        "city": "包头"
    },
    "0376": {
        "province": "河南",
        "city": "信阳"
    },
    "0377": {
        "province": "河南",
        "city": "南阳"
    },
    "0374": {
        "province": "河南",
        "city": "许昌"
    },
    "0357": {
        "province": "山西",
        "city": "临汾"
    },
    "0372": {
        "province": "河南",
        "city": "安阳"
    },
    "0373": {
        "province": "河南",
        "city": "新乡"
    },
    "0370": {
        "province": "河南",
        "city": "商丘"
    },
    "0371": {
        "province": "河南",
        "city": "郑州"
    },
    "0598": {
        "province": "福建",
        "city": "三明"
    },
    "0886": {
        "province": "云南",
        "city": "怒江"
    },
    "0887": {
        "province": "云南",
        "city": "迪庆"
    },
    "0578": {
        "province": "浙江",
        "city": "丽水"
    },
    "0579": {
        "province": "浙江",
        "city": "金华"
    },
    "0935": {
        "province": "甘肃",
        "city": "武威"
    },
    "0359": {
        "province": "山西",
        "city": "运城"
    },
    "0574": {
        "province": "浙江",
        "city": "宁波"
    },
    "0575": {
        "province": "浙江",
        "city": "绍兴"
    },
    "0576": {
        "province": "浙江",
        "city": "台州"
    },
    "0577": {
        "province": "浙江",
        "city": "温州"
    },
    "0570": {
        "province": "浙江",
        "city": "衢州"
    },
    "0571": {
        "province": "浙江",
        "city": "杭州"
    },
    "0572": {
        "province": "浙江",
        "city": "湖州"
    },
    "0573": {
        "province": "浙江",
        "city": "嘉兴"
    },
    "0394": {
        "province": "河南",
        "city": "周口"
    },
    "0395": {
        "province": "河南",
        "city": "漯河"
    },
    "0396": {
        "province": "河南",
        "city": "驻马店"
    },
    "0391": {
        "province": "河南",
        "city": "焦作"
    },
    "0392": {
        "province": "河南",
        "city": "鹤壁"
    },
    "0393": {
        "province": "河南",
        "city": "濮阳"
    },
    "0715": {
        "province": "湖北",
        "city": "咸宁"
    },
    "0745": {
        "province": "湖南",
        "city": "怀化"
    },
    "0692": {
        "province": "云南",
        "city": "德宏"
    },
    "0398": {
        "province": "河南",
        "city": "三门峡"
    },
    "0827": {
        "province": "四川",
        "city": "巴中"
    },
    "0790": {
        "province": "江西",
        "city": "新余"
    },
    "0791": {
        "province": "江西",
        "city": "南昌"
    },
    "0792": {
        "province": "江西",
        "city": "九江"
    },
    "0793": {
        "province": "江西",
        "city": "上饶"
    },
    "0794": {
        "province": "江西",
        "city": "抚州"
    },
    "0795": {
        "province": "江西",
        "city": "宜春"
    },
    "0796": {
        "province": "江西",
        "city": "吉安"
    },
    "0797": {
        "province": "江西",
        "city": "赣州"
    },
    "0798": {
        "province": "江西",
        "city": "景德镇"
    },
    "0799": {
        "province": "江西",
        "city": "萍乡"
    },
    "0954": {
        "province": "宁夏",
        "city": "固原"
    },
    "0557": {
        "province": "安徽",
        "city": "宿州"
    },
    "0952": {
        "province": "宁夏",
        "city": "石嘴山"
    },
    "0953": {
        "province": "宁夏",
        "city": "吴忠"
    },
    "0951": {
        "province": "宁夏",
        "city": "银川"
    },
    "0668": {
        "province": "广东",
        "city": "茂名"
    },
    "0955": {
        "province": "宁夏",
        "city": "中卫"
    },
    "0818": {
        "province": "四川",
        "city": "达州"
    },
    "0817": {
        "province": "四川",
        "city": "南充"
    },
    "0816": {
        "province": "四川",
        "city": "绵阳"
    },
    "0813": {
        "province": "四川",
        "city": "自贡"
    },
    "0812": {
        "province": "四川",
        "city": "攀枝花"
    },
    "0718": {
        "province": "湖北",
        "city": "恩施"
    },
    "0719": {
        "province": "湖北",
        "city": "十堰"
    },
    "0895": {
        "province": "西藏",
        "city": "昌都"
    },
    "0744": {
        "province": "湖南",
        "city": "张家界"
    },
    "0893": {
        "province": "西藏",
        "city": "山南"
    },
    "0892": {
        "province": "西藏",
        "city": "日喀则"
    },
    "0891": {
        "province": "西藏",
        "city": "拉萨"
    },
    "0710": {
        "province": "湖北",
        "city": "襄阳"
    },
    "0566": {
        "province": "安徽",
        "city": "池州"
    },
    "0565": {
        "province": "安徽",
        "city": "巢湖"
    },
    "0564": {
        "province": "安徽",
        "city": "六安"
    },
    "0563": {
        "province": "安徽",
        "city": "宣城"
    },
    "0562": {
        "province": "安徽",
        "city": "铜陵"
    },
    "0561": {
        "province": "安徽",
        "city": "淮北"
    },
    "0898": {
        "province": "海南",
        "city": "海口"
    },
    "0458": {
        "province": "黑龙江",
        "city": "伊春"
    },
    "0712": {
        "province": "湖北",
        "city": "孝感"
    },
    "0713": {
        "province": "湖北",
        "city": "黄冈"
    },
    "0314": {
        "province": "河北",
        "city": "承德"
    },
    "0919": {
        "province": "陕西",
        "city": "铜川"
    },
    "0427": {
        "province": "辽宁",
        "city": "盘锦"
    },
    "0315": {
        "province": "河北",
        "city": "唐山"
    },
    "0992": {
        "province": "新疆",
        "city": "奎屯"
    },
    "0993": {
        "province": "新疆",
        "city": "石河子"
    },
    "0943": {
        "province": "甘肃",
        "city": "白银"
    },
    "0714": {
        "province": "湖北",
        "city": "黄石"
    },
    "0701": {
        "province": "江西",
        "city": "鹰潭"
    },
    "0413": {
        "province": "辽宁",
        "city": "抚顺"
    },
    "0412": {
        "province": "辽宁",
        "city": "鞍山"
    },
    "0411": {
        "province": "辽宁",
        "city": "大连"
    },
    "0551": {
        "province": "安徽",
        "city": "合肥"
    },
    "0417": {
        "province": "辽宁",
        "city": "营口"
    },
    "0416": {
        "province": "辽宁",
        "city": "锦州"
    },
    "0415": {
        "province": "辽宁",
        "city": "丹东"
    },
    "0414": {
        "province": "辽宁",
        "city": "本溪"
    },
    "0556": {
        "province": "安徽",
        "city": "安庆"
    },
    "0419": {
        "province": "辽宁",
        "city": "辽阳"
    },
    "0418": {
        "province": "辽宁",
        "city": "阜新"
    },
    "0826": {
        "province": "四川",
        "city": "广安"
    },
    "0743": {
        "province": "湖南",
        "city": "吉首"
    },
    "0825": {
        "province": "四川",
        "city": "遂宁"
    },
    "0558": {
        "province": "安徽",
        "city": "亳州"
    },
    "0559": {
        "province": "安徽",
        "city": "黄山"
    },
    "0318": {
        "province": "河北",
        "city": "衡水"
    },
    "0319": {
        "province": "河北",
        "city": "邢台"
    },
    "0313": {
        "province": "河北",
        "city": "张家口"
    },
    "0990": {
        "province": "新疆",
        "city": "克拉玛依"
    },
    "0552": {
        "province": "安徽",
        "city": "蚌埠"
    },
    "0553": {
        "province": "安徽",
        "city": "芜湖"
    },
    "0316": {
        "province": "河北",
        "city": "廊坊"
    },
    "0317": {
        "province": "河北",
        "city": "沧州"
    },
    "0310": {
        "province": "河北",
        "city": "邯郸"
    },
    "0311": {
        "province": "河北",
        "city": "石家庄"
    },
    "0554": {
        "province": "安徽",
        "city": "淮南"
    },
    "0555": {
        "province": "安徽",
        "city": "马鞍山"
    }
}
CITYINFO = {
    "宁波": {
        "province": "浙江",
        "prov_city": "宁波"
    },
    "重庆": {
        "province": "",
        "prov_city": "重庆"
    },
    "无锡": {
        "province": "江苏",
        "prov_city": "江苏无锡"
    },
    "仁怀": {
        "province": "贵州",
        "prov_city": "贵州仁怀"
    },
    "南充": {
        "province": "四川",
        "prov_city": "四川南充"
    },
    "漳州": {
        "province": "福建",
        "prov_city": "福建漳州"
    },
    "奎屯": {
        "province": "新疆",
        "prov_city": "新疆奎屯"
    },
    "当阳": {
        "province": "湖北",
        "prov_city": "湖北当阳"
    },
    "哈密": {
        "province": "新疆",
        "prov_city": "新疆哈密"
    },
    "铜仁": {
        "province": "贵州",
        "prov_city": "贵州铜仁"
    },
    "邛崃": {
        "province": "四川",
        "prov_city": "四川邛崃"
    },
    "清远": {
        "province": "广东",
        "prov_city": "广东清远"
    },
    "沅江": {
        "province": "湖南",
        "prov_city": "湖南沅江"
    },
    "衡水": {
        "province": "河北",
        "prov_city": "河北衡水"
    },
    "枣庄": {
        "province": "山东",
        "prov_city": "山东枣庄"
    },
    "龙井": {
        "province": "吉林",
        "prov_city": "吉林龙井"
    },
    "永康": {
        "province": "浙江",
        "prov_city": "浙江永康"
    },
    "高碑店": {
        "province": "河北",
        "prov_city": "河北高碑店"
    },
    "莆田": {
        "province": "福建",
        "prov_city": "福建莆田"
    },
    "佛山": {
        "province": "广东",
        "prov_city": "广东佛山"
    },
    "镶黄旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古镶黄旗"
    },
    "邹城": {
        "province": "山东",
        "prov_city": "山东邹城"
    },
    "石河子": {
        "province": "新疆",
        "prov_city": "新疆石河子"
    },
    "张家港": {
        "province": "江苏",
        "prov_city": "江苏张家港"
    },
    "塔城": {
        "province": "新疆",
        "prov_city": "新疆塔城"
    },
    "桂平": {
        "province": "广西",
        "prov_city": "广西桂平"
    },
    "鹰潭": {
        "province": "江西",
        "prov_city": "江西鹰潭"
    },
    "安丘": {
        "province": "山东",
        "prov_city": "山东安丘"
    },
    "三亚": {
        "province": "海南",
        "prov_city": "海南三亚"
    },
    "恩施": {
        "province": "湖北",
        "prov_city": "湖北恩施"
    },
    "兴化": {
        "province": "江苏",
        "prov_city": "江苏兴化"
    },
    "准格尔旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古准格尔旗"
    },
    "德州": {
        "province": "山东",
        "prov_city": "山东德州"
    },
    "阿拉善左旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古阿拉善左旗"
    },
    "吕梁": {
        "province": "山西",
        "prov_city": "山西吕梁"
    },
    "鸡西": {
        "province": "黑龙江",
        "prov_city": "黑龙江鸡西"
    },
    "东阳": {
        "province": "浙江",
        "prov_city": "浙江东阳"
    },
    "宜宾": {
        "province": "四川",
        "prov_city": "四川宜宾"
    },
    "安阳": {
        "province": "河南",
        "prov_city": "河南安阳"
    },
    "江阴": {
        "province": "江苏",
        "prov_city": "江苏江阴"
    },
    "通辽": {
        "province": "内蒙古",
        "prov_city": "内蒙古通辽"
    },
    "宿迁": {
        "province": "江苏",
        "prov_city": "江苏宿迁"
    },
    "杭锦旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古杭锦旗"
    },
    "科尔沁右翼中旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古科尔沁右翼中旗"
    },
    "乐平": {
        "province": "江西",
        "prov_city": "江西乐平"
    },
    "黑河": {
        "province": "黑龙江",
        "prov_city": "黑龙江黑河"
    },
    "保山": {
        "province": "云南",
        "prov_city": "云南保山"
    },
    "五常": {
        "province": "黑龙江",
        "prov_city": "黑龙江五常"
    },
    "乐陵": {
        "province": "山东",
        "prov_city": "山东乐陵"
    },
    "库伦旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古库伦旗"
    },
    "阿拉尔": {
        "province": "新疆",
        "prov_city": "新疆阿拉尔"
    },
    "楚雄": {
        "province": "云南",
        "prov_city": "云南楚雄"
    },
    "厦门": {
        "province": "福建",
        "prov_city": "福建厦门"
    },
    "铁力": {
        "province": "黑龙江",
        "prov_city": "黑龙江铁力"
    },
    "宿州": {
        "province": "安徽",
        "prov_city": "安徽宿州"
    },
    "洪江": {
        "province": "湖南",
        "prov_city": "湖南洪江"
    },
    "安国": {
        "province": "河北",
        "prov_city": "河北安国"
    },
    "南宁": {
        "province": "广西",
        "prov_city": "广西南宁"
    },
    "东台": {
        "province": "江苏",
        "prov_city": "江苏东台"
    },
    "青州": {
        "province": "山东",
        "prov_city": "山东青州"
    },
    "鄂伦春自治旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古鄂伦春自治旗"
    },
    "老河口": {
        "province": "湖北",
        "prov_city": "湖北老河口"
    },
    "都匀": {
        "province": "贵州",
        "prov_city": "贵州都匀"
    },
    "揭阳": {
        "province": "广东",
        "prov_city": "广东揭阳"
    },
    "伊春": {
        "province": "黑龙江",
        "prov_city": "黑龙江伊春"
    },
    "三门峡": {
        "province": "河南",
        "prov_city": "河南三门峡"
    },
    "麻城": {
        "province": "湖北",
        "prov_city": "湖北麻城"
    },
    "柳州": {
        "province": "广西",
        "prov_city": "广西柳州"
    },
    "正蓝旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古正蓝旗"
    },
    "四会": {
        "province": "广东",
        "prov_city": "广东四会"
    },
    "吴川": {
        "province": "广东",
        "prov_city": "广东吴川"
    },
    "共青城": {
        "province": "江西",
        "prov_city": "江西共青城"
    },
    "三明": {
        "province": "福建",
        "prov_city": "福建三明"
    },
    "周口": {
        "province": "河南",
        "prov_city": "河南周口"
    },
    "靖江": {
        "province": "江苏",
        "prov_city": "江苏靖江"
    },
    "庆阳": {
        "province": "甘肃",
        "prov_city": "甘肃庆阳"
    },
    "泊头": {
        "province": "河北",
        "prov_city": "河北泊头"
    },
    "临海": {
        "province": "浙江",
        "prov_city": "浙江临海"
    },
    "上饶": {
        "province": "江西",
        "prov_city": "江西上饶"
    },
    "伊犁": {
        "province": "新疆",
        "prov_city": "新疆伊犁"
    },
    "安康": {
        "province": "陕西",
        "prov_city": "陕西安康"
    },
    "玉溪": {
        "province": "云南",
        "prov_city": "云南玉溪"
    },
    "凌源": {
        "province": "辽宁",
        "prov_city": "辽宁凌源"
    },
    "乐清": {
        "province": "浙江",
        "prov_city": "浙江乐清"
    },
    "武汉": {
        "province": "湖北",
        "prov_city": "湖北武汉"
    },
    "池州": {
        "province": "安徽",
        "prov_city": "安徽池州"
    },
    "晋州": {
        "province": "河北",
        "prov_city": "河北晋州"
    },
    "乐昌": {
        "province": "广东",
        "prov_city": "广东乐昌"
    },
    "高安": {
        "province": "江西",
        "prov_city": "江西高安"
    },
    "库尔勒": {
        "province": "新疆",
        "prov_city": "新疆库尔勒"
    },
    "莱州": {
        "province": "山东",
        "prov_city": "山东莱州"
    },
    "内江": {
        "province": "四川",
        "prov_city": "四川内江"
    },
    "临沂": {
        "province": "山东",
        "prov_city": "山东临沂"
    },
    "淮南": {
        "province": "安徽",
        "prov_city": "安徽淮南"
    },
    "阿拉善右旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古阿拉善右旗"
    },
    "朝阳": {
        "province": "辽宁",
        "prov_city": "辽宁朝阳"
    },
    "随州": {
        "province": "湖北",
        "prov_city": "湖北随州"
    },
    "湘西": {
        "province": "湖南",
        "prov_city": "湖南湘西"
    },
    "额济纳旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古额济纳旗"
    },
    "定西": {
        "province": "甘肃",
        "prov_city": "甘肃定西"
    },
    "克孜勒苏柯尔克孜": {
        "province": "新疆",
        "prov_city": "新疆克孜勒苏柯尔克孜"
    },
    "禹州": {
        "province": "河南",
        "prov_city": "河南禹州"
    },
    "临沧": {
        "province": "云南",
        "prov_city": "云南临沧"
    },
    "吐鲁番": {
        "province": "新疆",
        "prov_city": "新疆吐鲁番"
    },
    "扎鲁特旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古扎鲁特旗"
    },
    "金昌": {
        "province": "甘肃",
        "prov_city": "甘肃金昌"
    },
    "大安": {
        "province": "吉林",
        "prov_city": "吉林大安"
    },
    "和龙": {
        "province": "吉林",
        "prov_city": "吉林和龙"
    },
    "兰州": {
        "province": "甘肃",
        "prov_city": "甘肃兰州"
    },
    "腾冲": {
        "province": "云南",
        "prov_city": "云南腾冲"
    },
    "高密": {
        "province": "山东",
        "prov_city": "山东高密"
    },
    "吉首": {
        "province": "湖南",
        "prov_city": "湖南吉首"
    },
    "遵义": {
        "province": "贵州",
        "prov_city": "贵州遵义"
    },
    "荆州": {
        "province": "湖北",
        "prov_city": "湖北荆州"
    },
    "霍尔果斯": {
        "province": "新疆",
        "prov_city": "新疆霍尔果斯"
    },
    "泰安": {
        "province": "山东",
        "prov_city": "山东泰安"
    },
    "丰城": {
        "province": "江西",
        "prov_city": "江西丰城"
    },
    "南通": {
        "province": "江苏",
        "prov_city": "江苏南通"
    },
    "淮北": {
        "province": "安徽",
        "prov_city": "安徽淮北"
    },
    "永城": {
        "province": "河南",
        "prov_city": "河南永城"
    },
    "松原": {
        "province": "吉林",
        "prov_city": "吉林松原"
    },
    "察哈尔右翼中旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古察哈尔右翼中旗"
    },
    "景德镇": {
        "province": "江西",
        "prov_city": "江西景德镇"
    },
    "贵阳": {
        "province": "贵州",
        "prov_city": "贵州贵阳"
    },
    "界首": {
        "province": "安徽",
        "prov_city": "安徽界首"
    },
    "贵港": {
        "province": "广西",
        "prov_city": "广西贵港"
    },
    "梅州": {
        "province": "广东",
        "prov_city": "广东梅州"
    },
    "常州": {
        "province": "江苏",
        "prov_city": "江苏常州"
    },
    "同江": {
        "province": "黑龙江",
        "prov_city": "黑龙江同江"
    },
    "晋江": {
        "province": "福建",
        "prov_city": "福建晋江"
    },
    "磐石": {
        "province": "吉林",
        "prov_city": "吉林磐石"
    },
    "海北": {
        "province": "青海",
        "prov_city": "青海海北"
    },
    "五指山": {
        "province": "海南",
        "prov_city": "海南五指山"
    },
    "五家渠": {
        "province": "新疆",
        "prov_city": "新疆五家渠"
    },
    "都江堰": {
        "province": "四川",
        "prov_city": "四川都江堰"
    },
    "北京": {
        "province": "北京",
        "prov_city": "北京"
    },
    "涟源": {
        "province": "湖南",
        "prov_city": "湖南涟源"
    },
    "新沂": {
        "province": "江苏",
        "prov_city": "江苏新沂"
    },
    "芒": {
        "province": "云南",
        "prov_city": "云南芒"
    },
    "瑞昌": {
        "province": "江西",
        "prov_city": "江西瑞昌"
    },
    "扬州": {
        "province": "江苏",
        "prov_city": "江苏扬州"
    },
    "丹江口": {
        "province": "湖北",
        "prov_city": "湖北丹江口"
    },
    "林芝": {
        "province": "西藏",
        "prov_city": "西藏林芝"
    },
    "四平": {
        "province": "吉林",
        "prov_city": "吉林四平"
    },
    "密山": {
        "province": "黑龙江",
        "prov_city": "黑龙江密山"
    },
    "攀枝花": {
        "province": "四川",
        "prov_city": "四川攀枝花"
    },
    "敦化": {
        "province": "吉林",
        "prov_city": "吉林敦化"
    },
    "香港": {
        "province": "香港",
        "prov_city": "香港"
    },
    "商丘": {
        "province": "河南",
        "prov_city": "河南商丘"
    },
    "乌鲁木齐": {
        "province": "新疆",
        "prov_city": "新疆乌鲁木齐"
    },
    "赣州": {
        "province": "江西",
        "prov_city": "江西赣州"
    },
    "威海": {
        "province": "山东",
        "prov_city": "山东威海"
    },
    "荆门": {
        "province": "湖北",
        "prov_city": "湖北荆门"
    },
    "张掖": {
        "province": "甘肃",
        "prov_city": "甘肃张掖"
    },
    "延吉": {
        "province": "吉林",
        "prov_city": "吉林延吉"
    },
    "临江": {
        "province": "吉林",
        "prov_city": "吉林临江"
    },
    "凯里": {
        "province": "贵州",
        "prov_city": "贵州凯里"
    },
    "文山": {
        "province": "云南",
        "prov_city": "云南文山"
    },
    "连州": {
        "province": "广东",
        "prov_city": "广东连州"
    },
    "台湾": {
        "province": "台湾",
        "prov_city": "台湾"
    },
    "枝江": {
        "province": "湖北",
        "prov_city": "湖北枝江"
    },
    "黄骅": {
        "province": "河北",
        "prov_city": "河北黄骅"
    },
    "玉林": {
        "province": "广西",
        "prov_city": "广西玉林"
    },
    "个旧": {
        "province": "云南",
        "prov_city": "云南个旧"
    },
    "济源": {
        "province": "河南",
        "prov_city": "河南济源"
    },
    "衡阳": {
        "province": "湖南",
        "prov_city": "湖南衡阳"
    },
    "桂林": {
        "province": "广西",
        "prov_city": "广西桂林"
    },
    "义乌": {
        "province": "浙江",
        "prov_city": "浙江义乌"
    },
    "杭州": {
        "province": "浙江",
        "prov_city": "浙江杭州"
    },
    "博乐": {
        "province": "新疆",
        "prov_city": "新疆博乐"
    },
    "景洪": {
        "province": "云南",
        "prov_city": "云南景洪"
    },
    "鄂托克旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古鄂托克旗"
    },
    "福鼎": {
        "province": "福建",
        "prov_city": "福建福鼎"
    },
    "锡林浩特": {
        "province": "内蒙古",
        "prov_city": "内蒙古锡林浩特"
    },
    "安达": {
        "province": "黑龙江",
        "prov_city": "黑龙江安达"
    },
    "阿巴嘎旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古阿巴嘎旗"
    },
    "青岛": {
        "province": "山东",
        "prov_city": "山东青岛"
    },
    "铁门关": {
        "province": "新疆",
        "prov_city": "新疆铁门关"
    },
    "正镶白旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古正镶白旗"
    },
    "贵溪": {
        "province": "江西",
        "prov_city": "江西贵溪"
    },
    "包头": {
        "province": "内蒙古",
        "prov_city": "内蒙古包头"
    },
    "虎林": {
        "province": "黑龙江",
        "prov_city": "黑龙江虎林"
    },
    "广元": {
        "province": "四川",
        "prov_city": "四川广元"
    },
    "平顶山": {
        "province": "河南",
        "prov_city": "河南平顶山"
    },
    "溧阳": {
        "province": "江苏",
        "prov_city": "江苏溧阳"
    },
    "阿鲁科尔沁旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古阿鲁科尔沁旗"
    },
    "仙桃": {
        "province": "湖北",
        "prov_city": "湖北仙桃"
    },
    "台州": {
        "province": "浙江",
        "prov_city": "浙江台州"
    },
    "图木舒克": {
        "province": "新疆",
        "prov_city": "新疆图木舒克"
    },
    "韶山": {
        "province": "湖南",
        "prov_city": "湖南韶山"
    },
    "德兴": {
        "province": "江西",
        "prov_city": "江西德兴"
    },
    "绵阳": {
        "province": "四川",
        "prov_city": "四川绵阳"
    },
    "化州": {
        "province": "广东",
        "prov_city": "广东化州"
    },
    "龙岩": {
        "province": "福建",
        "prov_city": "福建龙岩"
    },
    "东兴": {
        "province": "广西",
        "prov_city": "广西东兴"
    },
    "丽江": {
        "province": "云南",
        "prov_city": "云南丽江"
    },
    "高邮": {
        "province": "江苏",
        "prov_city": "江苏高邮"
    },
    "福泉": {
        "province": "贵州",
        "prov_city": "贵州福泉"
    },
    "二连浩特": {
        "province": "内蒙古",
        "prov_city": "内蒙古二连浩特"
    },
    "江山": {
        "province": "浙江",
        "prov_city": "浙江江山"
    },
    "即墨": {
        "province": "山东",
        "prov_city": "山东即墨"
    },
    "中山": {
        "province": "广东",
        "prov_city": "广东中山"
    },
    "卫辉": {
        "province": "河南",
        "prov_city": "河南卫辉"
    },
    "龙泉": {
        "province": "浙江",
        "prov_city": "浙江龙泉"
    },
    "马尔康": {
        "province": "四川",
        "prov_city": "四川马尔康"
    },
    "西乌珠穆沁旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古西乌珠穆沁旗"
    },
    "廉江": {
        "province": "广东",
        "prov_city": "广东廉江"
    },
    "普宁": {
        "province": "广东",
        "prov_city": "广东普宁"
    },
    "黔东南": {
        "province": "贵州",
        "prov_city": "贵州黔东南"
    },
    "新余": {
        "province": "江西",
        "prov_city": "江西新余"
    },
    "娄底": {
        "province": "湖南",
        "prov_city": "湖南娄底"
    },
    "兴宁": {
        "province": "广东",
        "prov_city": "广东兴宁"
    },
    "牡丹江": {
        "province": "黑龙江",
        "prov_city": "黑龙江牡丹江"
    },
    "晋中": {
        "province": "山西",
        "prov_city": "山西晋中"
    },
    "蒙自": {
        "province": "云南",
        "prov_city": "云南蒙自"
    },
    "湘潭": {
        "province": "湖南",
        "prov_city": "湖南湘潭"
    },
    "三河": {
        "province": "河北",
        "prov_city": "河北三河"
    },
    "扬中": {
        "province": "江苏",
        "prov_city": "江苏扬中"
    },
    "蛟河": {
        "province": "吉林",
        "prov_city": "吉林蛟河"
    },
    "崇州": {
        "province": "四川",
        "prov_city": "四川崇州"
    },
    "霸州": {
        "province": "河北",
        "prov_city": "河北霸州"
    },
    "漯河": {
        "province": "河南",
        "prov_city": "河南漯河"
    },
    "克什克腾旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古克什克腾旗"
    },
    "乐山": {
        "province": "四川",
        "prov_city": "四川乐山"
    },
    "邳州": {
        "province": "江苏",
        "prov_city": "江苏邳州"
    },
    "淮安": {
        "province": "江苏",
        "prov_city": "江苏淮安"
    },
    "清镇": {
        "province": "贵州",
        "prov_city": "贵州清镇"
    },
    "如皋": {
        "province": "江苏",
        "prov_city": "江苏如皋"
    },
    "乌海": {
        "province": "内蒙古",
        "prov_city": "内蒙古乌海"
    },
    "东乌珠穆沁旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古东乌珠穆沁旗"
    },
    "土默特右旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古土默特右旗"
    },
    "扎兰屯": {
        "province": "内蒙古",
        "prov_city": "内蒙古扎兰屯"
    },
    "津": {
        "province": "湖南",
        "prov_city": "湖南津"
    },
    "安陆": {
        "province": "湖北",
        "prov_city": "湖北安陆"
    },
    "洪湖": {
        "province": "湖北",
        "prov_city": "湖北洪湖"
    },
    "焦作": {
        "province": "河南",
        "prov_city": "河南焦作"
    },
    "常德": {
        "province": "湖南",
        "prov_city": "湖南常德"
    },
    "泸水": {
        "province": "云南",
        "prov_city": "云南泸水"
    },
    "十堰": {
        "province": "湖北",
        "prov_city": "湖北十堰"
    },
    "石嘴山": {
        "province": "宁夏",
        "prov_city": "宁夏石嘴山"
    },
    "文山": {
        "province": "云南",
        "prov_city": "云南文山"
    },
    "胶州": {
        "province": "山东",
        "prov_city": "山东胶州"
    },
    "合肥": {
        "province": "安徽",
        "prov_city": "安徽合肥"
    },
    "乌兰浩特": {
        "province": "内蒙古",
        "prov_city": "内蒙古乌兰浩特"
    },
    "汾阳": {
        "province": "山西",
        "prov_city": "山西汾阳"
    },
    "舒兰": {
        "province": "吉林",
        "prov_city": "吉林舒兰"
    },
    "黄冈": {
        "province": "湖北",
        "prov_city": "湖北黄冈"
    },
    "五大连池": {
        "province": "黑龙江",
        "prov_city": "黑龙江五大连池"
    },
    "孝感": {
        "province": "湖北",
        "prov_city": "湖北孝感"
    },
    "乌拉特前旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古乌拉特前旗"
    },
    "南安": {
        "province": "福建",
        "prov_city": "福建南安"
    },
    "成都": {
        "province": "四川",
        "prov_city": "四川成都"
    },
    "新巴尔虎右旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古新巴尔虎右旗"
    },
    "灵武": {
        "province": "宁夏",
        "prov_city": "宁夏灵武"
    },
    "上海": {
        "province": "",
        "prov_city": "上海"
    },
    "文昌": {
        "province": "海南",
        "prov_city": "海南文昌"
    },
    "德宏": {
        "province": "云南",
        "prov_city": "云南德宏"
    },
    "开远": {
        "province": "云南",
        "prov_city": "云南开远"
    },
    "呼和浩特": {
        "province": "内蒙古",
        "prov_city": "内蒙古呼和浩特"
    },
    "莱阳": {
        "province": "山东",
        "prov_city": "山东莱阳"
    },
    "荣成": {
        "province": "山东",
        "prov_city": "山东荣成"
    },
    "江油": {
        "province": "四川",
        "prov_city": "四川江油"
    },
    "温州": {
        "province": "浙江",
        "prov_city": "浙江温州"
    },
    "延安": {
        "province": "陕西",
        "prov_city": "陕西延安"
    },
    "南宫": {
        "province": "河北",
        "prov_city": "河北南宫"
    },
    "晋城": {
        "province": "山西",
        "prov_city": "山西晋城"
    },
    "邵阳": {
        "province": "湖南",
        "prov_city": "湖南邵阳"
    },
    "鹤壁": {
        "province": "河南",
        "prov_city": "河南鹤壁"
    },
    "瓦房店": {
        "province": "辽宁",
        "prov_city": "辽宁瓦房店"
    },
    "凭祥": {
        "province": "广西",
        "prov_city": "广西凭祥"
    },
    "大冶": {
        "province": "湖北",
        "prov_city": "湖北大冶"
    },
    "偃师": {
        "province": "河南",
        "prov_city": "河南偃师"
    },
    "承德": {
        "province": "河北",
        "prov_city": "河北承德"
    },
    "日照": {
        "province": "山东",
        "prov_city": "山东日照"
    },
    "四子王旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古四子王旗"
    },
    "嵊州": {
        "province": "浙江",
        "prov_city": "浙江嵊州"
    },
    "北安": {
        "province": "黑龙江",
        "prov_city": "黑龙江北安"
    },
    "凌海": {
        "province": "辽宁",
        "prov_city": "辽宁凌海"
    },
    "怀化": {
        "province": "湖南",
        "prov_city": "湖南怀化"
    },
    "潮州": {
        "province": "广东",
        "prov_city": "广东潮州"
    },
    "昌吉": {
        "province": "新疆",
        "prov_city": "新疆昌吉"
    },
    "浏阳": {
        "province": "湖南",
        "prov_city": "湖南浏阳"
    },
    "宜昌": {
        "province": "湖北",
        "prov_city": "湖北宜昌"
    },
    "柳江区": {
        "province": "广西",
        "prov_city": "广西柳江区"
    },
    "乌审旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古乌审旗"
    },
    "邓州": {
        "province": "河南",
        "prov_city": "河南邓州"
    },
    "许昌": {
        "province": "河南",
        "prov_city": "河南许昌"
    },
    "禹城": {
        "province": "山东",
        "prov_city": "山东禹城"
    },
    "鄂托克前旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古鄂托克前旗"
    },
    "宜都": {
        "province": "湖北",
        "prov_city": "湖北宜都"
    },
    "烟台": {
        "province": "山东",
        "prov_city": "山东烟台"
    },
    "巩义": {
        "province": "河南",
        "prov_city": "河南巩义"
    },
    "福州": {
        "province": "福建",
        "prov_city": "福建福州"
    },
    "抚顺": {
        "province": "辽宁",
        "prov_city": "辽宁抚顺"
    },
    "茂名": {
        "province": "广东",
        "prov_city": "广东茂名"
    },
    "海门": {
        "province": "江苏",
        "prov_city": "江苏海门"
    },
    "桐城": {
        "province": "安徽",
        "prov_city": "安徽桐城"
    },
    "彭州": {
        "province": "四川",
        "prov_city": "四川彭州"
    },
    "济南": {
        "province": "山东",
        "prov_city": "山东济南"
    },
    "临汾": {
        "province": "山西",
        "prov_city": "山西临汾"
    },
    "新乐": {
        "province": "河北",
        "prov_city": "河北新乐"
    },
    "广安": {
        "province": "四川",
        "prov_city": "四川广安"
    },
    "山南": {
        "province": "西藏",
        "prov_city": "西藏山南"
    },
    "明光": {
        "province": "安徽",
        "prov_city": "安徽明光"
    },
    "镇江": {
        "province": "江苏",
        "prov_city": "江苏镇江"
    },
    "潜江": {
        "province": "湖北",
        "prov_city": "湖北潜江"
    },
    "石家庄": {
        "province": "河北",
        "prov_city": "河北石家庄"
    },
    "新泰": {
        "province": "山东",
        "prov_city": "山东新泰"
    },
    "大理": {
        "province": "云南",
        "prov_city": "云南大理"
    },
    "吉安": {
        "province": "江西",
        "prov_city": "江西吉安"
    },
    "肇庆": {
        "province": "广东",
        "prov_city": "广东肇庆"
    },
    "信阳": {
        "province": "河南",
        "prov_city": "河南信阳"
    },
    "武安": {
        "province": "河北",
        "prov_city": "河北武安"
    },
    "洮南": {
        "province": "吉林",
        "prov_city": "吉林洮南"
    },
    "抚远": {
        "province": "黑龙江",
        "prov_city": "黑龙江抚远"
    },
    "太原": {
        "province": "山西",
        "prov_city": "山西太原"
    },
    "辽源": {
        "province": "吉林",
        "prov_city": "吉林辽源"
    },
    "齐齐哈尔": {
        "province": "黑龙江",
        "prov_city": "黑龙江齐齐哈尔"
    },
    "双鸭山": {
        "province": "黑龙江",
        "prov_city": "黑龙江双鸭山"
    },
    "湘乡": {
        "province": "湖南",
        "prov_city": "湖南湘乡"
    },
    "原平": {
        "province": "山西",
        "prov_city": "山西原平"
    },
    "苏州": {
        "province": "江苏",
        "prov_city": "江苏苏州"
    },
    "新乡": {
        "province": "河南",
        "prov_city": "河南新乡"
    },
    "永州": {
        "province": "湖南",
        "prov_city": "湖南永州"
    },
    "衢州": {
        "province": "浙江",
        "prov_city": "浙江衢州"
    },
    "德惠": {
        "province": "吉林",
        "prov_city": "吉林德惠"
    },
    "阿尔山": {
        "province": "内蒙古",
        "prov_city": "内蒙古阿尔山"
    },
    "恩平": {
        "province": "广东",
        "prov_city": "广东恩平"
    },
    "嘉峪关": {
        "province": "甘肃",
        "prov_city": "甘肃嘉峪关"
    },
    "樟树": {
        "province": "江西",
        "prov_city": "江西樟树"
    },
    "甘孜": {
        "province": "四川",
        "prov_city": "四川甘孜"
    },
    "聊城": {
        "province": "山东",
        "prov_city": "山东聊城"
    },
    "温岭": {
        "province": "浙江",
        "prov_city": "浙江温岭"
    },
    "和田": {
        "province": "新疆",
        "prov_city": "新疆和田"
    },
    "日喀则": {
        "province": "西藏",
        "prov_city": "西藏日喀则"
    },
    "北票": {
        "province": "辽宁",
        "prov_city": "辽宁北票"
    },
    "洛阳": {
        "province": "河南",
        "prov_city": "河南洛阳"
    },
    "台山": {
        "province": "广东",
        "prov_city": "广东台山"
    },
    "防城港": {
        "province": "广西",
        "prov_city": "广西防城港"
    },
    "蚌埠": {
        "province": "安徽",
        "prov_city": "安徽蚌埠"
    },
    "泰兴": {
        "province": "江苏",
        "prov_city": "江苏泰兴"
    },
    "漳平": {
        "province": "福建",
        "prov_city": "福建漳平"
    },
    "咸宁": {
        "province": "湖北",
        "prov_city": "湖北咸宁"
    },
    "盘锦": {
        "province": "辽宁",
        "prov_city": "辽宁盘锦"
    },
    "葫芦岛": {
        "province": "辽宁",
        "prov_city": "辽宁葫芦岛"
    },
    "钦州": {
        "province": "广西",
        "prov_city": "广西钦州"
    },
    "崇左": {
        "province": "广西",
        "prov_city": "广西崇左"
    },
    "达拉特旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古达拉特旗"
    },
    "江门": {
        "province": "广东",
        "prov_city": "广东江门"
    },
    "奈曼旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古奈曼旗"
    },
    "资兴": {
        "province": "湖南",
        "prov_city": "湖南资兴"
    },
    "仪征": {
        "province": "江苏",
        "prov_city": "江苏仪征"
    },
    "海口": {
        "province": "海南",
        "prov_city": "海南海口"
    },
    "科尔沁左翼中旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古科尔沁左翼中旗"
    },
    "庐山": {
        "province": "江西",
        "prov_city": "江西庐山"
    },
    "辽阳": {
        "province": "辽宁",
        "prov_city": "辽宁辽阳"
    },
    "万源": {
        "province": "四川",
        "prov_city": "四川万源"
    },
    "宁安": {
        "province": "黑龙江",
        "prov_city": "黑龙江宁安"
    },
    "肇东": {
        "province": "黑龙江",
        "prov_city": "黑龙江肇东"
    },
    "张家界": {
        "province": "湖南",
        "prov_city": "湖南张家界"
    },
    "句容": {
        "province": "江苏",
        "prov_city": "江苏句容"
    },
    "丰镇": {
        "province": "内蒙古",
        "prov_city": "内蒙古丰镇"
    },
    "井冈山": {
        "province": "江西",
        "prov_city": "江西井冈山"
    },
    "岑溪": {
        "province": "广西",
        "prov_city": "广西岑溪"
    },
    "栖霞": {
        "province": "山东",
        "prov_city": "山东栖霞"
    },
    "阿拉山口": {
        "province": "新疆",
        "prov_city": "新疆阿拉山口"
    },
    "永济": {
        "province": "山西",
        "prov_city": "山西永济"
    },
    "宣城": {
        "province": "安徽",
        "prov_city": "安徽宣城"
    },
    "德令哈": {
        "province": "青海",
        "prov_city": "青海德令哈"
    },
    "马鞍山": {
        "province": "安徽",
        "prov_city": "安徽马鞍山"
    },
    "赤壁": {
        "province": "湖北",
        "prov_city": "湖北赤壁"
    },
    "应城": {
        "province": "湖北",
        "prov_city": "湖北应城"
    },
    "固原": {
        "province": "宁夏",
        "prov_city": "宁夏固原"
    },
    "敦煌": {
        "province": "甘肃",
        "prov_city": "甘肃敦煌"
    },
    "康定": {
        "province": "四川",
        "prov_city": "四川康定"
    },
    "龙海": {
        "province": "福建",
        "prov_city": "福建龙海"
    },
    "郴州": {
        "province": "湖南",
        "prov_city": "湖南郴州"
    },
    "莱芜": {
        "province": "山东",
        "prov_city": "山东莱芜"
    },
    "古交": {
        "province": "山西",
        "prov_city": "山西古交"
    },
    "遵化": {
        "province": "河北",
        "prov_city": "河北遵化"
    },
    "莫力达瓦": {
        "province": "内蒙古",
        "prov_city": "内蒙古莫力达瓦"
    },
    "招远": {
        "province": "山东",
        "prov_city": "山东招远"
    },
    "瑞安": {
        "province": "浙江",
        "prov_city": "浙江瑞安"
    },
    "锡林": {
        "province": "内蒙古",
        "prov_city": "内蒙古锡林"
    },
    "宜城": {
        "province": "湖北",
        "prov_city": "湖北宜城"
    },
    "尚志": {
        "province": "黑龙江",
        "prov_city": "黑龙江尚志"
    },
    "简阳": {
        "province": "四川",
        "prov_city": "四川简阳"
    },
    "本溪": {
        "province": "辽宁",
        "prov_city": "辽宁本溪"
    },
    "锦州": {
        "province": "辽宁",
        "prov_city": "辽宁锦州"
    },
    "海林": {
        "province": "黑龙江",
        "prov_city": "黑龙江海林"
    },
    "大庆": {
        "province": "黑龙江",
        "prov_city": "黑龙江大庆"
    },
    "松滋": {
        "province": "湖北",
        "prov_city": "湖北松滋"
    },
    "益阳": {
        "province": "湖南",
        "prov_city": "湖南益阳"
    },
    "天津": {
        "province": "天津",
        "prov_city": "天津"
    },
    "翁牛特旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古翁牛特旗"
    },
    "汉川": {
        "province": "湖北",
        "prov_city": "湖北汉川"
    },
    "巴林左旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古巴林左旗"
    },
    "曲阜": {
        "province": "山东",
        "prov_city": "山东曲阜"
    },
    "韩城": {
        "province": "陕西",
        "prov_city": "陕西韩城"
    },
    "肥城": {
        "province": "山东",
        "prov_city": "山东肥城"
    },
    "黄南": {
        "province": "青海",
        "prov_city": "青海黄南"
    },
    "扶余": {
        "province": "吉林",
        "prov_city": "吉林扶余"
    },
    "华阴": {
        "province": "陕西",
        "prov_city": "陕西华阴"
    },
    "怒江": {
        "province": "云南",
        "prov_city": "云南怒江"
    },
    "海城": {
        "province": "辽宁",
        "prov_city": "辽宁海城"
    },
    "六盘水": {
        "province": "贵州",
        "prov_city": "贵州六盘水"
    },
    "汨罗": {
        "province": "湖南",
        "prov_city": "湖南汨罗"
    },
    "儋州": {
        "province": "海南",
        "prov_city": "海南儋州"
    },
    "牙克石": {
        "province": "内蒙古",
        "prov_city": "内蒙古牙克石"
    },
    "蓬莱": {
        "province": "山东",
        "prov_city": "山东蓬莱"
    },
    "科尔沁左翼后旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古科尔沁左翼后旗"
    },
    "舞钢": {
        "province": "河南",
        "prov_city": "河南舞钢"
    },
    "绥化": {
        "province": "黑龙江",
        "prov_city": "黑龙江绥化"
    },
    "吴忠": {
        "province": "宁夏",
        "prov_city": "宁夏吴忠"
    },
    "金华": {
        "province": "浙江",
        "prov_city": "浙江金华"
    },
    "灵宝": {
        "province": "河南",
        "prov_city": "河南灵宝"
    },
    "海伦": {
        "province": "黑龙江",
        "prov_city": "黑龙江海伦"
    },
    "建瓯": {
        "province": "福建",
        "prov_city": "福建建瓯"
    },
    "雅安": {
        "province": "四川",
        "prov_city": "四川雅安"
    },
    "亳州": {
        "province": "安徽",
        "prov_city": "安徽亳州"
    },
    "桦甸": {
        "province": "吉林",
        "prov_city": "吉林桦甸"
    },
    "广水": {
        "province": "湖北",
        "prov_city": "湖北广水"
    },
    "石首": {
        "province": "湖北",
        "prov_city": "湖北石首"
    },
    "阿荣旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古阿荣旗"
    },
    "兴城": {
        "province": "辽宁",
        "prov_city": "辽宁兴城"
    },
    "临夏": {
        "province": "甘肃",
        "prov_city": "甘肃临夏"
    },
    "公主岭": {
        "province": "吉林",
        "prov_city": "吉林公主岭"
    },
    "邢台": {
        "province": "河北",
        "prov_city": "河北邢台"
    },
    "廊坊": {
        "province": "河北",
        "prov_city": "河北廊坊"
    },
    "昆明": {
        "province": "云南",
        "prov_city": "云南昆明"
    },
    "深圳": {
        "province": "广东",
        "prov_city": "广东深圳"
    },
    "开平": {
        "province": "广东",
        "prov_city": "广东开平"
    },
    "陈巴尔虎旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古陈巴尔虎旗"
    },
    "沁阳": {
        "province": "河南",
        "prov_city": "河南沁阳"
    },
    "东莞": {
        "province": "广东",
        "prov_city": "广东东莞"
    },
    "介休": {
        "province": "山西",
        "prov_city": "山西介休"
    },
    "邯郸": {
        "province": "河北",
        "prov_city": "河北邯郸"
    },
    "绥芬河": {
        "province": "黑龙江",
        "prov_city": "黑龙江绥芬河"
    },
    "运城": {
        "province": "山西",
        "prov_city": "山西运城"
    },
    "黄石": {
        "province": "湖北",
        "prov_city": "湖北黄石"
    },
    "琼海": {
        "province": "海南",
        "prov_city": "海南琼海"
    },
    "昌吉": {
        "province": "新疆",
        "prov_city": "新疆昌吉"
    },
    "科尔沁右翼前旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古科尔沁右翼前旗"
    },
    "红河": {
        "province": "云南",
        "prov_city": "云南红河"
    },
    "安顺": {
        "province": "贵州",
        "prov_city": "贵州安顺"
    },
    "辛集": {
        "province": "河北",
        "prov_city": "河北辛集"
    },
    "诸城": {
        "province": "山东",
        "prov_city": "山东诸城"
    },
    "通化": {
        "province": "吉林",
        "prov_city": "吉林通化"
    },
    "盖州": {
        "province": "辽宁",
        "prov_city": "辽宁盖州"
    },
    "什邡": {
        "province": "四川",
        "prov_city": "四川什邡"
    },
    "瑞丽": {
        "province": "云南",
        "prov_city": "云南瑞丽"
    },
    "潍坊": {
        "province": "山东",
        "prov_city": "山东潍坊"
    },
    "额尔古纳": {
        "province": "内蒙古",
        "prov_city": "内蒙古额尔古纳"
    },
    "贺州": {
        "province": "广西",
        "prov_city": "广西贺州"
    },
    "梧州": {
        "province": "广西",
        "prov_city": "广西梧州"
    },
    "敖汉旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古敖汉旗"
    },
    "广汉": {
        "province": "四川",
        "prov_city": "四川广汉"
    },
    "高平": {
        "province": "山西",
        "prov_city": "山西高平"
    },
    "白城": {
        "province": "吉林",
        "prov_city": "吉林白城"
    },
    "资阳": {
        "province": "四川",
        "prov_city": "四川资阳"
    },
    "阳春": {
        "province": "广东",
        "prov_city": "广东阳春"
    },
    "曲靖": {
        "province": "云南",
        "prov_city": "云南曲靖"
    },
    "长治": {
        "province": "山西",
        "prov_city": "山西长治"
    },
    "海西": {
        "province": "青海",
        "prov_city": "青海海西"
    },
    "果洛": {
        "province": "青海",
        "prov_city": "青海果洛"
    },
    "东宁": {
        "province": "黑龙江",
        "prov_city": "黑龙江东宁"
    },
    "湛江": {
        "province": "广东",
        "prov_city": "广东湛江"
    },
    "哈尔滨": {
        "province": "黑龙江",
        "prov_city": "黑龙江哈尔滨"
    },
    "呼伦贝尔": {
        "province": "内蒙古",
        "prov_city": "内蒙古呼伦贝尔"
    },
    "渭南": {
        "province": "陕西",
        "prov_city": "陕西渭南"
    },
    "鞍山": {
        "province": "辽宁",
        "prov_city": "辽宁鞍山"
    },
    "兴义": {
        "province": "贵州",
        "prov_city": "贵州兴义"
    },
    "博尔塔拉": {
        "province": "新疆",
        "prov_city": "新疆博尔塔拉"
    },
    "太仓": {
        "province": "江苏",
        "prov_city": "江苏太仓"
    },
    "榆林": {
        "province": "陕西",
        "prov_city": "陕西榆林"
    },
    "伊宁": {
        "province": "新疆",
        "prov_city": "新疆伊宁"
    },
    "峨眉山": {
        "province": "四川",
        "prov_city": "四川峨眉山"
    },
    "永安": {
        "province": "福建",
        "prov_city": "福建永安"
    },
    "长沙": {
        "province": "湖南",
        "prov_city": "湖南长沙"
    },
    "甘南": {
        "province": "甘肃",
        "prov_city": "甘肃甘南"
    },
    "乌苏": {
        "province": "新疆",
        "prov_city": "新疆乌苏"
    },
    "兴平": {
        "province": "陕西",
        "prov_city": "陕西兴平"
    },
    "中卫": {
        "province": "宁夏",
        "prov_city": "宁夏中卫"
    },
    "大石桥": {
        "province": "辽宁",
        "prov_city": "辽宁大石桥"
    },
    "常熟": {
        "province": "江苏",
        "prov_city": "江苏常熟"
    },
    "汕头": {
        "province": "广东",
        "prov_city": "广东汕头"
    },
    "武冈": {
        "province": "湖南",
        "prov_city": "湖南武冈"
    },
    "苏尼特左旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古苏尼特左旗"
    },
    "安庆": {
        "province": "安徽",
        "prov_city": "安徽安庆"
    },
    "临夏": {
        "province": "甘肃",
        "prov_city": "甘肃临夏"
    },
    "平度": {
        "province": "山东",
        "prov_city": "山东平度"
    },
    "富锦": {
        "province": "黑龙江",
        "prov_city": "黑龙江富锦"
    },
    "合作": {
        "province": "甘肃",
        "prov_city": "甘肃合作"
    },
    "泸州": {
        "province": "四川",
        "prov_city": "四川泸州"
    },
    "菏泽": {
        "province": "山东",
        "prov_city": "山东菏泽"
    },
    "德阳": {
        "province": "四川",
        "prov_city": "四川德阳"
    },
    "潞城": {
        "province": "山西",
        "prov_city": "山西潞城"
    },
    "乌拉特中旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古乌拉特中旗"
    },
    "丹阳": {
        "province": "江苏",
        "prov_city": "江苏丹阳"
    },
    "海南": {
        "province": "青海",
        "prov_city": "青海海南"
    },
    "陆丰": {
        "province": "广东",
        "prov_city": "广东陆丰"
    },
    "广州": {
        "province": "广东",
        "prov_city": "广东广州"
    },
    "阜阳": {
        "province": "安徽",
        "prov_city": "安徽阜阳"
    },
    "福安": {
        "province": "福建",
        "prov_city": "福建福安"
    },
    "岳阳": {
        "province": "湖南",
        "prov_city": "湖南岳阳"
    },
    "大连": {
        "province": "辽宁",
        "prov_city": "辽宁大连"
    },
    "龙口": {
        "province": "山东",
        "prov_city": "山东龙口"
    },
    "珲春": {
        "province": "吉林",
        "prov_city": "吉林珲春"
    },
    "丹东": {
        "province": "辽宁",
        "prov_city": "辽宁丹东"
    },
    "东港": {
        "province": "辽宁",
        "prov_city": "辽宁东港"
    },
    "钟祥": {
        "province": "湖北",
        "prov_city": "湖北钟祥"
    },
    "福清": {
        "province": "福建",
        "prov_city": "福建福清"
    },
    "察哈尔右翼后旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古察哈尔右翼后旗"
    },
    "三沙": {
        "province": "海南",
        "prov_city": "海南三沙"
    },
    "萍乡": {
        "province": "江西",
        "prov_city": "江西萍乡"
    },
    "察哈尔右翼前旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古察哈尔右翼前旗"
    },
    "六安": {
        "province": "安徽",
        "prov_city": "安徽六安"
    },
    "黔西南": {
        "province": "贵州",
        "prov_city": "贵州黔西南"
    },
    "澳门": {
        "province": "澳门",
        "prov_city": "澳门"
    },
    "定州": {
        "province": "河北",
        "prov_city": "河北定州"
    },
    "驻马店": {
        "province": "河南",
        "prov_city": "河南驻马店"
    },
    "海阳": {
        "province": "山东",
        "prov_city": "山东海阳"
    },
    "孝义": {
        "province": "山西",
        "prov_city": "山西孝义"
    },
    "霍林郭勒": {
        "province": "内蒙古",
        "prov_city": "内蒙古霍林郭勒"
    },
    "临清": {
        "province": "山东",
        "prov_city": "山东临清"
    },
    "巴林右旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古巴林右旗"
    },
    "沈阳": {
        "province": "辽宁",
        "prov_city": "辽宁沈阳"
    },
    "莱西": {
        "province": "山东",
        "prov_city": "山东莱西"
    },
    "登封": {
        "province": "河南",
        "prov_city": "河南登封"
    },
    "海东": {
        "province": "青海",
        "prov_city": "青海海东"
    },
    "阿勒泰": {
        "province": "新疆",
        "prov_city": "新疆阿勒泰"
    },
    "北镇": {
        "province": "辽宁",
        "prov_city": "辽宁北镇"
    },
    "新郑": {
        "province": "河南",
        "prov_city": "河南新郑"
    },
    "遂宁": {
        "province": "四川",
        "prov_city": "四川遂宁"
    },
    "北流": {
        "province": "广西",
        "prov_city": "广西北流"
    },
    "泉州": {
        "province": "福建",
        "prov_city": "福建泉州"
    },
    "河源": {
        "province": "广东",
        "prov_city": "广东河源"
    },
    "营口": {
        "province": "辽宁",
        "prov_city": "辽宁营口"
    },
    "保定": {
        "province": "河北",
        "prov_city": "河北保定"
    },
    "雷州": {
        "province": "广东",
        "prov_city": "广东雷州"
    },
    "安宁": {
        "province": "云南",
        "prov_city": "云南安宁"
    },
    "根河": {
        "province": "内蒙古",
        "prov_city": "内蒙古根河"
    },
    "七台河": {
        "province": "黑龙江",
        "prov_city": "黑龙江七台河"
    },
    "土默特左旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古土默特左旗"
    },
    "滁州": {
        "province": "安徽",
        "prov_city": "安徽滁州"
    },
    "朔州": {
        "province": "山西",
        "prov_city": "山西朔州"
    },
    "阜康": {
        "province": "新疆",
        "prov_city": "新疆阜康"
    },
    "张家口": {
        "province": "河北",
        "prov_city": "河北张家口"
    },
    "铜陵": {
        "province": "安徽",
        "prov_city": "安徽铜陵"
    },
    "长葛": {
        "province": "河南",
        "prov_city": "河南长葛"
    },
    "项城": {
        "province": "河南",
        "prov_city": "河南项城"
    },
    "平凉": {
        "province": "甘肃",
        "prov_city": "甘肃平凉"
    },
    "襄阳": {
        "province": "湖北",
        "prov_city": "湖北襄阳"
    },
    "北海": {
        "province": "广西",
        "prov_city": "广西北海"
    },
    "宜春": {
        "province": "江西",
        "prov_city": "江西宜春"
    },
    "义马": {
        "province": "河南",
        "prov_city": "河南义马"
    },
    "武威": {
        "province": "甘肃",
        "prov_city": "甘肃武威"
    },
    "靖西": {
        "province": "广西",
        "prov_city": "广西靖西"
    },
    "阿坝": {
        "province": "四川",
        "prov_city": "四川阿坝"
    },
    "宜州": {
        "province": "广西",
        "prov_city": "广西宜州"
    },
    "天水": {
        "province": "甘肃",
        "prov_city": "甘肃天水"
    },
    "阳泉": {
        "province": "山西",
        "prov_city": "山西阳泉"
    },
    "新民": {
        "province": "辽宁",
        "prov_city": "辽宁新民"
    },
    "梅河口": {
        "province": "吉林",
        "prov_city": "吉林梅河口"
    },
    "枣阳": {
        "province": "湖北",
        "prov_city": "湖北枣阳"
    },
    "咸阳": {
        "province": "陕西",
        "prov_city": "陕西咸阳"
    },
    "自贡": {
        "province": "四川",
        "prov_city": "四川自贡"
    },
    "云浮": {
        "province": "广东",
        "prov_city": "广东云浮"
    },
    "扎赉特旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古扎赉特旗"
    },
    "玉门": {
        "province": "甘肃",
        "prov_city": "甘肃玉门"
    },
    "宣威": {
        "province": "云南",
        "prov_city": "云南宣威"
    },
    "任丘": {
        "province": "河北",
        "prov_city": "河北任丘"
    },
    "新巴尔虎左旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古新巴尔虎左旗"
    },
    "喀喇沁旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古喀喇沁旗"
    },
    "拉萨": {
        "province": "西藏",
        "prov_city": "西藏拉萨"
    },
    "西昌": {
        "province": "四川",
        "prov_city": "四川西昌"
    },
    "西安": {
        "province": "陕西",
        "prov_city": "陕西西安"
    },
    "汉中": {
        "province": "陕西",
        "prov_city": "陕西汉中"
    },
    "昭通": {
        "province": "云南",
        "prov_city": "云南昭通"
    },
    "庄河": {
        "province": "辽宁",
        "prov_city": "辽宁庄河"
    },
    "西宁": {
        "province": "青海",
        "prov_city": "青海西宁"
    },
    "丽水": {
        "province": "浙江",
        "prov_city": "浙江丽水"
    },
    "喀什": {
        "province": "新疆",
        "prov_city": "新疆喀什"
    },
    "汝州": {
        "province": "河南",
        "prov_city": "河南汝州"
    },
    "玉树": {
        "province": "青海",
        "prov_city": "青海玉树"
    },
    "瑞金": {
        "province": "江西",
        "prov_city": "江西瑞金"
    },
    "铜川": {
        "province": "陕西",
        "prov_city": "陕西铜川"
    },
    "连云港": {
        "province": "江苏",
        "prov_city": "江苏连云港"
    },
    "深州": {
        "province": "河北",
        "prov_city": "河北深州"
    },
    "来宾": {
        "province": "广西",
        "prov_city": "广西来宾"
    },
    "直辖县级行政区划": {
        "province": "海南",
        "prov_city": "海南直辖县级行政区划"
    },
    "迪庆": {
        "province": "云南",
        "prov_city": "云南迪庆"
    },
    "鹤山": {
        "province": "广东",
        "prov_city": "广东鹤山"
    },
    "伊金霍洛旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古伊金霍洛旗"
    },
    "延边": {
        "province": "吉林",
        "prov_city": "吉林延边"
    },
    "达州": {
        "province": "四川",
        "prov_city": "四川达州"
    },
    "开封": {
        "province": "河南",
        "prov_city": "河南开封"
    },
    "合山": {
        "province": "广西",
        "prov_city": "广西合山"
    },
    "冷水江": {
        "province": "湖南",
        "prov_city": "湖南冷水江"
    },
    "香格里拉": {
        "province": "云南",
        "prov_city": "云南香格里拉"
    },
    "濮阳": {
        "province": "河南",
        "prov_city": "河南濮阳"
    },
    "河津": {
        "province": "山西",
        "prov_city": "山西河津"
    },
    "芜湖": {
        "province": "安徽",
        "prov_city": "安徽芜湖"
    },
    "醴陵": {
        "province": "湖南",
        "prov_city": "湖南醴陵"
    },
    "阳江": {
        "province": "广东",
        "prov_city": "广东阳江"
    },
    "迁安": {
        "province": "河北",
        "prov_city": "河北迁安"
    },
    "九江": {
        "province": "江西",
        "prov_city": "江西九江"
    },
    "华蓥": {
        "province": "四川",
        "prov_city": "四川华蓥"
    },
    "抚州": {
        "province": "江西",
        "prov_city": "江西抚州"
    },
    "汕尾": {
        "province": "广东",
        "prov_city": "广东汕尾"
    },
    "普洱": {
        "province": "云南",
        "prov_city": "云南普洱"
    },
    "开原": {
        "province": "辽宁",
        "prov_city": "辽宁开原"
    },
    "临湘": {
        "province": "湖南",
        "prov_city": "湖南临湘"
    },
    "铁岭": {
        "province": "辽宁",
        "prov_city": "辽宁铁岭"
    },
    "河间": {
        "province": "河北",
        "prov_city": "河北河间"
    },
    "大理": {
        "province": "云南",
        "prov_city": "云南大理"
    },
    "鹤岗": {
        "province": "黑龙江",
        "prov_city": "黑龙江鹤岗"
    },
    "章丘": {
        "province": "山东",
        "prov_city": "山东章丘"
    },
    "大同": {
        "province": "山西",
        "prov_city": "山西大同"
    },
    "宁国": {
        "province": "安徽",
        "prov_city": "安徽宁国"
    },
    "银川": {
        "province": "宁夏",
        "prov_city": "宁夏银川"
    },
    "毕节": {
        "province": "贵州",
        "prov_city": "贵州毕节"
    },
    "昌都": {
        "province": "西藏",
        "prov_city": "西藏昌都"
    },
    "格尔木": {
        "province": "青海",
        "prov_city": "青海格尔木"
    },
    "武穴": {
        "province": "湖北",
        "prov_city": "湖北武穴"
    },
    "调兵山": {
        "province": "辽宁",
        "prov_city": "辽宁调兵山"
    },
    "绵竹": {
        "province": "四川",
        "prov_city": "四川绵竹"
    },
    "商洛": {
        "province": "陕西",
        "prov_city": "陕西商洛"
    },
    "株洲": {
        "province": "湖南",
        "prov_city": "湖南株洲"
    },
    "新密": {
        "province": "河南",
        "prov_city": "河南新密"
    },
    "珠海": {
        "province": "广东",
        "prov_city": "广东珠海"
    },
    "万宁": {
        "province": "海南",
        "prov_city": "海南万宁"
    },
    "林州": {
        "province": "河南",
        "prov_city": "河南林州"
    },
    "灯塔": {
        "province": "辽宁",
        "prov_city": "辽宁灯塔"
    },
    "罗定": {
        "province": "广东",
        "prov_city": "广东罗定"
    },
    "昆山": {
        "province": "江苏",
        "prov_city": "江苏昆山"
    },
    "滕州": {
        "province": "山东",
        "prov_city": "山东滕州"
    },
    "利川": {
        "province": "湖北",
        "prov_city": "湖北利川"
    },
    "阜新": {
        "province": "辽宁",
        "prov_city": "辽宁阜新"
    },
    "图们": {
        "province": "吉林",
        "prov_city": "吉林图们"
    },
    "忻州": {
        "province": "山西",
        "prov_city": "山西忻州"
    },
    "乌兰察布": {
        "province": "内蒙古",
        "prov_city": "内蒙古乌兰察布"
    },
    "东方": {
        "province": "海南",
        "prov_city": "海南东方"
    },
    "巴中": {
        "province": "四川",
        "prov_city": "四川巴中"
    },
    "凉山": {
        "province": "四川",
        "prov_city": "四川凉山"
    },
    "兰溪": {
        "province": "浙江",
        "prov_city": "浙江兰溪"
    },
    "讷河": {
        "province": "黑龙江",
        "prov_city": "黑龙江讷河"
    },
    "信宜": {
        "province": "广东",
        "prov_city": "广东信宜"
    },
    "佳木斯": {
        "province": "黑龙江",
        "prov_city": "黑龙江佳木斯"
    },
    "榆树": {
        "province": "吉林",
        "prov_city": "吉林榆树"
    },
    "巴音郭楞": {
        "province": "新疆",
        "prov_city": "新疆巴音郭楞"
    },
    "孟州": {
        "province": "河南",
        "prov_city": "河南孟州"
    },
    "酒泉": {
        "province": "甘肃",
        "prov_city": "甘肃酒泉"
    },
    "阿图什": {
        "province": "新疆",
        "prov_city": "新疆阿图什"
    },
    "泰州": {
        "province": "江苏",
        "prov_city": "江苏泰州"
    },
    "韶关": {
        "province": "广东",
        "prov_city": "广东韶关"
    },
    "淄博": {
        "province": "山东",
        "prov_city": "山东淄博"
    },
    "西双版纳": {
        "province": "云南",
        "prov_city": "云南西双版纳"
    },
    "赤水": {
        "province": "贵州",
        "prov_city": "贵州赤水"
    },
    "侯马": {
        "province": "山西",
        "prov_city": "山西侯马"
    },
    "河池": {
        "province": "广西",
        "prov_city": "广西河池"
    },
    "英德": {
        "province": "广东",
        "prov_city": "广东英德"
    },
    "常宁": {
        "province": "湖南",
        "prov_city": "湖南常宁"
    },
    "鄂尔多斯": {
        "province": "内蒙古",
        "prov_city": "内蒙古鄂尔多斯"
    },
    "黔南": {
        "province": "贵州",
        "prov_city": "贵州黔南"
    },
    "南平": {
        "province": "福建",
        "prov_city": "福建南平"
    },
    "荥阳": {
        "province": "河南",
        "prov_city": "河南荥阳"
    },
    "鄂温克族自治旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古鄂温克族自治旗"
    },
    "沙河": {
        "province": "河北",
        "prov_city": "河北沙河"
    },
    "霍州": {
        "province": "山西",
        "prov_city": "山西霍州"
    },
    "黄山": {
        "province": "安徽",
        "prov_city": "安徽黄山"
    },
    "唐山": {
        "province": "河北",
        "prov_city": "河北唐山"
    },
    "白山": {
        "province": "吉林",
        "prov_city": "吉林白山"
    },
    "天长": {
        "province": "安徽",
        "prov_city": "安徽天长"
    },
    "南昌": {
        "province": "江西",
        "prov_city": "江西南昌"
    },
    "恩施": {
        "province": "湖北",
        "prov_city": "湖北恩施"
    },
    "吉林": {
        "province": "吉林",
        "prov_city": "吉林吉林"
    },
    "阆中": {
        "province": "四川",
        "prov_city": "四川阆中"
    },
    "高州": {
        "province": "广东",
        "prov_city": "广东高州"
    },
    "楚雄": {
        "province": "云南",
        "prov_city": "云南楚雄"
    },
    "乌拉特后旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古乌拉特后旗"
    },
    "集安": {
        "province": "吉林",
        "prov_city": "吉林集安"
    },
    "鄂州": {
        "province": "湖北",
        "prov_city": "湖北鄂州"
    },
    "凤城": {
        "province": "辽宁",
        "prov_city": "辽宁凤城"
    },
    "兴安盟": {
        "province": "内蒙古",
        "prov_city": "内蒙古兴安盟"
    },
    "滨州": {
        "province": "山东",
        "prov_city": "山东滨州"
    },
    "徐州": {
        "province": "江苏",
        "prov_city": "江苏徐州"
    },
    "阿克苏": {
        "province": "新疆",
        "prov_city": "新疆阿克苏"
    },
    "巢湖": {
        "province": "安徽",
        "prov_city": "安徽巢湖"
    },
    "东营": {
        "province": "山东",
        "prov_city": "山东东营"
    },
    "南阳": {
        "province": "河南",
        "prov_city": "河南南阳"
    },
    "寿光": {
        "province": "山东",
        "prov_city": "山东寿光"
    },
    "济宁": {
        "province": "山东",
        "prov_city": "山东济宁"
    },
    "巴彦淖尔": {
        "province": "内蒙古",
        "prov_city": "内蒙古巴彦淖尔"
    },
    "玉树": {
        "province": "青海",
        "prov_city": "青海玉树"
    },
    "惠州": {
        "province": "广东",
        "prov_city": "广东惠州"
    },
    "陇南": {
        "province": "甘肃",
        "prov_city": "甘肃陇南"
    },
    "南雄": {
        "province": "广东",
        "prov_city": "广东南雄"
    },
    "耒阳": {
        "province": "湖南",
        "prov_city": "湖南耒阳"
    },
    "百色": {
        "province": "广西",
        "prov_city": "广西百色"
    },
    "达尔罕茂明安联合旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古达尔罕茂明安联合旗"
    },
    "阿拉善盟": {
        "province": "内蒙古",
        "prov_city": "内蒙古阿拉善盟"
    },
    "杭锦后旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古杭锦后旗"
    },
    "长春": {
        "province": "吉林",
        "prov_city": "吉林长春"
    },
    "郑州": {
        "province": "河南",
        "prov_city": "河南郑州"
    },
    "青铜峡": {
        "province": "宁夏",
        "prov_city": "宁夏青铜峡"
    },
    "穆棱": {
        "province": "黑龙江",
        "prov_city": "黑龙江穆棱"
    },
    "太仆寺旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古太仆寺旗"
    },
    "眉山": {
        "province": "四川",
        "prov_city": "四川眉山"
    },
    "克拉玛依": {
        "province": "新疆",
        "prov_city": "新疆克拉玛依"
    },
    "宝鸡": {
        "province": "陕西",
        "prov_city": "陕西宝鸡"
    },
    "昌邑": {
        "province": "山东",
        "prov_city": "山东昌邑"
    },
    "涿州": {
        "province": "河北",
        "prov_city": "河北涿州"
    },
    "邵武": {
        "province": "福建",
        "prov_city": "福建邵武"
    },
    "盐城": {
        "province": "江苏",
        "prov_city": "江苏盐城"
    },
    "武夷山": {
        "province": "福建",
        "prov_city": "福建武夷山"
    },
    "白银": {
        "province": "甘肃",
        "prov_city": "甘肃白银"
    },
    "秦皇岛": {
        "province": "河北",
        "prov_city": "河北秦皇岛"
    },
    "宜兴": {
        "province": "江苏",
        "prov_city": "江苏宜兴"
    },
    "天门": {
        "province": "湖北",
        "prov_city": "湖北天门"
    },
    "启东": {
        "province": "江苏",
        "prov_city": "江苏启东"
    },
    "苏尼特右旗": {
        "province": "内蒙古",
        "prov_city": "内蒙古苏尼特右旗"
    },
    "双辽": {
        "province": "吉林",
        "prov_city": "吉林双辽"
    },
    "赤峰": {
        "province": "内蒙古",
        "prov_city": "内蒙古赤峰"
    },
    "沧州": {
        "province": "河北",
        "prov_city": "河北沧州"
    },
    "乳山": {
        "province": "山东",
        "prov_city": "山东乳山"
    },
    "南京": {
        "province": "江苏",
        "prov_city": "江苏南京"
    },
    "舟山": {
        "province": "浙江",
        "prov_city": "浙江舟山"
    },
    "长乐": {
        "province": "福建",
        "prov_city": "福建长乐"
    },
    "石狮": {
        "province": "福建",
        "prov_city": "福建石狮"
    },
    "宁德": {
        "province": "福建",
        "prov_city": "福建宁德"
    },
    "满洲里": {
        "province": "内蒙古",
        "prov_city": "内蒙古满洲里"
    },
    "弥勒": {
        "province": "云南",
        "prov_city": "云南弥勒"
    }
}

data = u"汉语，。、‘’“”【】测试（）#@%……&**（（%#@！~"


def hasChinese(strr):
    chinese = re.findall(u"[\u4e00-\u9fa5]", strr)
    if chinese:
        chinese = reduce(lambda x, y: x + y, chinese)
        return chinese
    return False


def hasAreaCode(strr):
    num = re.findall(u"[0-9]{3,5}", strr)
    if len(num) == 1:
        return num[0]
    return False


def fromAreaToStr(strr):
    city = ""
    for i in AREA_CODE.keys():
        if i == strr:
            city = AREA_CODE[i]["province"] + AREA_CODE[i]["city"]
            break
    if city:
        return city.decode('utf8')
    return False


def fillAreaStr(strr):
    city = ""
    for i in CITYINFO.keys():
        if i in strr:
            city = CITYINFO[i]['prov_city']
            break
    if city:
        return city
    return False


def formatArea(strr):
    try:
        if not isinstance(strr, unicode):
            strr = strr.decode('utf-8')
    except:
        error = traceback.format_exc()
        return "", u"{}".format(error)
    area_code = hasAreaCode(strr)
    area = ""
    if area_code:
        area = fromAreaToStr(area_code)
    if not area:
        area_str = hasChinese(strr)
        if area_str:
            area = fillAreaStr(area_str)
        else:
            return "", u"未发现符合要求的地区编码或名称"
    if area:
        return area.decode('utf8'), ""
    else:
        return "", u"未匹配到相应内容"


if __name__ == "__main__":

    test_list = [u"010", u"100", u"--", u"阿坝", u"安阳", u"保定", u"北京", u"北京 ", u"北京市", u"滨州", u"沧州", u"成都", u"成都市",
                 u"成都资阳眉山三地", u"承德", u"赤峰", u"大理", u"大庆", u"大同", u"东营", u"东营市", u"都匀", u"渡口", u"鄂州", u"佛山", u"甘孜",
                 u"广州", u"贵阳", u"桂林", u"国内", u"国内漫游", u"邯郸", u"杭州", u"杭州 ", u"河北保定", u"河北沧州", u"河北廊坊", u"河北石家庄", u"菏泽",
                 u"鹤壁", u"葫芦岛", u"淮安", u"淮南", u"黄冈", u"黄石", u"济南市", u"济宁", u"江门", u"焦作", u"晋中", u"凯里", u"昆明", u"拉萨",
                 u"兰州", u"廊坊", u"老挝 TANGO LAO", u"老挝LTC", u"乐山市", u"聊城", u"临汾", u"柳州", u"漯河", u"吕梁", u"马来西亚DiGi",
                 u"美国Cingular Wirel", u"美国Cingular Wireless(USACG)", u"美国VOICESTREAM-US", u"美国VOICESTREAM-USAW6", u"南通",
                 u"内蒙古", u"濮阳", u"齐齐哈尔", u"秦皇岛", u"青岛", u"日本 日本NTTDOCOMO公司", u"日本NTTDOCOMO", u"厦门", u"山东滨州", u"山东德州",
                 u"山东济南", u"山东潍坊", u"山东烟台", u"山南", u"商丘", u"上海", u"深圳", u"石家庄", u"四川成都", u"苏州", u"太原", u"泰国AIS",
                 u"泰国Real Future(True Move)", u"泰国TAC", u"泰国Truemove", u"唐山", u"天津", u"威海", u"潍坊", u"潍坊市", u"无锡", u"梧州",
                 u"武汉", u"武汉市", u"西藏(0891)", u"咸宁", u"忻州", u"新乡", u"信阳", u"邢台", u"徐州", u"许昌", u"雅安市", u"烟台", u"烟台市",
                 u"盐城", u"阳泉", u"岳阳", u"暂无", u"张家口", u"长沙", u"浙江宁波", u"郑州", u"中山", u"重庆", u"abdc", u"山西省临汾市", u"重庆重庆", u"023", u"北京市"
                 , u"内蒙古临河"
                 ]

    # print(formatArea(u"0891")[0])
    # test_list = ["河北省邯郸市"]
    import cProfile
    def test():
        for i in test_list:
            xx = formatArea(i)
            if xx[0]:
                print xx[0]
            else:
                print xx[1], "***"
    cProfile.run("test()")

