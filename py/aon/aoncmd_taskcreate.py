"""Create a new task in maniphest.

you can use the 'task id' output from this command as input to the
'arcyon task-update' command.

usage examples:
    create a new task with just a title:
    $ arcyon task-create 'title'
    Created a new task '99', you can view it at this URL:
      http://127.0.0.1/T99

    create a new task with just a title, only show url:
    $ arcyon task-create 'title' --format-url
    http://127.0.0.1/T99

    create a new task with just a title, only show id:
    $ arcyon task-create 'title' --format-id
    99

    create a new task with a title and description:
    $ arcyon task-create 'title' -d 'a description of the task' --format-id
    99

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_taskcreate
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function

import sys
import textwrap

import phlcon_maniphest
import phlcon_project
import phlcon_user
import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):

    # make a list of priority names in increasing order of importance
    priority_name_list = phlcon_maniphest.PRIORITIES.keys()
    priority_name_list.sort(
        key=lambda x: phlcon_maniphest.PRIORITIES[x])

    priorities = parser.add_argument_group(
        'optional priority arguments',
        'use any of ' + textwrap.fill(
            str(priority_name_list)))
    output_group = parser.add_argument_group(
        'Output format arguments',
        'Mutually exclusive, defaults to "--format-summary"')
    output = output_group.add_mutually_exclusive_group()
    opt = parser.add_argument_group(
        'Optional task arguments',
        'You can supply these later via the web interface if you wish')

    priorities.add_argument(
        '--priority',
        '-p',
        choices=priority_name_list,
        metavar="PRIORITY",
        default=None,
        type=str,
        help="the priority or importance of the task")

    parser.add_argument(
        'title',
        metavar='STRING',
        help='the short title of the task',
        type=str)

    opt.add_argument(
        '--description',
        '-d',
        metavar='STRING',
        help='the long description of the task',
        type=str)
    opt.add_argument(
        '--owner',
        '-o',
        metavar='USER',
        help='the username of the owner',
        type=str)
    opt.add_argument(
        '--ccs',
        '-c',
        nargs="*",
        metavar='USER',
        default=[],
        help='a list of usernames to cc on the task',
        type=str)
    opt.add_argument(
        '--projects',
        nargs="*",
        metavar='PROJECT',
        default=[],
        help='a list of project names to add the task to',
        type=str)

    output.add_argument(
        '--format-summary',
        action='store_true',
        help='will print a human-readable summary of the result.')
    output.add_argument(
        '--format-id',
        action='store_true',
        help='will print just the id of the new task, for scripting.')
    output.add_argument(
        '--format-url',
        action='store_true',
        help='will print just the url of the new task, for scripting.')

    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    if not args.title.strip():
        print('you must supply a non-empty title', file=sys.stderr)
        return 1

    conduit = phlsys_makeconduit.make_conduit(
        args.uri, args.user, args.cert, args.act_as_user)

    # create_task expects an integer
    priority = None
    if args.priority is not None:
        priority = phlcon_maniphest.PRIORITIES[args.priority]

    # conduit expects PHIDs not plain usernames
    user_phids = phlcon_user.UsernamePhidCache(conduit)
    if args.owner:
        user_phids.add_username_hint(args.owner)
    user_phids.add_username_hint_list(args.ccs)

    get_phid = user_phids.get_phid_from_username
    owner = get_phid(args.owner) if args.owner else None
    ccs = [get_phid(user) for user in args.ccs]

    # conduit expects PHIDs not plain project names
    projects = None
    if args.projects:
        project_to_phid = phlcon_project.make_project_to_phid_dict(conduit)
        projects = [project_to_phid[p] for p in args.projects]

    result = phlcon_maniphest.create_task(
        conduit, args.title, args.description, priority, owner, ccs, projects)

    if args.format_id:
        print(result.id)
    elif args.format_url:
        print(result.uri)
    else:  # args.format_summary:
        message = (
            "Created a new task '{task_id}', you can view it at this URL:\n"
            "  {url}"
        ).format(
            task_id=result.id,
            url=result.uri)
        print(message)


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
