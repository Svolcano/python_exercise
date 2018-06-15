# -*- coding: utf-8 -*-
import time
import clime
import base64
import requests
import traceback

from pprintpp import pprint as pp

_TEST_URL = 'http://localhost'
#_TEST_URL = 'http://crawl.crs.dianhua.cn'
_TEST_PORT = 8080

# GET
_FLOW_TYPE_URL =  '{}:{}/crawl/calls/flow_type?tel={}&uid={}'
_VERIFY_SMS_URL = '{}:{}/crawl/calls/verify/sms?sid={}'
_VERIFY_CAPTCHA_URL = '{}:{}/crawl/calls/verify/captcha?sid={}'
_VERIFY_SMS_CAPTCHA_URL = '{}:{}/crawl/calls/verify/sms_captcha?sid={}'
_ABORT_URL = '{}:{}/crawl/calls/abort?sid={}'
# POST
_LOGIN_URL = '{}:{}/crawl/calls/login'
_VERIFY_URL = '{}:{}/crawl/calls/verify'

def flow_type(tel, uid):
    print '\nACTION : GET flow_type'
    url = _FLOW_TYPE_URL.format(_TEST_URL, _TEST_PORT, tel, uid)
    r = requests.get(url)
    ret = r.json()
    return ret

def get_sms(sid):
    start = time.time()
    print '\nACTION : GetSMS'
    url = _VERIFY_SMS_URL.format(_TEST_URL, _TEST_PORT, sid)
    r = requests.get(url)
    ret = r.json()
    print 'cost {} secs'.format(time.time() - start)
    return ret

def get_captcah(sid):
    start = time.time()
    print '\nACTION : GetCaptch'
    url = _VERIFY_CAPTCHA_URL.format(_TEST_URL, _TEST_PORT, sid)
    r = requests.get(url)
    ret = r.json()
    pp(ret)
    captcha = base64.b64decode(ret['content'][len('data:image/png;base64,'):])
    with open('./image.png', 'w') as fp:
        fp.write(captcha)
    print 'cost {} secs'.format(time.time() - start)
    return ret

def get_smscaptcha(sid):
    start = time.time()
    print '\nACTION : GetSMSCaptch'
    url = _VERIFY_SMS_CAPTCHA_URL.format(_TEST_URL, _TEST_PORT, sid)
    r = requests.get(url)
    print r.text
    ret = r.json()
    pp(ret)
    captcha = base64.b64decode(ret['content'][len('data:image/png;base64,'):])
    with open('./image.png', 'w') as fp:
        fp.write(captcha)
    print 'cost {} secs'.format(time.time() - start)
    return ret

# def update_smscaptcha(sid,verify_type):
#     start = time.time()
#     print '\nACTION : GetSMSCaptch'
#     url = _VERIFY_SMS_CAPTCHA_URL.format(_TEST_URL, _TEST_PORT, sid)
#     data = {
#         'verify_type': verify_type
#     }
#     r = requests.get(url, params=data)
#     print r.text
#     ret = r.json()
#     pp(ret)
#     captcha = base64.b64decode(ret['content'][len('data:image/png;base64,'):])
#     with open('./image.png', 'w') as fp:
#         fp.write(captcha)
#     print 'cost {} secs'.format(time.time() - start)
#     return ret

def login(sid, tel, pin_pwd, sms_code, captcha_code):
    start = time.time()
    print '\nACTION: POST login'
    data = {
        'sid': sid,
        'full_name' : '毛羽建',
        'id_card'   : '330225198112260052',
        'pin_pwd': pin_pwd,
        'sms_code': sms_code,
        'captcha_code': captcha_code
    }
    url = '{}:{}/crawl/calls/login'.format(_TEST_URL, _TEST_PORT)
    r = requests.post(url, data=data)
    ret = r.json()
    print 'cost {} secs'.format(time.time() - start)
    return ret

