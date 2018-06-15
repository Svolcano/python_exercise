# logger 日志说明

### 通用方法，按日志分类名称`log_name`进行记录: `log(log_name, level, message, sid=None, crawler=None)`

## `logger` 数据结构 `*` 为必填

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `*` `log_name` | stirng | state_log | 日志分类名称，比如：状态日志名称为`state_log`，爬虫为`crawler_log`，API为`api`，mrq为`mrq` |
| `*` `level` | stirng | DEBUG | `DEBUG线上不记录此级别` `ERROR` `INFO` |
| `sid` | stirng | SID384cbde729894650a8fe390e53988200 | 唯一标识符SID |
| `*` `message` | string, mixed | 记录错误信息方便debug | `traceback.format_exc()`内容，或者自定义的错误消息 |
| `state_log` | [state_log](#state_log) | 运营商返回失败 | |
| `crawler` | stirng | china_mobile.shanghai | 爬虫名称 |
| `*` `file_name` | 文件名 | /call_history_crawler/worker/state/standard_state.py | 在哪个文件出错了 |
| `*` `file_line` | 行数 | 128 | 在第几行出错了 | 
| `*` `IPv4` | string | 172.18.19.219 | 创建时间 |
| `*` `created_at` | timestamp | 1498082878 | 创建时间 |

### `state_log` <span id="state_log">状态机日志数据结构</span>

| 名称 | 示例 | 描述 |
| ---- | --- | --- |
| `state_name` | WaitVerifyRequest | 当前状态机名称 |
| `execute_status` | 9999 | 状态码 |
| `execute_msg` | 9999 | 状态码 |
| `parameters` | [params](#params) | 爬虫debug日志 |
| `next_action` | GetSMS | 下一步操作 |
| `state_flag` | UnderVerifyRequest | 下一步状态机名称 |

### `crawler_log` 爬虫日志数据结构

| 名称 | 示例 | 描述 |
| ---- | --- | --- |
| `status_key` | `crawl_error` | 状态索引 |
| `req_url` | http://iservice.10010.com/e3/static/query/queryHistoryBill? | url |
| `req_params` | {tel:'...'} | 请求参数 |
| `req_header` | {Referer:'...'} | 请求头 |
| `res_status_code` | 200 | 响应状态码 |
| `res_header` | "Connection" : "keep-alive", "Content-Type" : "text/plain;charset=UTF-8", "Content-Encoding": ... | 响应头 |
| `res_body` | html, json, xml, xmljson | 响应内容 |

### crawler_log

```
{
    "_id" : ObjectId("5965919c763f4f9a49efb25d"),
    "log_name" : "crawler_log",
    "level" : "ERROR",
    "created_at" : 1499828635,
    "crawler_log" : {
        "func_name" : "crawl_call_log",
        "status_key" : "crawl_error",
        "req_header" : "{'Accept-Encoding': 'gzip, deflate', 'Host': 'shop.10086.cn', 'Accept': '*/*', 'User-Agent': u'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36', 'Connection': 'keep-alive', 'Referer': 'http://shop.10086.cn/i/?f=billdetailqry&welcome=1499828633436', 'Cookie': 'ssologinprovince=791; userinfokey=%7b%22loginType%22%3a%2201%22%2c%22provinceName%22%3a%22791%22%2c%22pwdType%22%3a%2201%22%2c%22userName%22%3a%2215070876044%22%7d; c=a9e526485588431e9cc7812b57516d12; loginName=15070876044; verifyCode=381503868de0d321816533e61034d1666b85c0b9; jsessionid-echd-cpt-cmcc-jt=EDBD5CB3DD4067F22CFFB567A27E1395; cmccssotoken=a9e526485588431e9cc7812b57516d12@.10086.cn; is_login=true'}",
        "res_body" : "({\"data\":[],\"retCode\":\"2039\",\"retMsg\":\"您选择时间段没有详单记录哦\",\"sOperTime\":\"20170712110354\"})",
        "req_params" : "None",
        "res_header" : "{'Content-Length': '110', 'wtlwpp-rest': '217_8713', 'Server': 'ngx_openresty', 'Connection': 'Keep-alive', 'Date': 'Wed, 12 Jul 2017 03:03:53 GMT', 'Content-Type': 'application/text;charset=utf-8'}",
        "req_url" : "https://shop.10086.cn/i/v1/fee/detailbillinfojsonp/15070876044?qryMonth=201702&callback=&step=100&curCuror=1&_=1499828632435&billType=02",
        "res_status_code" : "200"
    },
    "IPv4" : "cp216-WechatService01",
    "sid" : "SID217b56a678cd4a798cbc217e1f853681",
    "message" : "您选择时间段没有详单记录哦",
    "crawler" : "china_mobile.all_entry"
}
```

### state_log

```
"msg" : {
    "execute_status" : 0,
    "execute_message" : "",
    "state_name" : "Failed",
    "parameters" : {
        "province" : "吉林",
        "city" : "白山",
        "tel" : "15943910614",
        "flow_type" : "10086",
        "pin_pwd" : "193166",
        "verify_type" : "",
        "id_card" : "",
        "sms_code" : "261577",
        "full_name" : "",
        "sid" : "SID6b93c064587c4350a7d10fa2bddd48b1",
        "captcha_code" : "j3uilk",
        "crawler" : "worker.crawler.china_mobile.all_entry.main"
    },
    "next_action" : "Reset",
    "state_flag" : "",
}
```
