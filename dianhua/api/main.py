# -*- coding:utf-8 -*-
import uuid
import inspect
import traceback
import sys
import re
import time

reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask
from flask_restful import reqparse
from flask_restful import Resource, Api
from mrq import config as mrq_config
from mrq.context import set_current_config

if __name__ == '__main__':
    import os
    import sys
    package_path = os.path.abspath(__file__)
    package_path = os.path.dirname(package_path)
    package_path = os.path.join(package_path, '..')
    sys.path.append(package_path)

from setting.status_code import STATUS_CODE
from util import tel_loc_info, init_sid_info, set_sid_info,undo_sid_info
from util import send_crawl_task, check_crawler_state
from util import get_sid_info, pass_crawler_params
from util import check_sid_info_error
from com.logger import logger
from com.connection import db

from worker.call_log_data_fusion import data_fusion as call_log_fusion
from worker.call_log_data_fusion import  register_other_call_log
from worker.bill_data_fusion import  data_fusion as bill_fusion

def log(level, sid=None, message=None, **kwargs):
    """save log for api"""
    log_name = 'api_log'
    # level = inspect.stack()[1][3]
    # stack = inspect.stack()
    # the_class = stack[1][0].f_locals["self"].__class__
    # the_method = stack[1][0].f_code.co_name
    # level = '{}.{}()'.format(str(the_class), the_method).replace('__main__.', '')
    data = {'sid': sid,}
    if kwargs:
        data.update(kwargs)
    logger(log_name, level, message, **data)

# setup Flask
app = Flask(__name__)
#app.debug = True
api = Api(app)

# setup mrq configuration
cfg = mrq_config.get_config(sources=("file", "env", "args"))
set_current_config(cfg)

# init database
# if not init_sid_info():
    #app.logger.debug("Can't init sid collection index")
    # exit(1)

# Flask request parser util
def get_args(**kwarg):
    parser = reqparse.RequestParser()
    for _key, _type in kwarg.iteritems():
#        print _key, _type
        parser.add_argument(_key, help='', default='')
    args = parser.parse_args()
    return args

# RESTFUL API
class GetFlowType(Resource):

    def get(self):
        ret = {}
        try:
            args = get_args(tel=str,sid=str)
            tel = args.get('tel', '')
            sid = args.get('sid', '')

            tel_info = tel_loc_info(tel)
            if not tel_info:
                error = STATUS_CODE['invalid_tel']
                error['next_action'] = 'Reset'
                return error
            elif tel_info.get('telecom', u'virtual') == u'virtual':
                error = STATUS_CODE['no_supported_crawler']
                error['next_action'] = 'Unsupported'
                return error
            
            sid_info=db['sid_info'].find_one({'sid': sid,'status':{'$ne':0}})
            if sid_info:                
                if not undo_sid_info(sid, tel):
                    error = STATUS_CODE['invalid_sid']
                    error['next_action'] = 'Reset'
                    return error

            else:
                # if not has today result, we need to do crawling
                sid = 'SID{}'.format(uuid.uuid4())
                sid = sid.replace('-', '')

            # if len(sid)<1:
            #     # if not has today result, we need to do crawling
            #     sid = 'SID{}'.format(uuid.uuid4())
            #     sid = sid.replace('-', '')
            # else:
            #     if not undo_sid_info(sid,tel):
            #         error = STATUS_CODE['invalid_sid']
            #         error['next_action'] = 'Reset'
            #         return error

            info = {'tel': tel, 'tel_info': tel_info}
            if not set_sid_info(sid, tel, info):
                error = STATUS_CODE['duplicate_sid']
                error['next_action'] = 'Reset'
                return error

            # send crawl job to start crawler
            flow_type = tel_info['flow_type']
            province  = tel_info['province']
            city      = tel_info['city']
            if not send_crawl_task(sid, tel, flow_type, province, city):
                pass_crawler_params(sid, 'Abort', {})
                error = STATUS_CODE['queue_error']
                error['next_action'] = 'Reset'
                log('GetFlowType', sid=sid, message='params:Abort, error:{}'.format(error))
                return error

            # check crawler state
            status, state_info = check_crawler_state(sid)
            log('GetFlowType', sid=sid, message='state_info:{}'.format(state_info))
            if not status:
                pass_crawler_params(sid, 'Abort', {})
                return state_info['info']

            ret = state_info['info']
            ret['result'] = tel_info
            ret['result']['sid'] = sid
            ret['result'].update(state_info['need_parameters'])
            if ret['next_action'] == 'Unsupported':
                ret.update(STATUS_CODE['no_supported_crawler'])
            return ret
        except:
            message = traceback.format_exc()
            print message
            pass_crawler_params(sid, 'Abort', {})
            error = STATUS_CODE['unknown_error']
            error['next_action'] = 'Reset'
            log('GetFlowType', message=message)
            return error


