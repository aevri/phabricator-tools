"""Utility for working with dicts."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_dictutil
#
# Public Functions:
#   copy_dict_no_nones
#   ensure_keys
#   ensure_keys_default
#   set_if_true
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================


import copy


def copy_dict_no_nones(d):
    """Return a copy of the supplied 'd' minus any keys mapping to 'None'.

    Usage examples:
        >>> e = copy_dict_no_nones({'a': None, 'b': 1, 'c': None, 'd': 2})
        >>> e == {'b': 1, 'd': 2}
        True

    :d: the dictionary to copy
    :returns: a copy of 'd' minus any keys mapping to 'None'

    """
    return {k: v for k, v in d.items() if v is not None}


def ensure_keys(d, keys):
    """Modify supplied 'd'; ensure supplied 'keys', map to None if absent.

    Usage examples:
        >>> d = {'b': 1, 'd': 2}
        >>> ensure_keys(d, ['a', 'c'])
        >>> d == {'a': None, 'b': 1, 'c': None, 'd': 2}
        True

    :d: the dictionary to modify
    :keys: the keys to ensure are present
    :returns: None

    """
    for k in keys:
        if k not in d:
            d[k] = None


def ensure_keys_default(dic, default, keys):
    """Ensure that the dictionary has the supplied keys.

    Initialiase them with a deepcopy of the supplied 'default' if not.

    Usage examples:
        >>> d = {'b': 1, 'd': 2}
        >>> default = [0, 1, 2]
        >>> ensure_keys_default(d, default, ['a', 'c'])
        >>> default[:] = []  # clear the list in place
        >>> d == {'a': [0, 1, 2], 'b': 1, 'c': [0, 1, 2], 'd': 2}
        True

    :dic: the dictionary to modify
    :default: the default value (will be deep copied)
    :*keys: the keys to ensure
    :returns: None

    """
    for k in keys:
        if k not in dic:
            dic[k] = copy.deepcopy(default)


def set_if_true(dic, key, value):
    """Set the supplied 'key' to 'value' if 'value'.

    Can be used to simplify code like this:

        >>> d = {}
        >>> myvalue = None
        >>> if myvalue:
        ...     d['bananas'] = myvalue

    Usage examples:
        >>> set_if_true(d, 'bananas', None)
        >>> not 'bananas' in d
        True

        >>> set_if_true(d, 'bananas', 'we got em')
        >>> 'bananas' in d
        True
        >>> d['bananas']
        'we got em'

    :dic: the dictionary to update
    :key: the key to set
    :value: the value to set 'key' to
    :returns: None

    """
    if value:
        dic[key] = value


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
