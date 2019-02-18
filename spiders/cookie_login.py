import requests
import random

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/601.1.10 (KHTML, like Gecko) Version/8.0.5 Safari/601.1.10",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; ; NCT50_AAP285C84A1328) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
]

UA = random.choice(_USER_AGENTS)

c = {'Q': 'u%3D%25O0%25P1%25PN%25Q3%25O7%25R5%26n%3D%26le%3DZGR4AmxlAmDyAQOkpF5wo20%3D%26m%3DZGZ2WGWOWGWOWGWOWGWOWGWOBGt3%26qid%3D328784150%26im%3D1_t01386b81c31e58d8dd%26src%3Dpcw_so%26t%3D1', 'T': 's%3D8b7d6d31753aab39150f99b9bbdf4827%26t%3D1550147779%26lm%3D%26lf%3D2%26sk%3D701f3795f915c8838f7da100e8e2b966%26mt%3D1550147779%26rc%3D%26v%3D2.0%26a%3D1', 'quCapStyle': '2', 'quCryptCode': 'D6TqMQxFspnADE7diMHWEZQBqd8U8LXH%252FiwVr6yuxayCn4DcH%252Bxarv56kXDG0jl1'}

header = {'Accept': 'application/json, text/plain, */*',
 'Host': 'kuaichuan.360.cn',
 'Referer': 'http://kuaichuan.360.cn/',
 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
               '(KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}

resp = requests.get('http://kuaichuan.360.cn/user/detail', headers=header, cookies=c)
print(resp.content.decode('utf-8'))