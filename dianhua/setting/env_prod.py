# -*- coding: utf-8 -*-

# db_config
env = {
    'redis': {
        'host': '172.18.21.197',
        'port': 6379,
        'db': [0, 1, 2, 3, 4, 5],
    },
    'mongo': {
        'host': '172.18.21.117',
        'port': 27017,
        'db': 'crs'
    },
    # 'mysql':{
    #     'user': 'admin',
    #     'password': 'admin',
    #     'host': '172.18.19.155',
    #     'database': 'crawler'
    # },
    'proxies':{
        'launcher': True,
        'port': 8080,
        'timeout': 60,
        'redirects': True,
        'verify': False,
        'check_url': "https://www.baidu.com/duty/copyright.html",
        'try_times': 3,
        'cmcc_ip': [
            "squidbj01.yulore.com",
            "squidbj02.yulore.com",
            "squidbj03.yulore.com",
            "squidbj04.yulore.com",
            "squidbj05.yulore.com",
            "squidbj06.yulore.com",
            "squidbj07.yulore.com",
            "squidbj08.yulore.com",
            "squidbj09.yulore.com",
            "squidbj10.yulore.com",
            "squidbj11.yulore.com",
            "squidbj12.yulore.com",
            "squidbj13.yulore.com",
            "squidbj14.yulore.com",
            "squidbj15.yulore.com",
            "squidbj16.yulore.com",
            "squidbj17.yulore.com",
            "squidbj18.yulore.com",
            "squidbj19.yulore.com",
            "squidbj20.yulore.com",
            "squidbj21.yulore.com",
            "squidbj22.yulore.com",
            "squidbj23.yulore.com",
            "squidbj24.yulore.com",
            "squidbj25.yulore.com",
            "squidbj26.yulore.com",
            "squidbj27.yulore.com",
            "squidbj28.yulore.com",
            "squidbj29.yulore.com",
            "squidbj30.yulore.com",
        ],
        'cucc_ip': [
            "squidsh-unicom01.yulore.com",
            "squidsh-unicom02.yulore.com",
            "squidsh-unicom03.yulore.com",
            "squidsh-unicom04.yulore.com",
            "squidsh-unicom05.yulore.com",
            "squidsh-unicom06.yulore.com",
            "squidsh-unicom07.yulore.com",
            "squidsh-unicom08.yulore.com",
            "squidsh-unicom09.yulore.com",
            "squidsh-unicom10.yulore.com",
        ]
    },
}
