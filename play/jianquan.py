#coding:utf-8
import hashlib

def check_sign(api_key, api_secret, time_v, nonce, php_v):
    in_p = [api_key, api_secret, time_v, nonce]
    in_p.sort()
    in_str = ''.join(in_p)
    m = hashlib.md5()
    m.update(in_str)
    v1 = m.hexdigest()
    m2 = hashlib.md5()
    m2.update(v1)
    python_result = m2.hexdigest()
    print php_v, python_result
    print  python_result == php_v
api_key = '0aa2cb33d0eaedc4abe412348045dc8'
api_secret = '0b178ed2d1d049e46472711d8f92bf4'
time_v = '1528700577'
nonce = '6528'
php_v = 'e6d55a837bb6d7ba2ff4cd7d2df0747e' 
check_sign(api_key, api_secret, time_v, nonce, php_v)

api_key = '0aa2cb33d0eaedc4abe412348045dc8'
api_secret = '0b178ed2d1d049e46472711d8f92bf4'