import requests
import logging
import img_setting
import random
import time
import datetime
from lib.mp.base import Base
from requests_toolbelt import MultipartEncoder
import base64
import re
from lib.zhima_proxy import Proxy
from lib.tools.custom_exception import CustomException


class WangYi(Base):
    mp_id = 7
    zh_name = '网易号'

    @staticmethod
    def login(user, pswd, **kw):
        WangYi.logger.info("")
        session = requests.session()
        post_url = 'https://mail.163.com/entry/cgi/ntesdoor?funcid=loginone&language=-1&passtype=1&iframe=1&product=mail163&from=web&df=email163&race=-2_262_-2_hz&module=&uid={0}&style=-1&net=t&skinid=null'.format(
            user)
        session.post(
            post_url,
            data={
                'username': user,
                'url2': 'http://email.163.com/errorpage/error163.htm',
                'savalogin': '0',
                'password': pswd,
            })
        resp = session.get(
            'http://mp.163.com/wemedia/navinfo.do?t=0.4831746485143411',
            headers={
                "Host": "mp.163.com",
                "Connection": "keep-alive",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Linux; U; Android 7.0; zh-CN; BLN-AL10 Build/HONORBLN-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.1.2.992 Mobile Safari/537.36",
                "Accept-Language": "zh-CN,en-US;q=0.8",
            }
        ).json()
        if not resp['code']:
            return {}, ''
        cookies = session.cookies.get_dict()
        ss = session.get('http://mp.163.com/wemedia/navinfo.do?t=0.4831746485143411').json()
        t_name = ss['data']['tname']
        cookies.pop("OUTFOX_SEARCH_USER_ID", '')
        return cookies, t_name

    def img_con(self, content):
        self.logger.info("")
        row = random.choice(img_setting.wy_img)
        img_str = '<img src="{0}" contenteditable="false" _src="{1}">'.format(
            row, row)
        i_con = '<p style="text-align: center">' + img_str + '</p>' + content
        return i_con

    def publish(self, title, content, category, flag=1):
        """
          :param title:
          :param content:
          :param category:
          :return: status, cause
        """
        status = 3
        cause = ''
        self.logger.info("")
        headers = {
            "Host": "mp.163.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://mp.163.com",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android 7.0; zh-CN; BLN-AL10 Build/HONORBLN-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.1.2.992 Mobile Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Language": "zh-CN,en-US;q=0.8",
        }
        mid_resp = self.session.get(
            'http://mp.163.com/wemedia/navinfo.do?t=0.4831746485143411').json()
        logging.error(mid_resp)
        if not mid_resp['code']:
            cause = mid_resp['msg']
            self.logger.error(cause)
            return status, cause

        sign_resp = self.session.get(
            'http://mp.163.com/wemedia/article/checkTitle?title=%s' % title
        ).json()
        print(sign_resp)
        if not sign_resp['code']:
            cause = sign_resp['msg']
            raise CustomException(cause)

        data = {
            'mediaId': mid_resp['data']['wemediaId'],
            'articleId': -1,
            'title': title,
            'sign': sign_resp['data']['sign'],
            'timestamp': int(time.time() * 1000),
            'cover': 'auto',  # 自动的话是 auto
            'scheduled': 0,
            'operation': 'publish',
            'content': content,
            'userClassify': category,
            'NECaptchaValidate': '',
            'picUrl': ''
        }
        if flag == 3:
            result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)  # 查找p标签
            if not result:
                cause = '请上传文章封面'
                self.logger.error(cause)
                return status, cause
            u_list = []
            for item in result[:3]:
                u_list.append(item)
            data['picUrl'] = '||'.join(u_list)
            data['cover'] = 'threeImg'

        fw_response = self.session.post(
            'http://mp.163.com/wemedia/article/status/api/publish.do',
            data=data,
            headers=headers
        ).json()
        self.logger.info(fw_response)
        if fw_response['code'] == 100502:  # 100502 代表有图形验证
            c = 3
            while c:
                try:
                    proxies = Proxy.proxy()
                    fw_response = self.session.post(
                        'http://mp.163.com/wemedia/article/status/api/publish.do',
                        data=data,
                        headers=headers,
                        proxies=proxies,
                        timeout=40
                    ).json()
                    break
                except Exception as e:
                    logging.info("proxy publish error:%s", e)
                c -= 1
                time.sleep(10)
        if fw_response['code'] == 1 or '您在最近24小时内' in fw_response['msg']:
            status = 2
            return status, cause
        else:
            cause = "failed to get  publish: %s" % fw_response['msg']
            self.logger.info(cause)
            raise CustomException(cause)

    def read_count(self, start=datetime.datetime.now() - datetime.timedelta(days=int(7)),
                   end=datetime.datetime.now() - datetime.timedelta(days=int(1))):
        self.logger.info("")
        pv_resp = self.session.get(
            'http://mp.163.com/wemedia/data/content/article/pv/list.do?',
            params='_=1524046010181&start=%s&end=%s' % (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))).json()
        if pv_resp['code'] != 1:
            raise CustomException('账号或密码不正确')
        read_list = []
        for read in pv_resp['data']['list']:
            data = dict(
                day_time=read['statDate'],  # 时间
                user_name=read['tname'],  # 用户名字
                read_num=read['readCount'],  # 阅读
                share_num=read['shareCount'],  # 分享
                follow_num=read['commentCount'],  # 跟帖
                recomment_num=read['recommendCount'],  # 推荐
            )
            read_list.append(data)
        return read_list

    def check_user_cookies(self):
        try:
            self.logger.info("")
            resp = self.session.get(
                'http://mp.163.com/wemedia/navinfo.do?t=0.4831746485143411',
                headers={
                    "Host": "mp.163.com",
                    "Connection": "keep-alive",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Linux; U; Android 7.0; zh-CN; BLN-AL10 Build/HONORBLN-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.1.2.992 Mobile Safari/537.36",
                    "Accept-Language": "zh-CN,en-US;q=0.8",
                }
            ).json()
            return resp['code'] == 1
        except Exception as e:
            self.logger.error(e)
        return False

    def fetch_article_status(self, title):
        self.logger.info("")
        self.session.headers.update(
            {"Accept-Language": "zh-CN,zh;q=0.9",
             "Host": "mp.163.com",
             "Connection": "close",
             "Origin": "http://mp.163.com",
             "Referer": "http://mp.163.com/index.html",
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
        )
        mid_resp = self.session.get(
            'http://mp.163.com/wemedia/navinfo.do?t=0.4831746485143411').json()
        self.logger.info(mid_resp)
        self.session.headers.update(
            {"Connection": "keep-alive"})
        resp = self.session.post(
            'http://mp.163.com/wemedia/content/manage/list.do?_={0}&wemediaId={1}'.format(
                int(time.time() * 1000), mid_resp['data']['wemediaId']
            ), data={
                "wemediaId": mid_resp['data']['wemediaId'],
                "pageNo": "1",
                "contentState": "-1",
                "size": "20",
                "contentType": "4",
            }).json()['data']['list']
        res = [2, '没查询到该文章', '']
        for art in resp:
            # contentState =3 是发文成功，2是未发文成功  reason是原因
            if title != art['title']:
                continue
            if art['contentState'] == 3:
                art_id = art['articleId']
                url = 'http://dy.163.com/v2/article/detail/{}.html'.format(art_id)
                res = 4, '', url
            elif art['contentState'] == 4:
                res = 5, art['reason'], ''

        return res

    def upload_image(self, image_name, image_data):
        url = 'http://mp.163.com/api/v2/upload/nos/water'
        m = MultipartEncoder(
            fields={'uploadtype': 'cms', 'from': 'neteasecode_mp',
                    'bucketName': 'dingyue', 'watername': '0',
                    'field': (image_name, image_data, 'image/jpeg')}
        )
        self.session.headers.update({'Content-Type': m.content_type})
        resp = self.session.post(url, data=m)
        resp_json = resp.json()
        if resp_json.get('code') == 1:
            return resp_json.get('data').get('ourl')
        else:
            raise CustomException('上传图片失败')

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        self.session.headers.update(
            {"Accept-Language": "zh-CN,zh;q=0.9",
             "Host": "mp.163.com",
             "Connection": "close",
             "Origin": "http://mp.163.com",
             "Referer": "http://mp.163.com/index.html",
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
        )
        mid_resp = self.session.get(
            'http://mp.163.com/wemedia/navinfo.do?t=0.4831746485143411').json()
        self.logger.info(mid_resp)
        self.session.headers.update(
            {"Connection": "keep-alive"})
        resp = self.session.post(
            'http://mp.163.com/wemedia/content/manage/list.do?_={0}&wemediaId={1}'.format(
                int(time.time() * 1000), mid_resp['data']['wemediaId']
            ), data={
                "wemediaId": mid_resp['data']['wemediaId'],
                "pageNo": "1",
                "contentState": "-1",
                "size": "20",
                "contentType": "4",
            }).json()['data']['list']
        for art in resp:
            # contentState =3 是发文成功，2是未发文成功  reason是原因
            if title != art['title']:
                continue
            else:
                data = dict(
                    read_num=art['pvCount'],
                    recomment_num=art['recommendCount'],
                    publish_time=art['showTime'],
                    share_num=art['shareCount'],
                    collect_num=-1,
                    like_num=-1,
                    follow_num=-1,
                    comment_num=-1
                )
                return data
        return ''


if __name__ == '__main__':
    from control.db.api.account_api import DBAccountApi
    from lib.tools.log_mgr import Flogger

    Flogger()
    db_account_api = DBAccountApi()
    # title = '教育部:全国各地已整改有问题的校外培训机构'
    # content = '<p style="text-align: center"><img src="http://dingyue.nosdn.127.net/VGpwAFH8Ntq7m9toGaBTM8KRBCcT9ewHSRrDrtTtWBpjl1544097859074.jpeg" contenteditable="false" _src="http://dingyue.nosdn.127.net/VGpwAFH8Ntq7m9toGaBTM8KRBCcT9ewHSRrDrtTtWBpjl1544097859074.jpeg" id="netease154409786107386"></p><p style="text-align: center"><br></p><p style="text-align: center"><br></p><p>鲸媒体讯（文/乔木）近日，教育部消息显示，截至2018年11月30日，全国2963个县（市、区）已启动专项治理整改工作，其中1550县（市、区）已基本完成专项治理整改任务，县（市、区）完成率52.31%。全国共摸排校外培训机构401050所，存在问题机构272842所，现已完成整改211225所，完成整改率77.42%。</p><p>教育部强调，校外培训机构治理取得了阶段性成效，也进入了整改最关键时段，教育部将会同市场监管、民政、人社、应急管理等部门继续督促各地加快整改进度，确保按期完成整改任务。</p><p style="text-align: center"><img src="http://dingyue.nosdn.127.net/xBuaw9qAwLuVjJYXjGpmv3EseOcNl37h4pAGaQzD40reI1544097898083.jpeg" contenteditable="false" _src="http://dingyue.nosdn.127.net/xBuaw9qAwLuVjJYXjGpmv3EseOcNl37h4pAGaQzD40reI1544097898083.jpeg" id="netease1544097901562853"></p><p style="text-align: center"><img src="http://dingyue.nosdn.127.net/qxLZSgpdmE99Mx44DaD9iEtAfc3kRUll=Ygowwrydzi0z1544097905944.jpeg" contenteditable="false" _src="http://dingyue.nosdn.127.net/qxLZSgpdmE99Mx44DaD9iEtAfc3kRUll=Ygowwrydzi0z1544097905944.jpeg" id="netease1544097909139913"></p><p><br></p>'
    # flag = 3
    # category = '教育'
    # account = db_account_api.query(uid=9, mp_id=7, account='15501003995@163.com')[0]
    # bj = WangYi(account)
    # bj.publish(title, content, category, flag)