class Login(Resource):

    def post(sid):
        try:
            # Get user arguments
            args = get_args(sid=str, full_name=str, id_card=str,
                            pin_pwd=str, sms_code=str, captcha_code=str)
            sid = args.get('sid', '')
            full_name = args.get('full_name', '')
            id_card = args.get('id_card', '')
            pin_pwd = args.get('pin_pwd', '')
            sms_code = args.get('sms_code', '')
            captcha_code = args.get('captcha_code', '')
            if re.findall(r'[^\da-zA-Z]', sms_code):
                return {'status': 4003, 'message': u'验证码错误', 'next_action': 'Login'}
            if re.findall(r'[^\da-zA-Z]', captcha_code):
                return {'status': 4003, 'message': u'验证码错误', 'next_action': 'Login'}
            if re.findall(r'[^\d]', pin_pwd):
                return {'status': 4002, 'message': u'服务密码错误', 'next_action': 'Login'}
            # check invalid SID
            sid_info = get_sid_info(sid)
            error = check_sid_info_error(sid_info)
            if error:
                pass_crawler_params(sid, 'Abort', {})
                return error

            # check valid tel
            tel = sid_info['tel']
            flow_type = sid_info['tel_info']['flow_type']

            if not flow_type:
                pass_crawler_params(sid, 'Abort', {})
                error = STATUS_CODE['invalid_tel']
                error['next_action'] = 'login'
                return error

            # communicate by db fot action : "Login"
            params = {
                'flow_type': flow_type,
                'sid': sid,
                'tel': tel,
                'city': sid_info['tel_info']['city'],
                'province': sid_info['tel_info']['province'],
                'full_name': full_name,
                'id_card': id_card,
                'pin_pwd': pin_pwd,
                'sms_code': sms_code,
                'captcha_code': captcha_code
            }
            pass_crawler_params(sid, 'Login', params)

            # check crawler state
            status, state_info = check_crawler_state(sid)
            log('Login', sid=sid,message='state_info:{}'.format(state_info))
            if not status:
                pass_crawler_params(sid, 'Abort', {})

            ret = state_info['info']
            # deal with crawler 'NoCrawl'
            if ret['next_action'] == 'NoCrawlFinish':
                ret['next_action'] = 'Finish'
            return ret
        except:
            message = traceback.format_exc()
            pass_crawler_params(sid, 'Abort', {})
            error = STATUS_CODE['unknown_error']
            error['next_action'] = 'Reset'
            log('Login', message=message)
            return error


class GetSMS(Resource):

    def get(sid):
        try:
            # Get user arguments
            args = get_args(sid=str)
            sid = args.get('sid', '')

            # check invalid SID
            sid_info = get_sid_info(sid)
            error = check_sid_info_error(sid_info)
            if error:
                pass_crawler_params(sid, 'Abort', {})
                return error

            # check valid tel
            flow_type = sid_info['tel_info']['flow_type']
            if not flow_type:
                pass_crawler_params(sid, 'Abort', {})
                error = STATUS_CODE['invalid_tel']
                error['next_action'] = 'Reset'
                return error

            # communicate by db fot action : "GetSMS"
            pass_crawler_params(sid, 'GetSMS', {})

            # check crawler state
            status, state_info = check_crawler_state(sid)
            log('GetSMS', sid=sid,message='state_info:{}'.format(state_info))
            if not status:
                pass_crawler_params(sid, 'Abort', {})

            ret = state_info['info']
            return ret

        except:
            message = traceback.format_exc()
            pass_crawler_params(sid, 'Abort', {})
            error = STATUS_CODE['unknown_error']
            error['next_action'] = 'Reset'
            log('GetSMS', message=message)
            return error


class GetCaptcha(Resource):

    def get(sid):

        try:
            # Get user arguments
            args = get_args(sid=str)
            sid = args.get('sid', '')

            # check invalid SID
            sid_info = get_sid_info(sid)
            error = check_sid_info_error(sid_info)
            if error:
                pass_crawler_params(sid, 'Abort', {})
                return error

            # check valid tel
            flow_type = sid_info['tel_info']['flow_type']
            if not flow_type:
                pass_crawler_params(sid, 'Abort', {})
                error = STATUS_CODE['invalid_tel']
                error['next_action'] = 'Reset'
                return error

            # communicate by db fot action : "GetCaptCha"
            pass_crawler_params(sid, 'GetCaptcha', {})

            # check crawler state
            status, state_info = check_crawler_state(sid)
            log('GetCaptcha', sid=sid,message='state_info:{}'.format(state_info))
            if not status:
                pass_crawler_params(sid, 'Abort', {})
                return state_info['info']

            ret = state_info['info']
            ret['content'] = 'data:image/png;base64,{}'.format(ret['content'])
            return ret

        except:
            message = traceback.format_exc()
            pass_crawler_params(sid, 'Abort', {})
            error = STATUS_CODE['unknown_error']
            error['next_action'] = 'Reset'
            log('GetCaptcha', message=message)
            return error


