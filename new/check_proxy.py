import random
import requests

proxy_list = ["http://182.254.231.171:8080",
              "http://119.29.169.211:8080",
              "http://111.230.13.192:8080",
              ]

proxy_dict = {
    #"http": random.choice(proxy_list),
    "http":  "http://119.29.169.211:8080",
    "https":  "https://119.29.169.211:8080",
}
url = "http://www.ip.cn/"
resp = requests.get(url,
                    proxies=proxy_dict,
                    )
print(resp.headers)
print(resp.status_code)
print(resp.text)
print("done!@")