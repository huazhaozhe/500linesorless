# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/5/8 17:01
# @Author   : zhe
# @FileName : requests_aosa_book.py
# @Project  : PyCharm

import requests

response = requests.get('http://aosabook.org/en/500L/web-server/testpage.html')
print('status code', response.status_code)
print('content length', response.headers['content-length'])
print(response.text)