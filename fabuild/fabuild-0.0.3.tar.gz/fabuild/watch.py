"""
Contains utilities to watch files and run commands on file updates
"""
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from util import get_files, register_keep_alive, run_function_list


logger = logging.getLogger(__name__)


def watch(fns, path, files=None, run_immediately=True, recursive=False, keep_alive=True, handler=None):
    """

    Runs the given function list when items at path change

    :param fns: function list that will be run when path changes. Can be either a
                dict with 3 keys: fn, args, kwargs
                OR can be a partial function (using functools.partial)
                OR can be a list of either/both of those things.
    :param path: The path for the watchdog to observe
    :param files: The files to watch. File list will be retrieved using util.get_files,
                  If this is a dict and no path is specified, path will be passed in to files.
    :param run_immediately: True to run all functions immediately
    :param recursive: true to watch files in path recursively
    :param keep_alive: true to keep build script alive for this watch
    :param handler: the watch handler to use

    """

    logger.debug("Registering watch function")

    if not path:
        raise Exception("Must specify a path to watch")

    if not isinstance(fns, list):
        fns = [fns, ]

    if run_immediately:
        run_function_list(fns)

    # get_files call with a dict must specify a path anyway.
    if files:
        # If files is a dict and no path is specified, set the path on files.
        if isinstance(files, dict) and 'path' not in files:
            files['path'] = path
        # If files is a list of dicts and no path is specified on any of them, set the path for all
        # missing path information
        elif isinstance(files, list) and isinstance(files[0], dict):
            for f in files:
                if 'path' not in f:
                    f['path'] = path

    f = get_files(files) if files else None
    handler = handler or WatchHandler(fns, predicate=lambda event: not f or event.src_path in f)

    observer = Observer()
    observer.schedule(
        handler,
        path=path,
        recursive=recursive
    )

    observer.start()

    if keep_alive:
        register_keep_alive()


class WatchHandler(FileSystemEventHandler):
    """
    Default watch handler class
    """
    def __init__(self, fns, callback=None, predicate=None):
        """
        initialize watch handler
        :param fns: function list to run on event
        :param callback: function to call
        """
        self.fns = fns
        self.callback = callback
        self.predicate = predicate

    def dispatch(self, event):
        """Dispatches events to the appropriate methods.

        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """
        logger.debug("Got {} watch dispatch for path {}. Event: ".format(event.event_type,
                                                                         event.src_path,
                                                                         str(event)))
        if self.predicate and not self.predicate(event):
            return
        super(WatchHandler, self).dispatch(event)

    def on_any_event(self, event):
        """
        Run the functions on any event
        """
        logger.debug("Got {} event for path {}. Event: ".format(event.event_type,
                                                                event.src_path,
                                                                str(event)))

        try:
            def predicate(fn):
                """
                This predicate will determine if a function should run in the watch based on
                if the task files were modified for that function.
                :param fn: the functions to see if we should run
                :return: True if the function should run.
                """
                if isinstance(fn, dict) and fn.get('kwargs') and 'files' in fn['kwargs']:
                    return event.src_path in get_files(fn['kwargs']['files'])
                elif callable(fn) and fn.keywords and 'files' in fn.keywords:
                    return event.src_path in get_files(fn.keywords.files)

                return False

            run_function_list(self.fns)
            if self.callback:
                self.callback(event, self.fns)
        except:
            logger.exception(
                "An error occurred in watch. Event {} for {}".format(event.event_type,
                                                                     event.src_path),
                )


