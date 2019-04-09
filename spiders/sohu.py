# -*- coding:utf-8 -*-
import time
import requests
import logging
import hashlib
import re
import os
import datetime
import json

from lib.mp.base import Base
from lib.yundama import verify_captcha
from lib.tools.custom_exception import CustomException


class SoHu(Base):

    channelList = {
        '军事': [10, 1472], '文化': [12, 1187], '历史': [13, 1249], '财经': [15, 900],
        '体育': [17, 849], '汽车': [18, 903], '娱乐': [19, 1411], '时尚': [23, 1121],
        '健康': [24, 896], '教育': [25, 895], '母婴': [26, 898], '星座': [27, 904],
        '美食': [28, 1457], '旅游': [29, 1458], '科技': [30, 902], '公益': [38, 906],
        '警法': [40, 1274], '其他': [34, 901], '动漫': [41, 1434], '游戏': [42, 1329],
        '社会': [43, 1454], '宠物': [44, 1426], '搞笑': [45, 1427]
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    mp_id = 6
    zh_name = '搜狐号'

    @staticmethod
    def login(user, pswd, **kw):
        SoHu.logger.info("")
        session = requests.session()
        try:
            millis = int(round(time.time() * 1000))
            hl = hashlib.md5()
            hl.update(pswd.encode("utf-8"))
            pswd = hl.hexdigest()
            url = "https://passport.sohu.com/user/tologin"
            session.get(url)
            baseurl = "https://passport.sohu.com/apiv2/login"

            def get_cpptcha(user):
                co_url = "https://passport.sohu.com/apiv2/picture_captcha?userid=" + user
                response = session.get(co_url, verify=False)
                with open('captcah1.jpeg', 'wb') as f:
                    f.write(response.content)

            get_cpptcha(user)
            cid, result = verify_captcha('captcah1.jpeg', 1005)
            if result == "看不清":
                get_cpptcha(user)
                cid, result = verify_captcha('captcah1.jpeg', 1005)
            data = {
                "domain": "sohu.com",
                "callback": "passport200029113275484305756_cb" + str(millis),
                "appid": "9998",
                "userid": user,
                "password": pswd,
                "persistentcookie": "0",
                "captcha": result
            }
            if os.path.exists("captcah1.jpeg"):
                os.remove("captcah1.jpeg")
            resp = session.post(
                baseurl, data=data, verify=False,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"})
            pat = re.compile(r'"msg":"(.*?)"')
            msg = pat.findall(resp.text)
            if not msg[0]:
                raise CustomException('检查账号密码')
            session.get("https://passport.sohu.com/mypassport/index", verify=False)
            cookies = session.cookies.get_dict()
            cookies["date"] = str(int(time.time()))
            if 'lastdomain' in cookies:
                times = str(int(time.time() * 1000))
                res = session.get(
                    "https://mp.sohu.com/mp-accounts/accounts/list?_=%s" % times, verify=False
                ).json()
                nick_name = res['list'][0]['accountslist'][0]['nickName']
                return cookies, nick_name
        except Exception as e:
            raise CustomException(e)
        finally:
            session.close()

    def publish(self, title, content, category, flag=1):
        """
          :param title:
          :param content:
          :param category:
          :return: status, article_id, cause
        """
        self.logger.info('')
        result = re.compile(r'<img src="(.*?)".*?>', re.S).findall(content)
        cover = ''
        if result:
            cover = result[0]
        url = "https://mp.sohu.com/v3/news/publish"
        data = {
            "title": title,
            "brief": "",
            "content": content,
            "channelId": self.channelList[category][0],
            "categoryId": self.channelList[category][1],
            "id": 0,
            "userColumnId": 0,
            "isOriginal": 0,
            "cover": cover
        }
        fw_response = self.session.post(
            url=url, verify=False, data=data, headers=self.headers).text
        self.logger.info(fw_response)
        try:
            int(fw_response)
            status = 2
            cause = ''
            return status, cause
        except Exception as e:
            cause = e
            if '{"msg":"'in fw_response:
                ss = json.loads(fw_response)
                cause = ss['msg']
                raise CustomException(cause)

    def read_count(self,
                   start_date=datetime.datetime.now() - datetime.timedelta(days=int(7)),
                   end_date=datetime.datetime.now() - datetime.timedelta(days=int(1))):
        self.logger.info("")
        times = str(int(time.time() * 1000))
        res = self.session.get(
            "https://mp.sohu.com/mp-accounts/accounts/list?_=%s" % times, verify=False, timeout=30
        ).json()
        user_name = res['list'][0]['accountslist'][0]['nickName']
        accountId = res['list'][0]['accountslist'][0]['id']
        read_url = "https://mp.sohu.com/v3/users/stat/overall?type=1&startDate={}&endDate={}&accountId={}&_={}"\
            .format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), accountId, times)
        resp = self.session.get(read_url, timeout=30, verify=False)
        self.logger.info(resp.text)
        resp = json.loads(resp.text)
        if resp['status'] != 'ok':
            raise CustomException("账号异常")
        read_list = []
        for data in resp['result']['list']:
            readcount = {
                "day_time": data["date"],
                "recomment_num": data["diff"],
                "user_name": user_name,
                "read_num": data["diff"]}
            read_list.append(readcount)
        return read_list

    def fetch_article_status(self, title):
        self.logger.info("")
        times = str(int(time.time() * 1000))
        res = self.session.get(
            "https://mp.sohu.com/mp-accounts/accounts/list?_=%s" % times, verify=False
        ).json()
        accountId = res['list'][0]['accountslist'][0]['id']
        resp = self.session.get(
            'https://mp.sohu.com/v3/users/news/?newsType=1&statusType=1&pno=1&psize=10&_={}&accountId={}'.
                format(times, accountId), verify=False
        ).json()['news']
        res = [2, '没查询到该文章', '']
        for art in resp:
            if title != art['mobileTitle']:
                continue
            elif art['status'] == 4:
                art_id = art['id']
                uid = art['userId']
                url = 'https://www.sohu.com/a/{}_{}'.format(art_id, uid)
                res = 4, '', url
            elif art['status'] == 3:
                res = 5, self.session.get('https://mp.sohu.com/v3/news/rejectReason?newsId={}&_=1532682411408'.format(art['id']),
                verify=False).text, ''
        return res

    def upload_image(self, image_name, image_data):
        self.logger.info(image_name)
        files = {
            'file': (image_name, image_data, 'image/jpeg')
        }
        resp = self.session.post(
            'https://mp.sohu.com/commons/upload/file',
            files=files, verify=False
        )
        if resp.status_code == 200:
            resp_json = resp.json()
            img_url = resp_json.get('url')
            if not img_url:
                raise CustomException("%s" % resp_json['msg'])
            url = 'https:' + img_url
            return url

    def check_user_cookies(self):
        self.logger.info("")
        try:
            times = str(int(time.time() * 1000))
            res = self.session.get(
                "https://mp.sohu.com/mp-accounts/accounts/list?_=%s" % times, verify=False).json()
            return res['totalAccount'] == 1
        except Exception as e:
            self.logger.error(e)
            return False

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        times = str(int(time.time() * 1000))
        res = self.session.get(
            "https://mp.sohu.com/mp-accounts/accounts/list?_=%s" % times, verify=False
        ).json()
        accountId = res['list'][0]['accountslist'][0]['id']
        resp = self.session.get(
            'https://mp.sohu.com/v3/users/news/?newsType=1&statusType=1&pno=1&psize=10&_={}&accountId={}'.
                format(times, accountId), verify=False
        ).json()['news']
        for art in resp:
            if title != art['mobileTitle']:
                continue
            else:
                times = int(art['auditTime'] / 1000)
                time_local = time.localtime(times)
                dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                data = dict(
                    read_num=art['pv'],
                    recomment_num=-1,
                    publish_time=dt,
                    comment_num=-1,
                    share_num=-1,
                    like_num=-1,
                    collect_num=-1,
                    follow_num=-1
                )
                return data
        return ''


if __name__ == '__main__':
    from control.db.api.account_api import DBAccountApi
    from lib.tools.log_mgr import Flogger
    Flogger()
    db_account_api = DBAccountApi()
    account = db_account_api.query(uid=1, mp=7, account='15711082771')
    if account:
        account = account[0]
    bj = SoHu(account)