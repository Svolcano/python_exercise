import re
import time
import datetime
import requests
import execjs
import json
import rsa
import base64
import os

from lib.mp.base import Base
from lib.yundama import verify_captcha
from lib.tools.custom_exception import CustomException
from lib.tools import toutiao_login_js


class BaiJia(Base):
    mp_id = 3
    zh_name = '百家号'
    feed_cat = {'创意': '18', '美食': '22', '科学': '32', '女人': '21', '美图': '20', '辟谣': '38', '三农': '35', '游戏': '13',
                '两性': '25', '房产': '9',
                '娱乐': '4', '宠物': '31', '科技': '8', '汽车': '10', '军事': '14', '情感': '26', '生活': '16', '家居': '23',
                '教育': '11', '悦读': '37',
                '时尚': '12', '历史': '30', '职场': '34', '体育': '3', '国际': '1', '搞笑': '19', '健康': '24', '动漫': '33',
                '育儿': '28',
                '文化': '29', '财经': '6', '互联网': '7', '旅游': '15', '社会': '5'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'}

    @staticmethod
    def login(user, pswd, **kw):
        BaiJia.logger.info(user)
        session = requests.session()
        session.headers.update(BaiJia.headers)
        session.get('https://pan.baidu.com')
        gid = BaiJia._get_runntime().call('getGid')
        callback = BaiJia._get_runntime().call('getCallback')
        traceid = BaiJia._get_runntime().call('createHeadID')
        token = BaiJia.get_token(gid, callback, session)
        pubkey, key = BaiJia.get_rsa_key(token, gid, callback, session, traceid)
        pub = rsa.PublicKey.load_pkcs1_openssl_pem(pubkey.encode('utf-8'))
        encript_passwd = rsa.encrypt(pswd.encode('utf-8'), pub)
        password = base64.b64encode(encript_passwd).decode('utf-8')
        post_data = {
            "staticpage": "https://pan.baidu.com/res/static/thirdparty/pass_v3_jump.html",
            "charset": "UTF-8",
            "token": token,
            "tpl": "netdisk",
            "subpro": "netdisk_web",
            "apiver": "v3",
            "tt": int(time.time() * 1000),
            "codestring": "",
            "safeflg": "0",
            "u": "https://pan.baidu.com/disk/home",
            "isPhone": "",
            "detect": "1",
            "gid": gid,
            "quick_user": "0",
            "logintype": "basicLogin",
            "logLoginType": "pc_loginBasic",
            "idc": "",
            "loginmerge": "true",
            "foreignusername": "",
            "username": user,
            "password": password,
            "mem_pass": "on",
            "rsakey": key,
            "crypttype": "12",
            "ppui_logintime": "87162",
            "countrycode": "",
            "fp_uid": "",
            "fp_info": "",
            "loginversion": "v4",
            # "ds": "Hod9Kug32hLv7vGhxTCcWJVf/QXQYFHc8PZPH0+zODP158rYpLIoKIpgsiwjnpDmOW9UaBLEXW4X5efR6Sz7Uaq4zPr3sW4PzQYlNaMthOQ8jzhIFE73wsuCDuKkDB7Yy0zcxKXYbdPwb2QtOdt6p3vo7CID9dUWOeZezxJhdunwl7NmOFnoLWS/3I3EYOEcYt5ijPSv/ec154vXGAjR7+1gxkTP7VTxHDHHNccMRWR6y+lfhIQPEztmgZta6nuYtHZNqkYw6+wzkVX17Wm8pkLKQ1gLXBLK4gUgX4cReWEXWMR+6brnSuExcCsbiiQNiXYfjcuP3Eb81ELieJu0649Wt3sDofhLv2/efpuX+OmNnArLWYHL5S6O45L5nAwhUIayWwd797vrQtP/dufnYNezxx6tfEqA3Fmz/YiAJPRBzyiVd7GHkbIfeTmu/6dldEV+22xqtqlZFZMacR7OvhsurN0WVixqyr1jxrI9sPShMprA2z0QThgt1gySZe1BENPUom/e7FkvpacpMB0nWPCoe4G/HY6mTXw1zOkoHUfOurV6u1hPOBFJgzWkMbqWHO+bzazSQZ0XWEauKOr/jooE1JTplQlEXQEO/dx37dlsoHQO8h0Pp9CNs86noYbaQnoTS+7iFIfKMpYyz8IJ14ptmGnOx+NVEXBIfy5eN75eW2l82JUd6xhGyZ0RSIgYoIBv3/sHRhVmvlDgex6AxbRbq7muho8lk7Auj5IVnldC8nYFhogldtRuaLY34wJv25PHQNNmnVc/rbZNcrDmKtTHVvZ3LHDjIfE6TNTAiq+nOf4WaG44P8vBeWQYOV/6Jf3c1D+5cY/1f3Ubg23JWCJCSKAe9RsuXDybUeRmmNW9tEIjeKz2xVyvL9EfgX/VO/AspyTDdTr6hOp4zZ1Jruo9fEXjoW3hP5oh58FkqfAJoZiAsoGs31PeUPvXSaOpOm6ERI67VeVhXi3W9XB01xSvFiVtZk1LZh/Z2MnU7268sPARwZ9fP15CI3kYlIStnnYoSOoOjLbdMqztJKioaQGDhI4UNLMxkuueeieEoBiIpeDV2678VkvoG+ZhDEkmCFboX7yS01uILrfBc9fh9XbaF1sTOLsT2acMt34nFgoujbBkq6UW/K1tGqQNpWQHss/xb65WjgU5Cstpw1TgSsw/qetKeGlNkQt+mya+PPdr2q+lCbN9HufaeBor4cDKXXHVcFwbkibIZcrYwAW8yZ0xCZREZplCTDmBuscgf8rU3FmThstzx1vc80yGYqs+qVdzWjy9uDMuEwHPHvK6HlLhnySOgb/5TSNljcYARXk=",
            # "tk": "2006TG/w+3FOc0s137wM1+PWMcG/pf+Rcr2Z9GcdGBPugJU=",
            # "dv": "tk0.10998763779832511551159571840@mmr0hm94nxpkqGPQIGPmf-Ckq~9zf-943G9m-jOL-GpkniC4JX0kn-7rffpvxyPvfG94B~94Ow94nxpkqGPQIGPmf-C4qH76f-943G9m-jOL-Gpkny9W9y0q__vr0uv94qHCHfH9WJGCku~9m-w74D-pkux7mf-CWNR9m-w949yCmfRCRnGCk5fCkNG0knHCR3G9RuxpkBx94Bzp2oh43OrBJy0Kyh4J2wiKyYyDXIH4Z2gMKf-945ipk9X7rfX7k5X91-JBJx6J32CKyYBJyh0C2Y0Dv2RDzOeDZowxkkECku4nCODhurh9rfHpkDHGrQOvGfpWnf743~CRNRCRDx7k9HC4n-C4J-94JxC4D-7kBfhrQE6oiD69apHYfNL~jNZ2UM6JjNXYgpH-yPZoTMZTjMLB_~rs9mffpkn~7kDG74nXpknx9WqG94q~9mf-74ufpknx9WqG94qi7q__",
            "traceid": traceid,
            "callback": "parent." + callback,
        }
        resp = session.post(url='https://passport.baidu.com/v2/api/?login', data=post_data)
        ss = resp.text
        if 'err_no=0' in ss or 'err_no=23' in ss or 'err_no=400037' in ss or 'err_no=5' in ss:
            cookies = session.cookies.get_dict()
            return cookies, ''
        else:
            cookies = BaiJia.break_code(ss, session, post_data)
            session.cookies = requests.cookies.cookiejar_from_dict(cookies)
            resp = session.get('https://baijiahao.baidu.com/builder/app/appinfo').json()
            if resp['errmsg'] == 'success':
                BaiJia.logger.info('成功')
                cookies = session.cookies.get_dict()
                u_name = resp['data']['user']['username']
                BaiJia.logger.info(u_name)
                return cookies, u_name
            raise CustomException('账号或密码错误')

    @staticmethod
    def break_code(ss, session, post_data):
        flag = 5
        while flag:
            time.sleep(1)
            BaiJia.logger.info('重试{}次'.format(flag))
            callback = re.findall(r'callback=(.*?)&codeString', ss)[0]
            get_code = re.findall(r'codeString=(.*?)&userName', ss)[0]
            if not get_code:
                result = ''
            else:
                code = session.get("https://passport.baidu.com/cgi-bin/genimage", params=get_code, stream=True)
                if code.status_code == 200:
                    with open("code.png", 'wb') as f:
                        f.write(code.content)
                cid, result = verify_captcha('code.png', 5000)
            if os.path.exists('code.png'):
                os.remove('code.png')
            post_data['verifycode'] = result
            post_data['codestring'] = get_code
            post_data['callback'] = callback
            time.sleep(0.5)
            ss = session.post(url='https://passport.baidu.com/v2/api/?login', data=post_data)
            ss = ss.text
            BaiJia.logger.info(flag)
            BaiJia.logger.info(ss)
            if 'err_no=0' in ss or 'err_no=23' in ss or 'err_no=400037' in ss or 'err_no=5' in ss:
                cookies = session.cookies.get_dict()
                return cookies
            else:
                flag -= 1
        err = re.compile(r'"err_no=(.*?)&').findall(ss)[0]
        BaiJia.logger.info(err)
        if err == "120021":
            msg = '请用手机短信登录'
        elif err == "257":
            msg = '请输入验证码'
        else:
            msg = '账号密码不对'
        raise CustomException(msg)

    @staticmethod
    def get_token(gid, callback, session):
        get_data = {
            'tpl': 'netdisk',
            'subpro': 'netdisk_web',
            'apiver': 'v3',
            'tt': int(time.time() * 1000),
            'class': 'login',
            'gid': gid,
            'logintype': 'basicLogin',
            'callback': callback
        }
        session.cookies.update(
            dict(HOSUPPORT='1', expires='Sat, 15-May-2027 03:42:54 GMT; path=/', domain='passport.baidu.com; httponly'))
        resp = session.get(url='https://passport.baidu.com/v2/api/?getapi', params=get_data)
        if resp.status_code == 200 and callback in resp.text:
            data = json.loads(re.search(r'.*?\((.*)\)', resp.text).group(1).replace("'", '"'))
            return data.get('data').get('token')
        else:
            print('获取token失败')
            return None

    @staticmethod
    def get_rsa_key(token, gid, callback, session, traceid):
        get_data = {
            'token': token,
            'tpl': 'netdisk',
            'subpro': 'netdisk_web',
            'apiver': 'v3',
            'tt': int(time.time() * 1000),
            'gid': gid,
            'callback': callback,
            'loginversion': 'v4',
            'traceid': traceid
        }
        resp = session.get(url='https://passport.baidu.com/v2/getpublickey', params=get_data)
        if resp.status_code == 200 and callback in resp.text:
            data = json.loads(re.search(r'.*?\((.*)\)', resp.text).group(1).replace("'", '"'))
            return data.get('pubkey'), data.get('key')
        else:
            print('获取rsa key失败')
            return None

    @staticmethod
    def _get_runntime():
        """
        :param path: 加密js的路径,注意js中不要使用中文！估计是pyexecjs处理中文还有一些问题
        :return: 编译后的js环境，不清楚pyexecjs这个库的用法的请在github上查看相关文档
        """
        phantom = execjs.get()  # 这里必须为phantomjs设置环境变量，否则可以写phantomjs的具体路径
        source = toutiao_login_js.baidu_login_js
        return phantom.compile(source)

    def publish(self, title, content, category, flag=1):
        """
        :param title:
        :param content:
        :param category:
        :return: status, cause
        """
        try:
            status = 3
            cause = ''
            self.logger.info("account: %s title:%s " % (self.account.account, title))
            result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)  # 查找p标签
            if not result:
                cause = '请上传文章封面'
                self.logger.error(cause)
                return status, cause

            for img in result:
                con_img = img.replace("&", "&amp;")
                content = content.replace(img, con_img)
            cover = result[0]
            # 上传
            self.session.post(
                'https://baijiahao.baidu.com/builder/author/article/articleDiagnose',
                data={
                    'content': content,
                    'type': 'news'
                }, )
            self.session.post(
                'https://baijiahao.baidu.com/builder/author/article/titleRecommend',
                data={
                    'title': title,
                    'content': 'content',
                    'feed_cat': self.feed_cat[category]
                }
            )
            data = {
                'title': title,
                'content': content,
                'feed_cat': '11',
                'len': len(content),
                'original_status': '0',
                'source_reprinted_allow': '2',
                'cover_auto_images': '[{"src":"%s","width":476,"height":340,"is_suitable":true}]' % cover,
                'spd_info': '{"goods_info":[]}',
                'cover_layout': 'auto',
                'cover_images': '[]',
                '_cover_images_map': '[]',
                'type': 'news',
                'isBeautify': 'false',
                'announce_id': 0,
                'subtitle': ''
            }
            # if flag == 3:
            #     del data['cover_auto_images']
            #     data['cover_layout'] = 'three'
            #     cover_images = []
            #     for img in result[:3]:
            #         cover_images.append({"src": "{}".format(img), "cropData":
            #              {"x": 10, "y": 0, "width": 507, "height": 340}})
            #     data['cover_layout'] = cover_images
            self.session.get('https://ttl-bjh.baidu.com/cms/statistics/statistics/img/s.gif?op_time={}'
                             '&client_type=pc&app_id=1536772421402989&'
                             'page_url=https%3A%2F%2Fbaijiahao.baidu.com%2Fbuilder%2Frc%2Fedit%3Ftype%3Dnews%26'
                             'app_id%3D1536772421402989&refer=https%3A%2F%2Fbaijiahao.baidu.com%2Fbuilder%2Fauthor%2'
                             'Fregister%2Findex&urlkey=custom-%E5%8F%91%E6%96%87%E6%93%8D%E4%BD%9C-%E6%96%B0%E7%'
                             '89%88%E6%8E%A5%E5%8F%A3&bjh_param=%7B%22type%22%3A%22news%22%2C%22articleId%22%3Anull%7D'
                             .format(int(time.time() * 1000)))
            resp = self.session.post(
                'https://baijiahao.baidu.com/builder/author/article/publish',
                data=data,
            ).json()
            self.logger.info(resp)
            if resp['errno'] == 0:
                status = 2
                cause = ''
                return status, cause
            elif '频繁' in resp['errmsg']:
                return 1, ''
            else:
                cause = resp['errmsg']
                return 3, cause
        except Exception as e:
            self.logger.error('发文失败，检查账号可用性', e)
            raise CustomException('百家发文失败，检查账号：%s' % self.account.account)

    def read_count(self,
                   start_day=datetime.datetime.now() - datetime.timedelta(days=int(7)),
                   end_day=datetime.datetime.now() - datetime.timedelta(days=int(1))):
        self.logger.info("account: %s" % self.account.account)
        res = self.session.get(
            "https://baijiahao.baidu.com/builder/app/appinfo").json()
        if res['errno'] != 0:
            raise CustomException(res['errmsg'])
        username = res['data']['user']['name']
        res = self.session.post(
            "https://baijiahao.baidu.com/builder/author/statistic/appStatistic",
            data={
                "type": "news",
                "is_yesterday": "false",
                "start_day": start_day.strftime("%Y%m%d"),
                "end_day": end_day.strftime("%Y%m%d"),
                "stat": "0"}).json()
        read_list = []
        for data in res['data']['list']:
            if int(data['recommend_count']) == -1:
                continue
            readcount = {
                "day_time": time.strftime('%Y-%m-%d', time.strptime(data['event_day'], "%Y%m%d")),
                "user_name": username,
                "like_num": data.get("likes_count", 0),
                "recomment_num": data.get("recommend_count", 0),
                "read_num": data.get("view_count", 0),
                "comment_num": data.get("comment_count", 0),
                "share_num": data.get("share_count", 0),
                "collect_num": data.get("collect_count", 0)
            }
            read_list.append(readcount)
            # logging.info(readcount)
        return read_list

    def fetch_article_status(self, title):
        url = ''
        re_a = re.compile('<[a-zA-Z\/!].*?>', re.S)
        resp = self.session.get(
            'https://baijiahao.baidu.com/builder/article/lists?type=&collection=&pageSize=10&currentPage=1&search='
        ).json()
        if resp['errno'] != 0:
            raise CustomException('账号异常')
        articles = resp['data']['list']
        res = [2, '没查询到该文章', url]
        for art in articles:
            if title != art['title']:
                continue
            if art['status'] == 'rejected':
                url = art['url']
                res = 5, re_a.sub('', art['audit_msg']).replace('&nbsp;', ''), url
            elif art['status'] == 'publish':
                url = art['url']
                res = 4, '', url
        return res

    def upload_image(self, image_name, image_data):
        resp = self.session.post(
            'https://baijiahao.baidu.com/builderinner/api/content/file/upload',
            files={
                'media': (image_name, image_data, 'image/jpeg', {
                    'is_waterlog': '1', 'save_material': '1',
                    'type': 'image', "no_compress": '0',
                    'app_id': '1594805746441778',
                })}
        ).json()
        if resp['error_code'] != 0:
            raise CustomException('上传失败')
        return resp['ret']['no_waterlog_bos_url']

    def check_user_cookies(self):
        self.logger.info('')
        try:
            res = self.session.get(
                "https://baijiahao.baidu.com/builder/app/appinfo").json()
            if not res['errno']:
                return True
        except Exception as e:
            self.logger.error(e)
        return False

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        resp = self.session.get(
            'https://baijiahao.baidu.com/builder/article/lists?type=&collection=&pageSize=10&currentPage=1&search='
        ).json()
        if resp['errno'] != 0:
            raise CustomException(resp['errmsg'])
        arts = resp['data']['list']
        for art in arts:
            if title != art['title']:
                continue
            else:
                data = dict(
                    read_num=art['read_amount'],
                    recomment_num=art['rec_amount'],
                    comment_num=int(art['comment_amount']),
                    share_num=art['share_amount'],
                    like_num=int(art['like_amount']),
                    collect_num=art['collection_amount'],
                    publish_time=art['updated_at'],
                    follow_num=-1
                )
            return data
        return ''

    def query_account_message(self):
        return []


if __name__ == '__main__':
    ss = BaiJia.login('13522068263', 'JINGmeiti123')
    print(ss)
