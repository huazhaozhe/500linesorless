# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/5/8 17:13
# @Author   : zhe
# @FileName : server.py
# @Project  : PyCharm

from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):

    Page = '''
    <html>
    <body>
    <p>Hello, web!</p>
    </body>
    </html>
    '''

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(self.Page)))
        self.end_headers()
        self.wfile.write(self.Page.encode())

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    print('server run...')
    server.serve_forever()
