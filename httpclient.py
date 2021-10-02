#!/usr/bin/env python3
# coding: utf-8
# Copyright 2021 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Steven Heung
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
from typing import Tuple
# you may use urllib to encode data appropriately
import urllib.parse

## This assignment is heavily referenced from MDN Web Docs for HTTP request formats
## Author: Mozilla
## URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
DEBUG = True

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self) -> str:
        return f"Code: {self.code}\r\nBody:\r\n{self.body}"

    def __repr__(self) -> str:
        return self.__str__()

class HTTPClient(object):

    def __init__(self):
        super().__init__()
        self.socket = None

    def connect(self, host, port):
        '''Connect to the host:port and set the socket object'''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def parse_url(self, url) -> Tuple[int, str, str]:
        '''Parse the URL and return port, host and path'''
        # first, split the HTTP/HTTPS header and get the path
        specifiedPort = url.split(":")[-1].split("/")[0]
        path = url.split("//")[-1]
        httpType = url.split("//")[0].strip()
        try:
            port = int(specifiedPort)
        except ValueError:
            # We do not handle https
            port = 80

        # next, get the host and path
        items = [x for x in path.split("/") if x] # remove empty items
        host = items[0].split(":")[0] # host is the first item in list, and remove potential specificed port ':'
        items.pop(0)

        if len(items) > 0:
            path = '/' + '/'.join(items)
        else:
            path = '/'

        if DEBUG:
            print("Port:", port)
            print("Host:", host)
            print("Path:", path)
        return (port, host, path)

    '''
    def parse_url(self, url) -> Tuple[int, str, str]:
        result = urllib.parse.urlparse(url)
        port = result.port
        host = result.netloc.split(':')[0]
        path = result.path
        if not path:
            path = '/'
        
        if DEBUG:
            print("Port:", port)
            print("Host:", host)
            print("Path:", path)

        return (port, host, path)
    '''

    def get_code(self, result) -> int:
        '''Parse the HTTP response code'''
        try:
            code = result.split()[1]
            code = int(code)
        except (ValueError, IndexError):
            code = 500

        return code


    def get_body(self, result) -> str:
        '''Parse and get the response body'''
        body = result.split("\r\n")[-1]
        return body


    def sendall(self, data):
        '''Send the data with the given socket. '''
        if self.socket:
            self.socket.sendall(data.encode('utf-8'))
        else:
            print("Socket not initialized")
        
    def close(self):
        '''Close the socket'''
        if self.socket:
            self.socket.close()

    
    def recvall(self, sock) -> str:
        '''Read everything from the socket'''
        if not sock:
            print("Socket must be set!")
            return

        buffer = bytearray()
        done = False
        count = 1
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
            count += 1
        return buffer.decode('utf-8')

    def GET(self, url, args=None) -> HTTPResponse:
        '''Performs HTTP/1.1 GET'''
        port, host, path = self.parse_url(url)

        try:
            self.connect(host, port)
        except:
            print("Invalid Host or Port!")
            return None

        # Detect and insert query string. Only accept Dictionaries. 
        if args:
            if type(args) == dict:
                args = dict(args)
                queryString = ""
                for key, value in args.items():
                    temp = f"{key}={value}&"
                    queryString += temp
                path += "?" + queryString

        data = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\n\r\n"

        if DEBUG:
            print("GET request:", data)

        self.sendall(data)

        result = self.recvall(self.socket)
        code = self.get_code(result)
        body = self.get_body(result)

        return HTTPResponse(code, body)

    def POST(self, url, args=None) -> HTTPResponse:
        '''Performs HTTP/1.1 POST'''
        port, host, path = self.parse_url(url)

        try:
            self.connect(host, port)
        except:
            print("Invalid Host or Port!")
            return 

        data = f"POST {path} HTTP/1.1\r\nHost: {host}\r\n"

        if args: # check if args is supplied
            if type(args) == dict:
                args = dict(args)
                data += "Content-Type: application/x-www-form-urlencoded\r\n"
                body = ""
                for key, value in args.items():
                    temp = f"{key}={value}&"
                    body += temp
                body = body[:-1] # Remove the last &

                contentLength = len(body)
                data += f"Content-Length: {contentLength}\r\n\r\n"
                data += body
            else:
                data += "Content-Type: text/plain\r\n"
                data += f"Content-Length: {len(args)}\r\n"
                data += args
        else:
            # Set content type to plain test and 0 content length
            data += "Content-Type: text/plain\r\nContent-Length: 0\r\n\r\n"

        if DEBUG:
            print("POST request:", data)

        self.sendall(data)

        result = self.recvall(self.socket)
        code = self.get_code(result)
        body = self.get_body(result)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None) -> HTTPResponse:
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    client.GET("")
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
