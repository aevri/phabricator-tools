"""Wrapper to call Phabricator's users Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_user
#
# Public Classes:
#   Error
#   OneOrMoreUnknownUsernamesError
#   OneOrMoreUnknownPhidsError
#   UnknownUsernameError
#   UnknownPhidError
#   UsernamePhidCache
#    .add_username_hint
#    .add_username_hint_list
#    .get_phid_from_username
#    .get_username_from_phid
#
# Public Functions:
#   is_no_such_error
#   query_user_from_email
#   query_users_from_emails
#   query_users_from_phids
#   query_users_from_usernames
#   response_from_attribute
#   query_usernames_from_phids
#   make_username_phid_dict
#   make_phid_username_dict
#
# Public Assignments:
#   QueryResponse
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlsys_conduit
import phlsys_dictutil
import phlsys_namedtuple


QueryResponse = phlsys_namedtuple.make_named_tuple(
    'phlcon_user__QueryResponse',
    required=['phid', 'userName', 'realName', 'image', 'uri', 'roles'],
    defaults={},
    ignored=['currentStatus', 'currentStatusUntil'])


class Error(Exception):
    pass


class OneOrMoreUnknownUsernamesError(Error):

    def __init__(self, usernames, known_users):
        super(OneOrMoreUnknownUsernamesError, self).__init__(
            "usernames: {}\nknown users: {}".format(
                usernames,
                known_users))


class OneOrMoreUnknownPhidsError(Error):

    def __init__(self, phids, known_users):
        super(OneOrMoreUnknownPhidsError, self).__init__(
            "phids: {}\nknown users: {}".format(
                phids,
                known_users))


class UnknownUsernameError(Error):

    def __init__(self, username):
        super(UnknownUsernameError, self).__init__(username)


class UnknownPhidError(Error):

    def __init__(self, phid):
        super(UnknownPhidError, self).__init__(phid)


class UnknownEmailError(Error):

    def __init__(self, email):
        super(UnknownEmailError, self).__init__(email)


class UsernamePhidCache(object):

    """Efficiently retrieve the PHID for specified usernames."""

    def __init__(self, conduit):
        """Construct a cache attached to the specified 'conduit'."""
        super(UsernamePhidCache, self).__init__()
        self._username_to_phid = {}
        self._phid_to_username = {}
        self._email_to_username_phid = {}
        self._hinted_usernames = set()
        self._conduit = conduit

    def add_username_hint(self, username):
        """Register 'username' as a username we'll later query."""
        if username not in self._username_to_phid:
            self._hinted_usernames.add(username)

    def add_username_hint_list(self, username_list):
        """Register all 'username_list' as users we'll later query."""
        for username in username_list:
            self.add_username_hint(username)

    def get_phid_from_username(self, username):
        """Return the PHID for the specified 'username'."""
        self.add_username_hint(username)
        if username not in self._username_to_phid:

            try:
                username_to_phid = make_username_phid_dict(
                    self._conduit, list(self._hinted_usernames))
            except OneOrMoreUnknownUsernamesError:
                username_to_phid = None

            # if one of the usernames is invalid then the whole query may fail,
            # in this case we'll just retry this single username and clear the
            # hint list so that we may continue, albeit with degraded
            # performance
            if username_to_phid is None:
                self._hinted_usernames = set()
                username_to_phid = make_username_phid_dict(
                    self._conduit, [username])
                if username_to_phid is None:
                    raise UnknownUsernameError(username)

            self._username_to_phid.update(username_to_phid)
            phid_to_username = phlsys_dictutil.invert(username_to_phid)
            self._phid_to_username.update(phid_to_username)
            self._hinted_usernames = set()

        return self._username_to_phid[username]

    def get_username_from_phid(self, phid):
        """Return the username for the specified 'phid'."""
        if phid not in self._phid_to_username:

            phid_to_username = make_phid_username_dict(
                self._conduit, [phid])

            if phid_to_username is None:
                raise UnknownPhidError(phid)

            self._phid_to_username.update(phid_to_username)
            username_to_phid = phlsys_dictutil.invert(phid_to_username)
            self._username_to_phid.update(username_to_phid)
            self._hinted_usernames -= set(username_to_phid.iterkeys())

        return self._phid_to_username[phid]

    def get_username_phid(self, email):
        """Return the username and phid for the specified 'email'."""
        if email not in self._email_to_username_phid:

            user = query_user_from_email(self._conduit, email)
            if user is None:
                raise UnknownEmailError(email)

            self._email_to_username_phid[email] = (user.userName, user.phid)
            self._phid_to_username[user.phid] = user.userName
            self._username_to_phid[user.userName] = user.phid
            self._hinted_usernames.discard(user.userName)

        return self._email_to_username_phid[email]


