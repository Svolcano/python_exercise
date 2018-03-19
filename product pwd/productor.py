from os import urandom
from base64 import b64encode


us = urandom(8)
token = b64encode(us).decode('utf8')
print(token)
