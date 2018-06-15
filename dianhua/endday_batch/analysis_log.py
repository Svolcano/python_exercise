# -*- coding: utf-8 -*-


import pandas
import pandas as pd
import json,time

import sys
reload(sys)
sys.setdefaultencoding('utf8')

# df = pandas.read_csv('sid_info_test.csv')
# df.to_csv('elk_log_{}.csv'.format(time.strftime('%Y%m%d')), encoding='utf_8_sig', index=False)
# date = time.strftime('%Y%m%d')
date = '20180418'
df = pandas.read_csv('elk_log_{}.csv'.format(date))
print time.strftime('%Y%m%d')

"""
[u'cid', u'uid', u'source', u'sid', u'channel', u'tel', u'telecom',
 u'province', u'city', u'authen_status', u'crawl_status',
 u'report_status', u'authen_used', u'crawl_used', u'report_used',
 u'process', u'process_status', u'call_log_missing_list',
 u'call_log_prob_missing_list', u'call_log_part_missing_list',
 u'phone_bill_missing_list', u'flow_api-flow_api',
 u'flow_api-getcaptcha_api', u'flow_api-getsmscaptcha_api',
 u'flow_api-login_api', u'getcaptcha_api-flow_api',
 u'getcaptcha_api-getcaptcha_api', u'getcaptcha_api-login_api',
 u'getsmscaptcha_api-flow_api', u'getsmscaptcha_api-getsmscaptcha_api',
 u'getsmscaptcha_api-login_api', u'getsmscaptcha_api-verify_api',
 u'login_api-flow_api', u'login_api-getcaptcha_api',
 u'login_api-getsmscaptcha_api', u'login_api-login_api',
 u'login_api-verify_api', u'verify_api-flow_api',
 u'verify_api-getsmscaptcha_api', u'verify_api-verify_api',
 u'process_delta_time']
"""

# print df.columns
# print df.tail()
# print df.groupby('telecom')['telecom'].count()
# print df.groupby('telecom')['authen_status']

# print total_each
# print login_true_each, authen_true_pct
# print crawl_true_each, crawl_true_pct
# print report_true_each, report_true_pct
# exit()
# 数据格式化
# df['authen_used'] = df['login_time'] - df['start_time']
# df['crawl_used'] = df['end_time'] - df['login_time']
# df['report_used'] = df['report_create_time'] - df['end_time']
df['channel'] = df['channel'].fillna('yulore')
df['telecom'] = df['telecom'].str.replace('中国','')
# import pdb; pdb.set_trace()
# df['report_used'] = df['report_used'].map(lambda x: int(float(x)) if x else 0)
# df['province'] = df['province'].fillna('未知')
# df['city'] = df['city'].fillna('未知')

# print df.loc[(~(df.authen_status.isin([0]) )) & (df.crawler_channel == 'xinde')]
# print df.groupby('crawler_channel')['crawler_channel'].count()
# df = df.fillna(-99)


def get_stats(df):
    total = df.shape[0]
    authen_true = df.loc[df.authen_status == 0].shape[0]
    crawl_true = df.loc[(df.authen_status == 0) &
                        (df.crawl_status == 0)].shape[0]
    report_true = df.loc[(df.authen_status == 0) & (
        df.crawl_status == 0) & (df.report_status == 0)].shape[0]
    authen_true_pct = authen_true*100.0/total
    crawl_true_pct = crawl_true*100.0/authen_true if authen_true else 0
    report_true_pct = report_true*100.0/crawl_true if crawl_true else 0
    # print authen_true, crawl_true, report_true, report_true_pct
    return {
        "total": total,
        "authen_true": authen_true,
        "authen_true_pct": authen_true_pct,
        "crawl_true": crawl_true,
        "crawl_true_pct": crawl_true_pct,
        "report_true": report_true,
        "report_true_pct": report_true_pct,
    }


