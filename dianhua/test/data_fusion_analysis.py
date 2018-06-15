# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 16:56:51 2018

@author: admin
"""

import pymongo
import time
import datetime
import sys
import getopt
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#plt.rcParams['font.sans-serif'] = ['SimHei']        # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False          # 解决保存图像是负号'-'显示为方块的问题
from lxml import etree
from io import BytesIO
import base64
import urllib
sys.path.append('../')
reload(sys)
sys.setdefaultencoding("utf8")

COL_MAP={'rpt_date':'报告日期',
     'count_10010_sid_hit':'联通sid命中数',
     'count_10010_tel_hit':'联通tel命中数',
     'count_10010_sid_miss':'联通sid缺失数',
     'count_10010_tel_miss':'联通tel缺失数',
     'count_10010_all_tel':'联通当日总tel数',
     'count_10010_all_sid':'联通当日总sid数',
     'sid_10010_miss_hit_rate':'联通sid缺失被缓存命中比例',
     'tel_10010_miss_hit_rate':'联通tel缺失被缓存命中比例',
     'tel_10010_all_hit_rate':'联通tel命中数在总tel中占比',
     'count_10086_sid_hit':'移动sid命中数',
     'count_10086_tel_hit':'移动tel命中数',
     'count_10086_sid_miss':'移动sid缺失数',
     'count_10086_tel_miss':'移动tel缺失数',
     'count_10086_all_tel':'移动当日总tel数',
     'count_10086_all_sid':'移动当日总sid数',
     'sid_10086_miss_hit_rate':'移动sid缺失被缓存命中比例',
     'tel_10086_miss_hit_rate':'移动tel缺失被缓存命中比例',
     'tel_10086_all_hit_rate':'移动tel命中数在总tel中占比',
     'count_189_sid_hit':'电信sid命中数',
     'count_189_tel_hit':'电信tel命中数',
     'count_189_sid_miss':'电信sid缺失数',
     'count_189_tel_miss':'电信tel缺失数',
     'count_189_all_tel':'电信当日总tel数',
     'count_189_all_sid':'电信当日总sid数',
     'sid_189_miss_hit_rate':'电信sid缺失被缓存命中比例',
     'tel_189_miss_hit_rate':'电信tel缺失被缓存命中比例',
     'tel_189_all_hit_rate':'电信tel命中数在总tel中占比',
     'count_call_log_cache':'截至当日缓存中tel总数',}



MONGO_CONFIG = {
#    'host': '127.0.0.1',
    'host': '172.18.21.117',
    'port': 27017,
    'db': 'crs'
}
class Pro_MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self):
        self.conn = None
        self.set_pro_db_conn()

    def set_pro_db_conn(self):
        self.client = pymongo.MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'], connect=False)
        self.conn = self.client[MONGO_CONFIG['db']]

    def export_data(self,begindate,enddate):
        data = self.conn['data_fusion_rpt'].find({"rpt_date":{'$gte':begindate,'$lte':enddate}},{'_id':0})
        return data

def sid_miss_hit_rate(rpt_10010,rpt_10086,rpt_189):
#    ax1 = plt.subplot(1,1,1,facecolor='white')
    plt.title('7 day sid_miss_hit_rate')            #设置图体，plt.title
    plt.ylabel('sid miss hit count')                    #设置x轴名称,plt.xlabel
    plt.xlabel('date ')                    #设置y轴名称,plt.ylabel
    fig,ax = plt.subplots()
    ax.set_xticklabels(rpt_10010['rpt_date'],rotation=15)
#    ax1.plot(iris['rpt_date'],iris['count_10010_sid_hit'],alpha=0.5,color='r')   #线图：linestyle线性，alpha透明度，color颜色，label图>例文本
    plt.plot(rpt_10010['rpt_date'],rpt_10010['sid_10010_miss_hit_rate'],label='10010',color='green',marker='x')
    plt.plot(rpt_10086['rpt_date'],rpt_10086['sid_10086_miss_hit_rate'],label='10086',color='red',marker='x')
    plt.plot(rpt_189['rpt_date'],rpt_189['sid_189_miss_hit_rate'],label='10000',color='skyblue',marker='x')
    plt.legend()
    # figure 保存为二进制文件
    buffer = BytesIO()
    plt.savefig(buffer)
    plot_data = buffer.getvalue()
    return plot_data

def shape_2_html(plot_data):
    imb = base64.b64encode(plot_data)
    #imb = plot_data.encode('base64')   # 对于 Python 2.7可用
    ims = imb.decode()
    imd = "data:image/png;base64,"+ims
    iris_im = """<h1>7日联通sid命中情况(可视化调试中)</h1>""" + """<img src="%s">""" % imd
    return iris_im




BEGIN_DATE='2018-05-10'
END_DATE='2018-05-16'

if __name__=='__main__':
    pro_conn = Pro_MongodbConnection()
    opts, args = getopt.getopt(sys.argv[1:], "b:e:")
    for op, value in opts:
        if op == "-b":
            BEGIN_DATE = value
        elif op == "-e":
            END_DATE = value
    all_data=[]
    fusion_data_all=pro_conn.export_data(BEGIN_DATE,END_DATE)
    #fusion_data_all=pd.read_csv('rpt_fusion_data.csv')
    for one_record in fusion_data_all:
        columns=one_record.keys()
        line=one_record.values()
        all_data.append(line)
    all_data=np.array(all_data)
    rpt = pd.DataFrame(all_data,columns=columns)
    #print rpt
    #rpt=fusion_data_all
    col_10010=sorted([x for x in rpt.columns if '10010' in x],reverse=True)
    col_10086=sorted([x for x in rpt.columns if '10086' in x],reverse=True)
    col_189=sorted([x for x in rpt.columns if '189' in x],reverse=True)
    col_10010.insert(0,'rpt_date')
    col_10086.insert(0,'rpt_date')
    col_189.insert(0,'rpt_date')
    rpt_10010= pd.DataFrame(rpt,columns = col_10010)
    rpt_10086= pd.DataFrame(rpt,columns = col_10086)
    rpt_189= pd.DataFrame(rpt,columns = col_189)
    
    plot=sid_miss_hit_rate(rpt_10010,rpt_10086,rpt_189)
    
    rpt_10010.columns=[COL_MAP[x] for x in col_10010]
    rpt_10086.columns=[COL_MAP[x] for x in col_10086]
    rpt_189.columns=[COL_MAP[x] for x in col_189]
    iris_im=shape_2_html(plot)
    root = "<title>数据融合状态报告</title>"
    #pd.pivot_table(rpt, index=['rpt_date'])[:10]
    iris_10010_des = """<h1>联通7日数据融合报告数据汇总</h1>"""+rpt_10010.to_html()
    iris_10086_des = """<h1>移动7日数据融合报告数据汇总</h1>"""+rpt_10086.to_html()
    iris_189_des = """<h1>电信7日数据融合报告数据汇总</h1>"""+rpt_189.to_html()
    root = root + iris_10010_des+ iris_10086_des+ iris_189_des + iris_im  #将多个 html 格式的字符串连接起来

    # lxml 库的 etree 解析字符串为 html 代码，并写入文件
    html = etree.HTML(root)
    tree = etree.ElementTree(html)
    tree.write('iris.html')
    #print columns

#    # 最后使用默认浏览器打开 html 文件
#    import webbrowser
#    webbrowser.open('iris.html',new = 1)

