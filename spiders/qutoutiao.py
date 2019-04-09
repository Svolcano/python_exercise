# coding=utf-8
import re
import time
import datetime
import requests
import logging
import base64
from urllib import parse

from lib.mp.base import Base


class QuTouTiao(Base):
    mp_id = 13
    zh_name = '趣头条'

    @staticmethod
    def login(user, pswd, **kw):
        session = requests.session()
        resp = session.get(
            'https://mpapi.qutoutiao.net/member/login?email=&telephone={}&password={}&keep=&captcha=&source=1&k='
            '&dtu=200'.format(user, pswd)
        ).json()
        token = resp['data']['token']
        if not token:
            return {}
        req = requests.get(
            'https://mpapi.qutoutiao.net/member/getMemberInfo?token={}&dtu=200'.format(token)
        ).json()
        if req['code'] != 0:
            raise Exception('login fail')
        logging.error('登录成功')
        name = req['data']['nickname']
        return dict(token=token), name

    def publish(self, title, content, category, flag=1):
        token = self.session.cookies['token']
        status = 3
        ariticle_id = None
        cause = ''
        self.logger.info("")
        result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)
        if not result:
            cause = "请上传文章封面"
            self.logger.error(cause)
            return status, cause
        coves = self.session.get(result[0])
        img_data = 'data:image/jpeg;base64,' + base64.b64encode(coves.content).decode()
        post_cove = self.session.post('https://qupload.qutoutiao.net/api/v1.0/image/uploadBase64',
                                      data={
                                          'token': token,
                                          'action': 'image',
                                          'upfile': img_data,
                                          'dtu': 200}).json()
        cover = post_cove['data']['path']
        home = self.session.get(
            'https://mpapi.qutoutiao.net/member/getMemberInfo?token={}&dtu=200'.format(token)
        ).json()
        user_id = home['data']['member_id']
        flag_id = 'article' + user_id + str(int(time.time() * 1000))
        # 选择标签
        tag = self.session.get(
            'https://mpapi.qutoutiao.net/content/getCategoryList?token={}&dtu=200'.format(token)
        ).json()
        for item in tag['data']:
            if item['name'] == category:
                category = item['cates'][-1]
        data = {
            'id': '',
            'category': 22,
            'two_level_category': '[%s]' % category,
            'cover_type': 1,
            'cover': '["{}"]'.format(cover),
            'title': title,
            'detail': content,
            'image_list': '["{}"]'.format(result[0].split('com/')[-1]),
            'is_delay': 0,
            'is_origin': 1,
            'tag': '教育,人工智能,鲸媒体',
            'code': '',
            'flag_id': flag_id,
            'token': token,
            'dtu': 200,
        }
        self.session.get('https://mpapi.qutoutiao.net/content/checkTitle?'
                         'title={}&flag_id={}'
                         '&type=content&token={}&dtu=200'.format(title, flag_id, token))
        resp = self.session.post('https://mpapi.qutoutiao.net/content/saveNew', data=data).json()
        try:
            content_id = resp['data']['content_id']
        except Exception as e:
            QuTouTiao.logger.error(e)
            return 3, resp['message']
        self.session.post('https://mpapi.qutoutiao.net/content/setLocalChannel',
                          data={
                              'content_id': content_id,
                              'dtu': 200,
                              'local_channel_list': [],
                              'token': token
                          })
        change_url = 'https://mpapi.qutoutiao.net/content/changeStatus?id={}&status=5' \
                     '&flag_id={}&token={}&dtu=200'.format(content_id, flag_id, token)
        resp = self.session.get(change_url).json()
        logging.error(resp)
        if resp['code'] == 0:
            status = 2
            return status, ''
        else:
            status = 3
            return status, resp['message']

    def read_count(self,
                   start_day=datetime.datetime.now() - datetime.timedelta(days=7),
                   end_day=datetime.datetime.now() - datetime.timedelta(days=1)):
        token = self.session.cookies['token']
        url = 'https://mpapi.qutoutiao.net/report/brief?start_date={}&end_date={}' \
              '&submemberid=&token={}&dtu=200'.format(
            start_day.strftime('%Y-%m-%d'), end_day.strftime('%Y-%m-%d'), token)
        resp = self.session.get(url).json()['data']['data']['daily']
        read_list = []
        for item in resp:
            read_list.append(dict(
                recomment_num=item['list_pv'],
                read_num=item['pv'],
                share_num=item['share_num'],
                day_time=item['event_day']
            ))
        return read_list

    def fetch_article_status(self, title):
        res = [2, '没查询到该文章', '']
        token = self.session.cookies['token']
        resp = self.session.get('https://mpapi.qutoutiao.net/content/getList?status=&page=1&title=&submemberid='
                                '&nickname=&start_date=''&end_date=&isMotherMember=false&token={}&dtu=200'
                                .format(token)).json()['data']['data']
        for art in resp:
            if title != art['title']:
                continue
            elif art['status'] == '2':
                url = art['url']
                res = 4, '', url
            elif art['status'] == '3':
                res = 3, art['reason'], ''
        return res

    def check_user_cookies(self):
        token = self.session.cookies['token']
        req = self.session.get(
            'https://mpapi.qutoutiao.net/member/getMemberInfo?token={}&dtu=200'.format(token)
        ).json()
        if req['code'] != 0:
            return False
        return True

    def upload_image(self, image_name, image_data):
        files = {
            'upfile': (image_name, image_data, 'image/jpeg', {
                'id': 'WU_FILE_0', 'name': image_name, 'type': 'image/jpeg',
                "lastModifiedDate": 'Tue Jun 12 2018 19:22:30 GMT+0800 (中国标准时间)',
                'size': ''})}
        resp = self.session.post('https://editer2.1sapp.com/ueditor/php/controller.php?action=uploadimage&encode=utf-8',
                                 files=files).json()
        base_url = 'http://static.1sapp.com/image'
        img_url = base_url + resp['url']
        return img_url
