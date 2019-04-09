import requests
import re
import base64
import rsa
import binascii
import logging
import os
import datetime
import time
import json
from lib.mp.base import Base
from lib.yundama import verify_captcha
from lib.zhima_proxy import Proxy
from lib.tools.custom_exception import CustomException
import urllib3
import time
urllib3.disable_warnings()


class XinLang(Base):
    # 文章类型
    type_list = {
        "财经": 1, "科技": 2, "数码": 3, "体育": 4, "娱乐": 5, "影视": 6,
        "汽车": 7, "旅游": 8, "文化": 9, "时尚": 10, "健康": 11, "教育": 12,
        "育儿": 13, "历史": 14, "动漫": 15, "家居": 16, "星座": 17, "军事": 18,
        "情感": 19, "收藏": 20, "宠物": 21, "搞笑": 22, "科学": 23, "心理": 25,
        "摄影": 26, "美食": 27, "美女": 28, "游戏": 29, "职场": 30, "房产": 31,
        "财事": 32, "生活": 33, "社会": 34, "音乐": 35, "动物": 36, "风水": 37,
        "宗教": 38, "国际": 39, "本地": 40, "三农": 41}
    mp_id = 8
    zh_name = '新浪看点'

    @staticmethod
    def login(user, pswd, **kw):
        js_url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MTg2MjA2MDExMzI%3D&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}' \
            .format(int(time.time() * 1000))
        XinLang.logger.info("")
        def_ret = {}
        session = requests.session()
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'}
        key_data = session.get(
            js_url
        ).text
        pat = re.compile(
            r'"servertime":(.*?),.*"nonce":"(.*?)","pubkey":"(.*?)"')
        res = pat.findall(key_data)
        if not res:
            XinLang.logger.error("failed to pubkey")
            raise CustomException('登陆规则变')
        servertime, nonce, pubkey = res[0]
        name = base64.b64encode(user.encode()).decode()
        key = rsa.PublicKey(int(pubkey, 16), 65537)
        message = ('%s\t%s\n%s' % (servertime, nonce, pswd)).encode()
        passwd = rsa.encrypt(message, key)
        passwd = binascii.b2a_hex(passwd).decode()
        data = {
            "entry": "sso", "gateway": "1",
            "from": "null", "savestate": "30",
            "useticket": "0", "pagerefer": "",
            "vsnf": "1", "su": name,
            "service": "sso", "servertime": servertime,
            "nonce": nonce, "pwencode": "rsa2",
            "rsakv": "1330428213", "sp": passwd,
            "sr": "1920*1080", "encoding": "UTF-8",
            "cdult": "3", "domain": "sina.com.cn",
            "prelt": "21", "returntype": "TEXT",
        }
        post_resp = session.post(
            'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)',
            data=data).json()
        if post_resp['retcode'] == '4049':
            key_data = session.get(
                js_url
            ).text
            pat = re.compile(
                r'"servertime":(.*?),.*"nonce":"(.*?)","pubkey":"(.*?)"')
            res = pat.findall(key_data)
            servertime, nonce, pubkey = res[0]
            img_code = session.get(
                'https://login.sina.com.cn/cgi/pin.php?r=57148031&s=0')
            with open('sina.png', 'wb') as f:
                f.write(img_code.content)
            data['su'] = name
            data['servertime'] = servertime
            data['nonce'] = nonce
            cid, result = verify_captcha('sina.png', 1005)
            if result == '看不清':
                cid, result = verify_captcha('sina.png', 1005)
            data['door'] = result
            post_resp = session.post(
                'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)',
                data=data).json()
            if not post_resp.get('uid'):
                XinLang.logger.error('验证码错误')
                return def_ret, ''
            os.remove(os.path.abspath('sina.png'))
        nick_name = post_resp.get('nick')
        if not nick_name:
            raise CustomException(post_resp['reason'])
        session.get(
            'https://login.sina.com.cn/'
        )
        cookies = session.cookies.get_dict()
        return cookies, nick_name

    def publish(self, title, content, category, flag=1):
        """
          :param title:
          :param content:
          :param category:
          :return: status, article_id, cause
        """
        self.logger.info("")
        cause = ''
        self.session.get('http://mp.sina.com.cn/main/editor?vt=4#/SendArt/Edit')
        result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)
        if not result[0]:
            cause = "请上传文章封面"
            raise CustomException(cause)
        fbtime = str(int(time.time() * 1000))
        img = result[0]
        timestamp = time.time()
        time_local = time.localtime(timestamp)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 发布时间
        data = {
            "jsver": "1.7.3",
            "action": "submit",
            "title": title,
            "article_describe": "",
            "body": content,
            "images": img,
            "videos": "",
            "headImgModel": "0",
            "headImgSrc": img,
            "article_type": self.type_list[category],
            "quanzi_id": "0",
            "ansysCicle": "0",
            "article_smalltype": "0",
            "ansysWeibo": "0",
            "ansysLongWeibo": "0",
            "ansysSinaBlog": "0",
            "ori": "0",
            "reserve": "0",
            "reserve_time": dt,
            "Edit[mouse_click_num]": "18",
            "Edit[key_down_num]": "32",
            "Edit[stay_time]": "492.623",
            "Preview[mouse_click_num]": "27",
            "Preview[key_down_num]": "32",
            "Preview[stay_time]": "1304.256",
        }
        fw_response = self.session.post(
            "http://mp.sina.com.cn/aj/article?type=submit&callback=jQuery321032990596469580513_" + fbtime,
            data=data, verify=False).text
        self.logger.info(fw_response)
        if '{"status":"-10"' in fw_response:  # -10 代表有验证码 换个ip 尝试发文
            proxies = Proxy.proxy()
            fw_response = self.session.post(
                "http://mp.sina.com.cn/aj/article?type=submit&callback=jQuery321032990596469580513_" + fbtime,
                proxies=proxies, data=data, timeout=10, verify=False).text
        if '"status":1' in fw_response:
            status = 2
            return status, cause
        else:
            re_msg = re.compile(r'"message":"(.*?)"}', re.S)
            msg = re_msg.findall(fw_response)[0].encode('utf-8').decode('unicode_escape')
            # 状态没找到 找关键词
            if '不要连续' in msg:
                return 1, ''
            else:
                return 3, msg

    def read_count(self,
                   startday=datetime.datetime.now() - datetime.timedelta(days=7),
                   endday=datetime.datetime.now() - datetime.timedelta(days=1)):
        self.logger.info("")
        def_ret = []
        resp = self.session.get(
            "http://mp.sina.com.cn/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"},
            verify=False).text
        pat = re.compile('<span class="user_box_a_s">(.*?)</span>', re.S)
        res = pat.findall(resp)
        if not res:
            raise CustomException('统计失败')
        user_name = res[0].strip()
        res = self.session.get(
            "http://mp.sina.com.cn/aj/statistic/general",
            params="date_start=%s&date_end=%s" % (
                startday.strftime("%Y-%m-%d"), endday.strftime("%Y-%m-%d")),
        verify=False)
        res = json.loads(res.text[1:-1])
        if res['status'] != 1:
            raise CustomException('统计失败，请检查账号密码')
        read_list = []
        for count in res['data']['time']:
            count_data = dict(
                user_name=user_name,
                day_time=count["date"],
                recomment_num=count["info"]["exposure"],
                read_num=count["info"]["read"],
                comment_num=count["info"]["comment"],
                collect_num=count["info"]["collect"]
            )
            read_list.append(count_data)
        return read_list

    def fetch_article_status(self, title):
        self.logger.info("")
        resp = self.session.get(
            'http://mp.sina.com.cn/aj/article/list?shownew=1&showtype=all&list=all&page=1&pagesize=40&_=1538036815354&callback=Zepto1538036760734',
            verify=False
        )
        resp.encoding = 'utf8'
        json_re = re.compile(r'Zepto.*?\((.*?)\)', re.S)
        article = json.loads(json_re.findall(resp.text)[0])['data']
        logging.error(article)
        res = [2, '没查询到该文章', '']
        for art in article:
            if title != art['articleTitle']:
                continue
            if art['status'] == '1':
                logging.error(art)
                url = art['articleUrl']
                res = 4, '', url
            elif art['status'] == '0':
                res = 5, '不通过', ''
        return res

    def upload_image(self, image_name, image_data):
        self.logger.info("")
        resp = self.session.post(
            'http://mp.sina.com.cn/aj/upload?type=article&json=1',
            files={'img': (image_name, image_data, 'image/jpeg', {
                'id': 'WU_FILE_0', 'name': image_name, 'type': 'image/jpeg',
                "lastModifiedDate": 'Tue Jun 12 2018 19:22:30 GMT+0800 (中国标准时间)',
                'size': '',
            })},
            verify=False
        ).json()
        if resp['errno'] == 1:
            return resp['data']
        raise CustomException('上传图片失败，请检查账号密码')

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        resp = self.session.get(
            'http://mp.sina.com.cn/aj/article/list?shownew=1&showtype=all&list=1&page=1&pagesize=10&_=1541991946453&callback=Zepto1541991931895',
            verify=False
        )
        resp.encoding = 'utf8'
        json_re = re.compile(r'Zepto.*?\((.*?)\)', re.S)
        try:
            article = json.loads(json_re.findall(resp.text)[0])['data']
        except Exception as e:
            logging.error(e)
            raise CustomException("cookies is fail ")
        for art in article:
            if title != art['articleTitle']:
                continue
            else:
                data = dict(
                    publish_time=art['articlePubulisTime'],
                    read_num=art['articleReadCount'],
                    recomment_num=art['articleReadCount'],
                    comment_num=art['articleCommentCount'],
                    share_num=-1,
                    like_num=-1,
                    follow_num=-1,
                    collect_num=-1
                )
                return data
        return ''

    def check_user_cookies(self):
        try:
            self.logger.info("")
            resp = self.session.get(
                'http://mp.sina.com.cn/aj/media/row?_=1539071186724&callback=Zepto1539070837291', verify=False).text
            json_re = re.compile(r'Zepto.*?\((.*?)\)', re.S)
            response = json_re.findall(resp)
            if not response:
                return False
            response = json.loads(response[0])
            if isinstance(response, dict) and response['status'] == 1:
                return True
            return False
        except Exception as e:
            self.logger.error(e)
        return False

if __name__ == '__main__':
    from control.db.api.account_api import DBAccountApi
    from lib.tools.log_mgr import Flogger
    Flogger()
    db_account_api = DBAccountApi()
    account = db_account_api.query(uid=1, mp=7, account='15711082771')[0]
    bj = XinLang(account)