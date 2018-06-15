# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/6/15 13:44
# @Author   : zhe
# @FileName : crawler.py
# @Project  : PyCharm


import socket
import re
import urllib.parse
import time

def fetch(url):
    sock = socket.socket()
    sock.setblocking(False)
    try:
        sock.connect(('xkcd.com', 80))
    except BlockingIOError:
        pass
    request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(url)
    while True:
        try:
            sock.send(request.encode())
            print('sent')
            break
        except OSError:
            pass

    response = b''
    # chunk = sock.recv(4096)
    while True:
        try:
            chunk = sock.recv(4096)
            if chunk:
                response += chunk
            else:
                break
        except BlockingIOError:
            pass

    # links = parse_links(response)
    # q.add(links)
    print(response.decode())