# 爬虫开发检查列表

[ ] 手机号错误处理

[ ] 服务密码错误处理

[ ] 图片验证码错误处理

[ ] 短信验证码错误处理

[ ] 个人信息抓取错误日志记录

[ ] 月底账单抓取错误日志记录

[ ] 通话记录抓取错误日志记录

yum install urw-fonts libXext libXrender fontconfig libfontconfig.so.1


mongoexport -d crs -c sid_info --type=csv --fields=sid,tel_info.province,tel_info.telecom,original_channel,crawler_channel,login_status,status,status_report,start_time,login_time,end_time -q '{"start_time":{$gt:1502899200}}' --out vs.csv