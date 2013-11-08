"""Get the comments from a differential revision.

usage examples:
    list the comments for revision 1
    $ arcyon get-comments 1
    /file1
    /dir/file2


output formats:
    --format-python
        {u'bookmark': None,
        u'branch': None,
        u'changes': [{u'addLines': u'0',
                    u'awayPaths': [],
                    u'commitHash': None,
                    u'currentPath': u'NEWFILE',
                    u'delLines': u'0',
                    ...

    --format-json
        {
        "bookmark": null,
        "branch": null,
        "changes": [
            {
            "addLines": "0",
            "awayPaths": [],
            "commitHash": null,
            "currentPath": "NEWFILE",
            "delLines": "0",
            ...

    --format-unified
        diff -uNard a/ b/
        +++ a/foo.c
        --- b/foo.c
        @@ 1,3 +0,0 @@
         some
        +content
        -contnet
         file
        ...

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json
import pprint

import phlsys_makeconduit

import aont_conduitargs


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    parser.add_argument(
        'ids',
        type=int,
        nargs="*",
        default=[],
        help="the revisions to query (e.g. 1)")
    parser.add_argument(
        '--ids-file',
        metavar='FILE',
        type=argparse.FileType('r'),
        help="a file to read ids from, use '-' to specify stdin")

    output_group = parser.add_argument_group(
        'Output format arguments',
        'Mutually exclusive, defaults to "--list-files"')
    output = output_group.add_mutually_exclusive_group()

    output.add_argument(
        '--format-python',
        action='store_true',
        help='print python representation of the raw response from '
             'the server.')
    output.add_argument(
        '--format-json',
        action='store_true',
        help='print json representation of the raw response from '
             'the server.')
    output.add_argument(
        '--format-unified',
        action='store_true',
        help='outputs a unified diff that can be used to apply the changes'
             'locally to the working copy')
    output.add_argument(
        '--format-string',
        '--fs',
        type=str,
        metavar='STR',
        help='specify a custom format string for displaying the items, '
             'the string is applied to each revision that is returned. '
             'the strings will be applied using Python\'s str.format(), '
             'so you can use curly brackets to substitute for field names, '
             'e.g. "\{action\}". '
             'you can use "--format-python" to discover the field names.')

    aont_conduitargs.addArguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(args.uri, args.user, args.cert)

    d = {}

    if args.revision:
        d["revision_id"] = args.revision
    if args.diff:
        d["diff_id"] = args.diff

    result = conduit.call("differential.getdiff", d)

    if args.format_python:
        pprint.pprint(result)
    elif args.format_json:
        print json.dumps(result, sort_keys=True, indent=2)
    elif args.format_unified:
        print unified_diff(result)
    elif args.format_strings:
        fmt = args.format_strings[0]
        fmt_change = args.format_strings[1]
        if fmt:
            print fmt.format(**result)
        if fmt_change:
            for change in result["changes"]:
                print fmt_change.format(**change)
    else:  # args.list_files:
        paths = set()
        for change in result["changes"]:
            paths.add(change["currentPath"])
            paths.add(change["oldPath"])
        for path in paths:
            print path


def unified_diff(result):
    for change in result["changes"]:
        print '--- ' + change["oldPath"]
        print '+++ ' + change["currentPath"]
        for hunk in change["hunks"]:
            hunk_format = "@@ -{oldOffset},{oldLength}"
            hunk_format += " +{newOffset},{newLength} @@"
            print hunk_format.format(**hunk)
            print hunk["corpus"]

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

