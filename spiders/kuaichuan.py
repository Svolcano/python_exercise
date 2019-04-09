# 快传号

import requests
import random
import hashlib
import json
import re
import time
import datetime
import urllib3
from urllib import parse
from lib.yundama import verify_captcha
from lib.mp.base import Base
from requests.cookies import cookiejar_from_dict
from requests_toolbelt import MultipartEncoder

# urllib3.disable_warnings()

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/601.1.10 (KHTML, like Gecko) Version/8.0.5 Safari/601.1.10",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; ; NCT50_AAP285C84A1328) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
]

UA = random.choice(_USER_AGENTS)

LOGIN_URL = 'https://login.360.cn/'


class KuaiChuan(Base):
    realm_list = {'互联网': '4', '人才': '7', '体育': '8', '健康': '9', '健身': '11', '军事': '12', '历史': '14', '收藏': '15',
                  '国内': '16',
                  '国际': '17', '天气': '18', '娱乐': '20', '家居': '23', '房产': '27', '摄影': '28', '教育': '29', '数码': '30',
                  '旅游': '31',
                  '时尚': '32', '星座': '33', '母婴': '36', '汽车': '37', '游戏': '38', '社会': '40', '科技': '41', '美食': '44',
                  '艺术': '45',
                  '财经': '48', '心理': '50', '创意': '52', '其他': '54', '动漫': '65', '动物': '66', '搞笑': '67', '故事': '69',
                  '文化': '70',
                  '彩票': '71', '百科': '72', '电影': '73', '法律': '74', '户外': '77', '鸡汤': '78', '命理': '80', '情感': '81',
                  '三农': '82',
                  '文学': '83', '音乐': '84', '职场': '85', '宗教': '86', '美文': '87'}
    mp_id = 12
    zh_name = '快传号'

    @staticmethod
    def login(user, pswd, **kw):
        session = requests.session()
        session.headers.update({'User-Agent': UA})
        token = KuaiChuan.get_token(session, user)
        passwd = KuaiChuan.get_md5(pswd)
        login_param = {
            "src": "pcw_so",
            "from": "pcw_so",
            "charset": "UTF-8",
            "requestScema": "https",
            "quc_sdk_version": "6.7.0",
            "quc_sdk_name": "jssdk",
            "o": "sso",
            "m": "login",
            "lm": "0",
            "captFlag": "1",
            "rtype": "data",
            "validatelm": "0",
            "isKeepAlive": "1",
            "captchaApp": "i360",
            "userName": user,
            "smDeviceId": "",
            "type": "normal",
            "account": user,
            "password": passwd,
            "captcha": "",
            "token": token,
            "proxy": "http://kuaichuan.360.cn/psp_jump.html",
            "callback": "QiUserJsonp143798668",
            "func": "QiUserJsonp143798668",
        }
        login_resp = session.post(LOGIN_URL, data=login_param, verify=False, timeout=30)
        login_resp_text = login_resp.text
        print(login_resp_text)
        error_no = KuaiChuan.get_login_errno(login_resp_text)
        error_msg = KuaiChuan.get_login_errmsg(login_resp_text)
        if error_no == 0:
            print('success', login_resp_text)
            home_url = KuaiChuan.get_home_url(login_resp_text)
            session.get(home_url)
            name = KuaiChuan.get_mp_user_name(session)
            return session.cookies.get_dict(), name
        retry = 3
        while retry:
            captcha = KuaiChuan.get_capture(session)
            if not captcha:
                print("failed to get captcha")
                return {}, ''
            print(captcha)
            login_param['captcha'] = captcha
            login_resp = session.post(LOGIN_URL, data=login_param, verify=False, timeout=30)
            login_resp_text = login_resp.text
            error_no = KuaiChuan.get_login_errno(login_resp_text)
            error_msg = KuaiChuan.get_login_errmsg(login_resp_text)
            if error_no == 78000:
                retry -= 1
                continue
            elif error_no == 0:
                home_url = KuaiChuan.get_home_url(login_resp_text)
                session.get(home_url, timeout=30)
                name = KuaiChuan.get_mp_user_name(session)
                return session.cookies.get_dict(), name
            else:
                return {}, ''

    @staticmethod
    def get_md5(pwd):
        md5 = hashlib.md5()
        b_pwd = pwd.encode('utf-8')
        md5.update(b_pwd)
        a = md5.hexdigest()
        print(a)
        return a

    @staticmethod
    def get_timestamp():
        return int(time.time() * 1000)

    @staticmethod
    def get_jquery_fun(t):
        return f'jQuery19108193473241252336_{t}'

    @staticmethod
    def get_token(s, user):
        t = KuaiChuan.get_timestamp()
        url = (f'https://login.360.cn/?func={KuaiChuan.get_jquery_fun(t)}'
               f'&src=pcw_so&from=pcw_so&charset=UTF-8&requestScema=https'
               f'&quc_sdk_version=6.7.0&quc_sdk_name=jssdk'
               f'&o=sso&m=getToken&userName={user}&_={t}')
        resp = s.get(url, verify=False)
        resp_text = resp.text
        found = re.search('jQuery\d+_\d+\((.*)\)', resp_text)
        if found:
            ans_str = found.group(1)
            ans_obj = json.loads(ans_str)
            return ans_obj['token']
        return ''

    @staticmethod
    def get_jquery_result(t):
        found = re.search('jQuery.*?\((.*)\)', t)
        if found:
            ans_str = found.group(1)
            ans_obj = json.loads(ans_str)
            return ans_obj
        return None

    @staticmethod
    def get_capture(session):
        t = KuaiChuan.get_timestamp()
        capture_url = (f'http://i.360.cn/QuCapt/getQuCaptUrl?callback={KuaiChuan.get_jquery_fun(t)}'
                       f'&src=pcw_so&from=pcw_so&charset=UTF-8&requestScema=http&quc_sdk_version=6.7.0'
                       f'&quc_sdk_name=jssdk&captchaScene=login&captchaApp=i360&border=none&_={t}')

        resp = session.get(capture_url, timeout=30)
        resp_text = resp.text
        ans_obj = KuaiChuan.get_jquery_result(resp_text)
        if ans_obj:
            capture_pic_url = ans_obj['captchaUrl']
            pic_resp = session.get(capture_pic_url, verify=False)
            image_bin = pic_resp.content
            with open("kuaichuan.png", 'wb') as wh:
                wh.write(image_bin)
            cid, capture = verify_captcha('kuaichuan.png', 1005)
            return capture
        return 0, ''

    @staticmethod
    def get_login_errno(text):
        errno_re = r'&errno=(\d+?)&'
        found = re.search(errno_re, text)
        if found:
            return int(found.group(1))
        print("failed to get login errno ")
        return -1

    @staticmethod
    def get_login_errmsg(text):
        errno_re = r'&errmsg=(.*?)&'
        found = re.search(errno_re, text)
        if found:
            return parse.unquote(found.group(1))
        print("failed to get login errmsg ")
        return ''

    @staticmethod
    def get_home_url(t):
        rp = re.compile('location.href=\'(.*?)\';')
        found = rp.search(t)
        if found:
            home_url = found.groups()[0]
            return home_url
        return ''

    @staticmethod
    def get_mp_user_name(session):
        session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'http://kuaichuan.360.cn/'
        })
        resp = session.get('http://kuaichuan.360.cn/user/detail', timeout=30)
        print(resp.json())
        if resp:
            resp_json = resp.json()
            name = resp_json['data']['user_info']['name']
            return name
        return ''

    def check_user_cookies(self):
        try:
            name = KuaiChuan.get_mp_user_name(self.session)
            print(name)
            return True
        except Exception as e:
            print(e)
            return False

    def publish(self, title, content, category, flag=1):
        status = 3
        cause = ''
        result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)  # 查找p标签
        if not result:
            cause = '请上传文章封面'
            return status, cause
        self.session.headers.update({
            'Referer': 'http://kuaichuan.360.cn/',
        })
        get_token = self.session.get('http://kuaichuan.360.cn/token/gettoken', timeout=30).json()
        print(get_token)
        token = get_token['data']
        files = {
            "exclusive": "0",
            "status_fixed_time": "0",
            "fixed_time": "0",
            "is_promot": "0",
            "title": title,
            "realm": self.realm_list[category],
            "content": content,
            "image_list[]": "",
            "token": token
        }
        if flag == 3:
            del files['image_list[]']
            result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)  # 查找p标签
            print(result)
            if not result:
                cause = '请上传文章封面'
                return status, cause
            files.update({
                "image_list[0]": result[0],
                "image_list[1]": result[1],
                "image_list[2]": result[2],
                "image_style": '3',
            })
        else:
            files['image_style'] = '0'
        m = MultipartEncoder(fields=files)
        self.session.headers.update({'Accept': 'application/json, text/plain, */*',
                                     'Origin': 'http://kuaichuan.360.cn',
                                     'Content-Type': m.content_type
                                     })
        publish_url = 'http://kuaichuan.360.cn/articleManage/publish'
        resp = self.session.post(publish_url, data=m, timeout=30)
        resp_json = resp.json()
        print(resp_json)
        if resp_json['errno'] == 0:
            status = 2
            return status, cause
        else:
            cause = resp_json['errmsg']
            return status, cause

    def upload_image(self, image_name, image_data):
        resp = self.session.post(
            'http://kuaichuan.360.cn/upload/img?source=post',
            files={
                'img': (image_name, image_data, 'image/jpeg', {
                    'Content-Type': 'image/jpeg'
                })}, timeout=30
        ).json()
        if resp['errno'] == 0:
            url = resp['data']['url']
            return url
        else:
            raise Exception('上传图片失败')

    def fetch_article_status(self, title):
        resp = self.session.get('http://kuaichuan.360.cn/content/contentList?page=1', timeout=30)
        resp_json = resp.json()
        print(resp_json)
        data_list = resp_json['data']['list']
        res = [2, '没查询到该文章', '']
        for art in data_list:
            if title != art['title']:
                continue
            elif art['status'] == "3":
                res = 5, art['op_reason'], ''
            elif art['status'] == "2":
                res = 4, '', art['url']
        return res

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        resp = self.session.get('http://kuaichuan.360.cn/content/contentList?page=1&status=2', timeout=30)
        resp_json = resp.json()
        print(resp_json)
        data_list = resp_json['data']['list']
        for art in data_list:
            if title != art['title']:
                continue
            else:
                data = dict(
                    read_num=art['read_num'],
                    recomment_num=art['rec_num'],
                    publish_time=art['publish_time'],
                    comment_num=art['comment_num'],
                    share_num=art['fav_num'],
                    like_num=-1,
                    collect_num=-1,
                    follow_num=-1
                )
                return data
        return ''

    def read_count(self,
                   sd=datetime.datetime.now() - datetime.timedelta(days=7),
                   ed=datetime.datetime.now() - datetime.timedelta(days=1)
                   ):
        user_name = self.get_mp_user_name(self.session)
        resp = self.session.get('http://kuaichuan.360.cn/stat/user?start_time={}&end_time={}&pagesize=7'.format(
            sd.strftime('%Y-%m-%d'), ed.strftime('%Y-%m-%d')), timeout=30)
        resp_json = resp.json()
        if resp_json['errno'] != 0:
                return []
        read_list = []

        for item in resp_json['data']['list']:
            read_list.append(dict(
                user_name=user_name,
                day_time=item['display_date'],
                recomment_num=item['rec_num'],
                read_num=item['read_num'],
            ))
        return read_list


