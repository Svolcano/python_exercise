# CRS服务层爬虫接口

## 服務介紹
* 服务层与业务层互相沟通接口(flow_type, login, verify/sms, verify/captcha, verify)
* 流程：
    * `GET` flow_type : 任何爬取一开始的接口，用于取得登入介面配置, SID, 与号码詳細资讯
    * `GET` verify/sms     : 取得動態驗證 (optional)
    * `GET` verify/captcha : 取得圖形驗證 (optional)
    * `POST` login : 登入
    * `POST` verify : 输入验证码
    * `GET` abort (目前只有移動會需要再多一次動態驗證碼動作)

* 动作介绍：每一个接口，都会返回next_action，以供判断接下来需要呼叫的接口動作

| next_action | 參數描述 |
| ---- | --- |
| `Login` | 登入 --> POST login |
| `GetSMS` | 取得動態驗證 --> GET verify/sms |
| `GetCaptcha` | 取得圖形驗證 --> GET verify/captcha |
| `GetSMSCaptcha` | 同时取得两种验证（发短信, 取得图片）--> GET verify/sms_captcha |
| `Verify` | 验证验证码 --> POST verify |
| `Finish` | 动作结束，爬虫已开始爬取数据 |
| `Reset` | 爬虫异常，建议需重置所有动作 --> GET flow_type |
| `Unsupported` | 没有支持的爬虫(发生于GET flow_type 返回时) --> 建议使用第三方接口 |

## 接口介紹
### `GET` /crawl/calls/flow_type

* Input :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `tel` | string | 是 | 用戶电话号码 |
| `sid` | string | 否 | 用户有效SID |

* Output :

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `status` | string | 状态码 0 表示成功, 其他表是各种錯誤 |
| `message` | string | 状态返回细节讯息 |
| `next_action` | string | 下一个所需动作(参考上面动作说明) |
| `result` | json | 返回以下數據结果 |

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `sid` | string | session id，业务层与服务层间讯息通讯使用 |
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

* Sample :

```json
    {
        "status": 0,                      
        "message": "success",           
        "next_action": "Login",
        "result" :
        {
            "sid": "SID*10000000000",    
            "flow_type": "10010",         
            "need_full_name" : 0,           
            "need_id_card" : 0,           
            "need_pin_pwd" : 1,           
            "need_sms_verify": 1,
            "need_captcha_verify": 0,
            "register_link"    : "https://uac.10010.com/portal/register.html",
            "pwd_reset_link"   : "https://uac.10010.com/cust/resetpwd/inputName"
            "telecom" : "中国联通",
            "province" : "山东",
            "city" : "潍坊"
        }
    }
```


## GET /crawl/calls/verify/sms
* Input :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `sid` | string | 是 | 由/crwal/call/flow_type所取得本次爬取的session id |

* Output :

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `status` | string | 状态码 0 表示成功, 其他表是各种錯誤 |
| `message` | string | 状态返回细节讯息 |
| `next_action` | string | 下一個所需動作 |

* Sample :

```json
    {
        "status" : 0,
        "message": "success",
        "next_action": "Verify"
    }
```

## GET /crawl/calls/verify/captcha
* Input :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `sid` | string | 是 | 由/crwal/call/flow_type所取得本次爬取的session id |

* Output :

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `status` | string | 状态码 0 表示成功, 其他表是各种錯誤 |
| `message` | string | 状态返回细节讯息 |
| `next_action` | string | 下一個所需動作 |
| `content` | string | base64图档 |

* Sample :

```json
    {
        "status" : 0,
        "message": "success",
        "next_action" : "Verify",
        "content": "iVBORw0KGgoAAAANSUhEUgAAASwAAAA5CAIAAAADc....AAAAASUVORK5CYII="
    }
```

## GET /crawl/calls/verify/sms_captcha
* Input :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `sid` | string | 是 | 由/crwal/call/flow_type所取得本次爬取的session id |
| `verify_type` | string | 否 | 正常为空, 刷新短信验证码--'sms', 刷新图形验证码--'captcha' |

* Output :

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `status` | string | 状态码 0 表示成功, 其他表是各种錯誤 |
| `message` | string | 状态返回细节讯息 |
| `next_action` | string | 下一個所需動作 |
| `content` | string | base64图档 |

* Sample :

