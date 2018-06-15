## mongodb 索引

    统计:
    end_time  cid  status login_status status_report
    日志:
    tel_info.flow_type    tel  start_time  sid  crawler_channel

### sid_info

```
db.getCollection('sid_info').createIndex({'sid':1}, {background:true})
db.getCollection('sid_info').createIndex({'cid':1}, {background:true})
db.getCollection('sid_info').createIndex({'tel':1}, {background:true})
db.getCollection('sid_info').createIndex({'status':1}, {background:true})

db.getCollection('sid_info').createIndex({'start_time':1}, {background:true})
db.getCollection('sid_info').createIndex({'end_time':1}, {background:true, sparse:true})
db.getCollection('sid_info').createIndex({'login_status':1}, {background:true, sparse:true})

// 以下新增或者修改

db.sid_info.dropIndex( { 'status_report': 1 } )

db.sid_info.createIndex({'start_time':-1, 'tel_info.province':1, 'tel_info.flow_type':1, 'crawler_channel':1}, {background:true})

db.sid_info.createIndex({'end_time':-1, 'login_status':1, 'status_report':1}, {background:true, sparse:true})

db.call_log.createIndex({'tel':1, 'month':1}, {background:true})
db.getCollection('sid_info').createIndex({tag_del:-1},{background:true,sparse:true})
db.getCollection('sid_info').createIndex({cache_time:-1},{background:true,sparse:true})

```

### log

```
db.getCollection('log').createIndex({'log_name':1}, {background:true})
db.getCollection('log').createIndex({'sid':1}, {background:true, sparse:true})
db.getCollection('log').createIndex({'level':1}, {background:true})
db.getCollection('log').createIndex({'created_at':1}, {background:true})
db.getCollection('log').createIndex({'crawler':1}, {background:true, sparse:true})
```

### user_info

```
db.getCollection('user_info').createIndex({'tel':1}, {background:true})
```

### call_log

```
db.getCollection('call_log').createIndex({'sid':1, 'call_tel':1, 'call_time':1}, {background:true})
db.call_log.createIndex({'sid':1, 'call_tel':1, 'call_time':1}, {background:true})
db.call_log.createIndex({'sid':1}, {background:true})
db.call_log.createIndex({'month':1}, {background:true, sparse:true})
```

### params

```
db.getCollection('params').createIndex({'sid':1}, {background:true})
db.getCollection('state').createIndex({'sid':1}, {background:true})
```

### calls_push_log

```
db.getCollection('calls_push_log').createIndex({'sid':1, 'cid':1}, {background:true, sparse:true})
```

### report

```
db.getCollection('report').createIndex({'sid':1}, {background:true})
db.getCollection('report').createIndex({'tel':1}, {background:true})
db.report.createIndex({'sid':1}, {background:true})
```

### state_log

```
db.getCollection('state_log').createIndex({'msg.execute_status':1}, {background:true, sparse:true})
db.getCollection('state_log').createIndex({'msg.sid':1}, {background:true, sparse:true})
db.getCollection('state_log').createIndex({'msg.crawler':1}, {background:true, sparse:true})
```
