# 脸书任务

import requests
import random
import hashlib
from pprint import pprint
from lxml import etree
import json
import re
import time
import re
import mechanize
from urllib import parse
from dama.yundama import verify_captcha

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/601.1.10 (KHTML, like Gecko) Version/8.0.5 Safari/601.1.10",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; ; NCT50_AAP285C84A1328) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
]

UA = random.choice(_USER_AGENTS)


SEED_PAGE = 'https://www.facebook.com/'

header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': SEED_PAGE,
            'Origin': SEED_PAGE,
            'User-Agent': UA,
            'Connection': 'keep-alive',
        }




br = mechanize.Browser()
response1 = br.open(SEED_PAGE)
# follow second link with element text matching regular expression
assert br.viewing_html()
print(br.title())
print(response1.geturl())
print(response1.info())  # headers
print(response1.read())  # body

# br.select_form(name="order")
# # Browser passes through unknown attributes (including methods)
# # to the selected HTMLForm.
# br["cheeses"] = ["mozzarella", "caerphilly"]  # (the method here is __setitem__)
# # Submit current form.  Browser calls .close() on the current response on
# # navigation, so this closes response1
# response2 = br.submit()
#
# # print currently selected form (don't call .submit() on this, use br.submit())
# print br.form
#
# response3 = br.back()  # back to cheese shop (same data as response1)
# # the history mechanism returns cached response objects
# # we can still use the response, even though it was .close()d
# response3.get_data()  # like .seek(0) followed by .read()
# response4 = br.reload()  # fetches from server
#
# for form in br.forms():
# print form
# # .links() optionally accepts the keyword args of .follow_/.find_link()
# for link in br.links(url_regex="python.org"):
# print link
#     br.follow_link(link)  # takes EITHER Link instance OR keyword args
#     br.back()