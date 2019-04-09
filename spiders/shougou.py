import json
import random

import requests
import re
import logging
import datetime
from lib.mp.base import Base
from lib.tools.custom_exception import CustomException


class SouGou(Base):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        'Accept': 'application/json'}
    mp_id = 14
    zh_name = '搜狗号'
    category_dict = {
        '教育': '教育',
        '餐饮': '美食'
    }

    @staticmethod
    def login(user, pswd, **kw):  # 普通登录
        SouGou.logger.info(user)
        session = requests.session()
        try:
            login_url = 'http://mp.sogou.com/api/login'
            data = {
                'email': user,
                'pwd': pswd
            }
            login_rep = session.post(login_url, headers=SouGou.headers, data=data)
            rep_dict = json.loads(login_rep.text)
            if not rep_dict.get('nextUrl'):
                raise CustomException('检查账号密码')
            cookies = session.cookies.get_dict()
            name_rep = session.get(
                "http://mp.sogou.com/api/if-login?status=81", headers=SouGou.headers).json()
            user_name = name_rep.get('name')
            SouGou.logger.info('login success')
            return cookies, user_name
        except Exception as e:
            SouGou.logger.error(e)
            raise CustomException(e)
        finally:
            session.close()

    def publish(self, title, content1, category, flag=1):  # 发布内容
        """
          :param title:
          :param content:
          :param category:
          :return: status, article_id, cause
          """
        cause = ''
        self.logger.info("")
        blocks = []
        content = {}
        news = re.findall(r'<[ph].*?>(.*?)</[ph].*?>', content1)
        for i in range(len(news)):
            if '<img ' in news[i]:
                news[i] = ('img', re.findall(r'src="(.*?)"', news[i])[0])
            else:
                news[i] = re.sub(r'<.*?>', '', news[i])
        post_data = {
            "id": "",
            "title": title,
            "category": self.category_dict[category],
            "content": "",
            "type": 0
        }
        key = 0
        for new in news:
            block = {
                "key": "",
                "text": "",
                "type": "unstyled",
                "depth": 0,
                "inlineStyleRanges": [],
                "entityRanges": [],
                "data": {},
            }
            if type(new) != str:
                entity = {}
                img_list = []
                block["key"] = self.v_code()
                block["text"] = " "
                block["type"] = "atomic"
                entity["offset"] = 0
                entity["length"] = 1
                entity["key"] = key
                block["entityRanges"].append(entity)
                img_list.append(new[1])
                key += 1
            else:
                block["key"] = self.v_code()
                block["text"] = new
            blocks.append(block)
        entityMap = {}
        if key != 0:
            img_dict = {
                "type": "image",
                "mutability": "IMMUTABLE",
                "data": {}
            }
            for i in range(len(img_list)):
                data = {}
                data["src"] = img_list[i]
                img_dict["data"] = data
                entityMap[i] = img_dict
        content["blocks"] = blocks
        content["entityMap"] = entityMap
        content = json.dumps(content, ensure_ascii=False)
        post_data["content"] = str(content)
        url = "http://mp.sogou.com/api/articles"
        response = self.session.post(url=url, data=post_data, headers=self.headers)
        logging.error(response.text)
        if response.text.isdigit():
            self.logger.info("successs get articleid")
            status = 2
            return status, cause
        else:
            resp = json.loads(response.text)
            cause = resp['message']['quota']
            return 3, cause

    def read_count(self,
                   stime=datetime.datetime.now() - datetime.timedelta(days=int(7)),
                   etime=datetime.datetime.now() - datetime.timedelta(days=int(1))):
        self.logger.info("")
        name_rep = self.session.get(
            "http://mp.sogou.com/api/if-login?status=81", headers=self.headers).json()
        user_name = name_rep.get('name')
        self.logger.info(name_rep)
        res = self.session.get(
            "http://mp.sogou.com/api/statistics/arti-analysis/array",
            params="startDate=%s&endDate=%s" % (stime.strftime("%Y%m%d"), etime.strftime("%Y%m%d"))).json()
        read_list = []
        for data in res:
            readcount = {
                "day_time": data["date"],
                "user_name": user_name,
                "recomment_num": data["recommendedNum"],
                "read_num": data["readingNum"],
                "comment_num": data["commentsNum"],
                "share_num": data["sharedNum"],
                "collect_num": data["collectionNum"]
            }
            # logging.error(readcount)
            read_list.append(readcount)
        return read_list

    def fetch_article_status(self, title):
        fetch_url = 'http://mp.sogou.com/api/1/articles?status='
        rep = self.session.get(fetch_url, headers=self.headers).json()

        if rep.get('list'):
            url = ''
            status = 2
            cause = '没查询到该文章'
            for content in rep['list']:
                if title == content['title']:
                    if content['statusLabel'] == '已发布':
                        status = 4
                        cause = ''
                    elif content['statusLabel'] == '审核中':
                        cause = '审核中'
                    elif content['statusLabel'] == '未通过':
                        status = 5
                        cause = content['remark']
                    url = content['url']
                    return status, cause, url
            return status, cause, url
        raise CustomException('Cookies过期')

    def upload_image(self, image_name, image_data):
        self.logger.info('')
        files = {
            'file': (image_name, image_data, 'image/jpeg')
        }
        img_rep = self.session.post(
            'http://mp.sogou.com/api/articles/temp-image',
            files=files
        )
        if 'url' in img_rep.text:
            resp_json = img_rep.json()
            img_url = resp_json.get('url')
            return img_url
        else:
            raise CustomException('上传图片失败，请检查账号密码')

    def check_user_cookies(self):
        self.logger.info('')
        resp = self.session.get(
            "http://mp.sogou.com/api/if-login?status=81")
        if resp.status_code == 200:
            return True
        else:
            return False

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        url4 = 'http://mp.sogou.com/api/1/articles?status=1'
        rep4 = self.session.get(url4, headers=self.headers).json()
        if rep4.get('list'):
            for content in rep4['list']:
                if title == content['title']:
                    data = dict(
                        read_num=content['readingNum'],
                        recomment_num=content['recommendedNum'],
                        comment_num=content['commentsNum'],
                        share_num=content['forwardingNum'],
                        collect_num=content['collectionNum'],
                        publish_time=self.time_stamp(content['updatedAt']),
                        like_num=-1,
                        follow_num=-1
                    )
                    return data
        raise CustomException('Cookies过期')

    def query_account_message(self, auto):
        return []

    def time_stamp(self, times):
        """时间戳转化为标准时间"""
        # 使用datetime
        dateArray = datetime.datetime.utcfromtimestamp(times)
        otherStyleTime = dateArray.strftime("%Y--%m--%d %H:%M:%S")
        return otherStyleTime  # 2013--10--10 15:40:00

    def v_code(self):
        """生成随机key"""
        ret = ""
        for i in range(5):
            num = random.randint(0, 9)
            letter = chr(random.randint(97, 122))  # 取小写字母
            s = str(random.choice([num, letter]))
            ret += s
        return ret


if __name__ == '__main__':
    print(SouGou.login('11879274@qq.com', '19920704'))
    sougou = SouGou()
    print(SouGou.login('11879274@qq.com', '19920704'))
