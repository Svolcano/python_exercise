import struct
import socket
import subprocess

def hel():
    for i in range(10):
        yield i
    print('helo')
    for j in ['a', 'b', 'c']:
        yield j

if __name__ == '__main__':
    for k in hel():
        print(k)