# 统计 state_log

条件： 以爬虫为粒度，每个自然日为单位 `"execute_status" : 0` 的
统计每个爬虫从 `"state_flag" : "UnderCrawl"` 到 `"state_name" : "End"` 的平均时长，输出1+(n)个文件，

周期： 从 `20170512_1494518400` 到 `20170612_1497283200`

sid
tel
crawler
after_duration
befor_duration
date
flow_type

创建时间： `created`
爬虫名称： `crawler`

```
取出所有成功的：
created_end
result = select created, msg.sid, msg.crawler from mrq.state_log where msg.execute_status = 0 and msg.state_name = End and created < 1497283200

爬取成功时间：result.created 

created_mid
for循环result从msg.sid拿msg.state_flag = UnderCrawl的created
开始爬取时间 = select created from mrq.state_log where msg.state_flag = UnderCrawl and msg.sid = sid

再取 created_start： "state_name" : "Start", 的 created
```

## 总览文件 `state_log_agv.csv`

| 名称 | 示例 | 描述 |
| ---- | --- | --- |
| `crawler` | `china_mobile.shanghai` | 爬虫名称，去掉 `worker.crawler.` 和 `.main` 后的字符串 |
| `date` | 2017-12-28 | 日期，以结束时间`"state_flag" : "End"`为准 |
| `avg_time_consuming` | 99999 | 平时时长（秒） |

## 单个爬虫文件，以爬虫名称命名 `china_mobile.shanghai.csv`

| 名称 | 示例 | 描述 |
| ---- | --- | --- |
| `crawler` | china_mobile.shanghai | 爬虫名称，去掉 `worker.crawler.` 和 `.main` 后的字符串 |
| `date` | 2017-12-28 | 日期，以结束时间`"state_flag" : "End"`为准 |
| `time_consuming` | 99999 | 平时时长（秒） |


```json
{
    "_id" : ObjectId("58c48f91763f4f2bd8616a81"),
    "username" : "root",
    "relativeCreated" : 412039470.41893,
    "process" : 11224,
    "args" : [],
    "module" : "standard_state",
    "funcName" : "execute",
    "host" : "cp216-WechatService01",
    "exc_text" : null,
    "message" : {
        "execute_debug" : "",
        "pre" : {
            "execute_status" : -1,
            "execute_debug" : "",
            "execute_message" : ""
        },
        "execute_message" : "success",
        "next_action" : "",
        "state_name" : "Start",
        "parameters" : {
            "tel" : "13148832315",
            "sid" : "SIDd51515d5cd164fa4a86807569838c4be"
        },
        "verify" : {
            "login_verify_type" : "",
            "verify_content" : "",
            "verify_type" : ""
        },
        "sid" : "SIDd51515d5cd164fa4a86807569838c4be",
        "execute_status" : 0,
        "state_flag" : "WaitLogin",
        "crawler" : "worker.crawler.china_mobile.shanghai.main"
    },
    "name" : "worker.state.standard_state",
    "thread" : NumberLong(140176810903504),
    "created" : 1489276817.36343,
    "threadName" : "DummyThread-114",
    "msecs" : 363.432884216309,
    "filename" : "standard_state.py",
    "levelno" : 20,
    "processName" : "MainProcess",
    "pathname" : "/home/Code/call_history_crawler/worker/state/standard_state.py",
    "lineno" : 59,
    "time" : ISODate("2017-03-12T08:00:17.363Z"),
    "msg" : {
        "execute_debug" : "",
        "pre" : {
            "execute_status" : -1,
            "execute_debug" : "",
            "execute_message" : ""
        },
        "execute_message" : "success",
        "next_action" : "",
        "state_name" : "Start",
        "parameters" : {
            "tel" : "13148832315",
            "sid" : "SIDd51515d5cd164fa4a86807569838c4be"
        },
        "verify" : {
            "login_verify_type" : "",
            "verify_content" : "",
            "verify_type" : ""
        },
        "sid" : "SIDd51515d5cd164fa4a86807569838c4be",
        "execute_status" : 0,
        "state_flag" : "WaitLogin",
        "crawler" : "worker.crawler.unicom.main"
    },
    "exc_info" : null,
    "levelname" : "INFO"
}
```
