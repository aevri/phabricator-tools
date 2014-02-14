"""Per-repository configuration."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_repoconfig
#
# Public Classes:
#   Data
#
# Public Functions:
#   data_from_json
#   json_from_data
#   validate_data
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlsys_jsondata


class Data(object):

    def __init__(self):
        super(Data, self).__init__()
        self.description = None
        self.instance_uri = None
        self.branch_url_format = None
        self.review_url_format = None
        self.admin_emails = []


def data_from_json(json_string):
    """Returns a 'Data' from the supplied 'json_string'.

    The 'json_string' doesn't have to mention all the attributes of Data, it
    must not mention attributes that don't exist in Data already.

    :json_string: a string of the json data
    :returns: a abdt_repoconfig.Data based on 'json_string'

    """
    data = Data()
    return phlsys_jsondata.set_from_json(data, json_string)


def json_from_data(data):
    """Returns a json string from the supplied 'data'.

    :data: a abdt_repoconfig.Data to encode as json
    :returns: a json string based on 'data'

    """
    return phlsys_jsondata.json_from_obj(data)


def validate_data(data):
    """Raise if the supplied data is invalid in any way.

    :data: a Data() to be validated
    :returns: None

    """
    if data.branch_url_format is not None:
        branch = 'blahbranch'
        data.branch_url_format.format(branch=branch)

    if data.review_url_format is not None:
        review = 123
        data.review_url_format.format(review=review)


#------------------------------------------------------------------------------
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
#------------------------------- END-OF-FILE ----------------------------------
