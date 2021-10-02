#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
from typing import Tuple
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def __init__(self):
        super().__init__()
        self.socket = None

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def parse_url(self, url) -> Tuple[int, str, str]:
        # first, split the HTTP/HTTPS header and get the path
        print(url)
        specifiedPort = url.split(":")[-1].split("/")[0]
        path = url.split("//")[-1]
        httpType = url.split("//")[0].strip()
        try:
            port = int(specifiedPort)
        except ValueError:
            if httpType == "https:":
                port = 443
            else:
                port = 80

        # next, get the host and path
        items = [x for x in path.split("/") if x] # remove empty items
        host = items[0].split(":")[0] # host is the first item in list, and remove potential specificed port ':'
        items.pop(0)

        if len(items) > 0:
            path = '/'.join(items)
        else:
            path = '/'

        print("Port:", port)
        print("Host:", host)
        print("Path:", path)
        return (port, host, path)

    def get_code(self, result) -> int:
        code = result.split()[1]
        
        try:
            code = int(code)
        except ValueError:
            code = 500

        return code


    def get_body(self, result) -> str:
        body = result.split("\r\n")[-1]
        return body


    def sendall(self, data):
        if self.socket:
            self.socket.sendall(data.encode('utf-8'))
        else:
            print("Socket not initialized")
        
    def close(self):
        if self.socket:
            self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        count = 1
        while not done:
            print("recovering data:", count)
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
            count += 1
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        port, host, path = self.parse_url(url)

        try:
            self.connect(host, port)
        except:
            print("Invalid Host or Port!")

        data = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"

        self.sendall(data)

        result = self.recvall(self.socket)
        code = self.get_code(result)
        body = self.get_body(result)

        print("Code:", code)
        print("Body:", body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ''
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
