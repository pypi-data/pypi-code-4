"""
The records module defines the Record class, which gathers and stores
information about an individual simulation or analysis run.

Classes
-------

Record - gathers and stores information about an individual simulation or
         analysis run.
         Can be instantiated directly, but more usually created by the
         new_record() method of Project.
"""

from datetime import datetime
import time
import os
from os.path import relpath, normpath, join, basename, exists
import re
import getpass
from operator import or_
from formatting import get_formatter
import dependency_finder
from sumatra.core import TIMESTAMP_FORMAT
from sumatra.users import get_user
from versioncontrol import VersionControlError
import logging

logger = logging.getLogger("Sumatra")


def assert_equal(a, b, msg=''):
    assert a == b, "%s: %s %s != %s %s" % (msg, a, type(a), b, type(b))


class MissingInformationError(Exception):
    pass


class Record(object):
    """
    The :class:`Record` class has two main roles: capturing information about
    the context of a computation, and storing this information for later
    retrieval.
    """

    def __init__(self, executable, repository, main_file, version, launch_mode,
                 datastore, parameters={}, input_data=[], script_arguments='',
                 label=None, reason='', diff='', user='', on_changed='error',
                 input_datastore=None, stdout_stderr='Not launched.',
                 timestamp=None, timestamp_format=TIMESTAMP_FORMAT):
        # we allow for the timestamp to be set as an argument to allow for
        # distributed/batch simulations on machines with out-of-sync clocks,
        # but only do this if you really know what you're doing, otherwise the
        # association of output data with this record may be incorrect
        self.timestamp = timestamp or datetime.now() 
        self.label = label or self.timestamp.strftime(timestamp_format)
        assert len(self.label) > 0
        self.reason = reason
        self.duration = None
        self.executable = executable # an Executable object incorporating path, version, maybe system information
        self.repository = repository # a Repository object
        self.main_file = main_file
        self.version = version
        self.parameters = parameters
        self.input_data = input_data # a list containing DataKey objects
        self.script_arguments = script_arguments
        self.launch_mode = launch_mode # a LaunchMode object - basically, run serially or with MPI. If MPI, what configuration
        self.datastore = datastore.copy()
        self.input_datastore = input_datastore or self.datastore
        self.outcome = ''
        self.output_data = []
        self.tags = set()
        self.diff = diff
        self.user = user
        self.on_changed = on_changed
        self.stdout_stderr = stdout_stderr

    def register(self, working_copy):
        """Record information about the environment."""
        # Check the code hasn't changed and the version is correct
        logger.debug("Checking code")
        if len(self.diff) == 0:
            assert not working_copy.has_changed()
        assert_equal(working_copy.current_version(), self.version, "version")
        # Check the main file is in the working copy
        cwd_relative_to_wc = relpath(os.getcwd(), working_copy.path)
        if self.main_file:
            if not working_copy.contains(
                    normpath(join(cwd_relative_to_wc, self.main_file))):
                raise VersionControlError("Main file %s is not under version control" % self.main_file)
        # Record dependencies
        logger.debug("Recording dependencies")
        self.dependencies = []
        if self.main_file is None:
            if self.executable.requires_script:            
                raise MissingInformationError("main script file not specified")
        else:
            if len(self.main_file.split()) == 1: # this assumes filenames cannot contain spaces
                self.dependencies = dependency_finder.find_dependencies(self.main_file, self.executable)
            else: # if self.main_file contains multiple file names
                # this seems a bit hacky. Should perhaps store a list self.main_files, _and_ check that all files exist.
                for main_file in self.main_file.split():
                    self.dependencies.extend(dependency_finder.find_dependencies(main_file, self.executable))
            # if self.on_changed is 'error', should check that all the dependencies have empty diffs and raise an UncommittedChangesError otherwise
        # Record platform information
        logger.debug("Recording platform information")
        self.platforms = self.launch_mode.get_platform_information()
        # Record information about the current user
        self.user = get_user(working_copy)

    def run(self, with_label=False):
        """
        Launch the simulation or analysis.

        *with_label*
            adds the record label either to the parameter file
            (`with_label="parameters"`) or to the end of the command line
            (`with_label="cmdline"`), and appends the label to the datastore
            root. This allows the program being run to create files in a
            directory specific to this run.

        """
        logger.debug("Launching computation")
        data_label = None
        if with_label:
            if with_label == 'parameters':
                self.parameters.update({"sumatra_label": self.label})
            elif with_label == 'cmdline':
                data_label = self.label
            else:
                raise Exception("with_label must be either 'parameters' or 'cmdline'")
            self.datastore.root  = join(self.datastore.root, self.label)
        # run pre-simulation/analysis tasks, e.g. nrnivmodl
        self.launch_mode.pre_run(self.executable)
        # Write the executable-specific parameter file
        script_arguments = self.script_arguments
        if self.parameters:
            parameter_file_basename = self.label.replace("/", "_")
            self.parameter_file = self.executable.write_parameters(self.parameters, parameter_file_basename)
            script_arguments = script_arguments.replace("<parameters>", self.parameter_file)
        # Run simulation/analysis
        start_time = time.time()
        result = self.launch_mode.run(self.executable, self.main_file,
                                      script_arguments, data_label)
        self.duration = time.time() - start_time

        # try to get stdout_stderr from launch_mode
        try:
            if self.launch_mode.stdout_stderr not in (None,""):
                self.stdout_stderr = self.launch_mode.stdout_stderr
            else:
                self.stdout_stderr = "No output."
        except:
            self.stdout_stderr = "Not available."
        # Run post-processing scripts
        # pass # skip this if there is an error
        # Search for newly-created datafiles
        self.output_data = self.datastore.find_new_data(self.timestamp)
        if self.output_data:
            print "Data keys are", self.output_data
        else:
            print "No data produced."
        if self.parameters and exists(self.parameter_file):
            time.sleep(0.5) # execution of matlab: parameter_file is not always deleted immediately
            os.remove(self.parameter_file)

    def __repr__(self):
        return "Record #%s" % self.label

    def describe(self, format='text', mode='long'):
        """
        Return a description of the record.
        
        *mode*:
            either 'long' or 'short'
        *format*
            either 'text' or 'html'
        """
        formatter = get_formatter(format)([self])
        return formatter.format(mode)

    def __ne__(self, other):
        return bool(self.difference(other))

    def __eq__(self, other):
        return not self.__ne__(other)

    def difference(self, other_record, ignore_mimetypes=[], ignore_filenames=[]):
        """
        Determine the difference between this computational experiment and
        another (code, platform, results, etc.).

        Return a RecordDifference object.
        """
        return RecordDifference(self, other_record, ignore_mimetypes, ignore_filenames)

    def delete_data(self):
        """
        Delete any data files associated with this record.
        """
        self.datastore.delete(*self.output_data)
        self.output_data = []

    @property
    def command_line(self):
        """
        Return the command-line string for the computation captured by this
        record.
        """
        return self.launch_mode.generate_command(self.executable, self.main_file, self.script_arguments)


