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

    def result(self):
        return self.result

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)
    def __iter__(self):
        yield self
        return self.result

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


def connect(sock, address):
    f = Future()
    sock.setblocking(False)
    try:
        sock.connect(address)
    except BlockingIOError:
        pass
    def on_connected():
        f.set_result(None)
    selector.register(sock.fileno(), EVENT_WRITE, on_connected)
    yield from f
    selector.unregister(sock.fileno())

def read(sock):
    f = Future()
    def on_readable():
        f.set_result(sock.recv(4096))
    selector.register(sock.fileno(), EVENT_READ, on_readable)
    chunk = yield f
    selector.unregister(sock.fileno())
    return chunk

def read_all(sock):
    response = []
    chunk = yield from read(sock)
    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)
    return b''.join(response)


class Fetchar():
    def __init__(self, host, url, port=80):
        self.response = b''
        self.url = url
        self.sock = None
        self.host = host
        self.port = port


    def fetch(self):
        global concurrency_achieved, stopped
        concurrency_achieved = max(concurrency_achieved, len(urls_todo))
        sock = socket.socket()
        yield from connect(sock, (self.host, self.port))
        get = 'GET {0} HTTP/1.0\t\nHost: {1}\r\n\r\n'.format(self.url, self.host)
        sock.send(get.encode())
        self.response = yield from read_all(sock)
        self.parse_links()
        urls_todo.remove(self.url)
        if not urls_todo:
            stopped = True
        print(self.url)


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
            return
        if not self._is_html():
            print('url {} not html'.format(self.url))
            return
        urls = set(re.findall(r'''(?i)href=["']?([^\s"'<>]+)''', self.body()))
        # links = set()
        for url in urls:
            normalized = urllib.parse.urljoin(self.url, url)
            parts = urllib.parse.urlparse(normalized)
            if parts.scheme not in ('', 'http', 'https'):
                continue
            host, port = urllib.parse.splitport(parts.netloc)
            if host and host.lower() not in (self.host, 'www.'+self.host):
                continue
            defragmented, frag = urllib.parse.urldefrag(parts.path)
            # links.add(defragmented)
        # return links
            if defragmented not in seen_urls:
                urls_todo.add(defragmented)
                seen_urls.add(defragmented)
                Task(Fetchar(self.host, defragmented, self.port).fetch())

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
        callback()

print('{} URLs fetched in {:.1f} seconds, achieved concurrency = {}'.format(
    len(seen_urls),
    time.time() - start_time,
    concurrency_achieved
))

