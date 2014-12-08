"""Helpers for multi-processing."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import multiprocessing
import logging


@contextlib.contextmanager
def logging_context(logging_configurer_fn, logging_level=logging.DEBUG):
    logging_queue = multiprocessing.Queue()
    logging_process_object = multiprocessing.Process(
        target=logging_process,
        args=(logging_queue, logging_configurer_fn))
    logging_process_object.start()

    def log_client_configurer():
        handler = QueueLoggingHandler(logging_queue)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging_level)

    # configure the current process to log to the logger process
    log_client_configurer()

    try:
        yield log_client_configurer
    finally:
        # instruct the logger process to stop by sending it 'None'
        logging_queue.put_nowait(None)
        logging_process_object.join()


def logging_process(logging_queue, logging_configurer_fn):

    logging_configurer_fn()

    while True:
        record = logging_queue.get()

        # we will receive 'None' if we are to stop processing
        if record is None:
            break

        # dispatch to the appropriate logger, so that any individual
        # module customizations work as expected
        logger = logging.getLogger(record.name)
        logger.handle(record)


# in Python 3.2+ there is 'logging.QueueHandler' which does the same job
class QueueLoggingHandler(logging.Handler):

    def __init__(self, logging_queue):
        super(QueueLoggingHandler, self).__init__()
        self._logging_queue = logging_queue

    def _prepare(self, record):
        # Arguments and exceptions could cause us trouble when pickling them to
        # send over to the logging process. Bake them into the message string
        # instead of sending them as objects.

        if record.args:
            # note that this could raise, so should be caught by callers
            record.msg = record.msg % record.args

        if record.exc_info:
            # do a premature and unconfigured 'format' if we encounter an
            # exception, so that it won't need to be pickled over to the
            # logging process
            self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            self._logging_queue.put_nowait(
                self._prepare(record))
        except:
            self.handleError(record)


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
