"""Serialise data structures to and from json."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_jsondata
#
# Public Functions:
#   set_from_json
#   json_from_obj
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json


def set_from_json(obj, json_string):
    """Set attributes on 'obj' from the supplied 'json_string'.

    The 'json_string' doesn't have to mention all the attributes of 'obj',
    it must not mention attributes that don't exist on 'obj' already.

    :json_string: a string of the json data
    :returns: a abdt_repoconfig.Data based on 'json_string'

    """
    for key, value in json.loads(json_string).iteritems():
        getattr(obj, key)  # raise if the attribute doesn't already exist
        setattr(obj, key, value)


def json_from_obj(obj):
    """Returns a json string from the supplied 'obj'.

    It is assumed that 'obj' only has attributes which are of the
    'supported types':

        'str'

    Attributes may also be nested lists of the 'supported types'.

    :obj: an object to encode as json
    :returns: a json string based on 'obj', favors readability over compactness

    """
    return json.dumps(
        obj,
        default=lambda x: x.__dict__,
        sort_keys=True,
        indent=4)


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