```json
    {
        "status" : 0,
        "message": "success",
        "next_action" : "GetCaptcha",
        "content": "iVBORw0KGgoAAAANSUhEUgAAASwAAAA5CAIAAAADc....AAAAASUVORK5CYII="

    }
```

## POST /crawl/calls/login
* Input :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `sid` | string | 是 | 由/crwal/call/flow_type所取得本次爬取的session id |
| `full_name` | string | 否 | 用户姓名 |
| `id_card` | string | 否 | 用户身分证号 |
| `pin_pwd` | string | 否 | 用户服务密码 |
| `sms_code` | string | 否 | 用戶填入的SMS验证码 |
| `captcha_code` | string | 否 | 用戶填入的Captcha验证码 |

* Output :

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `status` | string | 状态码 0 表示成功, 其他表是各种錯誤 |
| `message` | string | 状态返回细节讯息 |
| `next_action` | stirng | 所需的下一個動作 |

* Sample :

```json
    {
        "status" : 0,
        "message" : "success",
        "next_action" : "GetSMS"
    }
```

## POST /crawl/calls/verify
* Input :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `sid` | string | 是 | 由/crwal/call/flow_type所取得本次爬取的session id |
| `sms_code` | string | 否 | 用戶填入的SMS驗證碼 |
| `captcha_code` | string | 否 | 用戶填入的Captcha驗證碼 |

* Output :

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `status` | string | 状态码 0 表示成功, 其他表是各种錯誤 |
| `message` | string | 状态返回细节讯息 |
| `next_action` | string | 下一個所需動作 |

* Sample :

```json
    {
        "status" : 0,
        "next_action" : "Login",
        "message" : "success"
    }
```

## GET /crawl/calls/abort
* Input :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `sid` | string | 是 | 由/crwal/call/flow_type所取得本次爬取的session id |

* Output :

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `status` | string | 状态码 0 表示成功, 其他表是各种錯誤 |
| `message` | string | 状态返回细节讯息 |
| `next_action` | string | 下一個所需動作 |

* Sample :

```json
    {
        "status" : 0,
        "message": "success",
        "next_action" : "Reset",
    }
```


## POST /crawl/calls/fusion_data
* Input :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `sid` | string | 是 | 由/crwal/call/flow_type所取得本次爬取的session id |
| `tel` | string | 是 | 用戶填入的手机号|
| `pad_code` | string | 是 | 融合的数据来自于哪个平台 |
| `call_log` | string | 是 | 详单数据 |
| `missing_month_list` | string | 是 | 完全缺失列表 |
| `possibly_missing_list` | string | 是 | 可能缺失列表 |
| `part_missing_list` | string | 是 | 部分缺失列表 |
| `bill_missing_list` | string | 是 | 账单缺失列表 |
| `phone_bill` | string | 是 | 账单明细 |

* Output :

| 名称 | 类型 | 必填 | 參數描述 |
| ---- | --- | --- | --- |
| `sid` | string | 是 | 由/crwal/call/flow_type所取得本次爬取的session id |
| `tel` | string | 是 | 用戶填入的手机号|
| `pad_code` | string | 是 | 融合的数据来自于哪个平台 |
| `final_call_logs` | string | 是 | 详单数据 |
| `missing_log_list` | string | 是 | 完全缺失列表 |
| `possibly_missing_list` | string | 是 | 可能缺失列表 |
| `part_missing_list` | string | 是 | 部分缺失列表 |
| `cache_hit_month_list` | string | 是 | 缓存命中列表 |
| `fusion_cost_time` | string | 是 | 数据融合耗时 |
| `bill_missing_list` | string | 是 | 账单缺失列表 |
| `phone_bill` | string | 是 | 账单明细 |
| `bill_cache_hit_month_list` | string | 是 | 账单缓存命中列表 |
| `bill_fusion_cost_time` | string | 是 | 账单融合耗时 |
| `status` | string | 是 | 状态码 0 表示成功, 其他表是各种錯誤 |

* Sample :

