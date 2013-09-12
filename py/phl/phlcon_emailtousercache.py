"""Cache the mapping from email address to phabricator username."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_emailtousercache
#
# Public Classes:
#   EmailToUserCache
#    .get_user
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import datetime

import phlcon_user


class EmailToUserCache(object):

    def __init__(self, retry_cooloff_secs=60):
        super(EmailToUserCache, self).__init__()
        self._email_to_user = {}
        self._email_unknown = {}
        self._retry_cooloff_secs = retry_cooloff_secs

    def _query_new_email(self, email, conduit):
        user = phlcon_user.query_user_from_email(email)
        if user is not None:
            self._email_to_user[email] = user.userName
            del self._email_unknown[email]
        else:
            self._email_unknown[email] = datetime.datetime.now()
        return user

    def _update_unknown_email(self, email, conduit):
        elapsed = datetime.datetime.now() - self._email_unknown[email]
        user = None
        if elapsed.total_seconds() > self._retry_cooloff_secs:
            user = self._query_new_email(email, conduit)
        return user

    def get_user(self, email, conduit):
        if email in self._email_to_user:
            return self._email_to_user[email]

        if email in self._email_unknown:
            return self._update_unknown_email(email, conduit)
        else:
            return self._query_new_email(email, conduit)


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
