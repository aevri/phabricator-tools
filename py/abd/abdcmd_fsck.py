"""Check the Arcyd files for consistency and fix any issues."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_fsck
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

import os

import phlgitx_ignoreident

import abdi_repo
import abdi_repoargs
import abdt_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):

    parser.add_argument(
        '--fix',
        action="store_true",
        help="resolve issues that are detected, where possible.")


def process(args):

    fs = abdt_fs.make_default_accessor()

    exit_code = 0

    with fs.lockfile_context():
        repo_config_path_list = fs.repo_config_path_list()

        for repo_config_path in repo_config_path_list:
            repo_filename = os.path.basename(repo_config_path)
            if not abdt_fs.is_config_name_valid(repo_filename):
                print "'{}' is not a valid repo config name".format(
                    repo_filename)
                exit_code = 1

        repo_name_config_list = abdi_repoargs.parse_config_file_list(
            repo_config_path_list)

        for repo_name, repo_config in repo_name_config_list:

            if not os.path.isdir(repo_config.repo_path):
                print "'{}' is missing repo '{}'".format(
                    repo_name, repo_config.repo_path)
                if args.fix:
                    repo_url = abdi_repoargs.get_repo_url(repo_config)
                    print "cloning '{}' ..".format(repo_url)
                    abdi_repo.setup_repo(repo_url, repo_config.repo_path)
                else:
                    exit_code = 1
            else:
                is_ignoring = phlgitx_ignoreident.is_repo_definitely_ignoring
                if not is_ignoring(repo_config.repo_path):
                    print "'{}' is not ignoring ident attributes".format(
                        repo_config.repo_path)
                    if args.fix:
                        print "setting {} to ignore ident ..".format(
                            repo_config.repo_path)

                        phlgitx_ignoreident.ensure_repo_ignoring(
                            repo_config.repo_path)
                    else:
                        exit_code = 1

    if exit_code != 0 and not args.fix:
        print "use '--fix' to attempt to fix the issues"

    return exit_code


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
