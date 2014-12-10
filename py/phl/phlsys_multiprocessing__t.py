"""Test suite for phlsys_multiprocessing."""
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

import multiprocessing
import unittest

import phlsys_multiprocessing


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_multiresource_breathing(self):

        def factory():
            return "resource"

        # make sure that we can get a resource in the main process
        multi_resource = phlsys_multiprocessing.MultiResource(1, factory)
        with multi_resource.resource_context() as resource:
            self.assertEqual("resource", resource)
        with multi_resource.resource_context() as resource:
            self.assertEqual("resource", resource)

        # make sure that worker processes can get a resource
        def worker(resource):
            print resource
        worker_list = []
        num_workers = 5
        for _ in xrange(num_workers):
            worker_list.append(
                multiprocessing.Process(target=worker, args=(resource,)))
            worker_list[-1].start()
        for w in worker_list:
            w.join()


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
