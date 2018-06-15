### sid_info

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `cid` | stirng | 开发者id |
| `sid` | stirng | 业务层与服务层间的通讯SID |
| `status` | int | 爬取数据状态码 |
| `status_report` | int | 报告生成状态 `1:生成中` `0：报告生成完成` `2:生成错误` |
| `message` | stirng | 状态码讯息 |
| `tel` | stirng | 用户电话号码 |
| `tel_info` | [tel_info](#tel_info) | 号码相关资讯 |
| `expire_time` | datetime | SID 过期时间 |
| `start_time` | datetime | 数据爬取起始时间 |
| `end_time` | datetime | 数据爬取结束时间 |
| `call_log_missing_month_list` | list | 语音通讯详单**整月缺失**月份列表，确认是运营商繁忙、系统稳定性报错等原因的问题月份列表 |
| `call_log_possibly_missing_month_list` | list | 语音通讯详单可能**整月缺失**的月份列表，不太确定是用户当月无通话记录还是因为运营商系统错误等原因的问题月份列表 |
| `call_log_part_missing_month_list` | list | 语音通讯详单可能**部分缺失**的月份列表，获取用户通话记录不完整的问题月份列表 |
| `phone_bill_missing_month_list` | list | 月度账单缺失月份列表 |
| `tags_label` | string | 本机号码标记名称 |
| `tags_label_times` | string | 本机号码标记次数 |
| `tags_yellow_page` | string | 黄页名称 |
| `emergency_contact` | [emergency_contact](#emergency_contact) | 紧急联系人信息 |
| `report_used`|stirng|报告生成耗时|
|`report_create_time`|int|报告创建时间|
|`report_message`|string|报告状态信息|

### `emergency_contact` <span id="emergency_contact">数据结构 (紧急联系人)</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `contact_priority` | string | 1 | 紧急联系人顺序优先级 |
| `contact_tel` | string | 13800138000 | 紧急联系人号码 |
| `contact_name` | string | 张三 | 紧急联系人姓名 |
| `contact_relationship` | string | 朋友 | 紧急联系人关系 |
| `contact_tags_financial` | string | 理财 | 紧急联系人号码金融标签 |
| `contact_tags_label` | string | `保险` | 紧急联系人号码标记 |
| `contact_tags_label_times` | string | `36` | 紧急联系人号码标记次数 |
| `contact_tags_yellow_page` | string | 北京三牛科技有限公司 | 紧急联系人黄页名称 |

### `tel_info` <span id="tel_info">号码相关资讯</span>

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `flow_type` | string | 代表号码所属运营商与后续验证方式 |
| `need_full_name` | int | 登入页面是否需用户名称 |
| `need_id_card` | int | 登入页面是否需用户身分证号 |
| `need_pin_pwd` | int | 登入页面是否需要输入服务密码 |
| `need_sms_verify` | int | 登入页面是否需要短信验证 |
| `need_captcha_verify` | int | 登入页面是否需要图型验证 |
| `register_link` | string | 免费注册网址 |
| `pwd_reset_link` | string | 密码忘记重新注册网址 |
| `telecom` | string | 號碼所屬运营商 |
| `province` | string | 号码所属省份 |
| `city` | string | 号码所属城市 |

### mongodb data:

```json
{
    "_id" : ObjectId("58af8f3e322fa972029cb344"),
    "status" : 3003,
    "tel_info" : {
        "province" : "山东",
        "city" : "潍坊",
        "need_captcha_verify" : 1,
        "telecom" : "中国移动",
        "need_sms_verify" : 0,
        "pwd_reset_link" : "https://bj.ac.10086.cn/ac/html/resetpassword.html",
        "register_link" : "https://login.10086.cn/html/register/register.html",
        "flow_type" : "10086",
        "sid" : "SID525f2307f8c44451a0f5c95e596b5b50",
        "need_pin_pwd" : 1,
        "need_full_name" : 0,
        "need_id_card" : 0
    },
    "tel" : "15762559079",
    "uid" : "",
    "sid" : "SID2876023ceae74262b56ec9a2780123ef",
    "expire_time" : 1487900810,
    "start_time" : 1487900478,
    "message" : "get parameter timeout",
    "end_time" : 1487900830
}
```