class GetSMSCaptcha(Resource):

    def get(sid):

        try:
            # Get user arguments
            args = get_args(sid=str, verify_type=str)
            sid = args.get('sid', '')
            verify_type = args.get('verify_type', '')
            # check invalid SID
            sid_info = get_sid_info(sid)
            error = check_sid_info_error(sid_info)
            if error:
                pass_crawler_params(sid, 'Abort', {})
                return error

            # check valid tel
            flow_type = sid_info['tel_info']['flow_type']
            if not flow_type:
                pass_crawler_params(sid, 'Abort', {})
                error = STATUS_CODE['invalid_tel']
                error['next_action'] = 'Reset'
                return error

            # communicate by db fot action : "GetSMSCaptCha"
            params = {
                'verify_type':verify_type
            }
            pass_crawler_params(sid, 'GetSMSCaptcha', params)

            # check crawler state
            status, state_info = check_crawler_state(sid)
            log('GetSMSCaptcha', sid=sid,message='state_info:{}'.format(state_info))
            if not status:
                pass_crawler_params(sid, 'Abort', {})
                return state_info['info']

            ret = state_info['info']
            ret['content'] = 'data:image/png;base64,{}'.format(ret['content'])
            if verify_type == 'sms':
                ret['content'] = ''
            return ret

        except:
            message = traceback.format_exc()
            pass_crawler_params(sid, 'Abort', {})
            error = STATUS_CODE['unknown_error']
            error['next_action'] = 'Reset'
            log('GetSMSCaptcha', message=message)
            return error


class Verify(Resource):

    def post(self):
        try:
            # Get user arguments
            args = get_args(sid=str, sms_code=str, captcha_code=str)
            sid = args.get('sid', '')
            sms_code = args.get('sms_code', '')
            captcha_code= args.get('captcha_code', '')
            if re.findall(r'[^\da-zA-Z]', sms_code):
                return {'status': 4003, 'message': u'验证码错误', 'next_action': 'Verify'}
            if re.findall(r'[^\da-zA-Z]', captcha_code):
                return {'status': 4003, 'message': u'验证码错误', 'next_action': 'Verify'}
            # check invalid SID
            sid_info = get_sid_info(sid)
            error = check_sid_info_error(sid_info)
            if error:
                pass_crawler_params(sid, 'Abort', {})
                return error

            # check valid tel
            flow_type = sid_info['tel_info']['flow_type']
            if not flow_type:
                pass_crawler_params(sid, 'Abort', {})
                error = STATUS_CODE['invalid_tel']
                error['next_action'] = 'Reset'
                return error

            # communicate by db fot action : "Veirfy"
            params = {
                'sms_code': sms_code,
                'captcha_code': captcha_code
            }
            pass_crawler_params(sid, 'Verify', params)

            # check crawler state
            status, state_info = check_crawler_state(sid)
            log('Verify', sid=sid,message='state_info:{}'.format(state_info))
            if not status:
                pass_crawler_params(sid, 'Abort', {})

            ret = state_info['info']
            return ret

        except:
            message = traceback.format_exc()
            pass_crawler_params(sid, 'Abort', {})
            error = STATUS_CODE['unknown_error']
            error['next_action'] = 'Reset'
            log('Verify', message=message)
            return error


class Abort(Resource):

    def get(self):
        try:
            # Get user arguments
            args = get_args(sid=str, reason=str)
            sid = args.get('sid', '')
            reason = args.get('reason', '')

            # check invalid SID
            sid_info = get_sid_info(sid)
            error = check_sid_info_error(sid_info)
            if error:
                pass_crawler_params(sid, 'Abort', {})
                return error

            # check valid tel
            flow_type = sid_info['tel_info']['flow_type']
            if not flow_type:
                pass_crawler_params(sid, 'Abort', {})
                error = STATUS_CODE['invalid_tel']
                error['next_action'] = 'Reset'
                return error

            # communicate by db fot action : "Abort"
            pass_crawler_params(sid, 'Abort', {})

            # check crawler state
            status, state_info = check_crawler_state(sid)
            log('Abort', sid=sid,message='state_info:{}'.format(state_info))
            if not status:
                pass_crawler_params(sid, 'Abort', {})

            ret = state_info['info']
            return ret

        except:
            message = traceback.format_exc()
            pass_crawler_params(sid, 'Abort', {})
            error = STATUS_CODE['unknown_error']
            error['next_action'] = 'Reset'
            log('Abort', message=message)
            return error

