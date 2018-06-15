[TOC]

# 运营商报告

## 数据结构

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `sid` | string | SID29de7514563f4570a818b0ddea549e50 | 会话id |
| `tel` | string | SID29de7514563f4570a818b0ddea549e50 | 手机号 |
| `overview` | [overview](#overview) | 号码使用总览 |
| `calls_sa_by_mergency_contact` | [calls_sa_by_mergency_contact](#calls_sa_by_mergency_contact) | 联系情况（6个月内） `紧急联系人` |
| `calls_sa_by_tags_financial` | [calls_sa_by_tags_financial](#calls_sa_by_tags_financial) | 联系情况（6个月内） `金融标签`  |
| `calls_sa_by_tags_extra` | [calls_sa_by_tags_extra](#calls_sa_by_tags_extra) | 联系情况（6个月内） `额外定义的联系号码`  |
| `calls_sa_by_times` | [calls_sa_by_times](#calls_sa_by_times) | 高频联系号码（TOP 10) |
| `calls_sa_by_length` | [calls_sa_by_length](#calls_sa_by_length) | 长时间联系号码（TOP 10) |
| `calls_sa_by_region` | [calls_sa_by_region](#calls_sa_by_region) | 联系人所在地分析 |
| `calls_sa_monthly_usage` | [calls_sa_monthly_usage](#calls_sa_monthly_usage) | 运营商月使用（近6个月） |
| `primary_tels_info` | [primary_tels_info](#primary_tels_info) | 号码查询信息 |
| `call_log_group_by_tel` | [call_log_group_by_tel](#call_log_group_by_tel) | 附录（通话号码列表） |
| `created_at` | timestamp | 1486976786 | 创建时间 |
| `updated_at` | timestamp | 1486976786 | 更新时间 |

## <span id="overview">数据结构</span> `overview`

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `area_active_most` | string | 北京 | 活跃地区（call_log通话地点最多的区域） |
| `area_contacted_most` | string | 上海 | 联系人所在地（call_log通话联系最多的区域） |
| `open_date` | string | 2013/10/2 | 入网时间（大于15天按一个月算，小于15天不计入） |
| `blank_times` | string | 连续3天以上无通话记录**4**次 | 手机静默情况（连续3天以上无通话记录次数） |
| `night_calls` | string | 夜间通话占全部通话**32%** | 夜间活动情况（夜间通话占比）（夜间为22:00至凌晨6:00） |

## `calls_sa_by_mergency_contact` <span id="calls_sa_by_tags_financial">联系情况（6个月内） `紧急联系人` (统计机主与金融标签号码的通讯情况) </span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `contact_name` | string | `[联系人1]` | 紧急联系人 |
| `call_times` | string | 12 | 联系次数 |
| `call_length` | string | 21 | 通话总时长 |
| `contact_first_time` | string | 2016-06-11 | 第一次联系时间 |
| `contact_last_time` | string | 2016-11-02 | 最后一次联系时间 |

## `calls_sa_by_tags_financial` <span id="calls_sa_by_tags_financial">联系情况（6个月内） `金融标签` (统计机主与金融标签号码的通讯情况)</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `tags_name` | string | `互联网金融` | 金融标签 |
| `call_times` | string | 12 | 联系次数 |
| `call_length` | string | 21 | 通话总时长 |
| `contact_first_time` | string | 2016-06-11 | 第一次联系时间 |
| `contact_last_time` | string | 2016-11-02 | 最后一次联系时间 |

## `calls_sa_by_extra_tel` <span id="calls_sa_by_tags_financial">联系情况（6个月内） `额外定义的联系号码` (统计机主与金融标签号码的通讯情况)</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `call_tel` | string | `110` | 额外定义的联系号码 |
| `call_times` | string | 12 | 联系次数 |
| `call_length` | string | 21 | 通话总时长 |
| `contact_first_time` | string | 2016-06-11 | 第一次联系时间 |
| `contact_last_time` | string | 2016-11-02 | 最后一次联系时间 |

## `calls_sa_by_times` <span id="calls_sa_by_times">数据结构 (统计与机主联系次数最多的10个号码)</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `call_tel` | string | `[联系人2]` 或者 `18612012053` | `紧急联系人` 或者 `电话号码` |
| `tags_yellow_page` | string | 快递送餐 | `黄页` |
| `tags_label` | string | 百度外卖送餐员 | `标记` |
| `tel_to` | string | 北京 | 号码归属地 |
| `call_times` | string | 12 | 联系次数 |
| `call_length` | string | 21 | 通话总时长 |
| `call_out_times` | string | 3 | 主叫次数 |
| `call_in_times` | string | 6 | 被叫次数 |

## `calls_sa_by_length` <span id="calls_sa_by_length">数据结构 (与机主累积通话时间最长的10个号码)</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `call_tel` | string | `[联系人2]` 或者 `18612012053` | `紧急联系人` 或者 `电话号码` |
| `tags_yellow_page` | string | 快递送餐 | `黄页` |
| `tags_label` | string | 百度外卖送餐员 | `标记` |
| `call_in_location` | string | 北京 | 号码归属地 |
| `call_times` | string | 12 | 联系次数 |
| `call_length` | string | 21 | 通话总时长 |
| `call_out_times` | string | 3 | 主叫次数 |
| `call_in_times` | string | 6 | 被叫次数 |

## `calls_sa_by_region` <span id="calls_sa_by_region">数据结构 (联系人号码归属地所有地区)</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `region` | string | 北京 | 区域 |
| `total_call` | integer | 79 | 号码数量 |
| `call_in_times` | string | 594/73% | 呼入次数 |
| `call_out_times` | string | 221/27% | 呼出次数 |
| `call_in_length` | string | 224分/39% | 呼入时长 |
| `call_out_length` | string | 382分/61% | 呼出时长 |
| `call_in_length_avg` | string | 0.37 | 平均呼入时长 |
| `call_out_length_avg` | string | 1.72 | 平均呼出时长 |

## `calls_sa_monthly_usage` <span id="calls_sa_monthly_usage">数据结构 (运营商月使用（近6个月）)</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `month` | string | 10-2016 | 月份，格式 `mm-yyyy` |
| `call_out_times` | string | 98 | 主叫次数 |
| `call_out_length` | string | 101 | 主叫时长 |
| `call_in_times` | string | 9 | 被叫次数 |
| `call_in_length` | string | 11 | 被叫时长 |

## `primary_tels_info` <span id="primary_tels_info">数据结构 (号码查询信息)</span>

[call_log_group_by_tel](sid_info.md)

## `call_log_group_by_tel` <span id="call_log_group_by_tel">附录 (通话号码列表)</span>

| 名称 | 类型 | 示例 | 描述 |
| ---- | --- | --- | --- |
| `call_tel` | string | 13800138000 | 通话号码 |
| `call_to` | string | 北京 | 号码归属地 |
| `call_times` | string | 12 | 联系次数 |
| `call_out_times` | string | 98 | 主叫次数 |
| `call_out_length` | string | 101 | 主叫时长 |
| `call_in_times` | string | 9 | 被叫次数 |
| `call_in_length` | string | 11 | 被叫时长 |
| `tags_financial` | string | 理财/贷款/互联网金融 | 金融标签 |
| `tags_label` | string | `保险` | 号码标记 |
| `tags_label_times` | string | `36` | 号码标记次数 |
| `tags_yellow_page` | string | 北京三牛科技有限公司 | 黄页名称 |


## 金融标签和标记情况反查结果示例：

```json
{
  "status": "0",
  "country": 86,
  "flag": {
    "type": "骚扰电话",
    "num": 80,
    "fid": 1
  },
  "itag_ids": [
    5
  ],
  "telnum": "02552493932"
}

//

{
  "status": "0",
  "id": "2890bc3597ed3adb40bcf1dd31c33324",
  "name": "安个家",
  "auth": 1,
  "teldesc": "电话",
  "catnames": [
    "其他企业",
    "其他企业"
  ],
  "slogan": "数据由电话邦审核认证",
  "slogan_img": "http://s.dianhua.cn/cmenu/icons/common/v/1/2.png",
  "act": {
    "type": "yellowpage/detail",
    "data": "2890bc3597ed3adb40bcf1dd31c33324"
  },
  "telnum": "021-61918566"
}
```

## 金融标签对应表：

```
1=银行
2=保险
3=证券
4=互联网金融
5=贷款
6=理财
7=赌博
8=典当
9=代办中介
10=法院检察院
11=公安局派出所
12=律师
13=催款
14=客服
15=营销合
```

