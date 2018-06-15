# -*- coding: utf-8 -*-
"""
Created on Thu May 24 10:01:14 2018

@author: huang
"""

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import smtplib
import time
import os

from_addr = 'zhijie.huang@yulore.com'
passwd = 'hzj4201'
to_addr = {'黄志杰':'zhijie.huang@yulore.com','徐志伟':'zhiwei.xu@yulore.com','薛胜光':'shengguang.xue@yulore.com','刘勇':'yong.liu@yulore.com'}
#to_addr = {'黄志杰':'zhijie.huang@yulore.com'}
smtp_addr = 'smtp.yulore.com'
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

end_date=time.strftime("%Y%m%d", time.localtime())
timeArray = time.strptime(end_date, "%Y%m%d")
enddate = time.mktime(timeArray)
begin_date=time.strftime("%Y%m%d", time.localtime(enddate-86400))

#cmd='ls'
cmd='python /data/script_exec/sid_info_anly/sid_info_anly.py -b{0} -e{1}'.format(begin_date,end_date)
print cmd
p=os.popen(cmd)
x=p.read()
print x
p.close()

s = smtplib.SMTP() #定义一个s对象
s.connect(smtp_addr,25)
s.set_debuglevel(1) #打印debug日志
s.login(from_addr,passwd) #auth发件人信息
for name,addr in to_addr.items():
    msg = MIMEMultipart()
    #msg = MIMEText(x, 'plain', 'utf-8')
    # 构造附件1，传送当前目录下的 test.txt 文件
    att1 = MIMEText(open('sid_info_anly.html', 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att1["Content-Disposition"] = 'attachment; filename="sid_info_anly.html"'
    msg.attach(att1)
    msg['From'] = _format_addr('黄志杰(系统自动发送) <%s>' % from_addr)
    msg['To'] = _format_addr('%s <%s>' %(name,addr))
    msg['Subject'] = Header('sid_info日终统计详情以及可疑手机号信息', 'utf-8').encode()
    s.sendmail(from_addr,addr,msg.as_string())
s.quit()
