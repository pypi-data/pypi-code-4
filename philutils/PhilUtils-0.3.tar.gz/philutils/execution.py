#!/usr/bin/env python

# Name: execution.py
# Author: Philip Zerull
# Date Created: Wednesday July 24, 2013


import os
import sys
import traceback
from multiprocessing import Process, Queue as PQueue
from threading import Thread
from Queue import Queue


def job_wrapper(job_function, resultsqueue, *args, **kwargs):
    """sticks the results of the function (or error info) into a queue"""
    final_result = return_result_or_error(job_function, *args, **kwargs)
    resultsqueue.put(final_result)


def return_result_or_error(some_function, *args, **kwargs):
    """Tries to execute a function, and returns a dictionary with the result.

    The dictionary has the following keys, 'status' and 'value'.  Status
    is either 'success' or 'failure' and the value is some_function's return
    value if the call was successful, otherwise it is a list contating the
    results sys.exc_info (except for the traceback is provided as a string,
    to maintain pickleability).
    """
    try:
        result = some_function(*args, **kwargs)
        status = 'success'
    except Exception as err:
        status = 'error'
        result = dict(exc_info=list(sys.exc_info()))
        result['exc_info'][2] = traceback.format_exc()
    final_result = dict(
        status=status,
        value=result
    )
    return final_result


class Job(object):

    """Represents a function to be run 'in the background'.

    This class spools an instance of Job.runner_class to execute the provided
    function_to_run with the given arguments and keyword arguments. It uses
    an instance of Job.collector_class to store the results from the function
    so that the finish command can return it like a normal function would.

    by default Job.runner_class is threading.Thread and
    job.collector_class is Queue.Queue.  if these are modified
    they must be changed to objects that have the same function signatures.
    """
    runner_class = Thread
    collector_class = Queue

    def __init__(self, function_to_run, *args, **kwargs):
        self._started = False
        self._response_collector = Job.collector_class()
        all_args = [function_to_run, self._response_collector]
        all_args.extend(args)
        self._runner = Job.runner_class(
            target=job_wrapper,
            args=all_args,
            kwargs=kwargs
        )

    def start(self):
        """Starts the job"""
        self._runner.start()
        self._started = True

    def finish(self):
        """Blocks the thread, finishes the job, and returns the restult.

        the result is a dictionary containing the following keys:
            1). status, which may be either 'success', or 'error'.
            2). value, which is the result of the function_to_be_called if
                it returned sucessfully and 'error' otherwise
        """
        if not self._started:
            self.start()
        self._runner.join()
        return self._response_collector.get()


class ProcessJob(Job):
    runner_class = Process
    collector_class = PQueue


def _run_multiple_jobs(joblist):
    results = []
    for job in joblist:
        job.start()
    for job in joblist:
        results.append(job.finish()['value'])
    return results


def run_multiple_functions(functionlist, *args, **kwargs):
    joblist = []
    for funk in functionlist:
        joblist.append(Job(funk, *args, **kwargs))
    return _run_multiple_jobs(joblist)


def run_multiple_args(funk, arglist=None, kwarglist=None):
    joblist = []
    if arglist is None and kwarglist is None:
        arglist = [[]]
        kwarglist = [{}]
    elif arglist is not None and kwarglist is None:
        kwarglist = [{}] * len(arglist)
    elif kwarglist is not None and arglist is None:
        arglist = [[]] * len(kwarglist)
    for cur_args, cur_kwargs in zip(arglist, kwarglist):
        newjob = Job(funk, *cur_args, **cur_kwargs)
        joblist.append(newjob)
    return _run_multiple_jobs(joblist)
