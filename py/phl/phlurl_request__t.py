"""Test suite for phlurl_request."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] URL utilities work correctly
# [ B] URL grouping works correctly
# [ C] Http requests can be issued using URLs
# [ D] Connections to host are reused for subsequent requests to same host/port
# [ E] Basic authentication is used if username/password details are provided
# [ F] '301 moved permanently' HTTP redirection is handled properly
# -----------------------------------------------------------------------------
# Tests:
# [ A] Test.test_join_url
# [ A] Test.test_split_url
# [ B] Test.test_group_urls
# [ C] HttpTest.test_get
# [ D] HttpTest.test_get_many
# [CE] HttpTest_Auth.test_get
# [DE] HttpTest_Auth.test_get_many
# =============================================================================

from __future__ import absolute_import

import unittest

import phlurl_request

import multiprocessing
import BaseHTTPServer
import SocketServer

class HttpReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write('OK')


class BasicAuthHttpReqHandler(HttpReqHandler):

    def do_GET(self):
        auth = self.headers.getheader('Authorization')
        if auth == None:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('Authentication required')
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(auth)


def httpd_serve_forever(parent_pipe, req_handler):
    httpd = SocketServer.TCPServer(("localhost", 0), req_handler, False)
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()
    parent_pipe.send(httpd.server_address)
    parent_pipe.close()
    httpd.serve_forever()


def start_httpd(request_handler):
    parent_conn, child_conn = multiprocessing.Pipe(False)
    
    httpd_process = multiprocessing.Process(target=httpd_serve_forever,
                                            args=(child_conn, request_handler,))
    httpd_process.start()
    child_conn.close()
    
    httpd_host, httpd_port = parent_conn.recv()
    return (httpd_process, httpd_host, httpd_port)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_join_url(self):
        self.assertEqual(phlurl_request.join_url('http://example.com/', 'mypage/'), 'http://example.com/mypage/')
        self.assertEqual(phlurl_request.join_url('http://example.com', 'mypage/'), 'http://example.com/mypage/')
        self.assertEqual(phlurl_request.join_url('https://example.com:443/', 'mypage/'), 'https://example.com:443/mypage/')
        self.assertEqual(phlurl_request.join_url('https://example.com:443', 'mypage/'), 'https://example.com:443/mypage/')

    def test_split_url(self):
        self.assertEqual(phlurl_request.split_url('https://www.bloomberg.com:80/index'),
                         phlurl_request.SplitUrlResult('https://www.bloomberg.com:80/index',
                                                       'https', 'www.bloomberg.com', 80, '/index', None, None))
        self.assertEqual(phlurl_request.split_url('HTTPS://WWW.BLOOMBERG.COM:80/INDEX'),
                         phlurl_request.SplitUrlResult('HTTPS://WWW.BLOOMBERG.COM:80/INDEX',
                                                       'https', 'www.bloomberg.com', 80, '/INDEX', None, None))
        self.assertEqual(phlurl_request.split_url('https://www.bloomberg.com/index'),
                         phlurl_request.SplitUrlResult('https://www.bloomberg.com/index',
                                                       'https', 'www.bloomberg.com', None, '/index', None, None))
        self.assertEqual(phlurl_request.split_url('https://www.bloomberg.com/index?a=index&b=c'),
                         phlurl_request.SplitUrlResult('https://www.bloomberg.com/index?a=index&b=c',
                                                       'https', 'www.bloomberg.com', None, '/index?a=index&b=c', None, None))


    def test_group_urls(self):
        self.assertEqual(phlurl_request.group_urls(['http://a.io/a', 'http://a.io/b', 'https://b.io/c']),
                         phlurl_request.GroupUrlResult(
                             {('a.io', None): [phlurl_request.SplitUrlResult('http://a.io/a',
                                                                             'http', 'a.io', None, '/a', None, None),
                                               phlurl_request.SplitUrlResult('http://a.io/b',
                                                                             'http', 'a.io', None, '/b', None, None)]},
                             {('b.io', None): [phlurl_request.SplitUrlResult('https://b.io/c',
                                                                             'https', 'b.io', None, '/c', None, None)]}))


class HttpTest(unittest.TestCase):

    def setUp(self):
        self.httpd_process, self.httpd_host, self.httpd_port = start_httpd(HttpReqHandler)

    def tearDown(self):
        self.httpd_process.terminate()

    def test_get(self):   
        self.assertEqual(phlurl_request.get('http://%s:%s/index' % (self.httpd_host, self.httpd_port)), 'OK')

    def test_get_many(self):
        self.assertEqual(phlurl_request.get_many(['http://%s:%s/a' % (self.httpd_host, self.httpd_port),
                                                  'http://%s:%s/b' % (self.httpd_host, self.httpd_port),
                                                  'http://%s:%s/c' % (self.httpd_host, self.httpd_port)]),
                         {'http://%s:%s/a' % (self.httpd_host, self.httpd_port): 'OK',
                          'http://%s:%s/b' % (self.httpd_host, self.httpd_port): 'OK',
                          'http://%s:%s/c' % (self.httpd_host, self.httpd_port): 'OK'})


class HttpTest_Auth(unittest.TestCase):

    def setUp(self):
        self.httpd_process, self.httpd_host, self.httpd_port = start_httpd(BasicAuthHttpReqHandler)

    def tearDown(self):
        self.httpd_process.terminate()

    def test_get(self):   
        self.assertEqual(phlurl_request.get('http://%s:%s/index' % (self.httpd_host, self.httpd_port)), 'Authentication required')
        self.assertEqual(phlurl_request.get('http://foo:bar@%s:%s/index' % (self.httpd_host, self.httpd_port)), 'Basic Zm9vOmJhcg==')

    def test_get_many(self):
        self.assertEqual(phlurl_request.get_many(['http://%s:%s/index' % (self.httpd_host, self.httpd_port),
                                                  'http://foo:bar@%s:%s/index' % (self.httpd_host, self.httpd_port),
                                                  'http://baz:buz@%s:%s/index' % (self.httpd_host, self.httpd_port)]),
                         {'http://%s:%s/index' % (self.httpd_host, self.httpd_port): 'Authentication required',
                          'http://foo:bar@%s:%s/index' % (self.httpd_host, self.httpd_port): 'Basic Zm9vOmJhcg==',
                          'http://baz:buz@%s:%s/index' % (self.httpd_host, self.httpd_port): 'Basic YmF6OmJ1eg=='})


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
# ------------------------------ END-OF-FILE ----------------------------------