def groupd_stats(df, groupd=None):
    data_list = list()
    if len(groupd) == 1:
        for k1, group in df.groupby(groupd):
            # print k1
            stats_dict = get_stats(group)
            stats_dict.update({groupd[0]: k1})
            data_list.append(stats_dict)
    elif len(groupd) == 2:
        for (k1, k2), group in df.groupby(groupd):
            # print k1,k2
            stats_dict = get_stats(group)
            stats_dict.update({groupd[0]: k1, groupd[1]: k2})
            data_list.append(stats_dict)
    elif len(groupd) == 3:
        for (k1, k2, k3), group in df.groupby(groupd):
            # print k1,k2,k3
            stats_dict = get_stats(group)
            stats_dict.update({groupd[0]: k1, groupd[1]: k2, groupd[2]: k3})
            data_list.append(stats_dict)
    return sorted(data_list, key=lambda k: k.get('total', 0), reverse=True)


# 总览
all_stats = df
# print all_stats

# 客户
cid_stats = groupd_stats(df, groupd=['cid'])
# print cid_stats

# 客户，渠道
cid_channel_stats = groupd_stats(df, groupd=['cid', 'channel'])
# print cid_channel_stats

# 客户，运营商
cid_cxcc_stats = groupd_stats(df, groupd=['cid', 'telecom'])
# print cid_cxcc_stats

# 客户，地区
cid_prov_stats = groupd_stats(df, groupd=['cid', 'province'])
# print cid_prov_stats

# 客户，渠道，运营商
cid_cxcc_prov_stats = groupd_stats(df, groupd=['cid', 'telecom', 'province'])
# print cid_cxcc_prov_stats

# 客户，渠道，运营商
cid_channel_cxcc_stats = groupd_stats(df, groupd=['cid', 'channel', 'telecom'])
# print cid_channel_cxcc_stats

# 运营商，地区
# prov_cxcc_stats = groupd_stats(df, groupd=['province', 'telecom'])
# print prov_cxcc_stats

# 渠道
# channel_stats = groupd_stats(df, groupd=['crawler_channel'])
# print channel_stats

# 运营商，渠道
# channel_cxcc_stats = groupd_stats(df, groupd=['crawler_channel', 'telecom'])
# print channel_cxcc_stats

# 运营商，地区，渠道
# channel_prov_cxcc_stats = groupd_stats(
    # df, groupd=['crawler_channel', 'province', 'telecom'])
# print channel_prov_cxcc_stats


# 失败原因分析
# import operator
# error_dict = df.groupby('crawl_status')['crawl_status'].count(
# ).sort_values(ascending=False).to_dict()
# error_list = sorted(error_dict.items(),
                    # key=operator.itemgetter(1), reverse=True)
# print error_list,len(error_list)

error_channel_stats = df.groupby(['crawl_status', 'channel'])[
    'crawl_status'].count()
error_channel_stats = error_channel_stats.rename('times')
# error_channel_dict = error_channel_stats.sort_values(ascending=False).to_dict()
# error_channel_list = sorted(error_channel_dict.items(),
                    # key=operator.itemgetter(1), reverse=True)
error_cid_channel_stats = df.groupby(['cid','crawl_status', 'channel'])[
    'crawl_status'].count()
error_cid_channel_stats = error_cid_channel_stats.rename('times')

# error_cid_channel_dict = error_cid_channel_stats.sort_values(ascending=False).to_dict()
# error_cid_channel_list = sorted(error_cid_channel_dict.items(),
                            # key=operator.itemgetter(1), reverse=True)
# exit()

df = df.loc[(df.authen_used >= 1) & (df.crawl_used >= 1) & (
    df.crawl_used <= 300) & (df.report_used >= 1) & (df.report_used <= 140)]

# 耗时


def used_stats(df, pattern='crawl_used'):
    used_min = df[pattern].min()
    used_max = df[pattern].max()
    used_mean = df[pattern].mean()
    used_75 = df[pattern].quantile(0.75)
    used_98 = df[pattern].quantile(0.98)
    return {
        "used_min": used_min,
        "used_max": used_max,
        "used_mean": used_mean,
        "used_75": used_75,
        "used_98": used_98,
    }


used_df = df
# 授权耗时
# print df.loc[df.report_used >= 200].count()
authen_used = used_stats(used_df, pattern='authen_used')
print authen_used

