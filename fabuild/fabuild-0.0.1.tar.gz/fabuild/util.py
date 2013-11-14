"""
Contains utility methods
"""
import atexit
import fnmatch
import itertools
import glob
import logging
import os
import re
import time
import thread

from fabric.api import env, settings

logger = logging.getLogger(__name__)


def _get_files(path=None, recursive=True, only_files=False,
               only_dirs=False, match=None, ignore=None,
               match_re=None, ignore_re=None,
               ignore_symlinks=True, **kwargs):
    """

    Gets a list of files based on the given parameters

    :param path: The root path at which to search
    :param recursive: True to recursively search path children
    :param only_files: True to only accept files
    :param only_dirs: True to only accept dirs
    :param match: List of name strings to match using fnmatch, tests against full path.
    :param ignore: List of name strings to ignore using fnmatch, tests against full path..
    :param match_re: List of name strings to match using regex, tests against full path.
    :param ignore_re: List of name strings to ignore using regex, tests against full path.
    :param ignore_symlinks: True if we want to ignore symlink files

    :returns: List of file strings
    """
    def tolist(x):
        x = x or []
        if isinstance(x, basestring):
            x = [x]
        if not isinstance(x, list):
            raise Exception("Invalid configuration - Must be list or string")
        return x

    match = tolist(match)
    ignore = tolist(ignore)
    match_re = tolist(match_re)
    ignore_re = tolist(ignore_re)

    if not path:
        raise Exception("Must specify a path when calling get_files with a dict.")

    path = os.path.abspath(os.path.expanduser(path))

    if not os.path.exists(path):
        raise ValueError("Path given to get_files does not exist: " + path)

    if os.path.isfile(path):
        return list({path})

    def should_add(path, f):
        if match_re and not any([m for m in match_re if re.search(m, f)]):
            return False

        if ignore_re and any([i for i in ignore_re if re.search(i, f)]):
            return False

        if match and not any([m for m in match if fnmatch.fnmatch(f, m)]):
            return False

        if ignore and any([i for i in ignore if fnmatch.fnmatch(f, i)]):
            return False

        if only_files and not os.path.isfile(os.path.join(path, f)):
            return False

        if only_dirs and os.path.isfile(os.path.join(path, f)):
            return False

        if ignore_symlinks and os.path.islink(os.path.join(path, f)):
            return False

        return True

    paths = set()
    if recursive:
        for top, dirs, files in os.walk(path, followlinks=not ignore_symlinks):
            children = [f for f in dirs + files if should_add(top, os.path.join(top, f))]
            for child in children:
                paths.add(os.path.join(top, child))
    else:
        paths = {os.path.join(path, f) for f in os.listdir(path) if
                 should_add(path, os.path.join(path, f))}

    return list(paths)


def get_files(files):
    """

    Takes a file variable and returns the list of files

    :param files: If a falsy value, returns an empty list.
                  If a string, is turned into a list then globbed like a list (see below).
                  If a tuple of strings, each string will have os.path.expanduser
                  and os.path.abspath ran on them, then they will be returned.
                  If a list of strings, each string is ran through glob.glob and
                  returned as a list containing all of the unique paths returned from glob.glob.
                  If list of dicts, each dict is ran through _get_files and
                  returns the list of unique paths retrieved from all the calls.
                  If dict is ran through _get_files.

    :returns: List of file strings
    """
    if not files:
        return []

    if isinstance(files, basestring):
        files = [files]

    if isinstance(files, tuple):
        return [os.path.abspath(os.path.expanduser(f)) for f in files]

    if isinstance(files, list):
        if isinstance(files[0], basestring):
            files = [os.path.abspath(os.path.expanduser(f)) for f in files]
            return list(set(itertools.chain(*[glob.glob(f) for f in files])))

        elif isinstance(files[0], dict):
            files = [_get_files(**f) for f in files]
            return list(set(itertools.chain(*files)))

    if isinstance(files, dict):
        return _get_files(**files)


def run_function_list(fns, predicate=None):
    """
    Runs a list of functions
    :param fns: list of dicts with three keys: fn (function object),
                                               args (list of args),
                                               kwargs (dict of kwargs)
    :param predicate: if this function returns false, given the current function, it will not be ran
    """
    for fn in fns:
        if predicate and not predicate(fn):
            continue

        if isinstance(fn, dict) and 'fn' in fn:
            fn['fn'](*fn.get('args', []), **fn.get('kwargs', {}))
        elif callable(fn):
            fn()
        else:
            raise Exception("Invalid function")