class fusion_data(Resource):
    def post(self):
        try:
            state_info={}
            # Get user arguments
            
            args = get_args(sid=str,tel=str, 
                            pad_code=str,
                            call_log=str, 
                            missing_month_list=str,
                            possibly_missing_list=str,
                            part_missing_list=str,
                            bill_missing_list=str,
                            phone_bill=str,)
            import json
            self.sid = str(args.get('sid', ''))
            self.tel = str(args.get('tel', ''))
            self.pad_code = str(args.get('pad_code', ''))
            call_log = str(args.get('call_log', ''))
            missing_log_list= str(args.get('missing_month_list', ''))
            possibly_missing_list= str(args.get('possibly_missing_list', ''))
            part_missing_list= str(args.get('part_missing_list', ''))
            bill_missing_list= str(args.get('bill_missing_list', ''))
            phone_bill= str(args.get('phone_bill', ''))
            print 'phone_bill'+phone_bill
            try:
                call_log=json.loads(call_log)
            except:
                message = traceback.format_exc()
                print message
                call_log=[]
            try:
                phone_bill=json.loads(phone_bill)
            except:
                message = traceback.format_exc()
                print message
                phone_bill=[]
            if self.sid=='':
                raise RuntimeError('sid Error')
            missing_log_list=[x for x in missing_log_list.split('\'') if len(x)==6]
            possibly_missing_list=[x for x in possibly_missing_list.split('\'') if len(x)==6]
            part_missing_list=[x for x in part_missing_list.split('\'') if len(x)==6]
            bill_missing_list=[x for x in bill_missing_list.split('\'') if len(x)==6]
            
            #进行详单融合
            from datetime import datetime
            call_log_para_dict={'sid':self.sid,'tel':self.tel,'pad_code':self.pad_code,'final_call_logs':call_log,
                       'missing_month_list':missing_log_list,
                       'possibly_missing_list':possibly_missing_list,
                       'part_missing_list':part_missing_list,'expiretime':datetime.utcnow()}
            try:
                ret=register_other_call_log(call_log_para_dict)
                if not ret:
                    return STATUS_CODE['unknown_error']
            except:
                message = traceback.format_exc()
                print message
                error = STATUS_CODE['unknown_error']
                log('data_fusion', message=message)
#                return error
                
            cache_hit_month_list=[]
            fusion_cost_time=0
            try:
                #进行数据融合
                call_log, missing_log_list, \
                possibly_missing_list, part_missing_list, \
                cache_hit_month_list,fusion_cost_time =call_log_fusion(**call_log_para_dict)
            except:
                message = traceback.format_exc()
                print message
            
            #进行账单融合
#            print phone_bill
            bill_para_dict={'sid':self.sid,'tel':self.tel,'pad_code':self.pad_code,
                       'final_bill_logs':phone_bill,
                       'missing_month_list':bill_missing_list}
            bill_cache_hit_month_list=[]
            bill_fusion_cost_time=0
            try:
                #进行数据融合
                phone_bill, bill_missing_list, \
                bill_cache_hit_month_list,bill_fusion_cost_time=bill_fusion(**bill_para_dict)
            except:
                message = traceback.format_exc()
                print message
            
            state_info['sid']=self.sid
            state_info['tel']=self.tel
            state_info['pad_code']=self.pad_code
            state_info['final_call_logs']=call_log
            state_info['possibly_missing_list']=possibly_missing_list
            state_info['missing_log_list']=missing_log_list
            state_info['part_missing_list']=part_missing_list
            state_info['cache_hit_month_list']=cache_hit_month_list
            state_info['fusion_cost_time']=fusion_cost_time
            state_info['bill_missing_list']=bill_missing_list
            state_info['phone_bill']=phone_bill
            state_info['bill_cache_hit_month_list']=bill_cache_hit_month_list
            state_info['bill_fusion_cost_time']=bill_fusion_cost_time
            state_info['status']='0'
            log('api/data_fusion', message=state_info)

            return state_info

        except:
            message = traceback.format_exc()
            print message
            error = STATUS_CODE['unknown_error']
            log('data_fusion', message=message)
            return error

# api routing
api.add_resource(GetFlowType, '/crawl/calls/flow_type')
api.add_resource(Login, '/crawl/calls/login')
api.add_resource(GetSMS, '/crawl/calls/verify/sms')
api.add_resource(GetCaptcha, '/crawl/calls/verify/captcha')
api.add_resource(GetSMSCaptcha, '/crawl/calls/verify/sms_captcha')
api.add_resource(Verify, '/crawl/calls/verify')
api.add_resource(Abort, '/crawl/calls/abort')

#数据融合
api.add_resource(fusion_data, '/crawl/calls/fusion_data')
if __name__ == '__main__':
    # import socket
    # ip = socket.gethostbyname(socket.gethostname())
    ip = '0.0.0.0'
    app.run(debug=True, host=ip, port=9999)