# 爬取耗时
crawl_used = used_stats(used_df)
print crawl_used

# 报告耗时
report_used = used_stats(used_df, pattern='report_used')
print report_used

# data = {
#     # 'all_stats': all_stats,
#     'cid_stats': cid_stats,
#     'cid_channel_stats': cid_channel_stats,
#     'cid_cxcc_stats': cid_cxcc_stats,
#     'cid_prov_stats': cid_prov_stats,
#     'cid_cxcc_prov_stats': cid_cxcc_prov_stats,
#     'cid_channel_cxcc_stats': cid_channel_cxcc_stats,
#     # 'error_list': error_list,
#     'authen_used': authen_used,
#     'crawl_used': crawl_used,
#     'report_used': report_used,
# }

# with open('elk_stats_{}.json'.format(date), 'w') as fp:
    # json.dump(data, fp, indent=4, sort_keys=True, ensure_ascii=False)

writer = pd.ExcelWriter('elk_stats_{}.xlsx'.format(date))

# all_stats_data = df
all_stats.to_excel(writer, 'all_stats', index=False)

cid_stats_df = pd.DataFrame(cid_stats).ix[:, ['cid', 'total', 'authen_true', 'authen_true_pct', 'crawl_true', 'crawl_true_pct', 'report_true', 'report_true_pct']]
cid_stats_df.to_excel(writer, 'cxcc_stats', index=False)

cid_channel_stats_df = pd.DataFrame(cid_channel_stats).ix[:, [
    'cid', 'channel', 'total', 'authen_true', 'authen_true_pct', 'crawl_true', 'crawl_true_pct', 'report_true', 'report_true_pct']]
cid_channel_stats_df.to_excel(writer, 'cid_channel_stats', index=False)

cid_cxcc_stats_df = pd.DataFrame(cid_cxcc_stats).ix[:, [
    'cid', 'telecom', 'total', 'authen_true', 'authen_true_pct', 'crawl_true', 'crawl_true_pct', 'report_true', 'report_true_pct']]
cid_cxcc_stats_df.to_excel(writer, 'cid_cxcc_stats', index=False)

cid_channel_cxcc_stats_df = pd.DataFrame(cid_channel_cxcc_stats).ix[:, [
    'cid', 'channel', 'telecom', 'total', 'authen_true', 'authen_true_pct', 'crawl_true', 'crawl_true_pct', 'report_true', 'report_true_pct']]
cid_channel_cxcc_stats_df.to_excel(writer, 'cid_channel_cxcc_stats', index=False)

cid_prov_stats_df = pd.DataFrame(cid_prov_stats).ix[:, [
    'cid', 'province', 'total', 'authen_true', 'authen_true_pct', 'crawl_true', 'crawl_true_pct', 'report_true', 'report_true_pct']]
cid_prov_stats_df.to_excel(writer, 'cid_prov_stats', index=False)

cid_cxcc_prov_stats_df = pd.DataFrame(cid_cxcc_prov_stats).ix[:, [
    'cid', 'province', 'telecom', 'total', 'authen_true', 'authen_true_pct', 'crawl_true', 'crawl_true_pct', 'report_true', 'report_true_pct']]
cid_cxcc_prov_stats_df.to_excel(writer, 'cid_cxcc_prov_stats', index=False)


# err_data = pd.DataFrame(error_list)
# err_data.columns = ['status', 'times']
# err_data.to_excel(writer, 'error_stats', index=False)

error_channel_stats.to_excel(writer, 'error_channel_stats')

error_cid_channel_stats.to_excel(writer, 'error_cid_channel_stats')

used_data = pd.DataFrame(
    {'authen_used': authen_used, 'crawl_used': crawl_used, 'report_used': report_used})
used_data.to_excel(writer, 'used_stats', index=False)

# err_channel_data = pd.DataFrame(error_channel_list)
# err_channel_data.to_excel(writer, 'err_channel_data')

# err_cid_channel_data = pd.DataFrame(error_cid_channel_list)
# err_cid_channel_data.to_excel(writer, 'err_cid_channel_data')
writer.save()

