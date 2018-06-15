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
    sock.connect(('xkcd.com', 80))
    request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(url)
    sock.send(request.encode())
    response = b''
    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096)

    # links = parse_links(response)
    # q.add(links)
    print(response.decode())