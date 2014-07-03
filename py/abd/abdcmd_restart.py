"""Restart the arcyd instance for the current directory."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_stop
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
import time

import phlsys_fs
import phlsys_pid

import abdt_fs
import argparse

import phlsys_daemonize
import phlsys_signal

import abdi_processrepos


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--force',
        action='store_true',
        help="kill the process.")
    parser.add_argument(
        '--foreground',
        action='store_true',
        help="supply this argument to run arcyd interactively in the "
             "foreground")
    parser.add_argument(
        '--no-loop',
        action='store_true',
        help="supply this argument to only process each repo once then exit")


def process(args):
    # exit gracefully if this process is killed
    phlsys_signal.set_exit_on_sigterm()

    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():
        pid = fs.get_pid_or_none()
        if pid is None or not phlsys_pid.is_running(pid):
            raise Exception("Arcyd is not running")

        if args.force:
            phlsys_pid.request_terminate(pid)
        else:
            killfile = 'var/command/killfile'
            phlsys_fs.write_text_file(killfile, '')

            if os.path.isfile(killfile):
                time.sleep(1)
                while os.path.isfile(killfile):
                    print 'waiting for arcyd to remove killfile ..'
                    time.sleep(1)

        # wait for Arcyd to not be running
        if phlsys_pid.is_running(pid):
            time.sleep(1)
            while phlsys_pid.is_running(pid):
                print 'waiting for arcyd to exit'
                time.sleep(1)

        if not args.foreground:
            phlsys_daemonize.do(
                stdout_path=fs.layout.stdout,
                stderr_path=fs.layout.stderr)

        # important that we do this *after* daemonizing
        pid = phlsys_pid.get()
        fs.set_pid(pid)

        parser = argparse.ArgumentParser()
        params = []

        for line in open(fs.layout.root_config):
            params.append(line.strip())

        if args.no_loop:
            params.append('--no-loop')

    # TODO: move parsing of repo configs under lockfile_context
    abdi_processrepos.setupParser(parser)
    args = parser.parse_args(params)
    abdi_processrepos.process(args, fs.repo_config_path_list())


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
