#-*- coding: utf-8 -*-
import importlib
from api_config import ENV

env = importlib.import_module('setting.env_{}'.format(ENV)).env

# 是否启用代理
CONFIG_IS_OPEN = env['proxies']['launcher']

PROXIES_PORT = env['proxies']['port']

TIMEOUT = env['proxies']['timeout']

ALLOW_REDIRECTS = env['proxies']['redirects']

VERIFY = env['proxies']['verify']

IS_IP_AVAILABLE_URL = env['proxies']['check_url']

TRY_TIMES = env['proxies']['try_times']

PROXIES_IP_POOLS = env['proxies']['cmcc_ip']

PROXIES_UNICOM_IP_POOLS = env['proxies']['cucc_ip']
