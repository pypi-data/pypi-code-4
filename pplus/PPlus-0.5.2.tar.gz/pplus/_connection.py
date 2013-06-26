"""PPlus connection interface."""

# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: new BSD.

import os
import uuid
import time
import shutil
import socket

from .core import pp
from . import ioutils
from .loggers import PPlusLogger
from .lockfile import FilesystemLock
from .jobutils import pplus_job, create_callback, JobError

# Config defaults
DEFAULT_JOB_RESUBMISSION_COUNTER = 0
DEFAULT_CACHE_WAITING_TIME = 2
DEFAULT_SESSION_LOG_LEVEL = 'DEBUG'
DEFAULT_EXPERIMENT_LOG_LEVEL = 'DEBUG'


class PPlusConnection(object):

    def __init__(self, id=None, config_file_path=None, debug=True,
                 local_workers_number=None, workers_servers=None, secret=None, experiment_label=None):
        """Implements common end point for accessing PPlus environment.

        Parameters
        ----------
        id : str, optional (default: None)
            experiment id. if None, create master connection instance;
            otherwise, create worker connection instance.

            Experiment ID is currently generated as :func:`uuid.uuid1` (for master
            connection) and :func:`uuid.uuid4` (for worker connection). See also
            "experiment_label" option.

        config_file_path : str, optional (default: None)
            path to PPlus configuration file.

            If None the configuration file will be searched in the
            current working directory and then in standard current and
            global location, '~/.pplus/pplus.cfg' and '/etc/pplus/pplus.cfg'.

            **In debug mode this option is ignored.**

        debug : bool, optional (default: True)
            if True create connection instance in PPlus debug mode.

        local_workers_number : int, optional (default: None)
            number of local workers forked by the master process.

            In debug mode, None means that `local_workers_number` is equal
            to the number of available cpus/cores.
            In normal mode, None means 0.

        workers_servers : list, optional (default: None)
            list of pplus servers addresses. It is possible to specify also port
            by using the format 'address:port'.
            Default port number is 60000
            If None, servers are automatically discovered (if they are running
            in auto-discovery mode).

            **In debug mode this option is ignored.**

        secret : str, optional (default: None)
            pass-phrase used to authenticate connections with workers servers.

            **In debug mode this option is ignored.**

        experiment_label : str, optional (default: None)
            label assigned to experiment

            If not None, the label will be prepended to experiment id, and
            experiment will be identified as '<label>_<id>'. This may ease the
            identification of particular experiment among others, since id is
            unique but not human readable. See "id" option notes for more details.

        Raises
        ------
        PPlusError
            when specified (or default) configuration file does not exist or
            when id does not contain proper mandatory option.

        """

        ### Loading and checking configuration file
        self._debug = debug
        if debug:
            # In debug mode we create fake cache and disk directories
            config = {'IO.DISK_PATH': 'disk', 'IO.CACHE_PATH': 'cache'}
            if not os.path.exists('disk'):
                os.mkdir('disk')
            if not os.path.exists('cache'):
                os.mkdir('cache')

            config_file_dir = os.getcwd()
        else:
            # input parameter has priority
            if config_file_path is None:

                config_cwd_path = 'pplus.cfg'
                config_user_path = os.path.expanduser('~/.pplus/pplus.cfg')
                config_system_path = os.path.normpath('/etc/pplus/pplus.cfg')

                # first search in current working directory
                if os.path.exists(config_cwd_path):
                    config_file_path = config_cwd_path
                elif os.path.exists(config_user_path):
                    config_file_path = config_user_path
                elif os.path.exists(config_system_path):
                    config_file_path = config_system_path
                else:
                    raise PPlusError("configuration file not found.")

            else:
                config_file_path = os.path.abspath(config_file_path)
                if not os.path.exists(config_file_path):
                    raise PPlusError("configuration file '%s' "
                                     "does not exist." % config_file_path)

            # configuration file found
            config = ioutils.read_config_file(config_file_path)

            # checking required parameters
            for required in ['IO.DISK_PATH', 'IO.CACHE_PATH']:
                if not required in config:
                    raise PPlusError("file '%s' is not a valid "
                                     "PPlus configuration file." %
                                     config_file_path)

            config_file_dir = os.path.dirname(config_file_path)

        ### Io Paths resolving, wrt config file directory
        config['IO.DISK_PATH'] = os.path.normpath(
                                    os.path.join(config_file_dir,
                                                 config['IO.DISK_PATH']))
        config['IO.CACHE_PATH'] = os.path.normpath(
                                    os.path.join(config_file_dir,
                                                 config['IO.CACHE_PATH']))

        ### Tasks counter
        self._task_cnt = 0

        ### Server options
        self._servers = workers_servers or ('*',)  # means autodiscovery
        self._secret = secret
        self._local_workers = local_workers_number

        ### Experiment and Session id creations
        ### Matteo 2013-02-28 The experiment ID is either
        ### 1) a string passed as an argument (in workers)
        ### 2) created appending an unique generated hash to a given experiment_label
        ### 3) a string generated by the uuid1() function
        if id:
            self._id = str(id)
            session_type = 'worker'
        elif experiment_label:
            self._id = experiment_label + "_" + str(uuid.uuid1().hex)
            session_type = 'master'
        else:
            self._id = uuid.uuid1().hex
            session_type = 'master'
        self._session_id = uuid.uuid4().hex

        ### Resubmission counter
        self.JOB_MAX_RESUBMISSION = int(config.get(
                                            'MASTER.JOB_MAX_RESUBMISSION',
                                            DEFAULT_JOB_RESUBMISSION_COUNTER))

        ### Cache waiting time
        self.CACHE_WAITING_TIME = int(config.get(
                                            'WORKER.CACHE_WAITING_TIME',
                                            DEFAULT_CACHE_WAITING_TIME))

        ### Experiment Paths
        disk_path = os.path.normpath(config['IO.DISK_PATH'])
        self._remote_path = os.path.abspath(os.path.join(disk_path, self.id))

        cache_path = os.path.normpath(config['IO.CACHE_PATH'])
        self._cache_path = os.path.abspath(os.path.join(cache_path, self.id))

        ### DISK: Experiment dir creation
        if not os.path.exists(self.disk_path):
            os.mkdir(self.disk_path)

        ### CACHE: Experiment dir creation (locked env)
        self._locked(self.cache_path, # Locked dir
                     ioutils.create_local_experiment_dirs, # Operation
                     args=(self.cache_path,), silent=True)  # Args

        ### Starting session logging
        # Logs are named as CACHE/logs/hostname.session.log
        sl_path = os.path.join(self.cache_path, 'logs',
                               '%s.%s.%s.log' % (socket.gethostname(),
                                                 session_type,
                                                 self.session_id))
        if self._debug:
            level = 'DEBUG'
        else:
            level = config.get('WORKER.SESSION_LOG_LEVEL',
                               DEFAULT_SESSION_LOG_LEVEL)
        self._session_logger = PPlusLogger('pplus.%s' % self.session_id, # Name
                                           sl_path,                      # Path
                                           level)                        # level
        # Logging started session
        msg = ('%s session %s of experiment '
               '%s initialized %s' % (session_type.title(),
                                      self.session_id, self.id,
                                      '(debug mode)' if self._debug else ''))
        self._session_logger.info(msg)

        ### Init server attribute
        self._server = None
        self._server_logger = None
        self._submitted_jobs = None
        self._executed_jobs = None
        if self._debug:
            self._server_logger_level = 'DEBUG'
        else:
            self._server_logger_level = config.get(
                                            'MASTER.EXPERIMENT_LOG_LEVEL',
                                            DEFAULT_EXPERIMENT_LOG_LEVEL)

    ### Read-Only attributes --------------------------------------------------
    @property
    def session_logger(self):
        """Instance of :class:`loggers.PPlusLogger`.

        Use this reference into job function to add messages in the session
        log.
        """
        return self._session_logger

    @property
    def disk_path(self):
        """Full path related with the current experiment on remote disk."""
        return self._remote_path

    @property
    def cache_path(self):
        """Full path related with the current experiment on local cache."""
        return self._cache_path

    @property
    def id(self):
        """Experiment ID of the current connection instance."""
        return self._id

    @property
    def session_id(self):
        """Session ID of the current connection instance."""
        return self._session_id

    @property
    def is_debug(self):
        """Indicates if the current connection instance is in debug mode."""
        return self._debug

    ### Public Methods: Disk managing  ----------------------------------------
    def put(self, key, src_path, overwrite=True):
        """Store specified file on currently configured disk resource, using
        specified file identifier.

        Parameters
        ----------
        key : str
            PPlus disk file identifier to use on remote side.

        src_path : str
            physical path to the file to be stored on remote disk resource.

        overwrite : bool, optional (default: True)
            if True, overwrite any existing remote file already associated
            with 'key' silently; otherwise, raise an error.

        Raises
        ------
        PPlusError
            when remote file is overwritten and silent overwriting of existing
            remote files is turned off.

        """
        self.session_logger.info("Putting file '%s' with "
                                 "key '%s'..." % (src_path, key))

        dst_path = os.path.join(self.disk_path, key)

        # Check file existence
        if not overwrite and os.path.exists(dst_path):
            msg = ("Key '%s' already used for "
                   "the current experiment (%s)" % (key, self.id))
            self.session_logger.error(msg)
            raise PPlusError(msg)

        shutil.copyfile(src_path, dst_path)
        self.session_logger.info("File '%s' with key '%s' "
                                 "successfully put" % (src_path, key))

    def remove(self, key):
        """Remove remote file, associated with specified file identifier, from
        currently configured disk resource.

        If requested remote file does not exist, do nothing.

        Parameters
        ----------
        key : string
            PPlus remote file identifier of requested file

        """
        self.session_logger.info("Removing file with key '%s'..." % key)

        remote_file_path = os.path.join(self.disk_path, key)
        cached_file_path = os.path.join(self.cache_path, key)

        # If already removed remotely: pass silently
        ioutils.remove_if_exists(remote_file_path)

        # Removing from cache in locked environment
        self._locked(cached_file_path, # we only lock the access to the file
                     ioutils.remove_if_exists, (cached_file_path,))

        self.session_logger.info("File with key '%s' successfully "
                                 "removed" % key)

    def get_path(self, key):
        """Get valid physical local path of the remote file associated with
        specified file identifier.

        This path is intended for opening the file **only** in read mode;
        use :func:`open_remotely` for write mode.

        The remote file is accessed through local cache. The first time it
        has been requested, it is transferred silently to the local cache.
        For every subsequent request, a copy from local cache will be accessed.

        Parameters
        ----------
        key : str
            PPlus remote file identifier of requested file.

        Returns
        -------
        physical_path : str
            physical path of remote file in the local cache,
            for opening the file in read mode **only**.

        Raises
        ------
        PPlusError
            if requested remote file cannot be accessed.

        """
        self.session_logger.info("Getting file path with key '%s'..." % key)

        # Path on remote disk and local cache
        src_path = os.path.join(self.disk_path, key)
        dst_path = os.path.join(self.cache_path, key)

        # Check if valid key
        if not os.path.exists(src_path):
            # If remotely removed, clean cached version
            self._locked(dst_path, ioutils.remove_if_exists, (dst_path,))

            msg = "Invalid file key '%s'!" % key
            self.session_logger.error(msg)

            raise PPlusError(msg)

        # Transfering file in the cache if it not already exists
        self._locked(dst_path, ioutils.copy_if_not_exists, (src_path,
                                                            dst_path))

        self.session_logger.info("File path with key '%s' "
                                 "successfully got" % key)
        return dst_path

    def write_remotely(self, key, binary=False, buffering= -1, overwrite=True):
        """Returns a file descriptor open for writing, associated with
        specified file identifier.

        The object returned by the function could also be used within a
        *with* statement.

        .. warning::
            The method returns a file-like object which actually write in
            worker's local cache. The file is transferred on the central
            disk only when you **close** it.
            Moreover, be aware that PPlus **does not check** for concurrent
            writing of the file.

        Parameters
        ----------
        key : str
            PPlus remote file identifier of requested file.

        binary : bool, optional (default: False)
            if True, force opening remote file in binary mode.

        buffering : int, optional (default: -1, system default)
            buffer size to use while opening remote file.
            If the buffering argument is given, 0 means unbuffered, 1 means
            line buffered, and larger numbers specify the buffer size.

        overwrite : bool
            if True, overwrite any existing remote file already associated
            with 'key' silently; otherwise, raise an error

        Returns
        -------
        fd : file
            file descriptor for the opened file

        Raises
        ------
        PPlusError
            when any error was reported during opening of remote file or
            when remote file is overwritten and silent overwriting of
            existing remote files is turned off

        See Also
        --------
        :class:`PPlusTemporaryCachedFile`

        """
        self.session_logger.info("Requested file opening "
                                 "with key '%s'..." % key)

        mode = 'wb' if binary else 'w'
        # Try to open the file
        try:
            # Temporary file in local cache
            cached_file = ioutils.PPlusTemporaryCachedFile(self, key,
                                                           mode, buffering,
                                                           overwrite)
        except IOError, e:
            self.session_logger.error(str(e))
            raise PPlusError(e)

        self.session_logger.info("File with key '%s' successfully "
                                 "opened" % key)
        return cached_file

    ### Public Methods: Jobs managing  ----------------------------------------
    def submit(self, function, args=(), depfuncs=(), modules=()):
        """Submit requested callable/deepfunction as a task to be executed in parallel
        within current PPlus environment.

        The callable **has to accept** as first parameter an instance
        of :class:`PPlusConnection` which will be instantiated and
        passed automatically by PPlus and may return any valid Python
        pickeable object.

        .. note::

            For `direct` submission, "function" is a callable. However, callable
            can be also submitted in `indirect` mode, where callable itself is
            added to `depfuncs` and callable name is given as "function". During
            job execution, callable is then reconstructed in correct scope by
            its name. This mechanism allows circumventing natural limitations
            of callable submission in Parallel Python (which stems from limitations
            of function pickling in Python itself), and allows submission of `any`
            function, if only accessible through :data:`sys.path`. See :ref:`submission`
            for more details.

        .. warning::

            If your job function produce a very big result may be more
            efficient to save the result on the disk.

            1. Create manually a file in the local cache (that we can assume
               writable)::

                   # pc = PPlusConnection instance given by PPlus
                   tmp_file = os.path.join(pc.cache_path, 'UNIQUE_FILE_NAME')

                   with open(tmp_file) as f:
                       # do something with f

                   pc.put('KEY', tmp_file)

            2. Use the :meth:`write_remotely` method::

                  # pc = PPlusConnection instance given by PPlus
                  with pc.write_remotely('KEY')) as f:
                      # do something with f

        Parameters
        ----------
        function : callable/string
            callable object/callable name to be sent as task for parallel execution.

            If string, "function" is interpreted as callable `name`. Subsequently,
            the corresponding callable MUST be added to `depfuncs`, otherwise an
            error will occur!

        args : iterable
            any positional arguments for requested callable.

        depfuncs : iterable
            any depended callables ('deep functions') for requested callable.

        modules : iterable
            list of module names that requested callable imports when
            executed on remote side.

        """

        self._submit_task(function, args, depfuncs, modules)

    def collect(self, clean_executed=False):
        """Wait for all submitted but not completed tasks; when all tasks are
        completed, collect their partial results and return them.

        If `clean_executed` is True new tasks can be submitted afterwards,
        allowing submission cycles::

                submit()      # 1
                ...
                submit()      # 10
                collect(True) # get 1..10
                collect(True) # get NULL
                submit()      # 11
                ...
                submit()      # 20
                collect(True) # get 11..20
                collect(True) # get NULL

        if False, preserve content of internal cache between calls, so older
        partial results will be available with newer ones::

                submit()       # 1
                ...
                submit()       # 10
                collect(False) # get 1..10
                collect(False) # get 1..10
                submit()       # 11
                ...
                submit()       # 20
                collect(False) # get 1..20
                collect(False) # get 1..20

        Parameters
        ----------
        clean_executed : bool, optional (default: True)
            if True, clean internal cache immediately after collection
            succeeded.

        Returns
        -------
        results : iterable
            partial results from each submitted and completed task

        Raises
        ------
        PPlusError
            when no task has been submitted yet

        """

        if self._server is None:
            msg = 'No task submitted or pending, nothing to collect!'
            self.session_logger.error(msg)
            raise PPlusError(msg)

        # Wait all the task are ended and select executed job
        if self._submitted_jobs:
            self._server.wait()
            self._executed_jobs.extend(self._select_executed_jobs())

        # Collect the results
        results = [f() for f in self._executed_jobs]

        # Cleaning executed jobs
        if clean_executed:
            self._executed_jobs = list()

        return results

    ### Private Methods: Jobs managing  ---------------------------------------
    def _submit_task(self, function, args, depfuncs, modules, task_id=None,
                     submission_cnt=0):
        """Internal submission method.

        Parameters
        ----------
        function : callable
            callable to be sent as task for parallel execution.

        args : iterable
            any positional arguments for requested callable.

        depfuncs : iterable
            any depended callables ('deep functions') for requested callable.

        modules : iterable
            list of module names that requested callable imports when
            executed on remote side.

        task_id : int, optional (default: None)
            unique progressive identifier associated to the task.

        submission_cnt : int, optional (default: 0)
            counter internally used to count how many times a job is
            resubmitted due of errors. When `submission_cnt` reaches the
            maximum number of resubmission, the job is not submitted anymore.

        """

        if self._server is None:
            self._prepare_server()

        # Callback creation (bounding self)
        job_callback = create_callback(self)
        if task_id is None:
            task_id = self._task_cnt = (self._task_cnt + 1)

        # Submission!
        job_args = (function, self.id, self._debug, args)
        callback_args = (function, args, depfuncs, modules,
                         task_id, submission_cnt)
        f = self._server.submit(pplus_job, args=job_args,
                                depfuncs=depfuncs, modules=modules,
                                callback=job_callback,
                                callbackargs=callback_args,
                                tid=task_id)
        self._submitted_jobs.append(f)

    def _prepare_server(self):
        log_path = os.path.join(self.disk_path, 'experiment.log')
        self._server_logger = PPlusLogger('pplus', log_path,
                                          self._server_logger_level)

        if self._debug:
            self._server = pp.Server(ppservers=())

            if self._local_workers is None:
                self._local_workers = self._server.get_ncpus()
            self._server.set_ncpus(self._local_workers)

        else:
            if self._local_workers is None:
                self._local_workers = 0
            self._server = pp.Server(ppservers=self._servers,
                                     ncpus=self._local_workers,
                                     secret=self._secret)

        self._submitted_jobs = list()
        self._executed_jobs = list()

    def _select_executed_jobs(self):
        executed_jobs = list()
        for f in self._submitted_jobs:
            if not f() is JobError:
                executed_jobs.append(f)
        self._submitted_jobs = list()

        return executed_jobs

    def _locked(self, lock_name, operation, args=(), silent=False):
        # File lock
        lock = FilesystemLock('%s.lock' % lock_name)

        # Trying to acquire the lock
        while not lock.lock():
            if not silent:
                self.session_logger.info('Cache locked, waiting %d seconds...'
                                         % self.CACHE_WAITING_TIME)
            time.sleep(self.CACHE_WAITING_TIME)

        # When the lock is acquired, perform the required operation
        if lock.locked:
            if not silent:
                self.session_logger.info('Cache lock acquired')
            try:
                result = operation(*args, clean=lock.clean)
            except:
                # This block catch and log exceptions and raise a PPlusError
                import sys
                e = sys.exc_info()[1]
                if not silent:
                    self.session_logger.error("%s '%s'" %
                                              (e.__class__.__name__, str(e)))
                raise PPlusError(e)
        else:
            msg = 'An error has occurred during cache locking!'
            if not silent:
                self.session_logger.critical(msg)
            raise PPlusError(msg)

        # Unlock and return result
        lock.unlock()
        return result


class PPlusError(Exception):
    """General exception used for reporting PPlus errors."""
    pass