def verify(sid, sms_code, captcha_code):
    start = time.time()
    print '\nACTION: POST verify'
    data = {
        'sid': sid,
        'sms_code': sms_code,
        'captcha_code': captcha_code
    }
    url = _VERIFY_URL.format(_TEST_URL, _TEST_PORT, sid, sms_code, captcha_code)
    r = requests.post(url, data=data)
    ret = r.json()
    print 'cost {} secs'.format(time.time() - start)
    return ret

def abort(sid):
    start = time.time()
    print '\nACTION: GET abort'
    url = _ABORT_URL.format(_TEST_URL, _TEST_PORT, sid)
    r = requests.get(url)
    ret = r.json()
    print 'cost {} secs'.format(time.time() - start)
    return ret

def crawl(tel, pin_pwd):
    next_action = ''
    try:
        sid = ''
        next_action = ''
        need_sms_verify = ''
        need_captcha_verify = ''
        sms_code = ''
        captcha_code = ''
        ret = {}
        while(next_action != 'Finish'):
            if next_action == '':
                ret = flow_type(tel, 'UIDxxxxxxxx')
                pp(ret)
                if ret['status']:
                    print 'Error'
                    return ret
                sid = ret['result']['sid']
                need_sms_verify = ret['result']['need_sms_verify']
                need_captcha_verify = ret['result']['need_captcha_verify']
            elif next_action == 'Login':
                if need_sms_verify == 1 or need_captcha_verify == 1:
                    sms_code = raw_input('Input verify code (sms): ')
                    captcha_code = raw_input('Input verify code (captcha): ')
                else:
                    sms_code = ''
                    captcha_code = ''
                ret = login(sid, tel, pin_pwd, sms_code, captcha_code)
                if ret['status']:
                    print u'ERROR : {}'.format(ret['status'])
            elif next_action == 'GetSMS':
                ret = get_sms(sid)
                if ret['status']:
                    print u'ERROR : {}'.format(ret['status'])
            elif next_action == 'GetCaptcha':
                ret = get_captcah(sid)
                if ret['status']:
                    print u'ERROR : {}'.format(ret['status'])
            elif next_action == 'GetSMSCaptcha':
                ret = get_smscaptcha(sid)
                if ret['status']:
                    print u'ERROR : {}'.format(ret['status'])
            elif next_action == 'Verify':
                # update_if = raw_input('if update verify_code(''/"sms"/"captcha")?: ')
                # if update_if == "sms":
                #     ret = update_smscaptcha(sid,update_if)
                #     if ret['status']:
                #         print u'ERROR : {}'.format(ret['status'])
                # elif update_if == "captcha":
                #     ret = update_smscaptcha(sid,update_if)
                #     if ret['status']:
                #         print u'ERROR : {}'.format(ret['status'])
                sms_code = raw_input('Input verify code (sms): ')
                captcha_code = raw_input('Input verify code (captcha): ')
                ret = verify(sid, sms_code, captcha_code)
                if ret['status']:
                    print u'ERROR : {}'.format(ret['status'])
            elif next_action == 'Reset':
                print u'Crawler status = {}, msg = {}'.format(
                        ret['status'],
                        ret['message'])
                break
            elif next_action == 'Unsupported':
                print 'No crawler supported!!'
                break
            elif next_action == 'NoCrawlFinish':
                print 'No crawl needed. Results are already exist.'
                break
            else:
                print next_action
                assert False, 'Abnormal case !!!'
            pp(ret)
            next_action = ret['next_action']
            #print next_action
            raw_input('next_action = {}'.format(next_action))
    except KeyboardInterrupt:
        ret = abort(sid)
        if ret['status']:
            print 'ERROR : {}'.format(ret['status'])
        next_action = ret['next_action']
    except:
        pp(ret)
        print traceback.format_exc()
        return 'Fatal Error.......................................'

    return next_action

if __name__ == '__main__':
    import clime.now
