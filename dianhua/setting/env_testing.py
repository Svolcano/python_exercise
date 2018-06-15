# -*- coding: utf-8 -*-

# db_config
env = {
    'redis': {
        'host': '172.18.19.101',
        'port': 6379,
        'db': [0, 1, 2, 3, 4, 5],
    },
    'mongo': {
        'host': '172.18.19.101',
        'port': 27017,
        'db': 'crs'
    },
    # 'mysql':{
    #     'user': 'admin',
    #     'password': 'admin',
    #     'host': '172.18.19.155',
    #     'database': 'crawler'
    # },
    'proxies': {
        'launcher': True,
        'port': 8080,
        'timeout': 60,
        'redirects': True,
        'verify': False,
        'check_url': "https://www.baidu.com/duty/copyright.html",
        'try_times': 3,
        'cmcc_ip': [
            "squidbj31.yulore.com",
            "squidbj32.yulore.com",
        ],
        'cucc_ip': [
            "squidbj31.yulore.com",
            "squidbj32.yulore.com",
        ]
    },
}
