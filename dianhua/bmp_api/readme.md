日期	rpt_date
客户名称 cid
运营商	telecom
渠道	crawler_channel
省	province
统计量
尝试量	total_nums
授权成功量	authen_nums
爬取成功量	crawl_nums
最终成功量	final_nums
报告生成量	report_nums
爬取成功号码量	tel_nums
详单完整量	call_log_intact_nums
账单完整量	bill_intact_nums
统计率
授权成功率	authen_pct
爬取成功率	crawl_pct
最终成功率	final_pct
报告生成率	report_pct
详单缺失率	log_loss_pct
账单缺失率	bill_loss_pct
单日号码重复率	tel_repeat_pct
耗时
授权耗时
最短耗时	authen_cost_min
最长耗时	authen_cost_max
75分位	authen_cost_75
99分位	authen_cost_99
均值	authen_cost_mean
爬取耗时
最短耗时	crawl_cost_min
最长耗时	crawl_cost_max
75分位	crawl_cost_75
99分位	crawl_cost_99
均值	crawl_cost_mean
报告耗时
最短耗时  report_used_min
最长耗时  report_used_max
75分位  report_used_75
99分位 report_used_99
均值    report_used_mean
错误码Top10   err_code_top10

注意项:
1、	统计数据中cid字段，原数据缺失情况下，使用（int）-1填充。
2、	其他数字类统计字段，缺失使用 0填充。
3、	err_code_top10统计字段，存在统计数据使用{key:value,错误码:次数}格式保存；缺失使用{}填充；经过统计发现，目前该字段没有达到10个key的情况，目前代码中未做截取top10，错误信息全部输出。
4、	其他string类字符串字段，缺失使用’miss’填充。
5、计算公式：
授权成功率=授权成功数/尝试授权量
爬取成功率=爬取成功量/授权成功量
报告生成率=报告生成量/爬取成功量
详单缺失率=（最终成功量-详单完整量）/最终成功量
账单缺失率=（最终成功量-账单完整量）/最终成功量

#关于新增加的密码重置次数的数据， 这些数据存在于：
tid_info 这个表中。
tid 是唯一所以， 每一个操作对应一个tid
status 状态为0 ， 表示重置成功 否则表示失败。
