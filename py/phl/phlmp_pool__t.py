"""Test suite for phlmp_pool."""
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

import phlmp_pool


class _TestJob(object):

    def __init__(self, value):
        self._value = value

    def __call__(self):
        return self._value


class _WaitForLockJob(object):

    def __init__(self, value, lock):
        self._value = value
        self._lock = lock

    def __call__(self):
        with self._lock:
            return self._value


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_breathing(self):

        input_list = list(xrange(100))
        job_list = [_TestJob(i) for i in input_list]
        result_list = []
        max_workers = multiprocessing.cpu_count()
        pool = phlmp_pool.CyclingPool(job_list, max_workers)

        def condition():
            return False

        for index, result in pool._cycle_results(condition):
            self.assertEqual(index, result)
            result_list.append(result)

        self.assertSetEqual(
            set(result_list),
            set(input_list))

    def test_can_overrun(self):

        def true_condition():
            return True

        lock = multiprocessing.Lock()

        max_workers = 10
        half_max_workers = max_workers // 2
        input_list = list(xrange(max_workers))
        block_input_list = input_list[:half_max_workers]
        normal_input_list = input_list[half_max_workers:]
        self.assertTrue(len(normal_input_list) >= len(block_input_list))

        block_job_list = [_WaitForLockJob(i, lock) for i in block_input_list]
        normal_job_list = [_TestJob(i) for i in normal_input_list]
        job_list = block_job_list + normal_job_list

        result_list = []
        pool = phlmp_pool.CyclingPool(job_list, max_workers)

        # Acquire lock before starting cycle, to ensure that 'block_job_list'
        # jobs won't complete. This will force the pool to overrun those jobs.
        with lock:
            for index, result in pool._cycle_results(true_condition):
                self.assertEqual(index, result)
                result_list.append(result)

        # make sure that all the normal jobs were processed and none of the
        # blocked jobs were processed
        self.assertSetEqual(
            set(result_list),
            set(normal_input_list))

        # finish all remaining jobs
        for index, result in pool.finish_results():
            self.assertEqual(index, result)
            result_list.append(result)

        # assert that all jobs have been processed
        self.assertSetEqual(
            set(result_list),
            set(input_list))


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
