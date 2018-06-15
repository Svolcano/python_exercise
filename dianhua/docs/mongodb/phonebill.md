[TOC]

# 运营商数据

## `phonebill` 运营商数据

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `sid` | stirng | SID384cbde729894650a8fe390e53988200 | 唯一标识符SID |
| `cid` | stirng | 1234567890 | 开发者id |
| `uid` | stirng | abc123 | 用户id |
| `status` | integer | 1 | 爬取数据状态码 |
| `message` | stirng | 状态码描述 |
| `login_status` | integer | 1 | 授权状态 `0：成功` `1:失败` |
| `report_status` | integer | 报告生成状态 `0：报告生成完成` `1:生成错误` |
| `flow` | [flow](#flow) | 授权流程信息 |
| `tel` | stirng | 用户电话号码 |
| `tel_info` | [tel_info](#tel_info) | 运营商登记信息 |
| `tel_tags_label` | string | 本机号码标记名称|
| `tel_tags_label_times` | string | 本机号码标记次数 |
| `tel_tags_yellow_page` | string | 黄页名称 |
| `user_info` | [user_info](#user_info) | 用户个人信息数据结构 |
| `user_contact` | [user_contact](#user_contact) | 紧急联系人信息数据结构 |
| `call_log` | [call_log](#call_log) | 通话详单 |
| `sms_log` | [sms_log](#sms_log) | 短信详单 |
| `data_log` | [data_log](#data_log) | 流量详单 |
| `data_access` | [data_access](#data_access) | 流量使用记录（目前只有联通有） |
| `phone_bill` | [phone_bill](#phone_bill) | 月度账单 |
| `expire_time` | timestamp | SID 过期时间 |
| `start_time` | timestamp | 数据爬取起始时间 |
| `end_time` | timestamp | 数据爬取结束时间 |

### `tel_info` <span id="tel_info">运营商登记信息</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `id_card` | string | `1102****1065` | 手机登记身份证号 |
| `full_name` | string | `王**` | 手机登记姓名 |
| `address` | string | `北京市通州区**新华北街9号院9号楼3单元401号` | 手机登记地址 |
| `open_date` | timestamp | `1487900810` | 开卡时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |

### `call_log` <span id="call_log">通话详单</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `call_tel` | string | 18202541892 | 电话号码 |
| `call_cost` | string | 0.00 | 通话费用 |
| `call_time` | timestamp | `1487900810` | 通话起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
| `call_method` | string | 主叫 | 呼叫类型, 固定枚举类型： `主叫`, `被叫`, 如果运营商原始数据不是主叫被叫，需要转换成主叫被叫字符串 |
| `call_type` | string | 本地 | 通话类型（本地, 长途）  |
| `call_from` | string | 北京市 | 本机通话地 |
| `call_to` | string | 长沙市 | 对方归属地 |
| `call_duration` | integer | 300 | 通话时长(秒), 如果运营商原始数据不是秒，需要转换成整型秒，已知类型： `00:12:04`, `0小时4分5秒` |

### `sms_log` <span id="sms_log">短信详单</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `sms_time` | timestamp | `1487900810` | 起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
| `sms_method` | stirng | 接收 | 通信类型, 固定枚举类型： `接收`, `发送`, 如果运营商原始数据不是接收发送，需要转换接收发送字符串 |
| `sms_tel` | stirng | 10086 | 对方号码 |
| `sms_loc` | stirng | 国内短信 | 通信地点, 已知类型： `国内短信`, `内地` |
| `sms_type` | stirng | 短信 | 信息类型, 已知类型： `短信`, `彩信` |
| `sms_fee` | stirng | 0.00 | 通信费 |

### `data_log` <span id="data_log">流量详单</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `data_log_time` | timestamp | `1487900810` | 起始时间, 如果运营商原始数据不是时间戳，需要转换成时间戳 |
| `data_log_loc` | stirng | 北京 | 上网地点 |
| `data_log_duration` | integer | 300 | 上网时长(秒), 如果运营商原始数据不是秒，需要转换成整型秒，已知类型： `00:12:04`, `0小时4分5秒` |
| `data_log_total` | stirng | 259.54 | 总流量(kb), 已知类型： `259.54`, `0.45KB` |
| `data_log_network` | stirng | 4G网络 | 网络类型 |
| `data_log_network_type` | stirng | 非定向流量 | 是否定向 |
| `data_log_fee_type` | stirng | 套餐内流量 | 计费类型, 已知类型： `套餐内流量`, `CMNET`, `免费流量` |
| `data_log_fee` | stirng | 0.000 | 通信费(元) |

### `data_access` <span id="data_access">流量使用记录（目前只有联通有）</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `data_access_type` | stirng | SSL安全类业务/上网（Web方式get)/TCP业务 | 流量类型, SSL安全类业务/上网（Web方式get)/TCP业务 |
| `data_access_domain` | stirng | 域名、IP | 访问网址 |
| `data_access_name` | stirng | 访问网址对应名称 | 网址名称 |

### `phone_bill` <span id="phone_bill">月度账单</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `bill_month` | string | 201612 | 账单月份 |
| `bill_amount` | string | 10.00 | 账单总额 |
| `bill_package` | string | 10.00 | 套餐及固定费 |
| `bill_ext_calls` | string | 10.00 | 套餐外语音通信费 |
| `bill_ext_data` | string | 10.00 | 套餐外上网费 |
| `bill_ext_sms` | string | 10.00 | 套餐外短信费 |
| `bill_zengzhifei` | string | 10.00 | 增值业务费 |
| `bill_daishoufei` | string | 10.00 | 代收业务费 |
| `bill_qita` | string | 10.00 | 其他费用 |

### `flow` <span id="flow">授权流程信息</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `flow_type` | string | 10086 | 代表号码所属运营商与后续验证方式 |
| `need_full_name` | integer | 0 | 登录页面是否需用户姓名 |
| `need_id_card` | integer | 0 | 登录页面是否需用户身分证号 |
| `need_pin_pwd` | integer | 1 | 登录页面是否需要输入服务密码 |
| `need_sms_verify` | integer | 1 | 登录页面是否需要短信验证 |
| `need_captcha_verify` | integer | 1 | 登录页面是否需要图型验证 |
| `register_link` | string | https://login.10086.cn/html/register/register.html | 免费注册网址 |
| `pwd_reset_link` | string | https://bj.ac.10086.cn/ac/html/resetpassword.html | 密码忘记重新注册网址 |
| `telecom` | string | 中国移动 | 號碼所屬运营商 |
| `province` | string | 天津 | 号码所属省份 |
| `city` | string | 天津 | 号码所属城市 |

### `user_info` <span id="user_info">用户信息</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `user_name` | string | 王小二 | 用户姓名 |
| `user_idcard` | string | 411422198000071510 | 用户身份证号码 |
| `user_province` | string | 河北 | 省 |
| `user_city` | string | 沧州 | 市 |
| `user_address` | string | 开发区新华北街9号院9号楼3单元401号 | 地址 |

### `emergency_contact` <span id="emergency_contact">紧急联系人数据结构</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `contact_priority` | string | 1 | 紧急联系人顺序优先级 |
| `contact_tel` | string | 13800138000 | 紧急联系人号码 |
| `contact_name` | string | 张三 | 紧急联系人姓名 |
| `contact_relationship` | string | 朋友 | 紧急联系人关系 |
| `contact_tags_financial` | string | 理财 | 紧急联系人号码金融标签 |
| `contact_tags_label` | string | `保险` | 紧急联系人号码标记 |
| `contact_tags_label_times` | integer | `36` | 紧急联系人号码标记次数 |
| `contact_tags_yellow_page` | string | 北京三牛科技有限公司 | 紧急联系人黄页名称 |

### mongodb data:

```json
{
    "_id" : "58af8f3e322fa972029cb344",
    "status" : 3003,
}
```