if __name__ == '__main__':
    user = '13633602987'
    pswd = 'yu19920704'
    # s, name = KuaiChuan.login(user, pswd)
    kc = KuaiChuan()
    # with open(r'C:\Users\qiao\Desktop\8633866_210108284151_2.jpg', 'rb') as f:
    #     image_data = f.read()
    # print(image_data)
    title = '核桃编程获1.2亿元人民币A+轮融资，高瓴领投'
    content = '<p>鲸媒体讯（文/浪子）少儿编程项目“核桃编程”近日公布已于数月前完成1.2亿元人民币A+轮融资，此轮融资由高瓴资本领投，老股东XVC、源码资本跟投。据悉，此项目A系列轮融资总额已超过2亿元。</p><p>核桃编程创始人曾鹏轩表示，核桃编程已经跑通数据驱动的半自适应化在线学习产品。未来将持续对技术和内容进行投入，从数据驱动的半自适应走向AI驱动的全自适应。</p><p>核桃编程创立于2017年7月，目前单月营收超1500万，总付费学员数十万人。核桃编程团队目前全职人员已超过300人，其中为提升教学效果设立的产品和内容研发岗位占比近50%。</p><p>据了解，核桃编程的课程体系，结合了《CSTA（Computer Science Teachers Association）美国计算机科学教育标准》与教育部2017年颁发的《普通高中信息技术课程标准》，创设十级编程学习评估标准。教学过程中，采用情境化教学模式，并结合了ARCS教学设计模型。核桃编程的课程把编程知识点融合进一系列动画剧情中，把知识点构建成一道道关卡，学生们需要借助课堂所学的内容，来推动故事的发展，帮助主人公成长。同时学员自己也在情境化的课堂中应用编程知识，在解决问题中学会编程。</p><p><img src="http://p2.qhimg.com/t01249f11863e9f3ad5.png?size=1272x718" alt="" width="1272" height="718" srcset="http://www.jingmeiti.com/wp-content/uploads/2019/02/2019021810395072.png 1272w, http://www.jingmeiti.com/wp-content/uploads/2019/02/2019021810395072-300x169.png 300w, http://www.jingmeiti.com/wp-content/uploads/2019/02/2019021810395072-768x434.png 768w, http://www.jingmeiti.com/wp-content/uploads/2019/02/2019021810395072-1024x578.png 1024w" sizes="(max-width: 1272px) 100vw, 1272px" data-ident="08336359424252926" data-replaced="true" data-uploading="false" data-failed="false"></p><p>此外，核桃编程还采用了“人机双师”学习系统，通过人机互动学习过程对每个孩子的学习情况进行数据采集分析，通过自适应练习系统和导师辅导实现大规模的个性化教学，旨在让学生配合项目制与剧情化交互体验的新型课程模式的同时，兼顾兴趣和效率。<img src="http://p2.qhimg.com/t0159260a2ae4d38179.jpg?size=1120x450" data-replaced="true"><img src="http://p8.qhimg.com/t01733bf24660596716.jpg?size=900x500" data-replaced="true"><br></p>'
    category = '教育'
    kc.publish(title, content, category, flag=3)

    # print(s)
