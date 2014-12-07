"""git-phab-log  - a Phabricator git-log parser.

Examine your git log for commits from Phabricator and associated info.

Operates on a list of Git commit hashes, which can be supplied by you on stdin
or calculated from commits that you provide as parameters.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# gabcmd_gitphablog
#
# Public Functions:
#   parse_args
#   main
#   passes_filters
#   get_revision_generator
#   parse_fields
#   parse_valid_fields
#
# Public Assignments:
#   FIELDS_LISTS
#   FIELDS_SINGLE_VALUE
#   FIELDS_TEXT
#   ALL_VALID_FIELDS
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================



import argparse
import collections
import re
import signal

import phlgit_log
import phlgit_revlist
import phlsys_git


_USAGE_EXAMPLES = """
usage examples:
    list information about revisions on your current branch:
    $ git-phab-log

    list information about commits on your branch but not 'origin/master':
    $ git-phab-log origin/master..

    list unreviewed commits on your branch:
    $ git-phab-log origin/master..

    list information about non-merge revisions on your current branch:
    $ git rev-list HEAD --no-merges | git-phab-log list-file -
"""

# these fields were compiled from observation of logs alone
# TODO: get the from the Phabricator source

FIELDS_LISTS = [
    'maniphest tasks',
    'reviewed by',
    'reviewers',
    'auditors',
    'cc',
]

FIELDS_SINGLE_VALUE = [
    'differential revision',
]

FIELDS_TEXT = [
    'test plan',
    'summary',
    'conflicts',
]

ALL_VALID_FIELDS = FIELDS_LISTS + FIELDS_SINGLE_VALUE + FIELDS_TEXT


def _get_set_or_none(list_or_none):
    if list_or_none is not None:
        list_or_none = set(list_or_none)
    return list_or_none


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    parser.add_argument(
        'commits',
        metavar="COMMITS",
        type=str,
        nargs='*',
        help="commits to traverse the 'parent' links of, to make the list of "
             "revisions to display. e.g. 'origin/master', 'origin/master..'. "
             "defaults to 'HEAD' if none are supplied here or via --list-file")

    parser.add_argument(
        '--list-file',
        metavar='FILE',
        type=argparse.FileType('r'),
        help="optional file to read list of commit from, use '-' to read from "
             "stdin")

    parser.add_argument(
        '--only-phab-reviewed',
        action='store_true',
        help="show only Phabricator-reviewed revisions")

    parser.add_argument(
        '--no-phab-reviewed',
        action='store_true',
        help="show only revisions that were not Phabricator-reviewed")

    parser.add_argument(
        '--approved-by-any-of',
        metavar='USERNAME',
        type=str,
        nargs='+',
        help="show only Phabricator-reviewed revisions approved by these.")

    parser.add_argument(
        '--approved-by-none-of',
        metavar='USERNAME',
        type=str,
        nargs='+',
        help="show only revisions not approved by these.")

    args = parser.parse_args()

    # these lists need to be sets for correctness and performance
    args.approved_by_any_of = _get_set_or_none(args.approved_by_any_of)
    args.approved_by_none_of = _get_set_or_none(args.approved_by_none_of)

    return args


def main():
    # ignore SIGPIPE or we'll be incompatible with commands like 'head'
    #
    # see:
    # http://newbebweb.blogspot.co.uk/2012/02/python-head-ioerror-errno-32-
    #                                                               broken.html
    #
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    args = parse_args()

    for revision in get_revision_generator(args):
        fields = parse_fields(revision.message)

        if not passes_filters(args, fields):
            continue

        # all bets are off if there's no differential revision
        review_url = fields.get('differential revision', None)
        if review_url is None:
            fields = {}
            review_url = ""

        reviewed_by = fields.get('reviewed by', None)
        if reviewed_by is not None:
            reviewed_by = ','.join(reviewed_by)
        else:
            reviewed_by = ""

        print("{commit_hash} {review_url} {reviewer}".format(
            commit_hash=revision.abbrev_hash,
            review_url=review_url,
            reviewer=reviewed_by))


def passes_filters(args, fields):
    is_phab_reviewed = 'differential revision' in fields

    # approved_by should be a set of approvers or None
    approved_by = fields.get('reviewed by', None)
    if is_phab_reviewed:
        if approved_by is not None:
            approved_by = set(approved_by)
    else:
        approved_by = None

    if args.only_phab_reviewed and not is_phab_reviewed:
        return False

    if args.no_phab_reviewed and is_phab_reviewed:
        return False

    required_approvers = args.approved_by_any_of
    if required_approvers:
        if not approved_by or not approved_by.issubset(required_approvers):
            return False

    banned_approvers = args.approved_by_none_of
    if banned_approvers:
        if approved_by and not approved_by.isdisjoint(banned_approvers):
            return False

    return True


def get_revision_generator(args):

    repo = phlsys_git.Repo('.')

    commit_list = []
    commits_to_follow = []
    did_specify_something = False

    if args.commits:
        did_specify_something = True
        commits_to_follow = args.commits

    if args.list_file:
        did_specify_something = True
        commit_list += args.list_file.read()

    if not did_specify_something:
        commits_to_follow = ['HEAD']

    if commits_to_follow:
        commit_list += phlgit_revlist.commits(repo, *commits_to_follow)

    make_rev = phlgit_log.make_revision_from_hash
    revision_generator = (make_rev(repo, commit) for commit in commit_list)

    return revision_generator


def parse_fields(message_body):
    fields = parse_valid_fields(message_body)

    # turn the list fields into space-separated lists
    for field in fields:
        if field in FIELDS_LISTS:
            list_items = fields[field].split()
            list_items = [l.strip(',') for l in list_items]
            fields[field] = list_items
        elif field in FIELDS_SINGLE_VALUE:
            fields[field] = fields[field].strip()

    return fields


def parse_valid_fields(message_body):
    identifier_re = re.compile('(\w+( \w+)*):\s*')
    current_field = 'summary'
    fields = collections.defaultdict(str)
    for line in message_body.splitlines():
        match = identifier_re.match(line)
        if match:
            lower_match = match.group(1).lower()
            if match and lower_match in ALL_VALID_FIELDS:
                current_field = lower_match
                line = line[len(match.group(0)):]
        if current_field:
            fields[current_field] += line + '\n'
    return dict(fields)


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
