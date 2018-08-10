import redis
import ujson


host = '172.18.18.162'
port = 6379

rh = redis.Redis(host=host, port=port, db=1)

all_keys = rh.keys('WE*')
res = []
c = 1000
for k in all_keys:
    v = rh.get(k)
    res.append((k.decode(), ujson.loads(v)))
    c -= 1
    print(c)
    if c == 0:
        break
print('get done')
with open("cache.txt", 'w', encoding='utf8') as wh:
    for v in res:
        wh.write(f"{v[0]}:{v[1]}\n")
        