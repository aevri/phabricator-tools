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
from __future__ import division
from __future__ import print_function

import BaseHTTPServer
import SocketServer
import multiprocessing
import unittest

import phlurl_request


class HttpReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        self.wfile = None  # for pychecker

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write('OK')


class BasicAuthHttpReqHandler(HttpReqHandler):

    def __init__(self, *args, **kwargs):
        HttpReqHandler.__init__(self, *args, **kwargs)
        self.headers = None  # for pychecker
        self.wfile = None  # for pychecker

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


def create_redirect_handler(host, port):

    class RedirectHttpReqHandler(HttpReqHandler):

        def __init__(self, *args, **kwargs):
            HttpReqHandler.__init__(self, *args, **kwargs)
            self.path = None  # for pychecker
            self.wfile = None  # for pychecker

        def do_GET(self):
            self.send_response(301)
            self.send_header(
                'Location', 'http://%s:%s%s' % (host, port, self.path))
            self.end_headers()
            self.wfile.write('Moved permanently')

    return RedirectHttpReqHandler


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
        self.assertEqual(phlurl_request.join_url(
            'http://example.com/', 'mypage/'), 'http://example.com/mypage/')
        self.assertEqual(phlurl_request.join_url(
            'http://example.com', 'mypage/'), 'http://example.com/mypage/')
        self.assertEqual(phlurl_request.join_url(
            'https://example.com:443/', 'mypage/'), 'https://example.com:443/mypage/')
        self.assertEqual(phlurl_request.join_url(
            'https://example.com:443', 'mypage/'), 'https://example.com:443/mypage/')

    def test_split_url(self):
        self.assertEqual(
            phlurl_request.split_url('https://www.bloomberg.com:80/index'),
            phlurl_request.SplitUrlResult(
                'https://www.bloomberg.com:80/index',
                'https', 'www.bloomberg.com', 80, '/index', None, None))
        self.assertEqual(
            phlurl_request.split_url('HTTPS://WWW.BLOOMBERG.COM:80/INDEX'),
            phlurl_request.SplitUrlResult(
                'HTTPS://WWW.BLOOMBERG.COM:80/INDEX',
                'https', 'www.bloomberg.com', 80, '/INDEX', None, None))
        self.assertEqual(
            phlurl_request.split_url('https://www.bloomberg.com/index'),
            phlurl_request.SplitUrlResult(
                'https://www.bloomberg.com/index',
                'https', 'www.bloomberg.com', None, '/index', None, None))
        self.assertEqual(
            phlurl_request.split_url(
                'https://www.bloomberg.com/index?a=index&b=c'),
            phlurl_request.SplitUrlResult(
                'https://www.bloomberg.com/index?a=index&b=c',
                'https', 'www.bloomberg.com', None, '/index?a=index&b=c', None, None))

    def test_group_urls(self):
        self.assertEqual(
            phlurl_request.group_urls(
                ['http://a.io/a', 'http://a.io/b', 'https://b.io/c']),
            phlurl_request.GroupUrlResult(
                {('a.io', None): [phlurl_request.SplitUrlResult('http://a.io/a',
                                                                'http', 'a.io', None, '/a', None, None),
                                  phlurl_request.SplitUrlResult(
                                      'http://a.io/b',
                                      'http', 'a.io', None, '/b', None, None)]},
                {('b.io', None): [phlurl_request.SplitUrlResult('https://b.io/c',
                                                                'https', 'b.io', None, '/c', None, None)]}))


class HttpTest(unittest.TestCase):

    def __init__(self, data):
        super(HttpTest, self).__init__(data)
        self.httpd_process = None
        self.httpd_host = None
        self.httpd_port = None

    def setUp(self):
        self.httpd_process, self.httpd_host, self.httpd_port = start_httpd(
            HttpReqHandler)

    def tearDown(self):
        self.httpd_process.terminate()

    def test_get(self):
        self.assertEqual(phlurl_request.get('http://%s:%s/index' %
                         (self.httpd_host, self.httpd_port)), (200, 'OK'))

    def test_get_many(self):
        self.assertEqual(
            phlurl_request.get_many(
                ['http://%s:%s/a' % (self.httpd_host, self.httpd_port),
                 'http://%s:%s/b' % (
                     self.httpd_host, self.httpd_port),
                 'http://%s:%s/c' % (self.httpd_host, self.httpd_port)]),
            {'http://%s:%s/a' % (self.httpd_host, self.httpd_port): (200, 'OK'),
             'http://%s:%s/b' % (self.httpd_host, self.httpd_port): (200, 'OK'),
             'http://%s:%s/c' % (self.httpd_host, self.httpd_port): (200, 'OK')})


class HttpTest_Auth(unittest.TestCase):

    def __init__(self, data):
        super(HttpTest_Auth, self).__init__(data)
        self.httpd_process = None
        self.httpd_host = None
        self.httpd_port = None

    def setUp(self):
        self.httpd_process, self.httpd_host, self.httpd_port = start_httpd(
            BasicAuthHttpReqHandler)

    def tearDown(self):
        self.httpd_process.terminate()

    def test_get(self):
        self.assertEqual(
            phlurl_request.get('http://%s:%s/index' %
                               (self.httpd_host, self.httpd_port)),
            (401, 'Authentication required'))
        self.assertEqual(
            phlurl_request.get('http://foo:bar@%s:%s/index' %
                               (self.httpd_host, self.httpd_port)),
            (200, 'Basic Zm9vOmJhcg=='))

    def test_get_many(self):
        self.assertEqual(
            phlurl_request.get_many(
                ['http://%s:%s/index' % (self.httpd_host, self.httpd_port),
                 'http://foo:bar@%s:%s/index' % (
                     self.httpd_host, self.httpd_port),
                 'http://baz:buz@%s:%s/index' % (self.httpd_host, self.httpd_port)]),
            {'http://%s:%s/index' % (self.httpd_host, self.httpd_port): (401, 'Authentication required'),
             'http://foo:bar@%s:%s/index' % (self.httpd_host, self.httpd_port): (200, 'Basic Zm9vOmJhcg=='),
             'http://baz:buz@%s:%s/index' % (self.httpd_host, self.httpd_port): (200, 'Basic YmF6OmJ1eg==')})


class HttpTest_Redirect(unittest.TestCase):

    def __init__(self, data):
        super(HttpTest_Redirect, self).__init__(data)
        self.dst_httpd_process = None
        self.dst_httpd_host = None
        self.dst_httpd_port = None
        self.src_httpd_process = None
        self.src_httpd_host = None
        self.src_httpd_port = None

    def setUp(self):
        self.dst_httpd_process, self.dst_httpd_host, self.dst_httpd_port = start_httpd(
            BasicAuthHttpReqHandler)
        self.src_httpd_process, self.src_httpd_host, self.src_httpd_port = start_httpd(
            create_redirect_handler(self.dst_httpd_host,
                                    self.dst_httpd_port))

    def tearDown(self):
        self.src_httpd_process.terminate()
        self.dst_httpd_process.terminate()

    def test_get(self):
        self.assertEqual(phlurl_request.get('http://%s:%s/index' %
                         (self.src_httpd_host, self.src_httpd_port)), (200, 'OK'))



# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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