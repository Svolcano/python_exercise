import logging
import PAM

logger = logging.getLogger(__name__)

def verify_passwd(user, password):
    def pam_conv(auth, query_list):
        resp = []
        for i in range(len(query_list)):
            query, type = query_list[i]
            if type == PAM.PAM_PROMPT_ECHO_ON:
                val = user
                resp.append((val, 0))
            elif type == PAM.PAM_PROMPT_ECHO_OFF:
                val = password
                resp.append((val, 0))
            elif type == PAM.PAM_PROMPT_ERROR_MSG or type == PAM.PAM_PROMPT_TEXT_INFO:
                print query
                resp.append(('', 0));
            else:
                print query
        return resp
    res = -3
    service = 'passwd'

    auth = PAM.pam()
    auth.start(service)
    auth.set_item(PAM.PAM_USER, user)
    auth.set_item(PAM.PAM_CONV, pam_conv)
    try:
        auth.authenticate()
        auth.acct_mgmt()
    except PAM.error, resp:
        logger.info('Go away! (%s)' % resp)

        # user not exist
        if 10 == resp[1]:
            res = -1

        # password not match
        if 7  == resp[1]:
            res = -2
    except:
        logger.info('Internal error')
        res = -3
    else:
        res = 0

    return res

