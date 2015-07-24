import logging
import socket

logger = logging.getLogger(__name__)

def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        result = sock.connect_ex((ip,port))
    except Exception,e:
        sock.close()
        logger.info(e)
        return 1        

    sock.close()
    return result

if __name__ == '__main__':
    for i in range(0,70000):
        check_port('gw1',i)

