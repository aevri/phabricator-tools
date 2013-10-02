"""Cache the mapping from email address to phabricator username."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_emailtousercache
#
# Public Classes:
#   EmailToUserCache
#    .get_user
#    .set_conduit
#    .clear_conduit
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
        self._cache = _EmailToUserCache(self, retry_cooloff_secs)

    def get_user(self, email):
        return self._cache.get_user(email)

    def set_conduit(self, conduit):
        self._cache.set_email_to_user_callable(
            _make_email_to_user_callable(conduit))

    def clear_conduit(self):
        self._cache.clear_email_to_user_callable = None


def _make_email_to_user_callable(conduit):

    def email_to_user(email):
        return phlcon_user.query_user_from_email(conduit, email)

    return email_to_user


class _EmailToUserCache(object):

    def __init__(self, retry_cooloff_secs):
        super(_EmailToUserCache, self).__init__()
        self._email_to_user = {}
        self._email_unknown = {}
        self._retry_cooloff_secs = retry_cooloff_secs
        self._email_to_user_callable = None

    def _query_new_email(self, email):
        user = self._email_to_user_callable(email)
        if user is not None:
            self._email_to_user[email] = user.userName
            del self._email_unknown[email]
        else:
            self._email_unknown[email] = datetime.datetime.now()
        return user

    def _update_unknown_email(self, email):
        elapsed = datetime.datetime.now() - self._email_unknown[email]
        user = None
        if elapsed.total_seconds() > self._retry_cooloff_secs:
            user = self._query_new_email(email)
        return user

    def get_user(self, email):
        if email in self._email_to_user:
            return self._email_to_user[email]

        if email in self._email_unknown:
            return self._update_unknown_email(email)
        else:
            return self._query_new_email(email)

    def set_email_to_user_callable(self, email_to_user_callable):
        self._email_to_user_callable = email_to_user_callable

    def clear_email_to_user_callable(self):
        self._email_to_user_callable = None


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
