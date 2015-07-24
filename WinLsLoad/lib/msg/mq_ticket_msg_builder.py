
class MsgBuilder(object):

    def __init__(self):
        pass


    def build_ticket_msg(self, id, appchain, result):
        msg = {}
        msg['id']       = id
        msg['appchain'] = appchain
        msg['result']   = result

        return msg
