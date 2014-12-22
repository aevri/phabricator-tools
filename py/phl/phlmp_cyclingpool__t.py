"""Test suite for phlmp_cyclingpool."""
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

import collections
import multiprocessing
import unittest

import phlmp_cyclingpool


class _TestJob(object):

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value


class _LockedJob(object):

    def __init__(self, value, lock):
        self.value = value
        self.lock = lock

    def __call__(self):
        with self.lock:
            return self.value


def _false_condition():
    return False


def _true_condition():
    return True


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pool_breathing(self):

        input_list = list(xrange(100))
        job_list = [_TestJob(i) for i in input_list]
        max_workers = multiprocessing.cpu_count()

        pool = phlmp_cyclingpool._Pool(job_list, max_workers)
        for i in input_list:
            pool.add_job_index(i)
        pool.finish()

        result_list = []

        while len(result_list) < len(input_list):
            pool.join_finished_workers()
            for index, result in pool.yield_available_results():
                self.assertEqual(index, result)
                result_list.append(result)

        self.assertSetEqual(
            set(result_list),
            set(input_list))

    def test_poollist_breathing(self):

        max_workers = multiprocessing.cpu_count()
        input_list = list(xrange(max_workers))
        job_list = [_TestJob(i) for i in input_list]

        pool_list = phlmp_cyclingpool._PoolList()

        pool = phlmp_cyclingpool._Pool(job_list, max_workers)
        for i in input_list:
            pool.add_job_index(i)
        pool.finish()

        pool_list.add_pool(pool)

        # all workers should be active
        self.assertEqual(
            pool_list.count_active_workers(),
            max_workers)

        result_list = []
        while not pool_list.is_yield_finished():
            for index, result in pool_list.yield_available_results():
                self.assertEqual(index, result)
                result_list.append(result)

        # no workers should be active
        self.assertFalse(pool_list.count_active_workers())

        self.assertSetEqual(
            set(result_list),
            set(input_list))

    def test_calc_should_overrun(self):

        fcond = _false_condition
        tcond = _true_condition

        expectations = (
            ({'active': 0, 'over': 1, 'cond': tcond, 'is_fin': False}, True),
            ({'active': 0, 'over': 1, 'cond': fcond, 'is_fin': False}, False),
            ({'active': 0, 'over': 1, 'cond': tcond, 'is_fin': True}, True),
            ({'active': 0, 'over': 1, 'cond': fcond, 'is_fin': True}, True),
            ({'active': 1, 'over': 1, 'cond': fcond, 'is_fin': False}, False),
            ({'active': 1, 'over': 1, 'cond': tcond, 'is_fin': False}, True),
            ({'active': 2, 'over': 1, 'cond': fcond, 'is_fin': False}, False),
            ({'active': 2, 'over': 1, 'cond': tcond, 'is_fin': False}, False),

            # these shouldn't happen, but test anyway
            ({'active': 1, 'over': 1, 'cond': fcond, 'is_fin': True}, True),
            ({'active': 1, 'over': 1, 'cond': tcond, 'is_fin': True}, True),
            ({'active': 2, 'over': 1, 'cond': fcond, 'is_fin': True}, True),
            ({'active': 2, 'over': 1, 'cond': tcond, 'is_fin': True}, True),
        )

        for e in expectations:
            args = e[0]
            print args
            self.assertEqual(
                phlmp_cyclingpool._calc_should_overrun(
                    num_active=args['active'],
                    num_overrunnable=args['over'],
                    condition=args['cond'],
                    is_finished=args['is_fin']),
                e[1])

    def test_calc_overrunnable_workers(self):

        expectations = (
            ({'max_workers': 1, 'max_overrunnable': 1, 'num_jobs': 1}, 0),
            ({'max_workers': 1, 'max_overrunnable': 1, 'num_jobs': 2}, 0),
            ({'max_workers': 1, 'max_overrunnable': 2, 'num_jobs': 1}, 0),
            ({'max_workers': 1, 'max_overrunnable': 2, 'num_jobs': 2}, 0),

            ({'max_workers': 2, 'max_overrunnable': 1, 'num_jobs': 1}, 0),
            ({'max_workers': 2, 'max_overrunnable': 1, 'num_jobs': 2}, 1),
            ({'max_workers': 2, 'max_overrunnable': 2, 'num_jobs': 1}, 0),
            ({'max_workers': 2, 'max_overrunnable': 2, 'num_jobs': 2}, 1),
            ({'max_workers': 2, 'max_overrunnable': 2, 'num_jobs': 3}, 1),
            ({'max_workers': 2, 'max_overrunnable': 3, 'num_jobs': 2}, 1),
            ({'max_workers': 2, 'max_overrunnable': 3, 'num_jobs': 3}, 1),

            ({'max_workers': 3, 'max_overrunnable': 2, 'num_jobs': 2}, 1),
            ({'max_workers': 3, 'max_overrunnable': 2, 'num_jobs': 3}, 2),
            ({'max_workers': 3, 'max_overrunnable': 3, 'num_jobs': 2}, 1),
            ({'max_workers': 3, 'max_overrunnable': 3, 'num_jobs': 3}, 2),
        )

        for e in expectations:
            print e[0]
            self.assertEqual(
                phlmp_cyclingpool._calc_overrunnable_workers(**e[0]),
                e[1])

    def test_cyclingpool_breathing(self):

        input_list = list(xrange(100))
        job_list = [_TestJob(i) for i in input_list]
        result_list = []
        max_workers = multiprocessing.cpu_count()
        max_overrunnable = max_workers // 2
        pool = phlmp_cyclingpool.CyclingPool(
            job_list, max_workers, max_overrunnable)

        for index, result in pool._cycle_results(_false_condition):
            self.assertEqual(index, result)
            result_list.append(result)

        self.assertSetEqual(
            set(result_list),
            set(input_list))

    def test_can_overrun(self):

        lock = multiprocessing.Lock()

        max_workers = 10
        max_overrunnable = max_workers // 2
        half_max_workers = max_workers // 2
        input_list = list(xrange(max_workers))
        block_input_list = input_list[:half_max_workers]
        normal_input_list = input_list[half_max_workers:]
        self.assertTrue(len(normal_input_list) >= len(block_input_list))

        block_job_list = [_LockedJob(i, lock) for i in block_input_list]
        normal_job_list = [_TestJob(i) for i in normal_input_list]
        job_list = block_job_list + normal_job_list

        result_list = []
        pool = phlmp_cyclingpool.CyclingPool(
            job_list, max_workers, max_overrunnable)

        # Acquire lock before starting cycle, to ensure that 'block_job_list'
        # jobs won't complete. This will force the pool to overrun those jobs.
        with lock:
            for index, result in pool._cycle_results(_true_condition):
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

    def test_can_loop(self):

        num_loops = 2
        num_jobs = 100
        input_list = list(xrange(num_jobs))
        job_list = [_TestJob(i) for i in input_list]
        max_workers = multiprocessing.cpu_count()
        max_overrunnable = max_workers // 2
        print "max workers:", max_workers

        result_list = []
        pool = phlmp_cyclingpool.CyclingPool(
            job_list, max_workers, max_overrunnable)
        for i in xrange(num_loops):

            loop_offset = i * num_jobs

            for index, result in pool._cycle_results(_false_condition):
                self.assertEqual(index + loop_offset, result)
                result_list.append(result)

            self.assertSetEqual(
                set(result_list),
                set(xrange(num_jobs + loop_offset)))

            # ensure the next batch of jobs continue the numbering at the next
            # loop offset
            for job in job_list:
                job.value += num_jobs

    def test_can_overrun_loop(self):

        max_workers = 10
        max_overrunnable = max_workers // 2
        half_max_workers = max_workers // 2
        num_loops = half_max_workers
        num_jobs = max_workers

        locks = [multiprocessing.Lock() for _ in xrange(half_max_workers)]

        input_list = list(xrange(num_jobs))

        block_input_list = input_list[:half_max_workers]
        normal_input_list = input_list[half_max_workers:]

        self.assertTrue(len(normal_input_list) >= len(block_input_list))

        block_job_list = [
            _LockedJob((0, i), locks[i])
            for i in block_input_list
        ]
        normal_job_list = [_TestJob((0, i)) for i in normal_input_list]
        job_list = block_job_list + normal_job_list

        result_list = []
        pool = phlmp_cyclingpool.CyclingPool(
            job_list, max_workers, max_overrunnable)

        print "max workers:", max_workers

        result_list = []
        for i in xrange(num_loops):

            # Acquire lock before starting cycle, to ensure that some of the
            # 'block_job_list' jobs won't complete. This will force the pool to
            # overrun those jobs.
            locks[i].acquire()

            loop_offset = i * num_jobs

            for index, result in pool._cycle_results(_true_condition):
                iteration, job_index = result
                self.assertEqual(index, job_index)
                result_list.append(result)

            # make sure that some of the jobs weren't processed yet
            self.assertTrue(
                len(set(result_list)) < loop_offset + num_jobs)

            # make sure that some jobs are still running
            self.assertTrue(pool.num_active_jobs)

            # mark subsequent jobs as coming from the next iteration
            for job in job_list:
                iteration, job_index = job.value
                job.value = (iteration + 1, job_index)

        # finish all remaining jobs
        for l in locks:
            l.release()
        for index, result in pool.finish_results():
            result_list.append(result)

        # assert no jobs left
        self.assertFalse(pool.num_active_jobs)

        # count iterations of each job
        job_counter = collections.Counter()
        for result in result_list:
            iteration, job_index = result
            job_counter[job_index] += 1

        # assert that all jobs were processed at least once
        for i in input_list:
            self.assertTrue(job_counter[i] >= 1)

        # assert that blocked jobs were processed at most the number of cycles
        # until they were blocked
        for i in block_input_list:
            self.assertTrue(job_counter[i] <= i + 1)


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
