import redis

host = '172.18.18.162'
port = 6379
def_db = 1

def clear_all():
    rh = redis.Redis(host=host, port=port)
    rh.flushall()

clear_all()
