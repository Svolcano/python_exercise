import datetime
import json
import random
import requests
from lxml import etree
# from control.db.redis_mgr import RedisApi
# from lib.mp.base import Base
# from lib.tools.log_mgr import get_logger
# from aip import AipOcr
from lib.mp.base import Base
from requests_toolbelt.multipart.encoder import MultipartEncoder
import re
import time
from w3lib.html import remove_tags
from lib.tools.getcookie import get_cookies


class XueQiu(Base):
    mp_id = 15
    zh_name = '雪球号'
    type_dict = {
        "生活": "116", "公司分析": "110", "投资理念": "111", "财报解读": "112", "技术方面": "113", "盘面解读": "114", "宏观": "115",
        "创投": "117",
        "基金": "118", "债券": "119", "理财": "120", "保险": "121", "私募": "122", "房产": "123", "白酒": "124", "银行": "125",
        "互联网": "126",
        "医疗": "127", "汽车": "128", "家电": "129", "传媒": "130",
    }
    base = 'https://xueqiu.com'
    header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'xueqiu.com',
        'Referer': base,
        'Origin': 'https://xueqiu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # cookie = get_cookies()
    @staticmethod
    def login(user, pswd, **kw):
        base = 'https://xueqiu.com'
        url = 'https://xueqiu.com/snowman/provider/geetest?t=' + str(int(time.time())) + '&type=login_pwd'
        # user_agent = random.choice(USER_AGENTS)
        cookie = get_cookies()
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': base,
            'Origin': base,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
            'Connection': 'keep-alive',
            'Cookie': cookie
        }
        s = requests.session()
        # now_cookies = s.cookies
        # now_cookies.clear()
        resp = s.get(url, headers=header).text
        challenge = re.findall(r'"challenge":".*?"', resp, re.S | re.M)[0]
        challenge = re.compile(r'"|challenge|:').sub('', challenge).strip()
        gt = re.findall(r'"gt":".*?"', resp, re.S | re.M)[0]
        gt = re.compile(r'"|gt|:').sub('', gt).strip()
        yk_url = 'https://api.yuekuai.tech/api/geetest3?token=Gvpr9TgK57&gt=b68f7c51ff1ee91cad5ece5b8a1c9a56&challenge=' + challenge
        a = requests.get(yk_url).text
        validate = re.findall(r'"validate":".*?"', a, re.S | re.M)[0]
        validate = re.compile(r'"|validate|:').sub('', validate)
        geetest_url = 'https://xueqiu.com/snowman/login'
        try:
            a = s.post(geetest_url, data={
                'remember_me': 'true',
                'username': user,
                'password': pswd,
                'captcha': '',
                'geetest_challenge': challenge,
                'geetest_validate': validate,
                'geetest_seccode': validate + ' | jordan'
            },
                       headers=header)
            dom = etree.HTML(a.content)
            name = dom.xpath('//span[@class="user-name"]/text()')[0]
            # print(name)
            return s.cookies.get_dict(), name
        except:
            raise Exception("登录失败，请检查账户密码")

    def publish(self, title, content, category, flag=1):
        self.logger.info('')
        base = 'https://xueqiu.com/'
        url = 'https://xueqiu.com/statuses/update.json'
        result = re.compile(r'<.*?img.*?src="(.*?)".*?>', re.S).findall(content)
        # header中的值发生变化时，会发送失败
        header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'xueqiu.com',
            'Referer': 'https://xueqiu.com/write',
            'Origin': 'https://xueqiu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        try:
            img_data_list = []
            img_data_str = ''
            if result:
                i = 0
                for item in result:
                    res = requests.get(item)
                    img_data = res.content
                    pic_name = str(i) + '.jpg'
                    img_data = self.upload_image(pic_name=pic_name, img_data=img_data)
                    img_data_list.append(img_data)
                    img_data = '<img class="ke_img" src="' + img_data + '!custom.jpg">'
                    img_data_str += img_data
                    i += 1
            # print(img_data_list)
            publish_params = {}
            a = self.session.get(
                'https://xueqiu.com/provider/session/token.json?api_path=%2Fstatuses%2Fupdate.json&_=' + str(
                    int(time.time())), headers=self.header).text
            reobj = re.compile(r'".*?":|"|{|}')
            a = reobj.sub('', a)
            publish_params["status"] = '<p>' + content + '</p>' + img_data_str
            publish_params["title"] = title
            publish_params["original"] = 0
            publish_params["right"] = 0
            publish_params["label_ids"] = ''
            publish_params["custom_label_names"] = category
            publish_params["cover_pic"] = img_data_list[0]
            publish_params["original_declare"] = 0
            publish_params["show_cover_pic"] = 1
            publish_params["session_token"] = a
            resp = self.session.post(url, data=publish_params, headers=header).text
            self.logger.info(resp)
            art_id = re.findall(r'"id":.*?,', resp, re.M)[0]
            art_id = re.compile(r'"|id|:|,').sub('', art_id).strip()
            user_id = re.findall(r'"user_id":.*?,', resp, re.M)[0]
            user_id = re.compile(r'"|user_id|:|,').sub('', user_id).strip()
            art_url = base + user_id + '/' + art_id
            # 发文成功后，返回文章ID
            return 2, ''
        except Exception as e:
            self.logger.error(e)
            return 3, '发送失败'

    def check_user_cookies(self):
        self.logger.info('')
        resp = self.session.get('https://xueqiu.com/')
        html = resp.text
        uname = html.xpath('//span[@class="user-name"]/text()')
        if uname:
            return True
        else:
            return False

    # def upload_image(self, img_data, content):
    #     return ''

    def fetch_article_status(self, title):
        return 4, '', ''

    def read_count(self,
                   start_date=datetime.datetime.now() - datetime.timedelta(days=int(7)),
                   end_date=datetime.datetime.now() - datetime.timedelta(days=int(1))):
        self.logger.info("")
        return []

    def upload_image(self, pic_name, img_data):
        base = 'https://xueqiu.com/'
        url = 'https://xueqiu.com/photo/upload.json?base_content_type=text/html'
        files = {
            'file': (pic_name, img_data, 'image/jpeg')
        }
        datas = MultipartEncoder(
            fields=files
        )
        self.header['Content-Type'] = datas.content_type
        resp = self.session.post(url, data=datas, headers=self.header).text
        img_url = re.findall(r'"filename":".*?\.jpg"', resp, re.S | re.M)[0]
        img_url = re.compile(r'"|filename|:').sub('', img_url).strip()
        img_data = '//xqimg.imedao.com/' + img_url
        return img_data

    # 需文章链接
    def query_article_data(self, title):
        """获取单篇文章阅读量"""
        u_id = self.session.cookies.get_dict()['u']
        url = 'https://xueqiu.com/v4/statuses/user_timeline.json?page=1&user_id=' + u_id
        resp = self.session.get(url, headers=self.header).text
        resp = json.loads(resp)
        for a in resp["statuses"]:
            if title == a["title"]:
                try:
                    # 收藏数列表
                    fav_count = a["fav_count"]
                    # 点赞数列表
                    like_count = a["like_count"]
                    # 评论数
                    reply_count = a["reply_count"]
                    # 转发数
                    retweet_count = a["retweet_count"]
                    # 阅读量
                    view_count = a["view_count"]
                    # 发布时间
                    created_at = a["created_at"]
                    created_at = int(created_at)
                    created_at = time.localtime(created_at / 1000)
                    created_at = time.strftime("%Y-%m-%d", created_at)
                    data = dict(
                        read_num=view_count,
                        comment_num=reply_count,
                        share_num=retweet_count,
                        collect_num=fav_count,
                        publish_time=created_at,
                        like_num=like_count,
                        follow_num=-1
                    )
                    return data
                except Exception as e:
                    return ''
            else:
                return ''


if __name__ == '__main__':
    user = '15832192007'
    pswd = '19931103SJYA'
    a = XueQiu()
    content = '我们都有一个家<p><img src="http://jingmeiti.oss-cn-beijing.aliyuncs.com/e1bf6d973702739dd4d96b28bbbd0b1f66982a6c.jpg"></p>'
    s = a.login(user=user, pswd=pswd)
    # title = '学习'
    # label_ids = 116
    # a.publish(content=content,s=s,title=title,label_ids=label_ids)
    art_id = 'https://xueqiu.com/7155471551/120916555'
    # a.query_article_data(art_id)
