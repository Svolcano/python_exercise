import struct
import socket
import subprocess

def hel():
    for i in range(10):
        yield i

    for j in ['a', 'b', 'c']:
        yield j


for k in hel():
    print(k)