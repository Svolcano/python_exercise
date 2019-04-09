import requests
import re
import time
import datetime
import settings
from selenium import webdriver
from w3lib.html import remove_tags
from lxml import etree
from raven import Client
from lib.tools.spider_tools import get_one_ua
from control.db.api.account_api import DBAccountApi
from control.db.api.article_api import DBArticleApi
from control.db.api.image_api import DBImageApi
from lib.tools.custom_exception import CustomException
from lib.tools.log_mgr import get_logger
from lib.mp.base import Base
from control.db.redis_mgr import RedisApi


class Twitter(Base):
    logger = get_logger()
    rs = RedisApi()
    login_url = 'https://twitter.com/login'
    post_url = 'https://twitter.com/sessions'
    home_url = 'https://twitter.com/home'
    user_url = 'https://twitter.com/i/search/typeahead.json?count=1200&media_tagging_in_prefetch=true&prefetch=true&result_type=users&users_cache_age=-1'
    create_url = 'https://twitter.com/i/tweet/create'
    mp_id = 10
    zh_name = 'Twitter'

    @staticmethod
    def login(user, pswd, **kw):
        _session = requests.session()
        token, rf, cookies = Twitter._get_values()
        _session.cookies = requests.cookies.cookiejar_from_dict(cookies)
        _session.headers.update({
            'User-Agent': get_one_ua(0), 'Referer': 'https://twitter.com/'})
        post_data = {
            'session[username_or_email]': user,
            'session[password]': pswd,
            'authenticity_token': token,
            'ui_metrics': rf,
            'scribe_log': '',
            'redirect_after_login': '',
            'authenticity_token': token,
            'remember_me': 1,
        }
        print(post_data)
        _session.post(Twitter.post_url, data=post_data, allow_redirects=False, timeout=30)
        cookies = _session.cookies.get_dict()
        _session.get(Twitter.home_url, allow_redirects=False)
        try:
            resp = _session.get(Twitter.user_url)
            if resp.status_code == 200:
                name = resp.json()['users'][0]['name']
                Twitter.logger.info(name)
            return cookies, name
        except:
            raise Exception('登录失败')

    @staticmethod
    def _get_values():
        opt = webdriver.ChromeOptions()
        opt.add_argument("--no-sandbox")
        opt.add_argument('user-agent={}'.format(get_one_ua(0)))
        opt.set_headless()
        chrome = webdriver.Chrome(options=opt)
        chrome.get(Twitter.login_url)
        resp = chrome.page_source
        token = re.compile(r'<input type="hidden" value="(.*?)" name="authenticity_token"', re.S).findall(resp)
        rf = re.compile(r'<input type="hidden" name="ui_metrics" autocomplete="off" value="(.*?)" />', re.S).findall(
            resp)
        if token:
            token = token[0]
        else:
            chrome.quit()
            raise Exception('token 获取失败')
        if rf:
            rf = rf[0]
            rf = rf.replace('&quot;', '"')
            # print(json.loads(rt))
        else:
            chrome.quit()
            raise Exception('rf获取错')
        cc = chrome.get_cookies()
        cookies = {}
        for s in cc:
            cookies[s['name']] = s['value']
        cookies['app_shell_visited'] = '1'
        cookies['path'] = '/'
        cookies['max-age'] = '5'
        chrome.quit()
        return token, rf, cookies

    def publish(self, content):
        self.session.headers['Referer'] = 'https://twitter.com/'
        result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)  # 查找img
        media_id_list = []
        if len(result) > 4:
            raise Exception('图片不能超过4张')
        for item in result:
            res = requests.get(item)
            img_data = res.content
            s = self._upload_img(img_data)
            media_id_list.append(str(s))
        media_id = ','.join(media_id_list)
        self.logger.info(media_id)
        # 剔除标签
        content = remove_tags(content)
        # if len(content.encode(encoding='gbk')) > 280:
        #     raise Exception('文章内容已超过最大长度')
        data = {
            "authenticity_token": "285baf78b4de28459a94ec0c0a3c5fa3f62fdfd5",
            "batch_mode": "off",
            "is_permalink_page": "false",
            "media_ids": media_id,
            "place_id": "",
            "status": content,
            "tagged_users": "",
        }
        if not media_id_list:
            del data['tagged_users']
            del data['media_ids']
        resp = self.session.post(
            self.create_url, data=data, timeout=30)
        resp_json = resp.json()
        try:
            tweet_id = resp_json['tweet_id']
            return 2, '', tweet_id
        except Exception as e:
            cause = resp_json['message']
            self.logger.error(e)
            return 3, cause, ''

    def _upload_img(self, img_data):
        b_img_l = len(img_data)
        url = 'https://upload.twitter.com/i/media/upload.json?command=INIT&total_bytes={}&media_type=image%2Fjpeg&media_' \
              'category=tweet_image'.format(b_img_l)
        data = {
            "command": "INIT",
            "total_bytes": b_img_l,
            "media_type": "image/jpeg",
            "media_category": "tweet_image",
        }
        resp = self.session.post(url, data=data, timeout=30).json()  # 获取图id
        media_id = resp['media_id']
        up_url = 'https://upload.twitter.com/i/media/upload.json?command=APPEND&media_id={}&segment_index=0'.format(
            media_id)
        file = {
            'media': ('blob', img_data, 'image/jpeg', {
                'Content-Type': 'application/octet-stream'
            })}

        # 上传
        self.session.post(up_url, files=file)
        self.session.post(
            'https://upload.twitter.com/i/media/upload.json?command=FINALIZE&media_id='.format(media_id),
            data={
                'command': 'FINALIZE',
                'media_id': media_id
            }, timeout=30)
        return media_id

    def upload_image(self, image_name, image_data):
        return ''

    def fetch_article_status(self, mp_article_id):
        resp = self.session.get(self.user_url, timeout=30)
        resp_json = resp.json()
        screen_name = resp_json['users'][0]['screen_name']
        url = 'https://twitter.com/{}/status/{}?conversation_id={}'.format(screen_name, mp_article_id, mp_article_id)
        return 4, '', url

    def query_article_data(self, mp_article_id):
        resp = self.session.get(self.user_url, timeout=30)
        resp_json = resp.json()
        screen_name = resp_json['users'][0]['screen_name']
        url = 'https://twitter.com/{}/status/{}?conversation_id={}'.format(screen_name, mp_article_id, mp_article_id)
        self.session.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        self.session.headers['Referer'] = 'https://twitter.com/'
        resp = self.session.get(url, timeout=30)
        html = etree.HTML(resp.text)
        datas = html.xpath('//span[@class="ProfileTweet-actionCountForAria"]/text()')
        if not datas:
            return ''
        reads = dict(
            comment_num=int(datas[0][0]),
            follow_num=int(datas[1][0]),
            like_num=int(datas[2][0])
        )
        return reads

    def check_user_cookies(self):
        try:
            resp = self.session.get(self.user_url, timeout=30)
            resp_json = resp.json()
            screen_name = resp_json['users'][0]['screen_name']
            if screen_name:
                return True
            else:
                self.logger.error('Twitter 规则改变')
                return False
        except:
            return False


if __name__ == '__main__':
    from control.db.api.account_api import DBAccountApi
    from lib.tools.log_mgr import Flogger

    Flogger()
    db_account_api = DBAccountApi()
    account = db_account_api.query(uid=1, mp_id=10)
    if account:
        account = account[0]
    tw = Twitter(account)
    title = '1082156664759869440'
    content = 'Hello, this is my talk'
    resp = tw.query_article_data(title)
    print(resp)
    # tw.publish(title, content, 1, flag=1)
    # user = '837253132@qq.com'
    # pswd = 'qiaolang521'
    # # # cookies = Twitter.login(user, pswd)
    # # # print(cookies)
    # title = '233333'
    # # content = 'Hello, this is an beautiful boy1'
    # # flag = 3
    # # category = '教育'
    # tw = Twitter()
    # # tw.publish(title, content, category, flag)
    # # tw.fetch_article_status(1)
    # tw.fetch_article_status('1078594593367547904')
