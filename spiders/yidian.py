import requests
import re
import base64
import rsa
import binascii
import logging
import time
import os
import datetime
import json
from w3lib.html import remove_tags
from lib.mp.base import Base
from lib.yundama import verify_captcha
from lib.tools.custom_exception import CustomException


class YiDian(Base):
    mp_id = 9
    zh_name = '一点资讯'

    @staticmethod
    def login(user, pswd, **kw):
        YiDian.logger.info("")
        def_ret = {}
        session = requests.session()
        session.get('https://mp.yidianzixun.com/',
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',                    })
        wb_aiplist = [
            '17190015815', '17152140096', '17190082448',
            '17190193956', '17190175480', '17310146526'
        ]
        if user not in wb_aiplist:
            resp = session.post(
                'https://mp.yidianzixun.com/sign_in?_rk={}'.format(int(time.time()*1000)),
                data=json.dumps({
                    "username": user,
                    "password": pswd
                }),
                headers={
                    "Host": "mp.yidianzixun.com",
                    "Connection": "keep-alive",
                    "Accept": "application/json, text/plain, */*",
                    "Origin": "https://mp.yidianzixun.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
                    "Content-Type": "application/json;charset=UTF-8",
                    "Referer": "https://mp.yidianzixun.com/",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                }
            ).json()
            logging.error(resp)
            if resp['status'] == 'insecurity':
                raise CustomException('请关闭账号保护')
            if not resp['status'] == 'success':
                YiDian.logger.error("Failed to get yidian code")
                raise CustomException('请检查账号密码')
            cookies = session.cookies.get_dict()
            response = session.get(
                'https://mp.yidianzixun.com/#/Home')
            response.encoding = 'utf8'
            name_re = re.compile(r'"media_name":"(.*?)"', re.S)
            user_name = name_re.findall(response.text)
            return cookies, user_name
        else:
            key_data = session.get(
                'https://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=MTU2MDA2Mzg2MDM%3D&rsakt=mod&client=ssologin.js(v1.4.15)&_=1531898376129'
            ).text
            pat = re.compile(
                r'"servertime":(.*?),.*"nonce":"(.*?)","pubkey":"(.*?)"')
            res = pat.findall(key_data)
            if not res:
                YiDian.logger.error("Failed to get key data")
                return def_ret
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
                "pagerefer": "",
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
                data=data,
            ).json()
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
                with open('yd_code.png', 'wb') as f:
                    f.write(img_code.content)
                data['su'] = name
                data['servertime'] = servertime
                data['nonce'] = nonce
                cid, result = verify_captcha('yd_code.png', 1005)
                if result == '看不清':
                    cid, result = verify_captcha('yd_code.png', 1005)
                data['door'] = result
                response = session.post(
                    'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_=1531898376166',
                    data=data).json()
                if not response['uid']:
                    YiDian.logger.error("Failed to get uid")
                    return def_ret, ''
                os.remove(os.path.abspath('yd_code.png'))
            if not session.get(response['crossDomainUrlList'][0]):
                YiDian.logger.error("failed to cross DomainUrlList")
                return def_ret, ''
            cc = session.cookies.get_dict()
            response = session.get(
                'https://mp.yidianzixun.com/#/Home', cookies=cc)
            response.encoding = 'utf8'
            name_re = re.compile(r'"media_name":"(.*?)"', re.S)
            user_name = name_re.findall(response.text)
            if not user_name:
                raise CustomException('登陆失败')
            cookies = session.cookies.get_dict()
            return cookies

    def publish(self, title, content, category, flag=1):
        """
          :param title:
          :param content:
          :param category:
          :return: status, article_id, cause
        """
        status = 3
        cause = ''
        data = {
            "id": "",
            "title": title,
            "cate": category,
            "cateB": "", "coverType": "default", "covers": [],
            "content": content,
            "hasSubTitle": 0, "subTitle": "", "hasSubCovers": 0,
            "subCovers": [], "subCoverType": "default",
            "original": 0, "reward": 0, "videos": [], "audios": [],
            "votes": {
                "vote_id": "", "vote_options": [],
                "vote_end_time": "", "vote_title": "", "vote_type": 1,
                "isAdded": "false"},
            "images": [], "goods": [], "is_mobile": 0, "status": 0,
            "import_url": "", "tags": [], "isPubed": "false",
            "lastSaveTime": datetime.datetime.now().strftime('%H:%M:%S'),
            "dirty": "false", "editorType": "articleEditor"
        }
        cover_list = []
        if flag == 3:
            result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)  # 查找p标签
            if not result:
                cause = '请上传文章封面'
                self.logger.error(cause)
                return status, cause
            for item in result[:3]:
                source = {"url": "{}".format(item), "source": ""}
                cover_list.append(source)
            data['covers'] = cover_list
            data['coverType'] = 'three'
        resp = self.session.post(
            'https://mp.yidianzixun.com/model/Article?',
            data=json.dumps(data),
            headers={
                'Content-Type': 'application/json',
            }).text
        if "检索类型参数错误" in resp:
            cause = '获取文章id失败'
            self.logger.error(cause)
            raise CustomException('请检查账号密码')
        html = json.loads(resp)
        fw_id = html['id']
        req = self.session.get(
            'https://mp.yidianzixun.com/api/post/publish?post_id=%s' % fw_id
        ).json()
        logging.error(req)
        if req['status'] == 'success':
            status = 2
            return status, cause
        else:
            raise CustomException('发文失败')

    def read_count(self,
                   sd=datetime.datetime.now() - datetime.timedelta(days=7),
                   ed=datetime.datetime.now() - datetime.timedelta(days=1)
                   ):
        self.logger.info("")
        def_ret = []
        response = self.session.get(
            'https://mp.yidianzixun.com/#/Home')
        response.encoding = 'utf8'
        name_re = re.compile(r'"media_name":"(.*?)"', re.S)
        user_name = name_re.findall(response.text)
        if not user_name:
            raise CustomException('重新登陆')
        user_name = user_name[0]
        resp = self.session.get(
            "http://mp.yidianzixun.com/api/source-data",
            params="date=%s&retdays=%s&_rk=dfb3e71523797641095" % (
                sd.strftime("%Y-%m-%d"), (ed - sd).days)
        ).json()
        datas = resp.get('result', {})or {}
        read_list = []
        for dt, data in datas.items():
            data = dict(
                user_name=user_name, day_time=dt,
                recomment_num=data['viewDoc'],  # 推荐
                read_num=data['clickDoc'],  # 阅读
                share_num=data['shareDoc'],  # 分享
                collect_num=data['likeDoc'])  # 收藏
            # logging.error(data)
            read_list.append(data)
        return read_list

    def fetch_article_status(self, title):
        self.logger.info("")
        resp = self.session.get(
            'https://mp.yidianzixun.com/model/Article?_rk=1532680633534&page=1&page_size=10&status=0,1,2,3,4,5,6,7,9,14&has_data=1&type=original&from_time=&to_time=&date=201807&title='
        ).json()['posts']
        res = [2, '没查询到该文章', '']
        for art in resp:
            if title != art['title']:
                continue
            if art['status'] == 2:
                art_id = art['newsId']
                url = 'https://www.yidianzixun.com/article/{}'.format(art_id)
                res = 4, '', url
            elif art['status'] == 3:
                res = 5, art['comment'], ''
        return res

    def upload_image(self, image_name, image_data):
        resp = self.session.post(
            'https://mp.yidianzixun.com/upload?action=uploadimage',
            files={'upfile': (image_name, image_data, 'image/jpeg', {
                'id': 'WU_FILE_0', 'name': image_name, 'type': 'image/jpeg',
                "lastModifiedDate": 'Tue Jun 12 2018 19:22:30 GMT+0800 (中国标准时间)',
                'size': '',
            })}).json()
        if resp['status'] == 'success':
            return resp['url']
        self.logger.error("Failed to get image")
        return None

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        resp = self.session.get(
            'https://mp.yidianzixun.com/model/Article?_rk=1541989635561&page=1&page_size=10&status=2,6,7&has_data=1&type=original&from_time=&to_time=&date=201811&title='
        ).json()['posts']
        for art in resp:
            if title != art['title']:
                continue
            else:
                times = int(art['updatedTime'] / 1000)
                time_local = time.localtime(times)
                dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                data = dict(
                    read_num=art['all_data']['clickDoc'],
                    recomment_num=art['all_data']['viewDoc'],
                    comment_num=art['all_data']['addCommentDoc'],
                    share_num=art['all_data']['shareDoc'],
                    like_num=art['all_data']['likeDoc'],
                    publish_time=dt,
                    follow_num=-1,
                    collect_num=-1
                )
                return data
        return ''

    def query_account_message(self, auto):
        resp = self.session.get(
            'https://mp.yidianzixun.com/model/Message?types=2&page=1&page_size=20&_rk=1542011347115'
        ).json()
        msg = []
        if auto:
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            yesterday = datetime.datetime.now().date()
        for item in resp['result']['message']:
            times = int(item['created_time'] / 1000)
            time_local = time.localtime(times)
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            if yesterday not in dt:
                continue
            s = re.sub(r'<a.*?>', "《", item['summary'], count=0)
            message = remove_tags(s.replace('</a>', '》'))
            data = dict(
                message=message,
                day_time=dt
            )
            msg.append(data)
        return msg

    def check_user_cookies(self):
        self.logger.info("")
        response = self.session.get(
            'https://mp.yidianzixun.com/#/Home')
        response.encoding = 'utf8'
        name_re = re.compile(r'"media_name":"(.*?)"', re.S)
        user_name = name_re.findall(response.text)
        if user_name:
            return True
        return False

