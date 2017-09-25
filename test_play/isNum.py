import struct
import socket
import subprocess

print (subprocess.getstatusoutput)

a = b'192.168d'
b = struct.unpack("2I", a)
print (b)