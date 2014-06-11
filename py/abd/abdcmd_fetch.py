"""Fetch managed repos.

This can be useful if you are switching from one arcyd instance to
another, to 'pre-fetch' before actually moving over.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_fetch
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

import argparse
import os

import phlsys_git
import phlurl_watcher

import abdi_processrepoargs
import abdi_repoargs
import abdt_fs
import abdt_git


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    pass


def process(args):

    _ = args
    fs = abdt_fs.make_default_accessor()

    repo_config_path_list = fs.repo_config_path_list()
    repo_name_config_list = []
    for repo_config_path in repo_config_path_list:
        print repo_config_path
        parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
        abdi_repoargs.setup_parser(parser)
        repo_config = parser.parse_args(['@' + repo_config_path])
        repo_name = repo_config_path.split('/')[-1]  # strip off the path
        repo_name_config = (repo_name, repo_config)
        abdi_repoargs.validate_args(repo_name_config[1])
        repo_name_config_list.append(repo_name_config)

    url_watcher = phlurl_watcher.Watcher()

    urlwatcher_cache_path = os.path.abspath('.arcyd.urlwatcher.cache')

    # load the url watcher cache (if any)
    if os.path.isfile(urlwatcher_cache_path):
        with open(urlwatcher_cache_path) as f:
            url_watcher.load(f)

    for repo_name, repo_config in repo_name_config_list:
        print repo_name
        snoop_url = abdi_repoargs.get_repo_snoop_url(repo_config)

        abd_repo = abdt_git.Repo(
            phlsys_git.Repo(repo_config.repo_path),
            "origin",
            repo_config.repo_desc)

        abdi_processrepoargs._fetch_if_needed(
            url_watcher,
            snoop_url,
            abd_repo,
            repo_config.repo_desc)

        # save the urlwatcher cache
        # TODO: git_url_watcher should manage this itself
        with open(urlwatcher_cache_path, 'w') as f:
            url_watcher.dump(f)


# -----------------------------------------------------------------------------
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
# ------------------------------ END-OF-FILE ----------------------------------