class RecordDifference(object):
    """Represents the difference between two Record objects."""

    ignore_mimetypes = [] #r'image/\w+', r'video/\w+']
    ignore_filenames = [r'\.log', r'^log']

    def __init__(self, recordA, recordB,
                 ignore_mimetypes=[],
                 ignore_filenames=[]):
        self.recordA = recordA
        self.recordB = recordB
        assert not isinstance(ignore_mimetypes, basestring) # catch a
        assert not isinstance(ignore_filenames, basestring) # common error
        self.ignore_mimetypes += ignore_mimetypes
        self.ignore_filenames += ignore_filenames
        self.executable_differs = recordA.executable != recordB.executable
        self.repository_differs = recordA.repository != recordB.repository
        self.main_file_differs = recordA.main_file != recordB.main_file
        self.version_differs = recordA.version != recordB.version
        for rec in recordA, recordB:
            if rec.parameters:
                rec.parameters.pop("sumatra_label", 1)
        self.parameters_differ = recordA.parameters != recordB.parameters
        self.script_arguments_differ = recordA.script_arguments != recordB.script_arguments
        self.launch_mode_differs = recordA.launch_mode != recordB.launch_mode
        self.diff_differs = recordA.diff != recordB.diff

    def __nonzero__(self):
        """
        Return True if there are differences in executable, code, parameters or
        output data between the records, otherwise return False.

        Differences in launch mode or platform are not counted, since those
        don't in principle make it a different experiment (they may do in
        practice, but then the output data will be different).
        """
        return reduce(or_, (self.executable_differs, self.code_differs,
                            self.input_data_differ, self.script_arguments_differ,
                            self.parameters_differ, self.output_data_differ))

    def __repr__(self):
        s = "RecordDifference(%s, %s):" % (self.recordA.label, self.recordB.label)
        if self.executable_differs:
            s += 'X'
        if self.code_differs:
            s += 'C'
        if self.parameters_differ:
            s += 'P'
        if self.output_data_differ:
            s += 'D'
        if self.input_data_differ:
            s += 'I'
        if self.script_arguments_differ:
            s += 'S'
        return s

    @property
    def code_differs(self):
        return reduce(or_, (self.repository_differs, self.main_file_differs,
                            self.version_differs, self.diff_differs,
                            self.dependencies_differ))

    @property
    def dependencies_differ(self):
        return set(self.recordA.dependencies) != set(self.recordB.dependencies)

    @property
    def dependency_differences(self):
        depsA = {}
        for dep in self.recordA.dependencies:
            depsA[dep.name] = dep
        depsB = {}
        for dep in self.recordB.dependencies:
            depsB[dep.name] = dep
        diffs = {}
        for name in depsA:
            if name in depsB:
                if depsA[name] != depsB[name]:
                    diffs[name] = (depsA[name], depsB[name])
            else:
                diffs[name] = (depsA[name], None)
        for name in depsB:
            if name not in depsA:
                diffs[name] = (None, depsB[name])
        return diffs

    def _list_datakeys(self, direction):
        keys = {self.recordA.label: {}, self.recordB.label: {}}
        assert direction in ('input_data', 'output_data')
        for rec in self.recordA, self.recordB:
            dataset = getattr(rec, direction)
            for key in dataset:
                ignore = False
                name = basename(key.path) # not sure this makes sense for archive data store
                if key.metadata['mimetype']:
                    for pattern in self.ignore_mimetypes:
                        if re.match(pattern, key.metadata['mimetype']):
                            ignore = True
                            break
                for pattern in self.ignore_filenames:
                    if re.search(pattern, name):
                        ignore = True
                        break
                if not ignore:
                    keys[rec.label][key.digest] = key
        return keys

    def _data_differ(self, direction):
        keys = self._list_datakeys(direction)
        A = set(keys[self.recordA.label].keys())
        B = set(keys[self.recordB.label].keys())
        if len(A) == len(B) == 0:
            return False
        if A.difference(B):
            return True
        else:
            return False

    @property
    def output_data_differ(self):
        return self._data_differ('output_data')

    @property
    def input_data_differ(self):
        return self._data_differ('input_data')

    def _data_differences(self, direction):
        keys = self._list_datakeys(direction)
        A = set(keys[self.recordA.label])
        B = set(keys[self.recordB.label])
        return ([keys[self.recordA.label][digest] for digest in A.difference(B)],
                [keys[self.recordB.label][digest] for digest in B.difference(A)])

    @property
    def output_data_differences(self):
        return self._data_differences('output_data')

    @property
    def input_data_differences(self):
        return self._data_differences('input_data')

    @property
    def launch_mode_differences(self):
        if self.launch_mode_differs:
            return self.recordA.launch_mode, self.recordB.launch_mode
        else:
            return None
