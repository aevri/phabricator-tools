"""Start a local webserver which intermittently fails."""

from __future__ import absolute_import

import BaseHTTPServer
import argparse
import os
import random


class _NotFoundError(Exception):
    pass


class _RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, program_args, *args):
        self._program_args = program_args
        self.path = None  # for pychecker
        self.wfile = None  # for pychecker
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):

        if random.randrange(100) < self._program_args.fail_percent:
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><body><h1>random fail</h1></body></html>")
            self.wfile.close()

        try:
            content = self._get_content()
        except _NotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><body><h1>404</h1></body></html>")
            self.wfile.close()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content)
            self.wfile.close()

    def _get_content(self):

        content = None

        path = self.path[1:]

        if os.path.isfile(path):
            with open(path) as f:
                content = f.read()
        else:
            raise _NotFoundError(self.path)

        return content


def _request_handler_factory(instaweb_args):

    def factory(*args):
        return _RequestHandler(instaweb_args, *args)

    return factory


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--port',
        metavar="PORT",
        type=int,
        default=8000,
        help="port to serve pages on")

    parser.add_argument(
        '--fail-percent',
        metavar="INT",
        type=int,
        default=10,
        help="port to serve pages on")

    args = parser.parse_args()

    # start a webserver
    server_address = ('', args.port)
    factory = _request_handler_factory(args)
    httpd = BaseHTTPServer.HTTPServer(server_address, factory)
    httpd.serve_forever()


if __name__ == '__main__':
    main()

#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------- END-OF-FILE ----------------------------------
