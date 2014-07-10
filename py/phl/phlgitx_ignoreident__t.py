"""Test suite for phlgitx_ignoreident."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# TODO
# -----------------------------------------------------------------------------
# Tests:
# TODO
# =============================================================================

from __future__ import absolute_import

import unittest

import phlsys_fs
import phlgitu_fixture
import phlgitx_ignoreident


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBreathing(self):
        with phlgitu_fixture.lone_worker_context() as worker:

            self.assertFalse(
                phlgitx_ignoreident.is_repo_definitely_ignoring(
                    worker.repo.working_dir))

            phlgitx_ignoreident.ensure_repo_ignoring(
                worker.repo.working_dir,
                worker.repo)

            self.assertTrue(
                phlgitx_ignoreident.is_repo_definitely_ignoring(
                    worker.repo.working_dir))

    def testFixesProblem(self):
        ident_path = 'ident_file'
        with phlgitu_fixture.lone_worker_context() as worker:
            # enable ident expansion and commit a pre-expanded file
            worker.commit_new_file(
                message='add .gitattributes, enable ident',
                relative_path='.gitattributes',
                contents='* ident\n')
            worker.commit_new_file(
                message='add ident, erroneously expanded already',
                relative_path=ident_path,
                contents='$Id: already expanded, whoops! $')
            print phlsys_fs.read_text_file(ident_path)

            # checkout onto a new branch to unexpand the ident
            worker.repo("checkout", "-b", "fix_ident")
            phlsys_fs.write_text_file(ident_path, "$Id$")
            print worker.repo('status')
            worker.repo('commit', '-am', 'fix {}'.format(ident_path))

            # try to checkout back to master
            worker.repo("checkout", "master")

    # def testSimpleFork(self):
    #     with phlgitu_fixture.lone_worker_context() as worker:
    #         worker.repo("branch", "fork")
    #         worker.commit_new_file("add ONLY_MASTER", "ONLY_MASTER")
    #         worker.repo("checkout", "fork")
    #         worker.commit_new_file("add ONLY_FORK", "ONLY_FORK")
    #         worker.commit_new_file("add ONLY_FORK2", "ONLY_FORK2")
    #         rawDiff = phlgit_diff.raw_diff_range_to_here(
    #             worker.repo, "master")
    #         rawDiff2 = phlgit_diff.raw_diff_range(
    #             worker.repo, "master", "fork")
    #         rawDiff3 = phlgit_diff.raw_diff_range(
    #             worker.repo, "master", "fork", 1000)
    #         self.assertEqual(
    #             set(["ONLY_FORK", "ONLY_FORK2"]),
    #             phlgit_diff.parse_filenames_from_raw_diff(rawDiff))
    #         self.assertEqual(
    #             set(["ONLY_FORK", "ONLY_FORK2"]),
    #             phlgit_diff.parse_filenames_from_raw_diff(rawDiff2))
    #         self.assertEqual(
    #             set(["ONLY_FORK", "ONLY_FORK2"]),
    #             phlgit_diff.parse_filenames_from_raw_diff(rawDiff3))


# -----------------------------------------------------------------------------
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
# ------------------------------ END-OF-FILE ----------------------------------
