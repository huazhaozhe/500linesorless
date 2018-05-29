# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/5/8 17:13
# @Author   : zhe
# @FileName : server.py
# @Project  : PyCharm

from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class ServerException(Exception):
    pass

class case_no_file():
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))

class case_existing_file():
    def test(self, handler):
        return os.path.isfile(handler.full_path)
    def act(self, handler):
        handler.handle_file(handler.handle_file)

class case_always_fail():
    def test(self, handler):
        return True
    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

class case_directory_index_file():
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')
    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))
    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class case_directory_no_index_file(case_directory_index_file):
    def act(self, handler):
        handler.list_dir(handler.full_path)




class RequestHandler(BaseHTTPRequestHandler):

    Page = '''
        <html>
        <body>
        <table>
        <tr>  <td>Header</td>         <td>Value</td>          </tr>
        <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
        <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
        <tr>  <td>Client port</td>    <td>{client_port}</td>  </tr>
        <tr>  <td>Command</td>        <td>{command}</td>      </tr>
        <tr>  <td>Path</td>           <td>{path}</td>         </tr>
        </table>
        </body>
        </html>
    '''

    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
    """

    Listing_Page = '''
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
    '''


    Case = [
        case_no_file(),
        case_existing_file(),
        case_directory_index_file(),
        case_always_fail(),

    ]

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            buildets = [
                '<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')
            ]
            page = self.Listing_Page.format('\n'.join(buildets))
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handler_error(msg)


    def do_GET(self):

        # if self.path == '/':
        #     self.handle_home()

        try:
            full_path = os.getcwd() + self.path
            if not os.path.exists(full_path):
                raise ServerException("'{0}' not found".format(self.path))
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            elif os.path.isdir(full_path):
                self.handle_dir(full_path)
            else:
                raise ServerException("Unknown object '{0}'".format(self.path))
        except Exception as msg:
            self.handle_error(msg)

    def handle_home(self):
        content = self.create_page()
        self.send_content(content)

    def handle_dir(self, full_path):
        content = self.list_dir(full_path)
        self.send_content(content)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'r') as reader:
                content = reader.read()
                print(content)
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read:{1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content.encode())

    def create_page(self):
        values = {
            'date_time': self.date_time_string(),
            'client_host': self.client_address[0],
            'client_port': self.client_address[1],
            'command': self.command,
            'path': self.path,
        }
        print(values)
        self.page = self.Page.format(**values)
        return self.page


if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    print('server run...')
    server.serve_forever()