if __name__ == '__main__':
    from control.db.api.account_api import DBAccountApi
    from lib.tools.log_mgr import Flogger
    Flogger()
    db_account_api = DBAccountApi()
    account = db_account_api.query(uid=9, mp_id=9, account='17310135047')[0]
    # bj = YiDian(account)
    # title = 'GES 2018大会落幕，释放未来教育六大风向'
    # content = '"<p><img src="http://si1.go2yd.com/get-image/0SfEd6drpTc" data-format=\"JPEG\" title=\"\"></p><p><img src="http://si1.go2yd.com/get-image/0SfEd6dhioS" data-format=\"JPEG\" title=\"\"></p><p data-name=\"active-node\"><img src="http://si1.go2yd.com/get-image/0SfEd7nivpo" data-format=\"JPEG\" title=\"\">鲸媒体讯（文/浪子）昨日，GES 2018未来教育大会落下帷幕，三天时间、20余场主旨演讲、圆桌论坛、主题对话，800多位来自全球学术界、政界、商界的精英汇聚一堂，共同探索新<a title=\"浏览关于“趋势”的文章\" style=\"background-color: rgb(255, 255, 255);\">趋势</a>，预见新未来。在思想交锋的同时，也释放出未来教育的六大风向。</p><p><img id=\"\" src=\"http://si1.go2yd.com/get-image/0SfEfakfLRA\"></p><h3></h3><h3><strong><b>风向一|</b></strong><strong><b>教育</b></strong><strong><b>公平</b></strong><strong><b>：多方关注</b></strong><strong><b>，</b></strong><strong><b>多管齐下</b></strong><strong><b> </b></strong></h3><p><a title=\"浏览关于“教育公平”的文章\">教育公平</a>牵系着千家万户的希望，在扶贫攻坚的关键时期显得尤为重要，也是此次GES大会的最强音。在本次大会上，来自政府、学校、课外机构和公益机构的各界人士都在呼吁教育的普惠公平，探讨如何让更多孩子享受公平有质量的教育，降低教育的水位差，阻断贫困的代际传递。</p><p>除了宏观层面的呼吁和情怀上的感召，参会嘉宾们针对教育公平存在的具体问题进行了深入讨论。根据各方调研情况来看，贫困地区的硬件差距已经明显缩小，软件设施也有明显改善，某种程度上实现了均衡发展。但是教育的关键因素——教师问题仍然突出：一方面表现在教师专业水平需要提高，另一方面是师资队伍亟待优化，要想办法让那些优秀的师范毕业生留下来。</p><p>比起数理化教师，在很多西部地区，音体美教师更为匮乏。有参会人士表示，培养孩子的审美观、想象力以及健康的体魄非常重要，教育中很多东西还没有被认识到，无论是企业还是公益组织可以专注在一些紧迫的领域进行深入探索。</p><p>相比其他教育形态，学前教育不均衡更为突出，尤其是少数民族地区，幼教师资的缺口非常大，也缺乏系统性的课程。作为人生教育的起点，学前教育所起的作用事半功倍，加大普惠性幼儿园建设、吸引更多幼儿教师迫在眉睫。</p><p>科技的进步为解决促进教育公平带来了想象空间。有参会者提出搭建线上线下平台来培养贫困地区教师，同时打造互通共享的教育资源为老师赋能。在一些地区已经有了很好的实践。不少政府机关和民办教育机构通过联手打造教育云、大数据平台、双师课堂等方式，不断扩大优质教育资源的共享范围，惠及更多孩子。当然，教育公平的鸿沟填补仍需时间。</p><div class=\"post-end\"></div>'
    # category = '教育'
    # flag = 3
    # print(bj.publish(title, content, category, flag))