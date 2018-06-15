# -*- coding:utf-8 -*-

"""
@version: v1.0
@author: xuelong.liu
@license: Apache Licence 
@contact: xuelong.liu@yulore.com
@software: PyCharm
@file: base_request_param.py
@time: 12/21/16 6:48 PM
"""


class RequestParam(object):
    """
    请求相关
    """

    # URL
    START_URL = "https://www.hn.10086.cn/service/static/componant/login.html"
    # GET_CAPTCHA_URL = "http://www.hn.10086.cn/service/ics/servlet/ImageServlet"
    GET_CAPTCHA_URL = "https://www.hn.10086.cn/service/ics/login/sendSms"
    # GET_CAPTCHA_URL = "http://www.hn.10086.cn/newservice/ics/servlet/ImageServlet?random=0.14531555527237483"
    LOGIN_URL = "https://www.hn.10086.cn/service/ics/login/SSOLogin"
    # GET_SMS_URL = "http://www.hn.10086.cn/newservice/ics/componant/initSendHattedCode?requestTel=%s&ajaxSubmitType=post&ajax_randomcode=0.5158618472543544"
    GET_SMS_URL_READY = "https://www.hn.10086.cn/service/ics/componant/initTelQCellCore?tel=%s&ajaxSubmitType=post&ajax_randomcode=0.9461358208494027"
    GET_SMS_URL = "https://www.hn.10086.cn/service/ics/componant/initSendHattedCode?requestTel=%s&ajaxSubmitType=post&ajax_randomcode=0.9461358208494027"
    # SMS_URL = "http://www.hn.10086.cn/newservice/ics/componant/initSmsCodeAndServicePwd"
    SMS_URL = "https://www.hn.10086.cn/service/ics/componant/initSmsCodeAndServicePwd?smsCode=%s&servicePwd=NaN&requestTel=%s&ajaxSubmitType=post&ajax_randomcode=0.012645535304207867"
    GET_CAL_LOG = "https://www.hn.10086.cn/service/ics/detailBillQuery/queryDetailBill"
    GET_USER_INFO = "https://www.hn.10086.cn/service/ics/basicInfo/queryUserBasicInfo"