def build_run(cmd, files=None, all_files=True, async=False, sync_first=False, keep_alive=0, *args, **kwargs):
    """
    Runs a command for the build system.  Respects remote building, but also allows
    for local access.  Supports asynchronous commands as well as keeping commands alive.

    :param cmd: The command to run.  Can be string for shell command, or function.

    :param files: The files to run the command against.  cmd should contain a '{}'
                  string which will then be replaced with each file name sequentially
                  through string.format if cmd is a shell command. If '{}' is missing,
                  files are just appended onto the shell command.  If cmd is a function,
                  files will be passed into the function as a kwarg.

    :param all_files: If true, will run the command with all files at once. If false,
                      calls the command separately for each file. Only applicable when using files.

    :param async: If true, this will run the command in a separate thread

    :param sync_first: If true and async is true, the command will run first synchronously,
                       then it will run in async mode.

    :param keep_alive: If non-0, wraps command with a loop that will automatically
                       re-run the command if it dies, waiting keep_alive seconds between
                       each run.  This can be used in two ways:
                       1) making sure a process that shouldn't ever die gets restarted
                       2) make a task that runs periodically every keep_alive seconds

    :param args: args to pass to run/local commands

    :param kwargs: kwarsg to pass to run/local commands

    :returns: Thread ID if async is True, else None
    """
    from fabric.api import run, local

    host = getattr(env, 'host', None)

    logger.info("Running command {} with args {} and kwargs {}".format(cmd, args, kwargs))

    # If this is a function, we will wrap it in a lambda to call it with the appropriate
    # args.  If it's a string, we assume a shell command, that will be ran through
    # the fabric local or run commands
    if callable(cmd):
        r = lambda c, *a, **k: c(*a, **k)
    else:
        r = local if not host or host == 'localhost' else run

    def keep_alive_fn(command, *a, **kws):
        """
        Function to run to keep command alive.  Can be used to ensure a command
        doesn't die, or to run a command periodically (every keep_alive seconds)
        """
        while True:
            try:
                # Don't kill on command exit
                with settings(warn_only=True):
                    r(command, *a, **kws)
                logger.warn(
                    "Command {} with args {} and kwargs {} died. "
                    "Restarting after 1 second.".format(command, a, kws)
                )
            except:
                logger.exception(
                    "Command {} with args {} and kwargs {} "
                    "caused an exception. Restarting after 1 second.".format(command, a, kws)
                )
            finally:
                time.sleep(keep_alive)

    run_fn = r
    if keep_alive > 0:
        register_keep_alive()
        run_fn = keep_alive_fn

    def run_seq_or_async(c, *a, **k):
        if async:
            # If async is true, run this function in an asynchronous task
            if sync_first:
                # If sync first is true, run this synchronously before kicking off async thread
                r(c, *a, **k)
            return thread.start_new_thread(run_fn, tuple([c] + list(a)), k)
        else:
            run_fn(c, *a, **k)

    if files:
        if callable(cmd):
            # If we have files and this is a function, run the function passing the files as kwargs
            if all_files:
                return run_seq_or_async(cmd, files=files, *args, **kwargs)
            else:
                for f in files:
                    return run_seq_or_async(cmd, files=f, *args, **kwargs)
                    
        else:
            # If we have files and this is shell command, run the shell command once per each file
            files = get_files(files)
            if all_files:
                cmd_files = " ".join(['"' + f + '"' for f in files])
                if '{}' in cmd:
                    # If we're using files, wrap in quotes and format them into the command using {}
                    return run_seq_or_async(cmd.format(cmd_files), *args, **kwargs)
                else:
                    return run_seq_or_async(cmd + ' ' + cmd_files, *args, **kwargs)
            else:
                for f in files:
                    if '{}' in cmd:
                        # If we're using files, wrap in quotes and format them into the command using {}
                        return run_seq_or_async(cmd.format('"' + f + '"'), *args, **kwargs)
                    else:
                        return run_seq_or_async(cmd + ' "' + f + '"', *args, **kwargs)
    else:
        return run_seq_or_async(cmd, *args, **kwargs)


def register_keep_alive():
    """
    Registers a hook to keep the process alive at system exit.
    Useful for running watches and keeping a debug session alive
    """
    logger.debug("Registering keep-alive function")
    build_keep_alive = getattr(env, 'build_keep_alive', False)
    if not build_keep_alive:
        env.build_keep_alive = True
        atexit.register(keep_alive)


def keep_alive():
    """
    Simple runtime loop to keep application alive
    """
    logger.debug("Running keep-alive function")
    while True:
        time.sleep(1)


