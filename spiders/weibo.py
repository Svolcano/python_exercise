import requests
import re
import base64
import rsa
import binascii
import logging
from urllib import parse
import os
import datetime
import time
import json
from lib.mp.base import Base
from lib.yundama import verify_captcha
from w3lib.html import remove_tags
from lib.tools.custom_exception import CustomException


class WeiBo(Base):
    mp_id = 4
    zh_name = '微博号'

    @staticmethod
    def login(user, pswd, **kw):
        js_url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MTg2MjA2MDExMzI%3D&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'\
            .format(int(time.time()*1000))
        WeiBo.logger.info("")
        default_ret = {}
        session = requests.session()
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
            'Connection': 'close'
        }
        session.adapters.DEFAULT_RETRIES = 3
        key_data = session.get(
            js_url
        ).text
        pat = re.compile(
            r'"servertime":(.*?),.*"nonce":"(.*?)","pubkey":"(.*?)"')
        res = pat.findall(key_data)
        if not res:
            return default_ret, {}
        servertime, nonce, pubkey = res[0]
        name = base64.b64encode(user.encode()).decode()
        key = rsa.PublicKey(int(pubkey, 16), 65537)
        message = ('%s\t%s\n%s' % (servertime, nonce, pswd)).encode()
        passwd = rsa.encrypt(message, key)
        passwd = binascii.b2a_hex(passwd).decode()
        data = {
            "entry": "sso", "gateway": "1",
            "from": "null", "savestate": "30",
            "useticket": "0", "pagerefer": "", "vsnf": "1",
            "su": name, "service": "sso",
            "servertime": servertime,
            "nonce": nonce, "pwencode": "rsa2",
            "rsakv": "1330428213",
            "sp": passwd, "sr": "1920*1080", "encoding": "UTF-8",
            "cdult": "3", "domain": "sina.com.cn",
            "prelt": "21", "returntype": "TEXT",
        }
        post_resp = session.post(
            'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)',
            data=data, verify=False).json()
        if post_resp['retcode'] == '4049':
            key_data = session.get(
                js_url, verify=False).text
            pat = re.compile(
                r'"servertime":(.*?),.*"nonce":"(.*?)","pubkey":"(.*?)"')
            res = pat.findall(key_data)
            servertime, nonce, pubkey = res[0]
            img_code = session.get(
                'https://login.sina.com.cn/cgi/pin.php?r=57148031&s=0', verify=False)
            with open('weibo.png', 'wb') as f:
                f.write(img_code.content)
            data['su'] = name
            data['servertime'] = servertime
            data['nonce'] = nonce
            cid, result = verify_captcha('weibo.png', 1005)
            if result == '看不清':
                cid, result = verify_captcha('weibo.png', 1005)
            data['door'] = result
            post_resp = session.post(
                'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)',
                data=data, verify=False).json()
            logging.error(post_resp)
            os.remove(os.path.abspath('weibo.png'))
        try:
            post_uid = post_resp.get('uid', None)
            if not post_uid:
                WeiBo.logger.error("failed to get uid")
                return default_ret, ''
        except Exception as e:
            WeiBo.logger.error("failed to get uid")
            return default_ret, ''
        passport_url = post_resp['crossDomainUrlList'][0]
        session.get(passport_url)
        uid = post_resp['uid']
        home_url = 'https://weibo.com/u/{}/home?wvr=5&lf=reg'.format(uid)
        session.get(home_url, verify=False)
        home = session.get('https://dss.sc.weibo.com/pc/index', verify=False).text
        name_re = re.compile(r'"screen_name":"(.*?)",', re.S)
        user_name = name_re.findall(home)
        cookies = session.cookies.get_dict()
        WeiBo.logger.info(cookies)
        return cookies, user_name[0]

    def publish(self, title, content, category, flag=1):
        """
          :param title:
          :param content:
          :param category:
          :return: status, article_id, cause
        """
        status = 3
        cause = ''
        self.session.get('https://card.weibo.com/article/v3/editor#/draft', verify=False)
        cover = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)
        if not cover:
            cause = "请上传文章封面"
            self.logger.error(cause)
            return status, cause
        video = re.compile(r'(<iframe class=".*?video.*?></iframe>)').findall(content)
        if video:
            content = self.rep_video(content, video[0])
        # 删除草稿, 防止溢出
        id_resp = self.session.get(
            'https://card.weibo.com/article/v3/aj/editor/draft/list'
            , verify=False).json()
        if id_resp['code'] != 100000:
            cause = id_resp['msg']
            self.logger.error(cause)
            raise CustomException(cause)

        id_list = id_resp['data']['list']
        for item in id_list:
            logging.error(item)
            article_id = item['id']
            del_resp = self.session.post(
                'https://card.weibo.com/article/v3/aj/editor/draft/delete',
                data={'id': article_id}, verify=False
            ).json()
            if del_resp['code'] != 100000:
                cause = "failed to get ariticle_id : %s" % item
                self.logger.error(cause)
                raise CustomException(cause)
        # 开始发文
        req = self.session.post(
            'https://card.weibo.com/article/v3/aj/editor/draft/create',
            data={
                "title": "未命名",
                "type": "draft",
                "summary": "",
                "writer": "",
                "cover": "",
                "content": "<p>​</p>",
            }, verify=False).json()
        logging.error(req)
        tmp_data = req['data']
        wart_id = None
        if tmp_data:
            wart_id = tmp_data['id']
        if not wart_id:
            cause = "cookies失效"
            self.logger.error(cause)
            raise CustomException(cause)
        self.session.get(
            'https://card.weibo.com/article/v3/aj/editor/draft/load?id=%s' %
            wart_id, verify=False)
        # 3
        self.session.get(
            'https://card.weibo.com/article/v3/aj/editor/settings/getpayinfo?id=%s' %
            wart_id, verify=False)

        # 4
        times = int(time.time() * 1000)
        pay = self.session.get(
            'https://e.weibo.com/v1/public/paid/initpid?bid=1000207805&_t=1&ispay=0&callback=STK_%s' % times,
            verify=False)
        pay.encoding = 'gbk'
        pay = pay.text
        logging.error(pay)
        p_re = re.compile(r'"pid":"(.*)",', re.S)
        pid = p_re.findall(pay)
        if not pid:
            cause = '网络cookies过期，请及时更换'
            self.logger.error(cause)
            raise CustomException(cause)
        # 设置不付费
        set_pay = self.session.post(
            'https://card.weibo.com/article/v3/aj/editor/settings/setpayinfo',
            data={
                'id': wart_id,
                'pay_setting': json.dumps({"pid": pid[0], "isreward": 1, "isvclub": 0, "ispay": 0})
            }, verify=False).json()
        if not set_pay['code']:
            cause = "Failed to get setpayinfo"
            self.logger.error(cause)
            raise CustomException(cause)
        resp = self.session.post(
            'https://card.weibo.com/article/v3/aj/editor/draft/save',
            data={
                "updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "id": wart_id,
                "type": "",
                "subtitle": "",
                "extra": "[]",
                "title": title,
                "status": "0",
                "isvclub": "0",
                "ispay": "0",
                "publish_at": "",
                "error_msg": "",
                "error_code": "0",
                "free_content": "",
                "content": content,
                "cover": cover[0],
                "summary": "",
                "writer": "",
                "is_word": "0",
                "article_recommend": "[]",
            }, verify=False
        ).json()
        logging.error(resp)
        if not resp['code']:
            cause = "failed to save draft"
            self.logger.error(cause)
            raise CustomException(cause)

        response = self.session.post(
            'https://card.weibo.com/article/v3/aj/editor/draft/publish',
            data={
                "id": wart_id,
                "text": "发布了头条文章：《{0}》 ".format(title),
                "follow_to_read": "0",
                "follow_official": "0",
                "sync_wb": "0",
                "is_original": "0",
                "time": "",
            }, verify=False).json()
        logging.error(response)
        if response['code'] == 100000:
            status = 2
            return status, cause
        else:
            cause = response['msg']
            raise CustomException(cause)

    def rep_video(self, content, video):
        v_re = re.compile(r'src="(.*?)"')
        urls = v_re.findall(video)
        try:
            for url in urls:
                resp = self.session.post('https://card.weibo.com/article/v3/aj/editor/plugins/video',
                                         data=dict(url=url)).json()
                if resp['code'] == 100000:
                    v_id = resp['data']['id']
                    card = '<card data-card-id="{}" data-card-type="video">​</card>'.format(v_id)
                    content = content.replace(video, card)
                else:
                    raise CustomException('正文中：%s' % resp['msg'])
            return content
        except:
            raise CustomException('重新登录，cookie 失效')

    def read_count(self,
                   starttime=datetime.datetime.now() - datetime.timedelta(days=7),
                   endtime=datetime.datetime.now() - datetime.timedelta(days=1)):
        self.logger.info("")
        default_ret = []
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
            'Connection': 'close'
        }
        home = self.session.get('https://dss.sc.weibo.com/pc/index', verify=False).text
        name_re = re.compile(r'"screen_name":"(.*?)",', re.S)
        user_name = name_re.findall(home)
        if not user_name:
            self.logger.error("failed to get user_name")
            return default_ret
        user_name = user_name[0]
        resp = self.session.get(
            'https://dss.sc.weibo.com/pc/aj/chart/content/weiboReadTrend',
            params='starttime={}&endtime={}&_=1528710535868'.format(
                starttime.strftime("%Y-%m-%d"), endtime.strftime("%Y-%m-%d")), verify=False
        ).json()
        if resp['code'] != 100000:
            self.logger.error("failed to get readtrend")
            return default_ret
        read_list = resp['data']['chart']['weiboReadTrend']['reads']
        r_list = []
        for i in range(len(read_list)):
            dt = (starttime + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            read_num = read_list[i]
            r_list.append(dict(day_time=dt, read_num=read_num, user_name=user_name, recomment_num=read_num))
        self.logger.info(r_list)
        return r_list

    def fetch_article_status(self, title):
        url = ''
        res = [2, '没查询到该文章', url]
        home = self.session.get('https://dss.sc.weibo.com/pc/index').text
        name_re = re.compile(r'{"id":(.*?),"idstr"', re.S)
        uid = name_re.findall(home)[0]
        home = self.session.get(
            'https://weibo.com/{}/profile?topnav=1&wvr=6'.format(uid)
        ).text
        domain = re.search(r"\$CONFIG\['domain'\]='(.*?)';", home).group(1)
        page_id = re.compile(r"\$CONFIG\['page_id'\]='(.*?)';", re.S).findall(home)[0]
        times = str(int(time.time() * 1000))
        url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain={0}&profile_ftype=1&is_article=1&pagebar=0&' \
              'pl_name=Pl_Official_MyProfileFeed__25&id={1}&script_uri=/p/{2}/home&feed_type=0' \
              '&page=1&pre_page=0&domain_op={3}&__rnd={4}'.format(domain, page_id, page_id, domain, times)
        logging.error(url)
        resp = self.session.get(url).json()
        html = resp['data']
        h_re = re.compile(
            r'<div class="WB_feed_detail clearfix" node-type="feed_content".*?>(.*?)<em class="W_ficon ficon_forward S_ficon">',
            re.S)
        result = h_re.findall(html)
        for item in result:
            ff = re.compile(r'来自(.*?)</a>', re.S)
            ffrom = remove_tags(ff.findall(item)[0]).replace('\\n', '').replace(' ', '')
            if '微博' in ffrom:
                if '发布了头条文章' in item:
                    u_re = re.compile(r'action-data="url=(.*?)&target=_blank"')
                    article_url = u_re.findall(item)
                    article_url = parse.unquote(article_url[0])
                    title_re = re.compile(r'发布了头条文章.*?《(.*?)》')
                    tit = title_re.findall(item)
                    if title != tit[0]:
                        continue
                    res = 4, '', article_url

        return res

    def upload_image(self, image_name, image_data):
        self.logger.info("")
        return

    def check_user_cookies(self):
        try:
            self.logger.info("")
            self.session.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
                'Connection': 'close'
            }
            home = self.session.get('https://dss.sc.weibo.com/pc/index', verify=False).text
            name_re = re.compile(r'"screen_name":"(.*?)",', re.S)
            user_name = name_re.findall(home)
            if user_name:
                return True
        except Exception as e:
            self.logger.error(e)
        return False

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        home = self.session.get('https://dss.sc.weibo.com/pc/index').text
        name_re = re.compile(r'{"id":(.*?),"idstr"', re.S)
        uid = name_re.findall(home)[0]
        home = self.session.get(
            'https://weibo.com/{}/profile?topnav=1&wvr=6'.format(uid)
        ).text
        domain = re.search(r"\$CONFIG\['domain'\]='(.*?)';", home).group(1)
        page_id = re.compile(r"\$CONFIG\['page_id'\]='(.*?)';", re.S).findall(home)[0]
        times = str(int(time.time() * 1000))
        url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain={0}&profile_ftype=1&is_article=1&pagebar=0&' \
              'pl_name=Pl_Official_MyProfileFeed__25&id={1}&script_uri=/p/{2}/home&feed_type=0' \
              '&page=1&pre_page=0&domain_op={3}&__rnd={4}'.format(domain, page_id, page_id, domain, times)
        logging.error(url)
        resp = self.session.get(url).json()
        html = resp['data']
        h_re = re.compile(
            r'<div class="WB_feed_detail clearfix" node-type="feed_content".*?>(.*?)<em class="W_ficon ficon_forward S_ficon">',
            re.S)
        result = h_re.findall(html)
        num_re = re.compile('\d+')
        for item in result:
            time_re = re.compile(r'<div class="WB_from S_txt2">(.*?)</a> 来自 ', re.S)
            f_re = re.compile(r'来自(.*?)</a>', re.S)
            ffrom = remove_tags(f_re.findall(item)[0]).replace('\\n', '').replace(' ', '')
            if '微博' not in ffrom:
                continue
            # 链接
            u_re = re.compile(r'action-data="url=(.*?)&target=_blank"')
            article_url = u_re.findall(item)
            url = ''
            if article_url:
                url = parse.unquote(article_url[0])
            # 阅读
            read_num = 0
            r_re = re.compile(r'<i class="S_txt2" title="此条微博已经被阅读.*次">阅读 (.*?)</i>')
            reads = r_re.findall(item)
            if reads:
                read_num = reads[0]
            # 转发
            share_num = 0
            s_re = re.compile(r'<span><em class="W_ficon ficon_forward S_ficon">(.*?)</em></span></span></span>')
            shares = s_re.findall(item)
            if shares:
                share = num_re.findall(shares[0])
                if share:
                    share_num = share[0]
            # 评论
            comment_num = 0
            com_re = re.compile(r'<em class="W_ficon ficon_repeat S_ficon">(.*?)</em></span></span></span>')
            comments = com_re.findall(item)
            if comments:
                comment = num_re.findall(comments[0])
                if comment:
                    comment_num = comment[0]
            # 点赞
            like_num = 0
            like_re = re.compile(r'<em class="W_ficon ficon_praised S_txt2">(.*?)</em></span> </span></span>', re.S)
            likes = like_re.findall(item)
            if likes:
                like = num_re.findall(likes[0])
                if like:
                    like_num = like[0]
            # 时间
            dt = remove_tags(time_re.findall(item)[0]).replace('\n', '').replace(' ', '')
            data = dict(
                # publish_time=dt,
                recomment_num=-1,
                read_num=read_num,
                comment_num=comment_num,
                like_num=like_num,
                share_num=share_num,
                url=url,
                follow_num=-1,
                collect_num=-1
            )
            return data
        return ''


if __name__ == '__main__':
    from control.db.api.account_api import DBAccountApi
    from lib.tools.log_mgr import Flogger

    Flogger()
    db_account_api = DBAccountApi()
    account = db_account_api.query(uid=1, mp=7, account='15711082771')[0]
    bj = WeiBo(account)
