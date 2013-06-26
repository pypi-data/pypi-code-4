"""Utils to manage PPlus jobs execution.

Internal use module.
"""

# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: new BSD.

import os

def detect_ncpus():
    """Detects the number of effective CPUs in the system."""
    #for Linux, Unix and MacOS
    if hasattr(os, "sysconf"):
        if "SC_NPROCESSORS_ONLN" in os.sysconf_names:
            #Linux and Unix
            ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
            if isinstance(ncpus, int) and ncpus > 0:
                return ncpus
        else:
            #MacOS X
            return int(os.popen2("sysctl -n hw.ncpu")[1].read())
    #for Windows
    if "NUMBER_OF_PROCESSORS" in os.environ:
        ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
        if ncpus > 0:
            return ncpus
    #return the default value
    return 1


def create_callback(pc_obj):
    """Callback function creator.

    The callback is called after each job and check if the job is ended
    correctly.
    """
    def _job_callback(function, args, depfuncs, modules,
                      task_id, submission_cnt, result):

        result_obj = result

        # Job resubmission
        if result_obj is JobError:
            # check maximum resubmission threshold
            if submission_cnt < pc_obj.JOB_MAX_RESUBMISSION:

                submission_cnt += 1

                msg = ('Resubmitting failed Task (#%s) '
                       'for %d time...' % (task_id, submission_cnt))
                pc_obj._server_logger.info(msg)

                pc_obj._submit_task(function, args, depfuncs, modules,
                                    task_id, submission_cnt)
            else:
                msg = ('Failed task (%s) reached maximum number of '
                       'resubmissions! (%d)' % (task_id,
                                                pc_obj.JOB_MAX_RESUBMISSION))
                pc_obj._server_logger.error(msg)

    return _job_callback


def pplus_job(function, experiment_id, debug, args=()):
    import pplus
    import traceback

    pc = None  # if an error happen during PPlusConnection instantiation

    # the function can be also "submitted" as dependance and found in scope here
    # (because the code of any dependance is physically transmitted by PP and
    # appears in this scope)
    # this way, we can circumvent necessity of submission of picklable function object
    # (which limits its use e.g. from within nested submodule calls due to the
    # mechanism of Python function pickling) and submit any function, if only
    # available in sys.path during "submit" call
    if isinstance(function, basestring):
        try:
            function_obj = globals()[function]
        except KeyError:
            function_obj = locals()[function]
        except:
            # we cannot log here
            import socket
            print 'Function "%s" not found in scope on %s!' % (function, socket.gethostname())
            print traceback.format_exc(None)
    else:
        function_obj = function

    try:
        pc = pplus.PPlusConnection(id=experiment_id, debug=debug)
        return function_obj(pc, *args)
    except:
        # This block catch and log each exception and returns a JobError

        if pc is None: # We cannot log!
            import socket
            print ("An error occured during pplus "
                   "initialization on %s!" % socket.gethostname())
            print traceback.format_exc(None)
        else:
            msg = "An exception was raised during task execution"
            pc.session_logger.error(msg, exc_info=True)
            pc.session_logger.info("The job will be restarted in a new "
                                   "session (if allowed).")

            if debug:
                import os
                log_path = pc.session_logger._handler.baseFilename
                print '%s (see %s)' % (msg, os.path.relpath(log_path))

        return pplus.JobError


class JobError(object):
    """Internal object used in task submission control."""
    pass
