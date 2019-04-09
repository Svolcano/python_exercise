import requests
import re
import base64
import rsa
import binascii
import logging
import os
import datetime
import time
from lib.mp.base import Base
from lib.yundama import verify_captcha
from urllib import parse
from lib.tools.custom_exception import CustomException
from control.db.redis_mgr import RedisApi

weibolists = [
    '17190015815', '17152140096', '17152140026', '17190082448', '17190193956',
    '17190175480', '17310146526']


class DaFeng(Base):
    rs = RedisApi()
    mp_id = 2
    zh_name = "大风号"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
    categorylist = {
        "百科": "5854cc129cd31025a647acb1", "争鸣": "5854cc129cd31025a647accc", "时政": "5858d867afbea52c129b4773",
        "人文": "5854cc129cd31025a647acc3",
        "财经": "5854cc129cd31025a647acb9", "军事": "5854cc129cd31025a647acaf", "社会": "5854cc129cd31025a647acb4",
        "时尚": "5854cc129cd31025a647acbf",
        "科技": "5854cc129cd31025a647acb2", "体育": "5854cc129cd31025a647acac", "历史": "5854cc129cd31025a647acb0",
        "视频": "5854cc129cd31025a647accd",
        "视觉": "5854cc129cd31025a647acc5", "汽车": "5854cc129cd31025a647acbd", "娱乐": "5854cc129cd31025a647acc2",
        "旅游": "5854cc129cd31025a647acb3",
        "佛教": "5858d89483d5222bee290986", "明星": "5858d88383d5222bee29097d", "房产": "5854cc129cd31025a647acb7",
        "电影": "5854cc129cd31025a647acc6",
        "情感": "5854cc129cd31025a647acc0", "公益": "5854cc129cd31025a647acb5", "母婴": "5854cc129cd31025a647acc1",
        "健康": "5854cc129cd31025a647acbe",
        "美食": "5854cc129cd31025a647acad", "星座": "5854cc129cd31025a647acae", "乐活": "5854cc129cd31025a647acc8",
        "教育": "5854cc129cd31025a647acbc",
        "媒体": "5854cc129cd31025a647acba", "漫画": "5854cc129cd31025a647acbb", "家居": "5854cc129cd31025a647acb8",
        "杂志": "5854cc129cd31025a647acca",
        "地方": "5854cc129cd31025a647accb",
    }

    @staticmethod
    def login(user, pswd, **kw):  # 普通登录
        DaFeng.logger.info(user)
        session = requests.session()
        try:
            if user not in weibolists:
                response = session.get(
                    'https://id.ifeng.com/public/authcode?_=%s' % str(int(time.time() * 1000)))
                with open('captcah.jpeg', 'wb') as f:
                    f.write(response.content)
                cid, result = verify_captcha('captcah.jpeg', 1004)
                if os.path.exists("captcah.jpeg"):
                    os.remove("captcah.jpeg")
                respon = session.post(
                    "https://id.ifeng.com/api/sitelogin",
                    data={
                        "u": user, "k": pswd, "auth": result,
                        "auto": "on", "comfrom": "", "type": "3"
                    },
                    headers={
                        "Host": "id.ifeng.com",
                        "Connection": "keep-alive",
                        "Cache-Control": "max-age=0",
                        "Origin": "http://id.ifeng.com",
                        "Upgrade-Insecure-Requests": "1",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Referer": "http://id.ifeng.com/allsite/login",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                    })
                cookies = session.cookies.get_dict()
                if 'sid' not in cookies:
                    raise CustomException('登录失败')
                res = session.get(
                    "http://fhh.ifeng.com/hapi/account/query").json()
                user_name = res['data']['weMediaName']
                return cookies, user_name
            else:
                key_data = session.get(
                    'https://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=MTU2MDA2Mzg2MDM%3D&rsakt=mod&client=ssologin.js(v1.4.15)&_=1531898376129'
                ).text
                pat = re.compile(
                    r'"servertime":(.*?),.*"nonce":"(.*?)","pubkey":"(.*?)"')
                res = pat.findall(key_data)
                if not res:
                    DaFeng.logger.error("Failed to login in sina")
                    raise CustomException('sina 登录规则变')
                servertime, nonce, pubkey = res[0]
                name = base64.b64encode(user.encode()).decode()
                key = rsa.PublicKey(int(pubkey, 16), 65537)
                message = ('%s\t%s\n%s' % (servertime, nonce, pswd)).encode()
                passwd = rsa.encrypt(message, key)
                passwd = binascii.b2a_hex(passwd).decode()
                data = {
                    "entry": "openapi",
                    "gateway": "1",
                    "from": "",
                    "savestate": "0",
                    "useticket": "1",
                    "pagerefer": "http%3A%2F%2Fid.ifeng.com%2Fallsite%2Flogin",
                    "ct": "1800",
                    "s": "1",
                    "vsnf": "1",
                    "vsnval": "",
                    "door": "",
                    "appkey": "1Jd1G6",
                    "su": name,
                    "service": "miniblog",
                    "servertime": servertime,
                    "nonce": nonce,
                    "pwencode": "rsa2",
                    "rsakv": "1330428213",
                    "sp": passwd,
                    "sr": "1920*1080",
                    "encoding": "UTF-8",
                    "cdult": "2",
                    "domain": "weibo.com",
                    "prelt": "499",
                    "returntype": "TEXT"
                }
                response = session.post(
                    "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)&_=1528351537613&openapilogin=qrcode",
                    data=data, ).json()
                if response['retcode'] == "4049":
                    key_data = session.get(
                        'https://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=MTU2MDA2Mzg2MDM%3D&rsakt=mod&client=ssologin.js(v1.4.15)&_=1531898376129'
                    ).text
                    pat = re.compile(
                        r'"servertime":(.*?),.*"nonce":"(.*?)","pubkey":"(.*?)"')
                    res = pat.findall(key_data)
                    servertime, nonce, pubkey = res[0]
                    img_code = session.get(
                        'https://login.sina.com.cn/cgi/pin.php?r=57148031&s=0')
                    with open('df_code.png', 'wb') as f:
                        f.write(img_code.content)
                    try:
                        data['su'] = name
                        data['servertime'] = servertime
                        data['nonce'] = nonce
                        cid, result = verify_captcha('df_code.png', 1005)
                        if result == '看不清':
                            cid, result = verify_captcha('df_code.png', 1005)
                        data['door'] = result
                        response = session.post(
                            'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_=1531898376166',
                            data=data).json()
                        if not response['uid']:
                            DaFeng.logger.info("Failed to get uid")
                            raise CustomException('登录失败')
                    finally:
                        os.remove(os.path.abspath('df_code.png'))
                session.post(
                    'https://api.weibo.com/oauth2/authorize',
                    headers={
                        "Host": "api.weibo.com",
                        "Connection": "keep-alive",
                        "Cache-Control": "max-age=0",
                        "Origin": "https://api.weibo.com",
                        "Upgrade-Insecure-Requests": "1",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Referer": "https://api.weibo.com/oauth2/authorize?client_id=1073104718&redirect_uri=http%3A%2F%2Fid.ifeng.com%2Fcallback%2Fsina&response_type=code",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    },
                    data={
                        "action": "login",
                        "display": "default",
                        "withOfficalFlag": "0",
                        "quick_auth": "false",
                        "withOfficalAccount": "",
                        "scope": "",
                        "ticket": response['ticket'],
                        "isLoginSina": "",
                        "response_type": "code",
                        "regCallback": "https%3A%2F%2Fapi.weibo.com%2F2%2Foauth2%2Fauthorize%3Fclient_id%3D1073104718%26response_type%3Dcode%26display%3Ddefault%26redirect_uri%3Dhttp%253A%252F%252Fid.ifeng.com%252Fcallback%252Fsina%26from%3D%26with_cookie%3D",
                        "redirect_uri": "http://id.ifeng.com/callback/sina",
                        "client_id": "1073104718",
                        "appkey62": "1Jd1G6",
                        "state": "",
                        "verifyToken": "null",
                        "from": "",
                        "switchLogin": "0",
                        "userId": "",
                        "passwd": "",
                    })
                session.get(
                    "https://api.weibo.com/oauth2/authorize?client_id=1073104718&redirect_uri=http%3A%2F%2Fid.ifeng.com%2Fcallback%2Fsina&response_type=code")
                cookies = session.cookies.get_dict()
                res = session.get(
                    "http://fhh.ifeng.com/hapi/account/query").json()
                user_name = res['data']['weMediaName']
                return cookies, user_name
        finally:
            session.close()

    def publish(self, title, content, category, flag=1):  # 发布内容
        """
          :param title:
          :param content:
          :param category:
          :return: status, article_id, cause
          """
        self.session.get('http://fhh.ifeng.com/publish/article')
        status = 3
        ariticle_id = None
        cause = ''
        self.logger.info("")
        result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)
        if not result:
            cause = "请上传文章封面"
            self.logger.error(cause)
            return status, ariticle_id, cause
        coverurl = result[0]
        udata = {
            "coverurl": coverurl
        }
        url_values = parse.urlencode(udata)
        url_values = url_values[9::]
        print(url_values)
        data = {
            "dataSource": "1",
            "title": title,
            "coverURL": url_values,
            "tags": "",
            "categoryId": self.categorylist[category],
            "isPublish": "true",
            "videoUrls": "",
            "audioUrls": "",
            "content": content,
            "articleURL": "",
            "coverPattern": "0",
            "type": "article",
            "isCreation": "0",
            "isMultiCoverTitle": "1",
            "title2": "",
            "coverURL2": "",
        }
        curl = ''
        if flag == 3:
            for item in result:
                udata = {
                    "coverurl": item
                }
                url_values = parse.urlencode(udata)
                url_values = url_values[9::]
                curl += url_values + ','
                data['coverURL'] = curl[:-1]
        print(data)
        url = "http://fhh.ifeng.com/api/article/insert"
        response = self.session.post(url=url, data=data, headers=self.headers).json()
        logging.error(response)

        if response['success']:
            self.logger.info("successs get articleid")
            status = 2
            return status, cause
        elif '过于频繁' in str(response):
            self.logger.error('发文频繁，等待下一次')
            return 1, cause
        else:
            return 3, str(response)

    def read_count(self,
                   stime=datetime.datetime.now() - datetime.timedelta(days=int(7)),
                   etime=datetime.datetime.now() - datetime.timedelta(days=int(1))):
        self.logger.info("")
        res = self.session.get(
            "http://fhh.ifeng.com/hapi/account/query").json()
        self.logger.info(res)
        user_name = res['data']['weMediaName']
        res = self.session.get(
            "http://fhh.ifeng.com/api/statistics/findstatlist",
            params="stime=%s&etime=%s&type=article&channel=0" % (
                stime.strftime("%Y-%m-%d"), etime.strftime("%Y-%m-%d"))).json()
        if not res['success']:
            raise CustomException('获取阅读数失败')
        read_list = []
        for data in res['data']['rows']:
            readcount = {
                "day_time": data["date"],
                "user_name": user_name,
                "recomment_num": data["ev"],
                "read_num": data["pv"],
                "comment_num": data["commentNum"],
                "share_num": data["shareNum"],
                "collect_num": data["collectNum"]
            }
            # logging.error(data)
            read_list.append(readcount)
        return read_list

    def fetch_article_status(self, title):
        resp = self.session.get(
            'http://fhh.ifeng.com/api/article/list?isOriginal=1&operationStatus=0&pageSize=30&pageNumber=1&_=1532677834082'
        ).json()['data']['rows']
        url = ''
        res = [2, '没查询到该文章', url]
        for art in resp:
            if title != art['title']:
                continue
            if art['operationStatus'] == 4:
                eArticleId = art['eArticleId']
                url = 'http://wemedia.ifeng.com/{}/wemedia.shtml'.format(eArticleId)
                res = 4, '', url
            elif art['operationStatus'] == 10:
                art_id = art['_id']
                url = 'http://fhh.ifeng.com/manage/articlePreview?id={}'.format(art_id)
                res = 5, art['auditReason'], url
            elif art['operationStatus'] == 16 or art['operationStatus'] == 6:
                cause = art['auditReason']
                if cause == 'null':
                    cause = '违反协议，已经下线'
                res = 5, cause, url
        return res

    def upload_image(self, image_name, image_data):
        self.logger.info('')
        return

    def check_user_cookies(self):
        self.logger.info('')
        resp = self.session.get(
            "http://fhh.ifeng.com/hapi/account/query").json()
        if resp['success']:
            return True
        else:
            return False

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        resp = self.session.get(
            'http://fhh.ifeng.com/api/article/list?isOriginal=1&operationStatus=4&pageSize=30&pageNumber=1&_=1541678014839'
        ).json()
        if resp['success']:
            for art in resp['data']['rows']:
                if title != art['title']:
                    continue
                else:
                    data = dict(
                        read_num=art['readNum'],
                        recomment_num=art['recommendNum'],
                        comment_num=art['commentNum'],
                        share_num=art['shareNum'],
                        collect_num=art['collectNum'],
                        publish_time=art['updateTime'],
                        like_num=-1,
                        follow_num=-1
                    )
                    return data
        raise CustomException('失败')

    def query_account_message(self, auto):
        return []


if __name__ == '__main__':
    from control.db.api.account_api import DBAccountApi
    from lib.tools.log_mgr import Flogger

    Flogger()
    db_account_api = DBAccountApi()
    # account = db_account_api.query(uid=9, mp_id=2, account='17710944592')
    # if account:
    #     account = account[0]
    # bj = DaFeng(account)
    # title = '新东方烹饪学校拟赴港上市，2018年前8个月营收20.55亿元'
    # content = '<img alt="null" src="http://d.ifengimg.com/q100/img1.ugc.ifeng.com/newugc/20181207/11/wemedia/601f7cf36505fdf036fefe4bdd33bd532b6be7fc_size40_w453_h340.jpg"><img alt="null" src="http://d.ifengimg.com/q100/img1.ugc.ifeng.com/newugc/20181207/11/wemedia/601f7cf36505fdf036fefe4bdd33bd532b6be7fc_size40_w453_h340.jpg"><img alt="null" src="http://d.ifengimg.com/q100/img1.ugc.ifeng.com/newugc/20181207/11/wemedia/bce11445e4d4748f7cb6cf30b5d67da71fa6ade9_size45_w506_h340.jpg"><p><br></p><p>鲸媒体讯 （文/琴不白）昨日晚间，中国东方教育控股有限公司（简称中国东方教育）向港交所递交招股书拟赴港上市。据招股书显示，2015年、2016年、2017年、2018年前8个月，公司营收分别为18.28亿元、23.36亿元、28.5亿元、20.55亿元，其对应的期内利润分别为3.35亿元、5.65亿元、6.42亿元、2.90亿元。</p>'
    # category = '教育'
    # flag = 3
