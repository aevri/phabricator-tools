"""conduit-proxy - a webserver for proxying connections to conduit.

It's useful to be able to create admin users for role-accounts in Phabricator
so that they may be able to perform tasks on behalf of users. For installs that
serve a lot of users, the amount of role accounts could get out of hand and
become difficult to audit.

Conduit-proxy allows a single admin role-account user to be re-used without
giving away admin credentials directly to multiple parties.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import argparse
import BaseHTTPServer
import json
import urlparse

import phlsys_conduit
import phlsys_makeconduit

_USAGE_EXAMPLES = """
"""

# TODO: consider thread-safety
# TODO: multiple conduit destinations
# TODO: authentication
# TODO: logging
# TODO: incoming https


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    phlsys_makeconduit.add_argparse_arguments(parser)

    parser.add_argument(
        '--port',
        metavar="PORT",
        type=int,
        default=8000,
        help="port to serve the conduit on")

    args = parser.parse_args()

    # start a webserver
    server_address = ('', args.port)
    factory = _request_handler_factory(args)
    httpd = BaseHTTPServer.HTTPServer(server_address, factory)
    httpd.serve_forever()


class _RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, conduitproxy_args, *args):
        self.__conduitproxy_args = conduitproxy_args
        self.__conduit = phlsys_makeconduit.make_conduit(
            self.__conduitproxy_args.uri,
            self.__conduitproxy_args.user,
            self.__conduitproxy_args.cert)

        self.path = None  # for pychecker
        self.wfile = None  # for pychecker
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):

        # do this before sending any response as we may raise an exception
        content = self.__get_content(self.__get_post_body())

        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(content)
        self.wfile.close()

    def __get_content(self, post_body):
        conduit_method = self.path[5:]
        query_string_data = urlparse.parse_qs(post_body)
        params_data = query_string_data['params'][0]
        conduit_data = json.loads(params_data)
        conduit_proxy_data = conduit_data.get('__conduit__', None)

        self.__handle_act_as_user(conduit_proxy_data)

        print
        print conduit_proxy_data
        print conduit_method
        print conduit_data
        print
        if conduit_method == 'conduit.connect':
            response = {
                "result": {},
                "error_code": phlsys_conduit.CONDUITPROXY_ERROR_CONNECT,
                "error_info": "This is a conduit proxy, no need to connect",
            }
        else:
            response = self.__conduit.raw_call(conduit_method, conduit_data)
        content = json.dumps(response)
        print content
        print
        return content

    def __get_post_body(self):
        content_len = int(self.headers.getheader('content-length', 0))
        return self.rfile.read(content_len)

    def __handle_act_as_user(self, conduit_proxy_data):
        act_as_user = None
        if conduit_proxy_data:
            # Note that we may throw here if conduit_proxy_data is not a dict,
            # this is ok because the BaseHTTPRequestHandler will handle it for
            # us.
            # TODO: check assumption that it handles this for us
            act_as_user = conduit_proxy_data.get('actAsUser', None)
        if act_as_user:
            self.__conduit.set_act_as_user()
        else:
            if self.__conduit.get_act_as_user():
                self.__conduit.clear_act_as_user()


def _request_handler_factory(instaweb_args):

    def factory(*args):
        return _RequestHandler(instaweb_args, *args)

    return factory


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
# ------------------------------ END-OF-FILE ----------------------------------
