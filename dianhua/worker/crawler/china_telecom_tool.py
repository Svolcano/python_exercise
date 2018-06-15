# -*- coding: utf-8 -*-
import hashlib
import traceback

from Crypto.Cipher import AES
import base64
import lxml.html

idx_field_map = {
    1: 'call_tel',
    2: 'call_method',
    3: 'call_time',
    4: 'call_duration',
    5: 'call_from',
    6: 'call_type',
    10: 'call_cost',
    11: 'call_to'
}

field_regx_map = {
    1: lambda text: text,
    2: lambda text: text,
    3: lambda text: text.replace('formateDate("','').replace('")',''),
    4: lambda text: str(float(text.replace('funcFmtTime("', '').replace('")', ''))),
    5: lambda text: text,
    6: lambda text: text.replace('empsub("','').replace('")', ''),
    10: lambda text: str(float(text.replace('getbF("','').replace('")',''))/100) if text else '',
    11: lambda text:''
}

def aes_encrypt(n):
    # this is the porting from telecom javascript
    BS = 16
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    n = pad(n)
    e = hashlib.md5('login.189.cn')
    t = e.hexdigest()
    i = t.encode('utf-8')
    r  = u'1234567812345678'.encode('utf-8')
    encryption_suite = AES.new(i, AES.MODE_CBC, r)
    cipher_text = encryption_suite.encrypt(n)
    base64.b64encode(cipher_text)
    return base64.b64encode(cipher_text)

def parse_call_record(html):
    records = []
    doc_string = html.replace("<script>formateB", "<tr class='call_record'><script>formateB")
    doc = lxml.html.document_fromstring(doc_string)
    records_elements = doc.xpath("//tr[@class='call_record']")
    for record_element in records_elements:
        record = parse_record_element(record_element)
        records.append(record)
    return records

def parse_record_element(record_element):
    record = {}
    for idx, term in enumerate(record_element.xpath('td')):
        text = term.text_content()
        if idx in idx_field_map:
            record[idx_field_map[idx]] = field_regx_map[idx](text)
    return record

def login_error(login_req, self):
    if u'账号不存在' in login_req.text or u'手机号码错误' in login_req.text or 'data-resultcode="9100"' in login_req.text or u"用户不存在" in login_req.text:
        self.log('user', 'invalid_tel', login_req)
        return 1, 'invalid_tel'
    # 9114 == 密码过于简单
    # 9103 == 密码错误
    # 9105 == 密码格式错误
    elif u'密码过于简单' in login_req.text or "9114" in login_req.text:
        self.log('user', 'sample_pwd', login_req)
        return 1, 'sample_pwd'
    elif u'短信验证码已过期' in login_req.text or "9117" in login_req.text:
        self.log("user", "login_param_error, ", login_req)
        return 2, 'login_param_error'
    elif u'密码错误' in login_req.text or "9103" in login_req.text or u'密码格式错误' in login_req.text or u'密码是6-18位字符串' in login_req.text:
        self.log('user', 'pin_pwd_error', login_req)
        return 1, 'pin_pwd_error'
    elif u'data-errmsg="验证码' in login_req.text:
        self.log('user', 'verify_error', login_req)
        return 2, 'verify_error'
    elif u'data-errmsg="密码已被锁定"' in login_req.text:
        self.log('user', 'verify_error', login_req)
        return 2, 'verify_error'
    elif u'账号锁定' in login_req.text or 'data-resultcode="9111"' in login_req.text:
        self.log('crawler', 'over_query_limit', login_req)
        return 9, 'account_locked'
    elif u"密码锁定" in login_req.text or 'data-resultcode="9113"' in login_req.text:
        self.log('user', 'website_busy_error', login_req)
        return 2, 'website_busy_error'
    # 系统繁忙的代号有时候 是9999， 有时候 报9998
    elif u'系统繁忙' in login_req.text or 'data-resultcode="9999"' in login_req.text or 'data-resultcode="9998"' in login_req.text:
        self.log('website', 'website_busy_error', login_req)
        return 9, 'website_busy_error'
    elif u'输入项中不能包含非法字符' in login_req.text:
        self.log("crawler", u"输入项有非法字符, 只有验证码会产生该错误, 手机号被验证过, 服务密码会直接报服务密码错", login_req)
        return 9, "verify_error"
    elif 'data-resultcode="9105"' in login_req.text:
        self.log("user", "登录参数错误", login_req)
        return 9, "login_param_error"
    else:
        # 此处如果报错建议在返回文档中搜索data-errmsg
        self.log('crawler', "unknown_error", login_req)
        return 9, "unknown_error"


# 统一登录方法
def login_unity(self, ProvinceID, **kwargs):
    try:
        pwd = aes_encrypt(kwargs['pin_pwd'])
    except:
        error = traceback.format_exc()
        self.log('crawler', 'login_param_error %s' % error, '')
        return 9, 'login_param_error'

    form_data = {
        "Account": kwargs['tel'],
        "UType": '201',
        "ProvinceID": ProvinceID,
        "AreaCode": "",
        "CityNo": "",
        "RandomFlag": '0',
        "Password": pwd,
        "Captcha": '',
    }
    # 4位字母数字
    codetype = 3004
    for i in range(self.max_retry):
        url = "http://login.189.cn/web/captcha?undefined&source=login&width=100&height=37"
        headers = {"Referer": "http://login.189.cn/login"}
        code, key, resp = self.get(url, headers=headers)
        if code != 0:
            return code, key
        try:
            key, result, cid = self._dama(resp.content, codetype)
        except:
            msg = traceback.format_exc()
            self.log('crawler', u'打码失败:{}'.format(msg), '')
            continue
        if key == "success" and result != "":
            form_data['Captcha'] = str(result).lower()
        else:
            continue

        header = {
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0; WOW64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 57.0.2987.133 Safari / 537.36',
            'Referer': 'http://login.189.cn/login',
            'Origin': 'http://login.189.cn/login'
        }

        LOGIN_URL = 'http://login.189.cn/web/login'
        code, key, login_req = self.post(url=LOGIN_URL, data=form_data, headers=header)
        if code != 0:
            return code, key
        if not login_req.history:
            if u'data-errmsg="验证码' in login_req.text:
                self.log('user', 'verify_error', resp)
                self._dama_report(cid)
                continue
            code, key = login_error(login_req, self)
            return code, key
        return 0, 'success'
    else:
        self.log('crawler', u'两次打码都失败', '')
        return 9, 'auto_captcha_code_error'

