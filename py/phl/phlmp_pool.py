"""Distribute jobs across multiple processes."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlmp_pool
#
# Public Classes:
#   CyclingPool
#    .cycle_results
#    .num_active_jobs
#    .overrun_cycle_results
#    .finish_results
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import multiprocessing
import multiprocessing.queues

import phlsys_timer


class CyclingPool(object):

    def __init__(self, job_list, max_workers):
        super(CyclingPool, self).__init__()
        self._job_list = job_list
        self._max_workers = max_workers
        self._overunnable_workers = max_workers // 2
        self._pool_list = []
        self._active_job_index_set = set()

    def cycle_results(self, overrun_secs):

        # make a timer out of the overrun_secs and pass to _cycle_results
        timer = phlsys_timer.Timer()
        timer.start()

        def overrun_condition():
            return timer.duration >= overrun_secs

        for index, result in self._cycle_results(overrun_condition):
            yield index, result

    @property
    def num_active_jobs(self):
        return len(self._active_job_index_set)

    def _cycle_results(self, overrun_condition):

        # clear up any dead pools and yield results
        for i, res in self.overrun_cycle_results():
            yield i, res

        self._start_new_cycle()

        # wait for results, overrun if half our workers are available
        should_wait = True
        while should_wait and self._active_job_index_set:

            active_workers = self._count_overrun_workers()
            workers_too_busy = active_workers > self._overunnable_workers
            should_wait = workers_too_busy or not overrun_condition()

            for index, result in self.overrun_cycle_results():
                yield index, result

    def _count_overrun_workers(self):
        overrun_workers = 0
        for pool in self._pool_list:
            overrun_workers += pool.count_active_workers()
        return overrun_workers

    def _start_new_cycle(self):

        max_new_workers = self._max_workers - self._count_overrun_workers()

        pool = _Pool(self._job_list, max_new_workers)

        # schedule currently inactive jobs in the new pool
        all_job_index_set = set(xrange(len(self._job_list)))
        inactive_job_index_set = all_job_index_set - self._active_job_index_set
        for i in inactive_job_index_set:
            pool.add_job_index(i)
            self._active_job_index_set.add(i)
        pool.finish()

        self._pool_list.append(pool)

    def overrun_cycle_results(self):

        # yield results
        for pool in self._pool_list:
            pool.join_finished_workers()
            for index, result in pool.yield_available_results():
                self._active_job_index_set.remove(index)
                yield index, result

        # clean up dead pools
        finished_pools = []
        for pool in self._pool_list:
            if pool.is_finished():
                finished_pools.append(pool)
        for pool in finished_pools:
            self._pool_list.remove(pool)

    def finish_results(self):
        while self._pool_list:
            for index, result in self.overrun_cycle_results():
                yield index, result


class _Pool(object):

    def __init__(self, job_list, max_workers):
        super(_Pool, self).__init__()

        # pychecker makes us do this, it won't recognise that
        # multiprocessing.queues is a thing.
        mp = multiprocessing
        self._job_index_queue = mp.queues.SimpleQueue()
        self._results_queue = mp.queues.SimpleQueue()

        # create the workers
        self._worker_list = []
        num_workers = min(max_workers, len(job_list))
        for _ in xrange(num_workers):
            worker = multiprocessing.Process(
                target=_worker_process,
                args=(job_list, self._job_index_queue, self._results_queue))
            worker.start()
            self._worker_list.append(worker)

    def add_job_index(self, job_index):
        self._job_index_queue.put(job_index)

    def finish(self):
        # the worker processes will stop when they process 'None'
        for _ in xrange(len(self._worker_list)):
            self._job_index_queue.put(None)

    def join_finished_workers(self):

        # join all finished workers and remove from list
        finished_workers = []
        for worker in self._worker_list:
            if not worker.is_alive():
                worker.join()
                finished_workers.append(worker)
        for worker in finished_workers:
            self._worker_list.remove(worker)

    def yield_available_results(self):
        while not self._results_queue.empty():
            yield self._results_queue.get()

    def count_active_workers(self):
        return len(self._worker_list)

    def is_finished(self):
        return not self._worker_list


def _worker_process(job_list, work_queue, results_queue):
    while True:
        job_index = work_queue.get()
        if job_index is None:
            break
        job = job_list[job_index]
        results = job()
        results_queue.put((job_index, results))


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
