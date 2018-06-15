# -*- coding:utf-8 -*-

# execute mode(prod/dev/testing)
ENV = 'prod'
# ENV = 'dev'
#ENV = 'testing'

# MRQ Task and Queue configuration
TASK_PATH  = 'worker.tasks.CrawlCallHistory'
QUEUE_NAME = 'q-crawl'
#QUEUE_NAME = 'zhijie-crawl'

# SID setting (sec)
SID_EXPIRE_TIME = 300

STATE_TIME_OUT = 170
CRAWLER_TIME_OUT = 1190
STEP_TIME = 0.5


# three main telecom website(聯通, 電信, 移動) flow
TELECOM_FLOW_INFO = {
    u'联通': {
        'flow_type': '10010',
        'register_link'  : 'https://uac.10010.com/portal/register.html',
        'pwd_reset_link' : 'https://uac.10010.com/cust/resetpwd/inputName'
    },
    u'电信': {
        'flow_type': '10000',
        'register_link'  : 'http://login.189.cn/reg',
        'pwd_reset_link' : 'http://login.189.cn/login'
    },
    u'移动': {
        'flow_type': '10086',
        'register_link'  : 'https://login.10086.cn/html/register/register.html',
        'pwd_reset_link' : 'https://bj.ac.10086.cn/ac/html/resetpassword.html'
    }
}