```json
    {
        "status" : 0,
        ...
    }


## 錯誤碼定義
| status code | message |
| --- | --- |
| `0` | success |
| `1` | under crawling |
| `2` | result already exists (will return the previous results' sid) |
| `3100` | no supported crawler |
| `4000` | login fail |
| `4001` | phone number is not valid |
| `4002` | pin pwd is not valid |
| `4003` | verify code is not valid |
| `4004` | user name is not valid |
| `4005` | user identification is not valid |
| `4010` | over max sms verification sending |
| `4017` | original website is busy. Please retry later |
| `4116` | send sms fail |
| `4999` | send sms too quick. Please send sms 30 seconds later |
| `5000` | invalid sid |
| `5001` | outdated sid |
| `5002` | duplicate sid |
| `5017` | 查询次数过多,请稍后重试 |
| `9999` | Unknown error |
| others | please ignore it .... |

## 數據庫collection定義：

* 账单 `phone_bill`

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `tel` | string | 电话号码 |
| `sid` | string | 会话id |
| `update_time` | string | 更新时间 |
| `phone_bill[][bill_month]` | string | 账单月份 |
| `phone_bill[][bill_amount]` | string | 账单总额 |

* call_log

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `call_tel` | string | 电话号码 |
| `update_time` | string | 更新时间戳 |
| `call_cost` | string | 爬取费用 |
| `call_time` | string | 通话起始时间 |
| `call_method` | string | 呼叫类型（主叫, 被叫） |
| `call_type` | string | 通话类型（本地, 长途）  |
| `call_from` | string | 本机通话地 |
| `call_to` | string | 对方归属地 |
| `call_duration` | string | 通话时长 |

* user_info

| 名称 | 类型 | 描述 |
| ---- | --- | --- |
| `tel` | stirng | 用户电话号码  |
| `update_time` | stirng | 更新时间戳 |
| `full_name` | stirng | 机主用户姓名  |
| `id_card` | stirng | 機主用戶身分證號(部分)  |
| `is_realname_register` | string | 是否实名制 |
| `open_date` | stirng | 入网時間 |

## 數據測試環境：

* 测试服务器：http://crawl.crs.dianhua.cn:8080
* 测试数据库：172.18.19.155:27017
* 数据库名称：crs

## 使用上简单流程范例(python code, 其中接口已经封装成function, 关注逻辑即可)

```python
def crawl(tel, pin_pwd):
    next_action = ''
    try:
        sid = ''
        next_action = ''
        need_sms_verify = ''
        need_captcha_verify = ''
        sms_code = ''
        captcha_code = ''
        ret = {}
        while(next_action != 'Finish'):
            if next_action == '':
                ret = flow_type(tel)
                if ret['status']:
                    print 'Error'
                    return ret
                sid = ret['result']['sid']
                need_sms_verify = ret['result']['need_sms_verify']
                need_captcha_verify = ret['result']['need_captcha_verify']
            elif next_action == 'Login':
                if need_sms_verify == 1 or need_captcha_verify == 1:
                    sms_code = raw_input('Input verify code (sms): ')
                    captcha_code = raw_input('Input verify code (captcha): ')
                else:
                    sms_code = ''
                    captcha_code = ''
                ret = login(sid, tel, pin_pwd, sms_code, captcha_code)
                if ret['status']:
                    print 'ERROR : {}'.format(ret['status'])
            elif next_action == 'GetSMS':
                ret = get_sms(sid)
                if ret['status']:
                    print 'ERROR : {}'.format(ret['status'])
            elif next_action == 'GetCaptcha':
                ret = get_captcah(sid)
                if ret['status']:
                    print 'ERROR : {}'.format(ret['status'])
            elif next_action == 'Verify':
                sms_code = raw_input('Input verify code (sms): ')
                captcha_code = raw_input('Input verify code (captcha): ')
                ret = verify(sid, sms_code, captcha_code)
                if ret['status']:
                    print 'ERROR : {}'.format(ret['status'])
            elif next_action == 'Reset':
                print 'Crawler status = {}, msg = {}'.format(
                        ret['status'],
                        ret['message'])
                break
            elif next_action == 'Unsupported':
                print 'No crawler supported!!'
                break
            else:
                print next_action
                assert False, 'Abnormal case !!!'
            pp(ret)
            next_action = ret['next_action']
            raw_input('next_action = {}'.format(next_action))
    except KeyboardInterrupt:
        ret = abort(sid)
        if ret['status']:
            print 'ERROR : {}'.format(ret['status'])
        next_action = ret['next_action']
    except:
        pp(ret)
        print traceback.format_exc()
        return 'Fatal Error.......................................'

    return next_action
```
