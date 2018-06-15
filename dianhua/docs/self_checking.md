## 爬虫自检项目

### import模块检查
- [ ] 是否有多余

### 日志
- [ ] 每一次请求是否有记日志
- [ ] 意外情况比如 try 时是否有记日志

### 登录逻辑检查

- [ ] 手机号 `tel`
> 运营商返回手机号错误的情况是否有处理

- [ ] 服务密码 `pin_pwd`
> 运营商返回服务密码的情况是否有处理
> 多次输入错误的服务密码时会发生什么

- [ ] 图形验证码 `captcha_code` 短信验证码 `sms_code`
> 验证码错误的情况是否有处理
> 重新获取验证码的是否有做
> 多次输入错误的验证码会发生什么

- [ ] 登录的异常处理
> 登录错误、失败时是否有处理


### 个人信息、月度账单、语音通话详单

- [ ] 个人信息、月度账单、语音通话详单字段的数据格式是否按文档要求进行了加工？


### 语音通话详单的错误处理

- [ ] 检查**分页**是否有处理

- [ ] `try...except` 当发生异常时应报 `9` 级别错误

> 所需位置：requests请求、json反序列化、xpath解析..., 可参照如下：

```
import traceback
try:
  json.loads(json_string)
  dom.xpath('//*[@id="dataset"]')
except:
  error = traceback.format_exc()
  return 'unknown_error', 9, error, ''
```


### 请求相关

- [ ] `headers 必加参数`

```
'User-Agent': UserAgent().chrome
'Accept': 'application/....''
'Referer': 'http://...'
如果是ajax请求：'X-Requested-With': 'XMLHttpRequest'
```

### 检查return 是否按接口要求返回了正确的

- [ ] 所有status_key、level 是否与message 相匹配
- [ ] 返回参数个数、格式是否正确
