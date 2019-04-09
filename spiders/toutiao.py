# coding=utf8
import logging
import img_setting
import random
import time
import json
import re
import os
import execjs
import cv2
import numpy as np
import requests
import datetime


from selenium import webdriver
from w3lib.html import remove_tags


from lib.mp.base import Base
from control.db.redis_mgr import RedisApi
from lib.tools.custom_exception import CustomException
from lib.tools import toutiao_login_js


class TouTiao(Base):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'}
    mp_id = 5
    zh_name = "今日头条"

    def init(self, account, loop=0):
        self.account = account
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': Base.UA
        }
        self.logger.info("mp:%s, account:%s" % (account.mp_id, account.account))
        rs = RedisApi()
        key = "{}:{}:{}".format(account.uid, account.mp_id, account.id)
        r_cookies = rs.get_value(key)
        if r_cookies:
            cookies = json.loads(r_cookies.decode('utf8'))
            self.session.cookies = requests.cookies.cookiejar_from_dict(cookies)
            try:
                if not self.check_user_cookies():
                    cookies = self._login(account, loop=loop)
            except:
                cookies = self._login(account, loop=loop)
        else:
            cookies = self._login(account, loop=loop)
        if cookies:
            self.session.cookies = requests.cookies.cookiejar_from_dict(cookies)
            return True
        else:
            return False

    @staticmethod
    def fetch_code(user, pswd, loop=3):
        session = requests.session()
        cookies = TouTiao.init_cookie()
        fp = cookies.get('s_v_web_id', '')
        if not fp:
            TouTiao.logger.error('获取初始化cookies失败')
            return False
        session.cookies = requests.cookies.cookiejar_from_dict(cookies)
        session.headers.update({
            "User-Agent": Base.UA
        })
        resp = TouTiao.get_mobile_code(session, user, fp)  # init  click fetch toutiao_code
        if resp.json()['error_code'] == 1105:
            while loop:
                TouTiao.logger.error(f'break_code:{loop}次')
                code_resp = TouTiao.break_code(session, fp, user)
                # 获取验证吗
                if code_resp['ret'] == 200:
                    resp = TouTiao.get_mobile_code(session, user, fp)
                    resp_json = resp.json()
                    TouTiao.logger.error(resp_json)
                    if resp_json['error_code'] == 0:
                        TouTiao.logger.info(f'{user}获取mobile——code成功')
                        rs = RedisApi()
                        cookies = session.cookies.get_dict()
                        rs.set_value(user, json.dumps(cookies), ex=300)
                        return True
                    elif resp_json['error_code'] == 1206:  # 验证太频繁
                        TouTiao.logger.error(resp_json['description'])
                        raise CustomException(resp_json['description'])
                    else:
                        time.sleep(1)
                        TouTiao.logger.error(f'重试：{loop}')
                        TouTiao.logger.error('刷新滑块')
                        loop -= 1
                else:
                    time.sleep(1)
                    TouTiao.logger.error(f'滑动失败，重试{loop}')
                    loop -= 1
            return False
        else:
            rs = RedisApi()
            cookies = session.cookies.get_dict()
            rs.set_value(user, json.dumps(cookies), ex=300)
            return True

    @staticmethod
    def get_mobile_code(session, user, fp):
        session.headers = {
            "User-Agent": Base.UA
        }
        send_code_url = 'https://sso.toutiao.com/send_activation_code/v2/'
        resp = session.get(send_code_url,
                           params=dict(aid=24, service='https://www.toutiao.com/',
                                       account_sdk_source="web", type=24,
                                       mobile=user, fp=fp))
        return resp

    @staticmethod
    def break_code(session, fp, user):
        reply, ids, mode = TouTiao.parse_code(session, fp, user)
        data = {
            'modified_img_width': 268,
            'id': ids,
            'mode': mode,
            "reply": reply
        }
        session.headers.update({'Referer': 'https://sso.toutiao.com/',
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Origin': 'https://sso.toutiao.com',
                                'Host': 'verify.snssdk.com',
                                'Accept': '*/*'
                                })
        code_resp = session.post(
            f'https://verify.snssdk.com/verify?external=&fp={fp}&aid=24&lang=zh&app_name=sso&iid=0&vc=1.0'
            f'&did=0&ch=pc_slide&os=2&challenge_code=1105',
            data=json.dumps(data)
        ).json()
        return code_resp

    @staticmethod
    def init_cookie():
        opt = webdriver.ChromeOptions()
        opt.add_argument("--no-sandbox")
        opt.add_argument('user-agent={}'.format(
            Base.UA))
        opt.set_headless()
        chrome = webdriver.Chrome(options=opt)
        chrome.get('https://sso.toutiao.com/')
        cc = chrome.get_cookies()
        cookies = {}
        for s in cc:
            cookies[s['name']] = s['value']
        chrome.quit()
        return cookies

    @staticmethod
    def parse_code(session, fp, user):
        session.headers.update({
            'Referer': 'https://sso.toutiao.com/',
            'Origin': 'https://sso.toutiao.com'
        })
        url = 'https://verify.snssdk.com/get'
        params = {
            "external": "",
            "fp": fp,
            "aid": "24",
            "lang": "zh",
            "app_name": "sso",
            "iid": "0",
            "vc": "1.0",
            "did": "0",
            "ch": "pc_slide",
            "os": "2",
            "challenge_code": "1105",
        }
        loop = 3
        while loop:
            resp = session.get(url, params=params)
            TouTiao.logger.error(resp.text)
            resp_json = resp.json()
            if resp_json['ret'] == 200:
                ids = resp_json['data']['id']
                big_img_url = resp_json['data']['question']['url1']
                s_img_url = resp_json['data']['question']['url2']
                tip_y = resp_json['data']['question']['tip_y']
                mode = resp_json['data']['mode']
                resp1 = session.get(big_img_url)
                resp2 = session.get(s_img_url)
                target = f'{user}bg.jpg'
                template = f'{user}gap.png'
                with open(target, 'wb') as f:
                    f.write(resp1.content)
                with open(template, 'wb') as f:
                    f.write(resp2.content)
                com_x = TouTiao.match(target, template)
                reply = TouTiao.sliding_track(com_x, tip_y)
                if os.path.exists(target):
                    os.remove(target)
                if os.path.exists(template):
                    os.remove(template)
                return reply, ids, mode
            else:
                loop -= 1
        raise CustomException('获取验证码图片失败')

    @staticmethod
    def match(target, template):
        img_rgb = cv2.imread(target)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template, 0)
        run = 1
        w, h = template.shape[::-1]
        print(w, h)
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        # 使用二分法查找阈值的精确值
        L = 0
        R = 1
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            TouTiao.logger.error(threshold)
            if threshold < 0:
                TouTiao.logger.error('Error')
                return None
            loc = np.where(res >= threshold)
            TouTiao.logger.error(len(loc[1]))
            if len(loc[1]) > 1:
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                TouTiao.logger.error('目标区域起点x坐标为：%d' % loc[1][0])
                return loc[1][0]
            elif len(loc[1]) < 1:
                R -= (R - L) / 2

    @staticmethod
    def sliding_track(com_x, tip_y):
        gj = [1, 2, 3, 4, 5, 6, 7, 8]
        stime = int(time.time() * 1000)
        # 开始
        l = []
        start_x = random.choice(gj)
        while True:
            time.sleep(random.uniform(0.05, 0.1))
            m_time = int(time.time() * 1000)
            relative_time = m_time - stime
            start_x += random.choice(gj)
            l.append(dict(relative_time=relative_time, y=tip_y, x=start_x))
            if start_x > com_x:
                break
        return l

    @staticmethod
    def login(user, pswd, code):
        TouTiao.logger.info("")
        session = requests.session()
        try:
            rs = RedisApi()
            tem_cookie = json.loads(rs.get_value(user))
            session.cookies = requests.cookies.cookiejar_from_dict(tem_cookie)

            fp = tem_cookie.get('s_v_web_id', '')
            if not fp:
                return {}, ''
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
            })
            e = {'fp': fp, 'code': code, 'mobile': user}
            n = ["mobile", "code"]
            ss = TouTiao._get_encry().call('encryptParams', e, n)
            data = {
                "aid": "24",
                "service": "https://www.toutiao.com/",
                "account_sdk_source": "web",
            }
            data.update(ss)
            url = 'https://sso.toutiao.com/quick_login/v2/'
            resp = session.get(url, params=data)
            resp_json = resp.json()
            redirect_url = resp_json.get('redirect_url', '')
            if not redirect_url:
                TouTiao.logger.error('登录失败')
                return {}, ''
            session.get(redirect_url)
            session.get('https://www.toutiao.com/')
            home = session.get(
                'https://mp.toutiao.com/get_media_info/').json()
            user_name = home['data']['user']['screen_name']
            cookies = session.cookies.get_dict()
            return cookies, user_name
        except Exception as e:
            TouTiao.logger.error(e)
            return {}, ''
        finally:
            session.close()

    @staticmethod
    def _get_encry():
        source = toutiao_login_js.toutiao_login_js
        phantom = execjs.get()
        return phantom.compile(source)

    def publish(self, title, content, category, flag=1):
        """
          :param title:
          :param content:
          :param category:
          :return: status, article_id, cause
        """
        status = 3
        cause = ''
        self.logger.info("")
        content = remove_tags(content, which_ones=('a', 'h3', 'span',))
        # 找img 标签
        imgs = re.compile(r'(<img.*?src=.*?>)', re.S).findall(content)
        for img in imgs:
            result = re.compile(r'src="(.*?)"').findall(img)
            if result:
                src = result[0]
                web_uri = src.split('large/')[-1]
                tou_tag = '<p><br></p><div class="pgc-img"><img class="" src="{}" data-ic="false" data-ic-uri=""' \
                          ' data-height="340" data-width="488"' \
                          ' image_type="1" web_uri="{}" img_width="488" img_height="340">' \
                          '<p class="pgc-img-caption"></p></div>'.format(src, web_uri)
                content = content.replace(img, tou_tag)
        ret = self.check()
        if not ret:
            cause = "failed to check"
            self.logger.error(cause)
            return status, cause

        data = {
            'activity_tag': '0',
            'add_third_title': '0',
            'article_ad_type': '2',
            'article_label': '',
            'article_type': '0',
            'claim_origin': '0',
            'column_chosen': '0',
            'content': content,
            'from_diagnosis': '0',
            'govern_forward': '0',
            'is_fans_article': '0',
            'need_pay': '0',
            'pgc_feed_covers': '[]',
            'pgc_id': '0',
            'push_android_summary': '',
            'push_android_title': '',
            'push_ios_summary': '',
            'push_status': '0',
            'recommend_auto_analyse': '0',
            'save': '1',
            'tag': '',
            'timer_status': '0',
            'timer_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'title': title,
            'title_id': '1531209953842_1593706095426573',
        }
        if flag == 3:
            image_urls = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)
            u1, u2, u3 = image_urls[:3]
            u1s = u1.split('list/')[-1]
            u2s = u2.split('list/')[-1]
            u3s = u3.split('list/')[-1]
            data['qy_self_recommendation'] = '0'
            data['quote_hot_spot'] = '0'
            data['pgc_feed_covers'] = json.dumps([{'ic_uri': '',
                                                   'id': 1,
                                                   'origin_uri': u1s,
                                                   'thumb_height': 741,
                                                   'thumb_width': 1240,
                                                   'uri': u1s,
                                                   'url': u1
                                                   },
                                                  {'ic_uri': '',
                                                   'id': 2,
                                                   'origin_uri': u2s,
                                                   'thumb_height': 340,
                                                   'thumb_width': 506,
                                                   'uri': u2s,
                                                   'url': u2
                                                   },
                                                  {'ic_uri': '',
                                                   'id': 3,
                                                   'origin_uri': u3s,
                                                   'thumb_height': 340,
                                                   'thumb_width': 678,
                                                   'uri': u3s,
                                                   'url': u3
                                                   }
                                                  ])
        data['content'] = '<div>' + content + '</div>'
        resp = self.session.post(
            'https://mp.toutiao.com/core/article/edit_article_post/?source=mp&type=article',
            data=data,
            headers=self.headers).json()
        self.logger.info(resp)
        if resp['code'] == 2222:  # 表示发文不成功需要验证
            self.session.get(
                'https://sso.toutiao.com/auth_index/?service=https://mp.toutiao.com/pc_auth_confirm/')
            self.session.post(
                'https://mp.toutiao.com/article/spell_check_switch/?',
                headers={
                    'Host': 'mp.toutiao.com',
                    'Connection': 'keep-alive',
                    'Origin': 'https://mp.toutiao.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': '*/*',
                    'Referer': 'https://mp.toutiao.com/profile_v3/graphic/publish',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                },
                data={
                    'status': 2},
            ).json()
            self.session.get(
                'https://m.toutiao.com/log/sentry/v2/api/slardar/main/?ev_type=ajax&ax_status=200&ax_type=post&ax_duration=77&ax_size=26&ax_protocol=https&ax_domain=mp.toutiao.com&ax_path=%2Farticle%2Fspell_check_switch%2F&version=1.0.0&bid=toutiao_mp&pid=index_new&hostname=mp.toutiao.com&protocol=https&timestamp={}'.format(
                    int(time.time() * 1000), headers=self.headers)
            )
            self.session.get(
                'https://mlab.toutiao.com/auth/toutiao/login',
                headers=self.headers)
            resp = self.session.post(
                'https://mp.toutiao.com/core/article/edit_article_post/?source=mp&type=article',
                data=data,
                headers=self.headers).json()
            logging.error(resp)
        try:
            if resp['data']['pgc_id']:
                return 2, ''
        except Exception as e:
            cause = resp['message']
            raise CustomException(cause)

    def get_img(self):
        self.logger.info("")
        row = random.choice(img_setting.toutiao_img)
        return row

    def check(self):
        self.logger.info("")
        resp = self.session.post(
            'https://mp.toutiao.com/article/spell_check_switch/?',
            data={
                'status': 2
            }, headers=self.headers
        ).json()
        if resp['message'] == 'success':
            return True
        else:
            return False

    def upload_img(self, row):
        self.logger.info("")
        resp = self.session.post(
            'https://mp.toutiao.com/micro/image/upload',
            data={
                'platform': 'toutiaohao',
                'position': 'articleup_sub',
                'image_info': [
                    {"url": row, "remark": "", "title": "", "content": "", "width": "960", "height": "540"}]},
            headers=self.headers).json()
        if resp['msg'] == 'ok':
            return True
        else:
            return False

    def read_count(self,
                   starttime=datetime.datetime.now() - datetime.timedelta(days=7),
                   endtime=datetime.datetime.now() - datetime.timedelta(days=1)):
        self.logger.info("")
        self.session.headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Host": "mp.toutiao.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        }
        home = self.session.get(
            'https://mp.toutiao.com/get_media_info/', headers=self.headers,
        ).json()
        self.logger.info(home)
        user_name = home['data']['user']['screen_name']
        # logging.error(user_name)
        if not user_name:
            raise CustomException('账号异常 %s' % self.account.account)
        self.session.headers['Referer'] = 'https://mp.toutiao.com/profile_v3/index/content-analysis/overview'
        res = self.session.get(
            'https://mp.toutiao.com/statistic/content_daily_stat/?start_date={}&end_date={}&pagenum=1'.format(
                starttime.strftime("%Y-%m-%d"), endtime.strftime("%Y-%m-%d")),
            headers=self.headers,
        ).json()
        self.logger.info(res)
        resp = res['data']['data_list']
        read_list = []
        for i in range(len(resp) - 1, -1, -1):
            if int(resp[i]['impression_count']) == 0 and int(resp[i]['go_detail_count']) == 0:  # 表示没更新
                continue
            read_list.append(dict(day_time=resp[i]['date'], user_name=user_name,
                                  recomment_num=resp[i]['impression_count'],
                                  read_num=resp[i]['go_detail_count'],
                                  collect_num=resp[i]['share_count'],
                                  follow_num=resp[i]['repin_count']))

        return read_list

    def fetch_article_status(self, title):
        self.logger.info("")
        self.headers['accept-language'] = 'zh-CN,zh;q=0.9'
        self.session.get('https://mp.toutiao.com/profile_v3/graphic/articles')
        self.headers['accept'] = 'application/json, text/plain, */*'
        self.headers['referer'] = 'https://mp.toutiao.com/profile_v3/graphic/articles'
        self.session.keep_alive = False
        title = title.replace(' ', '')
        resp = self.session.get(
            'https://mp.toutiao.com/core/article/media_article_list/?count=20&status=all&from_time=0&item_id=&feature=0'
        ).json()['data']['articles']
        res = [2, '没查询到该文章', '']
        for art in resp:
            if title != str(art['title']):
                continue
            elif art['status'] == 3:
                url = art['article_url']
                return 4, '', url
            elif art['status'] == 0:
                return 5, art['confirm_reason'], ''
        return res

    def upload_image(self, image_name, image_data):
        self.logger.info("")
        try:
            resp = self.session.post(
                'https://mp.toutiao.com/tools/upload_picture/?type=ueditor&pgc_watermark=1&action=uploadimage&encode=utf-8',
                files={'upfile': (
                    image_name, image_data, 'image/jpeg', {'type': 'image/jpeg'})}
            ).json()
            if resp['state'] == 'SUCCESS':
                return resp['url']
            else:
                raise CustomException('上传图片失败')
        except:
            raise CustomException('上传图片失败，检查账号或密码')

    def check_user_cookies(self):
        self.logger.info("")
        home = self.session.get(
            'https://mp.toutiao.com/get_media_info/', headers=self.headers,
        ).json()
        logging.error(home)
        if home['message'] == 'success':
            return True
        else:
            return False

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        resp = self.session.get(
            'https://mp.toutiao.com/pgc/mp/core/article/list?size=20&status=passed&from_time=0&start_time=0&end_time=0&search_word=&page=1&feature=0&source=all'
        ).json()
        articles = resp['data']['content']
        for art in articles:
            if title != art['title']:
                continue
            else:
                times = int(art['verify_time'])
                time_local = time.localtime(times)
                dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                data = dict(
                    publish_time=dt,
                    recomment_num=art['impression_count'],
                    read_num=art['go_detail_count'],
                    comment_num=art['comment_count'],
                    share_num=-1,
                    collect_num=-1,
                    like_num=-1,
                    follow_num=-1
                )
                return data
        return ''


if __name__ == '__main__':
    user = '18519864469'
    pswd = 'JINGmeiti123'
    # TouTiao.fetch_code(user, pswd)
    print(TouTiao.login(user, pswd, code='4494'))
