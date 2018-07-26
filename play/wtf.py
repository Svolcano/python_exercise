import requests
import json
import csv


tel = '075561884778'
name = '赛门科技'
url = ("http://172.18.19.152:8000/v2/qualityname?"
f"tel={tel}&third_party_api=1"
f"&name={name}"
"&switch=1_2_3")

resp = requests.get(url)
print(json.loads(resp.text))