def is_no_such_error(e):
    """Return True if the supplied ConduitException is due to unknown user.

    :e: a ConduitException
    :returns: True if the supplied ConduitException is due to unknown user

    """
    errConduitCore = "ERR-CONDUIT-CORE"
    noSuchEmail = ""
    noSuchEmail += "Array for %Ls conversion is empty. "
    noSuchEmail += "Query: SELECT * FROM %s WHERE userPHID IN (%Ls) "
    noSuchEmail += "AND UNIX_TIMESTAMP() BETWEEN dateFrom AND dateTo %Q"
    return e.error == errConduitCore and e.errormsg == noSuchEmail


def query_user_from_email(conduit, email):
    """Return a QueryResponse based on the provided email.

    If the email does not correspond to a username then return None.

    :conduit: must support 'call()' like phlsys_conduit
    :email: an email address as a string
    :returns: a QueryResponse or None

    """
    response = response_from_attribute(conduit, 'emails', [email])

    if response:
        if len(response) != 1:
            raise Exception("unexpected number of entries")
        return QueryResponse(**response[0])
    else:
        return None


def query_users_from_emails(conduit, emails):
    """Return a list of username strings based on the provided emails.

    If an email does not correspond to a username then None is inserted in
    its place.

    :conduit: must support 'call()' like phlsys_conduit
    :emails: a list of strings corresponding to user email addresses
    :returns: a list of strings corresponding to Phabricator usernames

    """
    users = []
    for e in emails:
        u = query_user_from_email(conduit, e)
        if u is not None:
            users.append(u.userName)
        else:
            users.append(None)
    return users


def query_users_from_phids(conduit, phids):
    """Return a list of QueryResponse based on the provided phids.

    If a phid does not correspond to a username then return None.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to user phids
    :returns: a list of QueryResponse

    """
    response = response_from_attribute(conduit, 'phids', phids)
    if response is None:
        return None

    if len(response) != len(phids):
        raise OneOrMoreUnknownPhidsError(
            phids, response)

    return [QueryResponse(**u) for u in response]


def query_users_from_usernames(conduit, usernames):
    """Return a list of QueryResponse based on the provided usernames.

    :conduit: must support 'call()' like phlsys_conduit
    :usernames: a list of strings corresponding to usernames
    :returns: a list of QueryResponse

    """
    response = response_from_attribute(conduit, 'usernames', usernames)
    if response is None:
        return None

    if len(response) != len(usernames):
        raise OneOrMoreUnknownUsernamesError(
            usernames, response)

    return [QueryResponse(**u) for u in response]


def response_from_attribute(conduit, attribute_name, attribute_list):
    """Return the response from conduit for the given query.

    :conduit: must support 'call()' like phlsys_conduit
    :attribute_name: a string naming the attribute to query on
    :attribute_list: a list of strings corresponding to the attribute type
    :returns: the response dict

    """
    if not isinstance(attribute_list, list):
        raise ValueError("'attribute_list' must be a list")
    d = {attribute_name: attribute_list, "limit": len(attribute_list)}

    response = None
    try:
        response = conduit("user.query", d)
    except phlsys_conduit.ConduitException as e:
        if not is_no_such_error(e):
            raise

    return response


def query_usernames_from_phids(conduit, phids):
    """Return a list of username strings based on the provided phids.

    If a phid does not correspond to a username then raise.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to user phids
    :returns: a list of strings corresponding to Phabricator usernames

    """
    usernames = [u.userName for u in query_users_from_phids(conduit, phids)]
    return usernames


def make_username_phid_dict(conduit, usernames):
    """Return a dictionary of usernames to phids.

    Return None if any of 'usernames' is invalid.

    :conduit: must support 'call()' like phlsys_conduit
    :usernames: a list of strings corresponding to Phabricator usernames
    :returns: a dictionary of usernames to corresponding phids

    """
    users = query_users_from_usernames(conduit, usernames)
    if users is None:
        return None
    else:
        return {u.userName: u.phid for u in users}


def make_phid_username_dict(conduit, phids):
    """Return a dictionary of phids to usernames.

    Return None if any of 'phids' is invalid.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to Phabricator PHIDs
    :returns: a dictionary of usernames to corresponding phids

    """
    users = query_users_from_phids(conduit, phids)
    if users is None:
        return None
    else:
        return {u.phid: u.userName for u in users}


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
