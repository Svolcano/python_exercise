import logging
import requests
import time
import datetime
import urllib3
import re
import random
import img_setting
import difflib
from urllib import parse
from lib.mp.base import Base
from lib.zhima_proxy import Proxy
from lib.tools.custom_exception import CustomException

urllib3.disable_warnings()


class DaYu(Base):
    mp_id = 1
    zh_name = "大鱼号"

    @staticmethod
    def login(user, pswd, **kw):
        proxies = Proxy.proxy()
        print(proxies)
        session = requests.session()
        try:
            resp = session.post(
                'https://api.open.uc.cn/cas/custom/login/commit?custom_login_type=common',
                data={
                    "client_id": "328",
                    "redirect_uri": "https://mp.dayu.com/login/callback",
                    "display": "mobile", "change_uid": "1",
                    "transmission_mode": "pm", "": "登录",
                    "login_name_new": "", "has_captcha": "false", "sig": "",
                    "session_id": "", "token": "", "key": "",
                    "nc_appkey": "CF_APP_uc_login_h5", "origin": "*",
                    "login_name": user, "password": pswd,
                    "captcha_val": "", "captcha_id": ""},
                headers={
                    "user-agent": "Mozilla/5.0 (iPhone 84; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.0 MQQBrowser/7.8.0 Mobile/14G60 Safari/8536.25 MttCustomUA/2 QBWebViewType/1 WKType/1"},
                proxies=proxies, verify=False, timeout=5
            ).json()
            if resp['status'] != 20000:
                DaYu.logger.error("Faield to login dayu")
                raise CustomException('登陆失败')
            # 请求js获取登陆页面
            session.headers.update(
                {"Connection": "close"})
            res = session.get(
                'https://mp.dayu.com/login-url?redirect_url=%2Fmobile%2Fdashboard%2Findex%3Fuc_biz_str%3DS%3Acustom%257CC%3Aweb_default%257CK%3Atrue&st={}&display=mobile&_=0.8983112526997874 '.format(
                    resp['data'],
                    headers={
                        'Referer': 'https://mp.dayu.com/mobile/index?uc_biz_str=S:custom%7CC:web_default%7CK:true',
                        "user-agent": "Mozilla/5.0 (iPhone 84; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.0 MQQBrowser/7.8.0 Mobile/14G60 Safari/8536.25 MttCustomUA/2 QBWebViewType/1 WKType/1"
                    }, proxies=proxies, verify=False)
            ).json()
            logging.info(res)
            home_url = res['data']['redirectUrl']
            session.get(home_url)
            cookies = session.cookies.get_dict()
            home = session.get('https://mp.dayu.com/dashboard/index').text
            us_re = re.compile(r'"weMediaName":"(.*?)",', re.S)
            user_name = us_re.findall(home)
            return cookies, user_name[0]
        finally:
            session.close()

    def publish(self, title, content, category, flag=1):
        """
          :param title:
          :param content:
          :param category:
          :return: status(0 default, 1 success), article_id(), cause
        """
        status = 3
        resp = self.session.get('https://mp.dayu.com/dashboard/index').text
        u_re = re.compile(r'"utoken":"(.*?)"', re.S)
        utoken = u_re.findall(resp)[0]
        if not utoken:
            cause = "Failed to get token"
            self.logger.error(cause)
            return status, cause
        # 账号的uid
        w_re = re.compile(r'"wmid":"(.*?)",', re.S)
        wmid = w_re.findall(resp)[0]
        logging.info(wmid)
        if not wmid:
            cause = "Failed to get wmid"
            return status, cause
        # sign
        s_re = re.compile(r'"nsImgCutSign":"(.*?)",', re.S)
        sign = s_re.findall(resp)[0]
        if not sign:
            cause = "Failed to get sign"
            return status, cause
        # 账号的名字
        n_re = re.compile(r'"weMediaName":"(.*?)",', re.S)
        wmname = n_re.findall(resp)[0]
        if not wmname:
            cause = "Failed to get wmname"
            return status, cause
        result = re.compile(r'<img.*?src="(.*?)".*?>', re.S).findall(content)
        if not result:
            cause = "请上传文章封面"
            return status, cause

        img_url = result[0]
        cont_img = content
        # 图片封面
        img_post = 'https://ns.dayu.com/article/imagecut?appid=website&wmid={}&sign={}'.format(wmid, sign)
        cover_data = {
            "cutX": "0",
            "cutY": "44",
            "imgSrc": img_url,
            "oriHeight": "252",
            "oriWidth": "447",
            "saveHeight": "252",
            "saveWidth": "447",
            "utoken": utoken, }
        cover_resp = self.session.post(img_post, data=cover_data).json()
        # 图片的url
        cover_img = cover_resp['data']['url']
        ret = self.fitter_con(cont_img, utoken, title)
        if not ret:
            cause = "failed to fitter_con"
            raise CustomException(cause)
        sav_data = {
            "aoyun": "false",
            "article_activity_id": "",
            "article_activity_title": "",
            "article_id": "",
            "article_type": "1",
            "assistantStat[contentDiversionsCount]": "0",
            "assistantStat[contentTyposCount]": "0",
            "assistantStat[contentUpdateEndAt]": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            "assistantStat[contentUpdateStartAt]": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            "assistantStat[imageDiversionItemsCount]": "0",
            "assistantStat[previousTitle]": title,
            "assistantStat[textDiversionItemsCount]": "0",
            "assistantStat[titleTyposCount]": "0",
            "assistantStat[titleUpdateStartAt]": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            "assistantStat[titleWarningCount]": "0",
            "assistantStat[totalContentDiversionsCount]": "0",
            "assistantStat[totalContentTyposCount]": "0",
            "assistantStat[totalCorrectContentTypoCount]": "0",
            "assistantStat[totalImageDiversionItemsCount]": "0",
            "assistantStat[totalTextDiversionItemsCount]": "0",
            "assistantStat[totalTitleTyposCount]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleTypoTypeCounts][]": "0",
            "assistantStat[totalTitleWarningCount]": "0",
            "author": "",
            "content": cont_img,
            "coverImg": cover_img,
            "covers[0][url]": "",
            "covers[1][url]": "",
            "covers[2][url]": "",
            "curDaySubmit": "false",
            "defaultAuthor": "false",
            "draft_id": "",
            "is_exclusive": "false",
            "is_original": "0",
            "is_show_ad": "false",
            "is_timed_release": "false",
            "isCloseAdManual": "false",
            "isPaste": "1",
            "keyword": "",
            "open_award": "0",
            "open_reproduce": "0",
            "origin_cover_img": "ec9797da2698f77f74ac1aaea605f0fb",
            "second_title": "",
            "simpleMode": "true",
            "source": "1",
            "time_for_release": int(time.time() * 1000),
            "title": title,
            "use_multi_cover": "false",
            "use_second_title": "false",
            "useTime": "85057",
            "utoken": utoken,
            "weixin_promote": "false",
        }
        if flag == 3:
            u_list = []
            for item in result[:3]:
                cover_data['imgSrc'] = item
                cover_resp = self.session.post(img_post, data=cover_data).json()
                # 图片的url
                cover_img = cover_resp['data']['url']
                u_list.append(cover_img)
            c1, c2, c3 = u_list
            sav_data['covers[0][url]'] = c1
            sav_data['covers[0][srcUrl]'] = c1
            sav_data['covers[0][from]'] = 'fallback_replaced'
            sav_data['covers[0][origin_img]'] = c1.split('/')[-1]
            sav_data['covers[1][url]'] = c2
            sav_data['covers[1][srcUrl]'] = c2
            sav_data['covers[1][from]'] = 'fallback'
            sav_data['covers[1][origin_img]'] = c2.split('/')[-1]
            sav_data['covers[2][url]'] = c3
            sav_data['covers[2][srcUrl]'] = c3
            sav_data['covers[2][from]'] = 'fallback'
            sav_data['covers[2][origin_img]'] = c3.split('/')[-1]
        da_id = self.save_con(sav_data)
        if not da_id:
            raise CustomException('发文失败')
        self.check_aricle(da_id, utoken, title)
        ret = self.submit_article(da_id, utoken)
        if not ret:
            raise CustomException('发文失败')
        status = 2
        cause = ''
        return status, cause

    def get_img(self):
        return random.choice(img_setting.dayu_img)

    def fitter_con(self, cont_img, utoken, title):
        try:
            data = {
                "author": '',
                "content": cont_img,
                "title": title,
                "utoken": utoken,
            }
            resp = self.session.post(
                'https://mp.dayu.com/filterContent',
                data=data,
                headers={
                    "Host": "mp.dayu.com",
                    "Connection": "keep-alive",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "utoken": utoken,
                    "Origin": "https://mp.dayu.com",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                }
            ).json()
            if resp['result'] == 0:
                return True
        except Exception as e:
            self.logger.error(e)
        return False

    def save_con(self, sav_data):
        da_id = None
        try:
            resp = self.session.post(
                'https://mp.dayu.com/dashboard/save-draft',
                data=sav_data,
                headers={
                    "Host": "mp.dayu.com",
                    "Connection": "keep-alive",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "utoken": sav_data['utoken'],
                    "Origin": "https://mp.dayu.com",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                }
            ).json()
            da_id = resp['data']['_id']
            return da_id
        except Exception as e:
            self.logger.error(e)
        return da_id

    def check_aricle(self, da_id, utoken, title):
        resp = self.session.post(
            'https://mp.dayu.com/checkArticle',
            data={
                "dataList[0][_id]": da_id,
                "dataList[0][isDraft]": "1",
                "dataList[0][title]": title,
                "utoken": utoken,
            },
            headers={
                "Host": "mp.dayu.com",
                "Connection": "keep-alive",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "utoken": utoken,
                "Origin": "https://mp.dayu.com",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept-Language": "zh-CN,zh;q=0.9", }
        ).json()

    def submit_article(self, da_id, utoken):
        resp = self.session.post(
            'https://mp.dayu.com/dashboard/submit-article',
            data={
                "dataList[0][_id]": da_id,
                "dataList[0][isDraft]": "1",
                "dataList[0][reproduce]": "",
                "curDaySubmit": "false",
                "utoken": utoken,
            },
            headers={
                "Host": "mp.dayu.com",
                "Connection": "keep-alive",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "utoken": utoken,
                "Origin": "https://mp.dayu.com",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept-Language": "zh-CN,zh;q=0.9",
            }
        ).json()
        try:
            if resp['data']['_id']:
                return True
        except:
            raise CustomException('提交失败，检查文章内容')
        else:
            self.logger.error(resp)
            return False

    def read_count(self,
                   start_day=datetime.datetime.now() - datetime.timedelta(days=7),
                   end_day=datetime.datetime.now() - datetime.timedelta(days=1)):
        home = self.session.get('https://mp.dayu.com/dashboard/index').text
        us_re = re.compile(r'"weMediaName":"(.*?)",', re.S)
        user_name = us_re.findall(home)
        if not user_name:
            self.logger.error('获取用户名失败，检查cookie')
            raise CustomException('检查账号密码')
        user_name = user_name[0]
        read_resp = self.session.get(
            'https://mp.dayu.com/api/stat/article/all/daylist',
            params='beginDate=%s&endDate=%s&origin=manual&_=1527488958270' % (
                start_day.strftime('%Y-%m-%d'), end_day.strftime('%Y-%m-%d'))
        ).json()
        log_resp = self.session.get(
            'https://mp.dayu.com/dashboard/feature/star/starinfo',
            params='beginDate={}&endDate={}'.format(
                start_day.strftime('%Y%m%d'), end_day.strftime('%Y%m%d')),
        ).json()
        read_list = []
        read_obj_list = read_resp['data']['list']
        log_obj_list = log_resp['data']
        for i, read in enumerate(read_obj_list):
            log = log_obj_list[i]
            read_list.append(dict(
                user_name=user_name,
                day_time=read['date'],
                recomment_num=read['show_pv'],
                read_num=read['click_pv'],
                comment_num=read['cmt_pv'],
                share_num=read['share_pv'],
                collect_num=read['fav_pv'],
                like_num=read['like_pv'],
                log=log['total_score']
            ))
        return read_list

    def fetch_article_status(self, title):
        title = self.C_trans_to_E(title)
        resp = self.session.get(
            'https://mp.dayu.com/dashboard/getArticleList?keyword=&currentView=all&source=all&page=1&_=1532519526578'
        ).json()['dataList']['data']
        res = [2, '没查询到该文章', '']
        for art in resp:
            flag = difflib.SequenceMatcher(None, title, art['title']).quick_ratio()
            if flag < 0.9:
                continue
            elif art['status'] == 1:
                url = art['previewUrl']
                wm_id = url.split('&wm_id=')[-1]
                wm_aid = art['origin_id']
                art_url = 'https://mparticle.uc.cn/article.html?spm=a2s0i.db_contents.content.10.65dd3caaybiHDu&' \
                          'uc_param_str=frdnsnpfvecpntnwprdssskt' \
                          '&wm_id={}&wm_aid={}'.format(wm_id, wm_aid)
                res = 4, '', art_url
            elif art['status'] == 4:
                res = 5, art['_app_extra']['audit_remark'], ''
        return res

    def upload_image(self, image_name, image_data):
        resp = self.session.get('https://mp.dayu.com/dashboard/index').text
        w_re = re.compile(r'"wmid":"(.*?)",', re.S)
        wmid = w_re.findall(resp)[0]
        if not wmid:
            raise CustomException('检查账号密码')
        # sign
        s_re = re.compile(r'"nsImageUploadSign":"(.*?)",', re.S)
        sign = s_re.findall(resp)[0]
        if not sign:
            self.logger.error("Failed to get sign")
            raise CustomException('检查账号密码')
        us_re = re.compile(r'"weMediaName":"(.*?)",', re.S)
        user_name = us_re.findall(resp)[0]
        wmname = parse.urlencode({'wmname': user_name})
        url = 'https://ns.dayu.com/article/imageUpload?appid=website&fromMaterial=0&wmid={0}&{1}&sign={2}'.format(
            wmid, wmname, sign
        )
        res = self.session.post(url, files={
            'upfile': (image_name, image_data, 'image/jpeg', {
                'id': 'WU_FILE_0', 'name': image_name, 'type': 'image/jpeg',
                "lastModifiedDate": 'Tue Jun 12 2018 19:22:30 GMT+0800 (中国标准时间)',
                'size': ''})}
                                ).json()
        if res['code'] == 0:
            return res['data']['imgInfo']['url']
        else:
            raise CustomException('上传图片失败， 检查账号密码')

    def check_user_cookies(self):
        home = self.session.get('https://mp.dayu.com/dashboard/index').text
        us_re = re.compile(r'"weMediaName":"(.*?)",', re.S)
        user_name = us_re.findall(home)
        if not user_name:
            self.logger.error('获取用户名失败，检查cookie')
            return False
        return True

    def C_trans_to_E(self, string):
        """转换中文符号"""
        E_pun = u',.!?[]()<>""\':'
        C_pun = u'，。！？【】（）《》”“‘：'
        table = {ord(f): ord(t) for f, t in zip(C_pun, E_pun)}
        return string.translate(table)

    def query_article_data(self, title):
        """获取单篇文章阅读"""
        title = self.C_trans_to_E(title)
        start_day = datetime.datetime.now() - datetime.timedelta(days=7)
        end_day = datetime.datetime.now() - datetime.timedelta(days=1)
        resp = self.session.get(
            'https://mp.dayu.com/api/stat/article/detail/articlelist?beginDate={}&endDate={}'
            '&origin=manual&page=1&_=1541992692706'.format(start_day.strftime('%Y-%m-%d'), end_day.strftime('%Y-%m-%d'))
        ).json()['data']
        for art in resp:
            if title != art['title']:
                continue
            else:
                data = dict(
                    read_num=art['click_pv'],
                    recomment_num=art['show_pv'],
                    comment_num=art['cmt_pv'],
                    share_num=art['share_pv'],
                    collect_num=art['fav_pv'],
                    publish_time=art['publish_at'],
                    like_num=art['like_pv'],
                    follow_num=-1
                )
                return data
        return ''


if __name__ == '__main__':
    from control.db.api.account_api import DBAccountApi
    from lib.tools.log_mgr import Flogger

    Flogger()
    db_account_api = DBAccountApi()
    account = db_account_api.query(uid=9, mp_id=1, account='15501003753@163.com')[0]
    bj = DaYu(account)
    # title = '又推在线少儿英语品牌aiKID, 今日头条教育梦不灭'
    # content = '<p class="imgbox"><img src="https://mp.dayu.com/images/165c598ca3684a0d9aa31efb7fe3bf1d448e1b5ecb38c9e6d65c8225a87f817b1544158999202" data-infoed="1" data-width="509" data-height="340" data-format="JPEG" data-size="33354" data-phash="A54A61A257E9E571" data-md5="3e09191ce773f04296f840d6bcf581e3" _src="https://mp.dayu.com/images/165c598ca3684a0d9aa31efb7fe3bf1d448e1b5ecb38c9e6d65c8225a87f817b1544158999202" data-alt="&nbsp;"></p><p class="imgbox_desc"><span class="1544159003496_0">&nbsp;</span></p><p class="imgbox"><img src="https://mp.dayu.com/images/10497288e8324a15b71c5214df294a745ecdb8b64e6cdd11a3153967696c34021544158999108" data-infoed="1" data-width="509" data-height="340" data-format="JPEG" data-size="33641" data-phash="E9A2752397496535" data-md5="5b09bd9d28f9f564716dd7f44383d88c" _src="https://mp.dayu.com/images/10497288e8324a15b71c5214df294a745ecdb8b64e6cdd11a3153967696c34021544158999108" data-alt="&nbsp;"></p><p class="imgbox_desc"><span class="1544159003496_1">&nbsp;</span></p><p class="imgbox"><img src="https://mp.dayu.com/images/c018da4605a148b49feab919b6df2dfb3770efc0d35717214d1d9426429be88f1544158999322" data-infoed="1" data-width="506" data-height="340" data-format="JPEG" data-size="29426" data-phash="0E3E5082CE84BF7B" data-md5="61dab5c3a160209ced961cc865b1ceed" _src="https://mp.dayu.com/images/c018da4605a148b49feab919b6df2dfb3770efc0d35717214d1d9426429be88f1544158999322" data-alt="&nbsp;"></p><p class="imgbox_desc"><span class="1544159003496_2">&nbsp;</span></p><p>官网显示，该产品使用1对1专属北美外教，拥有AI自适应学习系统及AI智能语音识别、AI注意力模型、AI课后分析报告等功能；运用全身反应教学法（TPR），适配国内英语主流英语教材，满足1-4年级学习需求。</p><p>公开资料显示，aiKID少儿英语介绍为：用AI赋能<span>在线少儿英语</span>教育，将北美外教和人工智能技术结合，为孩子定制适合自己少儿英语学习内容，并实时调整学习策略。</p><p>据企查查信息显示，<span>aiKID隶属于北京比特智学科技有限公司，该公司成立于2018年2月1日，注册资本1000万元，由北京闪星科技有限公司100%控股，而闪星科技是字节跳动有限公司的全资子公司。</span></p>'
    # category = '教育'
    # flag = 3
    # print(bj.publish(title, content, category, flag))
