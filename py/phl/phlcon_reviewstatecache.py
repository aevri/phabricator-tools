"""Cache the status of Differential revisions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_reviewstatecache
#
# Public Classes:
#   ReviewStateCache
#    .get_status
#    .refresh_active_reviews
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlcon_differential


class ReviewStateCache(object):

    def __init__(self):
        super(ReviewStateCache, self).__init__()
        self._review_to_state = {}
        self._active_reviews = set()

    def get_status(self, review_id, conduit):
        if review_id not in self._review_to_state:
            state = phlcon_differential.get_revision_status(conduit, review_id)
            self._review_to_state[review_id] = state

        self._active_reviews.add(review_id)
        return self._review_to_state[review_id]

    def refresh_active_reviews(self, conduit):
        self._review_to_state = {}
        if self._active_reviews:
            responses = phlcon_differential.query(
                conduit, list(self._active_reviews))
            for r in responses:
                self._review_to_state[r.id] = r.status
            self._active_reviews = set()


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
