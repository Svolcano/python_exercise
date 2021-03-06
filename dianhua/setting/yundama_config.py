# -*- coding: utf-8 -*-

# APIURL
APIURL = 'http://api.yundama.com/api.php'
# 用户名
USERNAME = 'dianhua2017'
# 密码
PASSWORD = 'jazx9012'
# 软件ＩＤ，开发者分成必要参数。登录开发者后台【我的软件】获得！
APPID = 3653
# 软件密钥，开发者分成必要参数。登录开发者后台【我的软件】获得！
APPKEY = '431bc0e9b06e4c26289cb70d076c0924'
# # 图片文件
# FILENAME = 'getimage.jpg'
# 超时时间，秒
TIMEOUT = 35

# 云打码返回错误码
YUNDAMA_CODE = {
"-1001": "密码错误(检查账号密码是否输入正确，如果账号被盗请联系客服处理)",
"-1002": "软件ID/密钥有误(开发者后台修改了软件密钥，或者没有调用YDM_SetAppInfo)",
"-1003": "用户被封(用户违规操作，需联系客服解封)",
"-1004": "IP被封(该IP违规操作，需联系客服解封)",
"-1005": "软件被封(软件恶意报错，需联系客服解封)",
"-1006": "登录IP与绑定的区域不匹配(用户后台指定了登录区域，需在绑定区域IP登录云打码)",
"-1007": "账号余额为零(账号没有余额，请在【用户后台充值】)",
"-2001": "验证码类型(codetype)有误(请在此查看可用的【验证码类型】)",
"-2002": "验证码图片太大(请上传不大于2M的验证码图片)",
"-2003": "验证码图片损坏(请检查您上传的文件是不是图片类型 jpg/png/bmp/gif)",
"-2004": "上传验证码图片失败(一般为网络问题)",
"-3001": "验证码ID不存在(验证码ID具有时效性，YDM_GetResult 需尽快调用)",
"-3002": "验证码正在识别(YDM_GetResult 需放在循环里调用，直到超时)",
"-3003": "验证码识别超时(注意 YDM_SetTimeOut 参数单位是秒，超时码不会扣费)",
"-3004": "验证码看不清(打码工反馈看不清，一般不用处理)",
"-3005": "验证码报错失败(重复报错或者恶意报错可导致此错误)",
"-4001": "充值卡号不正确或已使用(开发者可先在后台查询此卡号的使用情况)",
"-5001": "注册用户失败(用户名，密码，邮箱为必填项)",
}
