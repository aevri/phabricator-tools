"""Distribute jobs across multiple processes."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlmp_pool
#
# Public Functions:
#   generate_results
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import multiprocessing
import multiprocessing.queues


def CyclingPool(object):

    def __init__(self, job_list, max_workers):
        super(CyclingPool, self).__init__()
        self._job_list = job_list
        self._max_workers = max_workers
        self._overunnable_workers = max_workers // 2
        self._pool_list = []
        self._active_job_index_set = set()

    def cycle_results(self, overrun_secs):
        # make a timer out of the overrun_secs and pass to _cycle_results
        pass

    def _cycle_results(self, overrun_condition):

        # clear up any dead pools and yield results
        for i, res in self.overrun_cycle_results():
            yield i, res

        num_overrun_workers = ???

        # create a new pool and start yielding from that
        max_new_workers = self._max_workers - num_overrun_workers
        pool = _Pool(
            self._job_list,
            max_new_workers)

        # schedule currently inactive jobs in the new pool
        all_job_index_set = set(xrange(len(self._job_list)))
        inactive_job_index_set = all_job_index_set - self._active_job_index_set
        for i in inactive_job_index_set:
            pool.add_job_index(i)

        active_worker_count =
        should_wait = True

        # wait for results, overrun if half our workers are available
        while should_wait and pool.is_running()):

            ??? active_worker_count

            workers_too_busy = active_worker_count > self._overunnable_workers
            should_wait =  has_workers and overrun_condition

            pool.join_finished_workers()
            for i, res in pool.yield_available_results():
                yield i, res
            for i, res in self.overrun_cycle_results():
                yield i, res

    def overrun_cycle_results(self):
        pass


def _Pool(object):
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


def generate_results(job_list, max_workers):
    """Yield (job_index, result) by calling each in job_list concurrently.

    Example usage:

        >>> job_list = [(lambda: 1)]
        >>> for job_index, result in generate_results(job_list, 1):
        ...     print result
        1

    :job_list: a list of callables
    :returns: None

    """

    # pychecker makes us do this, it won't recognise that
    # multiprocessing.queues is a thing.
    mp = multiprocessing
    job_index_queue = mp.queues.SimpleQueue()
    results_queue = mp.queues.SimpleQueue()

    # create the workers
    worker_list = []
    num_workers = min(max_workers, len(job_list))
    for _ in xrange(num_workers):
        worker = multiprocessing.Process(
            target=_worker_process,
            args=(job_list, job_index_queue, results_queue))
        worker.start()
        worker_list.append(worker)

    # populate the job queue
    for job_index in xrange(len(job_list)):
        job_index_queue.put(job_index)

    # append a token to stop the workers
    for _ in xrange(len(worker_list)):
        job_index_queue.put(None)

    while worker_list:

        # join all finished workers and remove from list
        finished_workers = []
        for worker in worker_list:
            if not worker.is_alive():
                worker.join()
                finished_workers.append(worker)
        for worker in finished_workers:
            worker_list.remove(worker)

        # .. yield results ..
        while not results_queue.empty():
            yield results_queue.get()


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
