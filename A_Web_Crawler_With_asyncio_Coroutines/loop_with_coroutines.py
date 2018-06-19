# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/6/19 10:18
# @Author   : zhe
# @FileName : loop_with_coroutines.py
# @Project  : PyCharm


import re
import socket
import urllib.parse
import time
from selectors import *

selector = DefaultSelector()
urls_todo = set()
seen_urls = set()
concurrency_achieved = 0
stopped = False


class Future():
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)

class Task():
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        try:
            next_future = self.coro.send(future.result)
        except StopIteration:
            return
        next_future.add_done_callback(self.step)


class Fetchar():
    def __init__(self, host, url, port=80):
        self.response = b''
        self.url = url
        self.sock = None
        self.host = host
        self.port = port


    def fetch(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)
        try:
            self.sock.connect((self.host, self.port))
        except BlockingIOError:
            pass
        f = Future()
        # 合并connected
        def on_connected(key, mask):
            f.set_result(key)
        selector.register(
            self.sock.fileno(),
            EVENT_WRITE,
            on_connected
        )
        key = yield f
        self.connected(key, None)
        # selector.unregister(self.sock.fileno())
        # print('connected!')

    def connected(self, key, mask):
        print('url {} connected!'.format(self.url))
        selector.unregister(key.fd)
        request = 'GET {0} HTTP/1.0\r\nHost: {1}\r\n\r\n'.format(self.url, self.host)
        self.sock.send(request.encode())
        selector.register(
            key.fd,
            EVENT_READ,
            self.read_response
        )

    def read_response(self, key, mask):
        global stopped
        chunk = self.sock.recv(4096)
        if chunk:
            self.response += chunk
        else:
            time.sleep(1)
            self.sock.close()
            selector.unregister(key.fd)
            links = self.parse_links()
            for link in links.difference(seen_urls):
                urls_todo.add(link)
                print('new link:', link)
                Task(Fetchar(self.host, link, self.port).fetch())
            seen_urls.update(links)
            urls_todo.remove(self.url)
            # print(seen_urls, urls_todo)
            if not urls_todo:
                stopped = True

    def parse_links(self):
        if not self.response:
            print('url error: {}'.format(self.url))
            return set()
        if not self._is_html():
            print('url {} not html'.format(self.url))
            return set()
        urls = set(re.findall(r'''(?i)href=["']?([^\s"'<>]+)''', self.body()))
        links = set()
        for url in urls:
            normalized = urllib.parse.urljoin(self.url, url)
            parts = urllib.parse.urlparse(normalized)
            if parts.scheme not in ('', 'http', 'https'):
                continue
            host, port = urllib.parse.splitport(parts.netloc)
            if host and host.lower() not in (self.host, 'www.'+self.host):
                continue
            defragmented, frag = urllib.parse.urldefrag(parts.path)
            links.add(defragmented)
        return links

    def _is_html(self):
        head, body = self.response.split(b'\r\n\r\n', 1)
        headers = dict(h.split(': ') for h in head.decode().split('\r\n')[1:])
        return headers.get('Content-Type', headers.get('Content-type', '')).startswith('text/html')

    def body(self):
        body = self.response.split(b'\r\n\r\n', 1)[1]
        return body.decode()

start_time = time.time()
# fetcher = Fetchar('www.nbbaocheng.com', '/', 80)
fetcher = Fetchar('huazhaozhe.info', '/', 80)
seen_urls.update([fetcher.url])
urls_todo.update([fetcher.url])
Task(fetcher.fetch())

while not stopped:
    events = selector.select()
    for event_key, event_mask in events:
        callback = event_key.data
        callback(event_key, event_mask)

print('{} URLs fetched in {:.1f} seconds, achieved concurrency = {}'.format(
    len(seen_urls),
    time.time() - start_time,
    concurrency_achieved
))

