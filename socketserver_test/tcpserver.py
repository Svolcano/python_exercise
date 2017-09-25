#coding:utf-8
#python3.6

import socketserver

HOST, PORT = "localhost", 49898

class MyTcpHandler(socketserver.BaseRequestHandler):

    def setup(self):
        print("i am in setup")

    def handle(self):
        print("i am in handle")
        print(self.client_address)
        self.data = self.request.recv(1024).strip()
        print(self.data)
        self.request.sendall(self.data.upper())

    def finish(self):
        print("i am in finish")



server = socketserver.TCPServer((HOST, PORT), MyTcpHandler)
server.serve_forever()


