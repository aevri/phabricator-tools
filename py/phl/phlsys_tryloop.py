"""Conveniently retry exception-prone operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_tryloop
#
# Public Functions:
#   make_delay_secs_repeats
#   make_default_short_retry
#   make_default_endless_retry
#   try_loop_delay
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================



import datetime
import itertools
import time


def make_delay_secs_repeats(seconds, repeats):
    """Return a list of delays of the specified 'seconds', 'repeats' long.

    The output suitable for use with 'try_loop_delay'.

    Usage example:
        >>> make_delay_secs_repeats(10, 2)
        [datetime.timedelta(0, 10), datetime.timedelta(0, 10)]

    :seconds: the number of seconds to wait for
    :repeats: how many times to wait
    :returns: a list of datetime.timedelta

    """
    return [datetime.timedelta(seconds=seconds)] * repeats


def make_default_short_retry():
    """Return a list of delays suitable as a 'default' retry.

    The output suitable for use with 'try_loop_delay'.

    :returns: a list of datetime.timedelta

    """
    return make_delay_secs_repeats(seconds=3, repeats=3)


def make_default_endless_retry():
    """Return an endless iterable of delays suitable as a 'default' retry.

    The output suitable for use with 'try_loop_delay'.

    This is the sort of thing you might want to use if you are willing to retry
    something forever.

    The delays used gradually increase so that whichever system is being tried
    is not overly stressed.

    The delays are arranged such that if you observe 6 fails in any particular
    hour then there's a problem starting or ongoing.

    :returns: an endless iterable of datetime.timedelta

    """
    delays = []

    # the sum of the initial delays is roughly one of the 'forever' delays,
    # also there are 6 of them, which matches the number of 'forever' delays
    # per hour.
    delays += [datetime.timedelta(seconds=3)] * 1
    delays += [datetime.timedelta(seconds=15)] * 1
    delays += [datetime.timedelta(minutes=1)] * 2
    delays += [datetime.timedelta(minutes=3)] * 2

    # 6-7 times an hour shouldn't stress the system too much, 9 minutes isn't
    # too long to wait for an automatic recovery.
    forever = itertools.repeat(datetime.timedelta(minutes=9))

    delays = itertools.chain(delays, forever)

    return delays


def try_loop_delay(
        toTry, delays, exceptionToIgnore=Exception, onException=None):
    """Return the value returned by the supplied 'toTry' operation.

    If 'toTry()' raises an 'exceptionToIgnore' then do 'onException(e, delay)'
    if 'onException' is supplied, where 'e' is the exception object and
    'delay' is the next delay.  Note that 'delay' will be None on the last try.

    The function will continue looping until it runs out of delays or 'toTry()'
    stops raising 'exceptionToIgnore'.

    :toTry: a function which takes no parameters
    :delays: an iterable of datetime.timedelta
    :exceptionToIgnore: class of exception to ignore, defaults to 'Exception'
    :onException: function taking (exception, delay)
    :returns: return value from toTry()

    """
    # TODO: None may arise by mistake in 'delays', use a unique object as
    #       sentinel
    for delay in itertools.chain(delays, [None]):
        try:
            return toTry()
        except exceptionToIgnore as e:
            if onException is not None:
                onException(e, delay)
            if delay is None:
                raise e
        time.sleep(delay.total_seconds())


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
