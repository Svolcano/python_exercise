import json
import requests
import re
from lxml import etree
from requests_toolbelt.multipart.encoder import MultipartEncoder

from lib.mp.base import Base

from w3lib.html import remove_tags

SUCCESS = 'OK'
FIALED = 'FAIL'

SESSION_TIMEOUT = 30

class FaceBook(Base):
    base = 'https://mbasic.facebook.com'
    mp_id = 11
    zh_name = 'FaceBook'

    @staticmethod
    def login(user, pswd, **kw):
        base = 'https://mbasic.facebook.com'

        user_agent = FaceBook.UA
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': base,
            'Origin': base,
            'User-Agent': user_agent,
            'Connection': 'keep-alive',
        }
        s = requests.session()
        now_cookies = s.cookies
        now_cookies.clear()
        resp = s.get(base, headers=header, timeout=SESSION_TIMEOUT)
        login_url = 'https://mbasic.facebook.com/login/device-based/regular/login/?refsrc=https://mbasic.facebook.com/&lwv=100&refid=8'
        dom = etree.HTML(resp.content)
        inputs = dom.xpath("//form//input")
        login_params = {}
        for i in inputs:
            k = i.get('name')
            v = i.get('value')
            login_params[k] = v
        login_params['try_number'] = 0
        login_params['email'] = user
        login_params['pass'] = pswd
        login_params['login'] = 'Log In'
        resp = s.post(login_url, data=login_params, timeout=SESSION_TIMEOUT)
        if "Log In With One Tap" in resp.text:
            relogin_url = 'https://mbasic.facebook.com/login/device-based/update-nonce/'
            relogin_param = {}
            dom = etree.HTML(resp.content)
            inputs = dom.xpath("//form/input")
            for i in inputs:
                k = i.get('name')
                v = i.get('value', '')
                relogin_param[k] = v
            try:
                resp = s.post(relogin_url, data=relogin_param, timeout=SESSION_TIMEOUT)
                resp = etree.HTML(resp.content)
                name = resp.xpath('//div[@id="bookmarkmenu"]/div/table/tbody/tr/td/a/text()')[0]
                return s.cookies.get_dict(), name
            except:
                raise Exception("登录失败，请检查账户密码")
        if "一键登录" in resp.text:
            relogin_url = 'https://mbasic.facebook.com/login/device-based/update-nonce/'
            relogin_param = {}
            dom = etree.HTML(resp.content)
            inputs = dom.xpath("//form/input")
            for i in inputs:
                k = i.get('name')
                v = i.get('value', '')
                relogin_param[k] = v
            try:
                resp = s.post(relogin_url, data=relogin_param, timeout=SESSION_TIMEOUT)
                resp = etree.HTML(resp.content)
                try:
                    name = resp.xpath('//a[@id="mbasic_logout_button"]/text()')[0]
                    reObj = re.compile(r'退出（|）')
                    name = reObj.sub('',name).strip()
                except:
                    name = ''
                return s.cookies.get_dict(), name
            except:
                raise Exception("登录失败，请检查账户密码")


    def publish(self, content, s=None):
        s = s.strip()
        if not s:
            home_url = 'https://mbasic.facebook.com/home.php?_rdr'
        else:
            home_url = s
        result = re.compile(r'<.*?img.*?src="(.*?)".*?>', re.S).findall(content)
        resp = self.session.get(home_url, timeout=SESSION_TIMEOUT)
        media_id_list = []
        content = remove_tags(content)
        if result:
            if len(result) > 3:
                raise Exception('图片不能超过三张')
            img_data_list = []
            for item in result:
                res = requests.get(item, timeout=SESSION_TIMEOUT)
                img_data = res.content
                img_data_list.append(img_data)
            img_data1 = b''
            img_data2 = b''
            img_data = img_data_list[0]
            if len(result) == 2:
                img_data1 = img_data_list[1]

            if len(result) == 3:
                img_data1 = img_data_list[1]
                img_data2 = img_data_list[2]
            s = self._upload_image(img_data, img_data1, img_data2, content, url=home_url)
            media_id_list.append(str(s))
            media_id = ','.join(media_id_list)
            self.logger.info(media_id)
            return 2, '', media_id
        else:
            post_params = {}
            dom = resp.content
            dom = etree.HTML(dom)
            inputs = dom.xpath("//form/input")
            for i in inputs:
                k = i.get('name')
                v = i.get('value', '')
                post_params[k] = v
            post_suffix = dom.xpath('//form[@method="post"]/@action')[0]
            post_url = f"{self.base}{post_suffix}"
            post_params['view_post'] = 'Post'
            post_params['xc_message'] = content
            try:
                resp = self.session.post(post_url, data=post_params, timeout=SESSION_TIMEOUT)
                dom = etree.HTML(resp.content)
                artid_list = dom.xpath('//div[@role="article"]/@data-ft')
                if not artid_list:
                    artid_list = dom.xpath('//div[@id="u_0_3"]/@data-ft')
                    if not artid_list:
                        raise Exception('文章ID获取失败')
                for artid in artid_list:
                    if "top_level_post_id" in artid:
                        artid = re.compile(r'top_level_post_id.*?,', re.S).findall(artid)[0]
                        reobj3 = re.compile(r'top_level_post_id|"|,|:')
                        artid = reobj3.sub('', artid).strip()
                        return 2, '', artid

            except Exception as e:
                self.logger.error(e)
            return 3, '发送失败', ''

    def _upload_image(self, img_data, img_data1, img_data2, content, url=base):
        user_agent = FaceBook.UA
        post_params = {}
        resp = self.session.get(url, timeout=SESSION_TIMEOUT)
        dom = etree.HTML(resp.content)
        inputs = dom.xpath("//form/input")
        for i in inputs:
            k = i.get('name')
            v = i.get('value', '')
            post_params[k] = v
        post_params['view_photo'] = 'Photo'
        if not content:
            content = ''
        post_params['xc_message'] = content
        post_suffix = dom.xpath('//form[@method="post"]/@action')[0]
        post_url = f"{self.base}{post_suffix}"
        resp = self.session.post(post_url, data=post_params)
        post_params = {}
        dom = etree.HTML(resp.content)
        inputs = dom.xpath("//form//input")
        img_name1 = ''
        img_name2 = ''
        img_type1 = 'application/octet-stream'
        img_type2 = 'application/octet-stream'
        if img_data1:
            img_name1 = '2'
            img_type1 = 'image/jpeg'
        if img_data2:
            img_name2 = '3'
            img_type2 = 'image/jpeg'
        files = {
            'file1': ('1', img_data, 'image/jpeg'),
            'file2': (img_name1, img_data1, img_type1),
            'file3': (img_name2, img_data2, img_type2),
        }
        for i in inputs:
            k = i.get('name')
            if not k.startswith('file'):
                v = i.get('value', '')
                files[k] = v
        datas = MultipartEncoder(
            fields=files
        )
        post_suffix = dom.xpath('//form[@method="post"]/@action')[0]
        post_url = f"{self.base}{post_suffix}"
        header = {
            'Content-Type': '',
            'Referer': self.base,
            'Origin': self.base,
            'User-Agent': user_agent,
            'Connection': 'keep-alive',
        }
        header['Content-Type'] = datas.content_type
        resp = self.session.post(
            post_url,
            data=datas,
            headers=header, timeout=SESSION_TIMEOUT

        )
        post_param = {}
        dom = etree.HTML(resp.content)
        inputs = dom.xpath("//form//input")
        photo_ids = []
        for i in inputs:
            k = i.get('name')
            v = i.get('value', '')
            if k == 'photo_ids[]':
                photo_ids.append(v)
            post_param[k] = v
        if not content:
            content = ''
        post_param['photo_ids[]'] = photo_ids
        post_param['xc_message'] = content
        post_suffix = dom.xpath('//form[@method="post"]/@action')[0]
        post_url = f"{self.base}{post_suffix}"
        try:
            resp = self.session.post(post_url, data=post_param, timeout=SESSION_TIMEOUT)
            if "TagFriends" in resp.text:
                # post_suffix = dom.xpath('//form[@method="post"]/@action')[0]
                dom = etree.HTML(resp.content)
                post_suffix = dom.xpath("//div[@id='header']//a[@class='r s']/@href")[0]
                url0 = f'{self.base}{post_suffix}'
                resp = self.session.get(url0, timeout=SESSION_TIMEOUT)
                dom = etree.HTML(resp.content)
                url1 = dom.xpath('//div[@id="bookmarkmenu"]//td[@class="s"]/a/@href')[0]
                url1 = f"{self.base}{url1}"
                resp = self.session.get(url1, timeout=SESSION_TIMEOUT)
                dom = etree.HTML(resp.content)
                artid_list = dom.xpath('//div[@id="m_newsfeed_stream"]/div/div/@data-ft')
                if not artid_list:
                    raise Exception('文章ID获取失败')
                for artid in artid_list:
                    if "top_level_post_id" in artid:
                        artid = re.compile(r'top_level_post_id.*?,', re.S).findall(artid)[0]
                        reobj3 = re.compile(r'top_level_post_id|"|,|:')
                        artid = reobj3.sub('', artid).strip()
                        return 2, '', artid
            elif "标记好友" in resp.text:
                # post_suffix = dom.xpath('//form[@method="post"]/@action')[0]
                dom = etree.HTML(resp.content)
                post_suffix = dom.xpath("//div[@id='header']//a[@class='r s']/@href")[0]
                url0 = f'{self.base}{post_suffix}'
                resp = self.session.get(url0, timeout=SESSION_TIMEOUT)
                dom = etree.HTML(resp.content)
                url1 = dom.xpath('//div[@id="bookmarkmenu"]//td[@class="s"]/a/@href')[0]
                url1 = f"{self.base}{url1}"
                resp = self.session.get(url1, timeout=SESSION_TIMEOUT)
                dom = etree.HTML(resp.content)
                artid_list = dom.xpath('//div[@id="m_newsfeed_stream"]/div/div/@data-ft')
                if not artid_list:
                    raise Exception('文章ID获取失败')
                for artid in artid_list:
                    if "top_level_post_id" in artid:
                        artid = re.compile(r'top_level_post_id.*?,', re.S).findall(artid)[0]
                        reobj3 = re.compile(r'top_level_post_id|"|,|:')
                        artid = reobj3.sub('', artid).strip()
                        return 2, '', artid
            else:
                dom = etree.HTML(resp.content)
                # if url == self.base:
                artid_list = dom.xpath('//div[@id="m_newsfeed_stream"]/div/div/@data-ft')
                if artid_list == []:
                    artid_list = dom.xpath('//div[@id="recent"]/div/div/div/@data-ft')
                if not artid_list:
                    raise Exception('文章ID获取失败')
                for artid in artid_list:
                    if "top_level_post_id" in artid:
                        artid = re.compile(r'top_level_post_id.*?,', re.S).findall(artid)[0]
                        reobj3 = re.compile(r'top_level_post_id|"|,|:')
                        artid = reobj3.sub('', artid).strip()
                        return artid
        except Exception as e:
            self.logger.error(e)
            return 3, '发文失败', ''

    def upload_image(self, img_data, content):
        return ''

    def fetch_article_status(self, title):
        return 4, '', ''

    def query_article_data(self, title, s=None):

        if s:
            main_page_dict = self.get_mainpage_ov()
            # s = 'Mylove Type'
            art_id = 'like_' + title
            url = main_page_dict[s]
            resp = self.session.get(url, timeout=SESSION_TIMEOUT)
            dom = etree.HTML(resp.content)
            comment_list, like_list, share_list, artids_list = self.get_value(dom=dom, status_code='1')

            for i in range(len(artids_list)):
                if str(artids_list[i]) == str(title):
                    comment = re.compile(r'\d+', re.S).findall(comment_list[i])
                    if comment:
                        comment = comment[0]
                    else:
                        comment = '0'
                    share = re.compile(r'\d+', re.S).findall(share_list[i])
                    if share:
                        share = share[0]
                    else:
                        share = '0'
                    like_num = re.compile(r'\d+', re.S).findall(like_list[i])
                    if like_num:
                        like_num = like_num[0]
                    else:
                        like_num = '0'
                    dicts = {}
                    dicts['content'] = int(artids_list[i])
                    dicts['comment_num'] = int(comment)
                    dicts['follow_num'] = int(share)
                    dicts['like_num'] = int(like_num)
                    return dicts


        else:
            url = 'https://mbasic.facebook.com/'
            resp = self.session.get(url, timeout=SESSION_TIMEOUT)
            dom = etree.HTML(resp.content)
            user_center = dom.xpath('//div[@id="bookmarkmenu"]/div/table/tbody/tr/td[@class="s"]/a/@href')[1]
            get_url = f"{self.base}{user_center}"
            resp = self.session.get(get_url, timeout=SESSION_TIMEOUT)
            dom = etree.HTML(resp.content)
            comment_list, like_list, share_list, artids_list = self.get_value(dom=dom)
            next_page_url = dom.xpath('//div[@id="u_0_4"]/a/@href')[0]
            next_url = f'{self.base}{next_page_url}'

            resp = self.session.get(next_url, timeout=SESSION_TIMEOUT)
            dom = etree.HTML(resp.content)
            comment_list, like_list, share_list, artids_list = self.get_value(dom=dom, comment_list=comment_list,
                                                                              like_list=like_list,
                                                                              share_list=share_list,
                                                                              artids_list=artids_list)

            for i in range(len(artids_list)):
                if str(artids_list[i]) == str(title):
                    comment = re.compile(r'\d+', re.S).findall(comment_list[i])
                    if comment:
                        comment = comment[0]
                    else:
                        comment = '0'
                    share = re.compile(r'\d+', re.S).findall(share_list[i])
                    if share:
                        share = share[0]
                    else:
                        share = '0'
                    like_num = re.compile(r'\d+', re.S).findall(like_list[i])
                    if like_num:
                        like_num = like_num[0]
                    else:
                        like_num = '0'
                    dicts = {}
                    dicts['content'] = int(artids_list[i])
                    dicts['comment_num'] = int(comment)
                    dicts['follow_num'] = int(share)
                    dicts['like_num'] = int(like_num)
                    return dicts

    def get_value(self, dom, comment_list=[], like_list=[], share_list=[], artids_list=[], status_code='0'):

        if status_code == '0':
            # like_nums = dom.xpath('//div[@class="cl ef"]/span[@class="cj ed"]/a/text()')
            like_nums = dom.xpath('//div[@id="structured_composer_async_container"]/div/div/div/div/span/a/text()')
            # print(like_nums)
            comment_nums = dom.xpath('//div[@class="cj ed"]/a/text()')[::5]
            share_nums = dom.xpath('//div[@id="structured_composer_async_container"]/div/div/div/div/a/text()')[1::5]
            reObj = re.compile(r'Comment|评论|条')
            for comment in comment_nums:
                comment = reObj.sub('', comment).strip()
                if not comment:
                    comment = '0'
                comment_list.append(comment)
            reObj1 = re.compile(r'Like|React|留下心情|赞')
            for num in like_nums:
                if num == 'React':
                    like_list.pop()
                if num == '留下心情':
                    like_list.pop()
                num = reObj1.sub('', num).strip()
                if not num:
                    num = '0'
                like_list.append(num)
                if 'More' in like_list:
                    like_list.pop()
                if '展开' in like_list:
                    like_list.pop()
            reObj2 = re.compile(r'Share|分享')
            for share in share_nums:
                share = reObj2.sub('', share).strip()
                if not share:
                    share = '0'
                share_list.append(share)
            artid_list = dom.xpath('//div[@id="structured_composer_async_container"]/div/div/@data-ft')
            for artid in artid_list:
                if "throwback_story_fbid" in artid:
                    artid = re.compile(r'throwback_story_fbid.*?,', re.S).findall(artid)[0]
                    reobj3 = re.compile(r'throwback_story_fbid|"|,|:')
                    artid = reobj3.sub('', artid).strip()
                    artids_list.append(artid)
            return comment_list, like_list, share_list, artids_list
        if status_code == '1':
            like_nums = dom.xpath('//div[@class="bo fe fq"]/div[@class="gf"]/div[@class="cl ef"]//a//text()')[0::8]
            comment_nums = dom.xpath('//div[@class="bo fe fq"]/div[@class="gf"]/div[@class="cl ef"]//a//text()')[2::8]
            share_nums = dom.xpath('//div[@class="bo fe fq"]/div[@class="gf"]/div[@class="cl ef"]//a//text()')[3::8]
            comment_list = [], like_list = [], share_list = [], artids_list = []
            reObj = re.compile(r'Comment|评论|条')
            for comment in comment_nums:
                comment = reObj.sub('', comment).strip()
                if not comment:
                    comment = '0'
                comment_list.append(comment)
            reObj1 = re.compile(r'Like|React|留下心情|赞')
            for num in like_nums:
                if num == 'React':
                    like_list.pop()
                if num == '留下心情':
                    like_list.pop()
                num = reObj1.sub('', num).strip()
                if not num:
                    num = '0'
                like_list.append(num)
                if 'More' in like_list:
                    like_list.pop()
                if '展开' in like_list:
                    like_list.pop()
            reObj2 = re.compile(r'Share|分享')
            for share in share_nums:
                share = reObj2.sub('', share).strip()
                if not share:
                    share = '0'
                share_list.append(share)
            artid_list = dom.xpath('//div[@id="mPagesFinchTimeline"]/div/div/div/div/@data-ft')
            for artid in artid_list:
                if "top_level_post_id" in artid:
                    artid = re.compile(r'top_level_post_id.*?,', re.S).findall(artid)[0]
                    reobj3 = re.compile(r'top_level_post_id|"|,|:')
                    artid = reobj3.sub('', artid).strip()
                    artids_list.append(artid)

    def check_user_cookies(self):
        resp = self.session.get('https://www.facebook.com/', timeout=SESSION_TIMEOUT)
        html = resp.text
        uname = html.xpath('//div[@id="userNav"]//div[@class="linkWrap noCount"]/text()')
        if uname:
            return True
        else:
            return False

    # 获取个人主页的链接
    # @staticmethod
    def get_mainpage_ov(self, fb_account):
        resp = requests.post(f'{HW_IP}/api/get_main_page', json={
            "uid": fb_account.uid,
            "account": fb_account.account,
            "mp_id": FaceBook.mp_id,
        }, timeout=SESSION_TIMEOUT)
        if resp.status_code == 200:
            resp_obj = resp.json()
            if resp_obj['status'] == SUCCESS:
                main_page = resp_obj['data']
                return main_page
        tmsg = '请求main_page失败。'
        self.logger.info(tmsg)
        return {}

    def get_mainpage(self):
        url = 'https://mbasic.facebook.com/pages/?ref_component=mbasic_home_header&ref_page=%2Fwap%2Fhome.php&refid=7'
        resp = self.session.get(url, timeout=SESSION_TIMEOUT)
        main_page_dict = {}
        try:
            if '你负责的主页' in resp.text:
                resualt = ''.join(re.findall(r'你负责的主页.*?推荐主页', resp.text, re.S | re.M))
                main_page_name_list = re.findall(r'<span>.*?</span>', resualt, re.S | re.M)
                main_page_url_list = re.findall(r'<a href=".*?"><img', resualt, re.S | re.M)

                i = 0
                reObj = re.compile(r'<a href="|"><img')
                base_url = 'https://mbasic.facebook.com'
                for name in main_page_name_list:
                    name = remove_tags(name)
                    url = reObj.sub('', main_page_url_list[i]).strip()
                    url = f'{base_url}{url}'
                    main_page_dict[name] = url
                    i += 1
                return main_page_dict
            else:
                return main_page_dict
        except Exception as e:
            msg = '获取主页信息失败'
            self.logger.error("%s%s", msg, e)
            return main_page_dict


if __name__ == '__main__':
    tw = FaceBook()
    title = '111'
    content = 'hello<p><img src="http://jingmeiti.oss-cn-beijing.aliyuncs.com/2f923184a82fc7513df47ca6562977d0006d1928.jpg"></p >,<p><img src="http://jingmeiti.oss-cn-beijing.aliyuncs.com/d2d2bc9ac0fef4214489f38a1c501f9913349787.jpg"></p >,<p><img src="http://jingmeiti.oss-cn-beijing.aliyuncs.com/a7e5a377b8a8b883aba676a9b91c144d57b0af88.jpg">'
    # content = 'hello my beautiful girl'
    ss = tw.publish(content=content)
    print(ss)
    # title = '235885247356091'
    # s = tw.query_article_data(title=title)
    # print(s)
