#!/usr/bin/env python3.2
#
# Copyright (c) Net24 Limited, Christchurch, New Zealand 2011-2012
#       and     Voyager Internet Ltd, New Zealand, 2012-2013
#
#    This file is part of py-magcode-core.
#
#    Py-magcode-core is free software: you can redistribute it and/or modify
#    it under the terms of the GNU  General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Py-magcode-core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU  General Public License for more details.
#
#    You should have received a copy of the GNU  General Public License
#    along with py-magcode-core.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import sys
import json
import threading
import copy
from subprocess import *

from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import make_transient

from magcode.core.globals_ import settings
from magcode.core.logging import *
from magcode.core.database import *
from magcode.core.database.state_machine import StateMachine
from magcode.core.database.state_machine import SMEvent
from magcode.core.database.state_machine import StateMachineError
from magcode.core.database.state_machine import StateMachineFatalError
from magcode.core.database.state_machine import smregister
from magcode.core.database.event import Event
from magcode.core.database.event import eventregister


# some state static constant
PSTATE_START = 'START'
PSTATE_RUN = 'RUN'
PSTATE_SUCCESS = 'SUCCESS'
PSTATE_FAILURE = 'FAILURE'
process_sm_states = (PSTATE_START, PSTATE_RUN, PSTATE_SUCCESS, PSTATE_FAILURE)

_process_list = []

# Error Exceptions
class ProcessError(StateMachineError):
    """
    Base exception for Process State Machine.
    """
    pass

class ProcessFatalError(StateMachineFatalError):
    """
    Base exception for Process State Machine Fatal errors.
    """
    pass

class ProcessExecError(ProcessFatalError):
    """
    Process could not be executed. Typically file not found, or
    Invalid arguments to POpen
    """
    def __init__(self, *args, **kwargs):
        if (not len(args) and not len(kwargs)):
            ProcessFatalError.__init__(self, "Execution failure")
        else:
            ProcessFatalError.__init__(self, *args, **kwargs)

class ProcessExitError(ProcessFatalError):
    """
    Process exited with an error. Typically wrong arguments or something
    """
    def __init__(self, *args, **kwargs):
        if (not len(args) and not len(kwargs)):
            ProcessFatalError.__init__(self, "Process exit() error")
        else:
            ProcessFatalError.__init__(self, *args, **kwargs)

class ProcessSignalError(ProcessFatalError):
    """
    Process killed by signal.
    """
    def __init__(self, *args, **kwargs):
        if (not len(args) and not len(kwargs)):
            ProcessFatalError.__init__(self, "Process killed by signal")
        else:
            ProcessFatalError.__init__(self, *args, **kwargs)

class ProcessTempFailError(ProcessError):
    """
    Temporary failure - resource termporarily not available
    """
    def __init__(self, *args, **kwargs):
        if (not len(args) and not len(kwargs)):
            ProcessError.__init__(self, "Temporary execution failure")
        else:
            ProcessError.__init__(self, *args, **kwargs)

class ProcessNoArgumentError(ProcessFatalError):
    """
    No arguments or command given for a process
    """
    def __init__(self, *args, **kwargs):
        if (not len(args) and not len(kwargs)):
            ProcessFatalError.__init__(self, 
                    "No Arguments of command given for a process")
        else:
            ProcessFatalError.__init__(self, *args, **kwargs)

class ProcessNotAnEventError(ProcessFatalError):
    """
    Event sent on success of process is not an event at all
    """
    def __init__(self, pseudo_event=None, *args, **kwargs):
        if (pseudo_event):
            self.pseudo_event = pseudo_event
            ProcessFatalError.__init__(self, "%s is not one of %s" 
                    % (str(pseudo_event), sql_data['event_type_list']))
        elif (not len(args) and not len(kwargs)):
            ProcessFatalError.__init__(self, 
                "Object or string submitted is not representative of an Event()")
        else:
            ProcessFatalError.__init__(self, *args, **kwargs)


# State Machine Events
@eventregister
class ProcessSMExecEvent(SMEvent):
    """
    Start a process running
    """
    pass

@eventregister
class ProcessSMResetEvent(SMEvent):
    """
    Event issued to clean up and reset process SM to START
    """
    pass

# State Machine class
@smregister
class ProcessSM(StateMachine):
    """
    Process State machine

    Runs a process.  State kept in SQL database. Uses the subprocess module,
    running from a thread.
    Event objects are ProcessSMExecEvent, ProcessSMSuccessEvent, and 
    ProcessSMFailureEvent 
    """
    # SQL Alchemy database table name
    _table = 'sm_process'
    # Events asscoiated with this state machine
    _sm_events = (ProcessSMExecEvent, ProcessSMResetEvent)

    # Event action methods
    def _exec(self, event):
        """
        Spawn a Thread that watches event via subprocess module
        """
        db_session = event.db_session
        self.state = PSTATE_RUN
        self.start = db_clock_time(db_session)
        db_session.flush()
        log_str = "ProcessSM.run_thread() %s(%s)" \
                    % (self.name, self.exec_path)
        error_str = None
        try:
            # Do the Dirty Work eh eh ahh!
            argv = json.loads(self.argv)
            process = Popen(args=argv, executable=self.exec_path, 
                    cwd=self.cwd, env=self.env,
                    stdin=PIPE, stdout=PIPE, stderr=PIPE)
            # On Posix, processes consume bytes (which could be utf-8)
            stdin = bytes(self.stdin, 'utf8')
            (stdout, stderr) = process.communicate(stdin)
            # Convert returned text to Python unicode
            self.stdout = stdout.decode()
            self.stderr = stderr.decode()
        
        except OSError as exc:
            error_str = "%s %s - %s" % (log_str, exc.filename, exc.strerror)
        except ValueError as exc:
            error_str = "%s - %s" % (log_str, str(exc))
        
        if (error_str):
            # Typically can't execute process
            self.state = PSTATE_FAILURE
            self.result_code = RCODE_FATAL
            raise ProcessExecError(error_str)
        
        if (process.returncode == os.EX_TEMPFAIL):
            # Process terminated with a temporary failure
            self.state = PSTATE_START
            self.exit_code = process.returncode
            self.result_code = RCODE_ERROR
            self.finish = db_clock_time(db_session)
            raise ProcessTempFailError(log_str + " - temporary failure.")
        
        elif (process.returncode):
            # Process termainated with > 0 exit code
            self.state = PSTATE_FAILURE
            self.result_code = RCODE_FATAL
            self.exit_code = process.returncode
            self.finish = db_clock_time(db_session)
            raise ProcessExitError(log_str + " - failed." )
        
        elif (process.returncode < 0):
            # Process terminated by signal -N
            self.state = PSTATE_FAILURE
            self.result_code = RCODE_ERROR
            self.exit_code = None
            self.finish = db_clock_time(db_session)
            raise ProcessSignalError(log_str + " - killed by signal %s." 
                    % process.returncode * -1)
        
        msg = log_str + " - ran successfully."
        self.state = PSTATE_SUCCESS
        self.exit_code = process.returncode
        self.result_code = RCODE_OK
        self.finish = db_clock_time(db_session)

        # This can blow up in a real spectacular fashion!
        # Need to register Events to a list of classes?
        if (self.success_event):
            if (not self.success_event in sql_data['event_type_list']):
                raise ProcessNotAnEventError(pseudo_event=self.success_event)
            elif (self.success_event_kwargs):
                se_kwargs = json.loads(self.success_event_kwargs)
                s_event = eval ("%s(**se_kwargs)" % self.success_event)
            else:
                s_event = eval ("%s()" % self.success_event)
            db_session.add(s_event)

        return (RCODE_OK, msg)

    def _reset(self, event):
        self.state = PSTATE_START
        self.exit_code = None
        self.result_code = None
        self.stdout = None
        self.stderr = None
        self.start = None
        self.finish = None
        return (RCODE_OK, "Process %s(%s) - cleared output."
                % (self.name, self.exec_path))

    _sm_table = {
        PSTATE_START:   {
            ProcessSMExecEvent: _exec,
            },
        # PSTATE_RUN occurs within an event
        # thus empty row here.
        PSTATE_RUN: {},
        PSTATE_FAILURE: {
            ProcessSMResetEvent: _reset
            },
        PSTATE_SUCCESS: {
            ProcessSMResetEvent: _reset
            },
    }

    def __init__(self, exec_path=None, argv=None, stdin=None,
            name=None, success_event=None, success_event_kwargs=None):
        self.state = PSTATE_START
        if (not exec_path and not argv):
            raise ProcessNoArgumentError
        if (exec_path):
            self.exec_path = exec_path
        elif (argv):
            self.exec_path = argv[0]
        else:
            raise ProcessNoArgumentError
        if (name):
            self.name = name
        else:
            self.name = os.path.basename(self.exec_path)
        if (argv):
            self.argv = json.dumps(argv)
        self.stdin = stdin
        if (success_event):
            # This is a mess, but people will pass in all types of stuff,
            # and we need text name of class for DB
            if (type(success_event) is str):
                if (success_event not in sql_data['event_type_list']):
                    raise ProcessNotAnEventError(psuedo_event=success_event)
                self.success_event = success_event
            elif (type(success_event) is type):
                if (not issubclass(success_event, Event)):
                    raise ProcessNotAnEventError(psuedo_event=success_event)
                self.success_event = success_event.__name__
            elif (isinstance(success_event, Event)):
                self.success_event = success_event.__class__.__name__
            else:
                raise ProcessNotAnEventError(psuedo_event=success_event)
        else:
            self.success_event = None
        if (success_event_kwargs):
            self.success_event_kwargs = json.dumps(success_event_kwargs)

def new_process(db_session, commit=False, time=None, delay=None, *args, **kwargs):
    """
    Create a new process to be run at time, or after a delay
    Time is in Unix Epoch, and delay in seconds. If time or delay are
    not specified, it executes now.
    time is a datetime.datetime, delay is datetime.timeinterval
    """
    process_sm = ProcessSM(*args, **kwargs)
    db_session.add(process_sm)
    db_session.flush()
    db_session.refresh(process_sm)
    exec_event = ProcessSMExecEvent(process_sm.id_)
    if (not time):
        time = db_time(db_session)
    exec_event.scheduled = time
    if (delay):
        exec_event.scheduled += delay
    db_session.add(exec_event)
    process_id = process_sm.id_
    if commit:
        db_session.commit()
    else:
        db_session.flush()
    return process_id

def get_process_results(db_session, sm_id):
    """
    Get the results of a process.  Returns sm_object from the database,
    given an id.
    """
    try:
        sm_obj = event.db_session.query(ProcessSM)\
                        .filter("id = '%s'" % sm_id).one()
    except NoResultFound: 
        sm_obj = None
    return sm_obj

def reset_process(db_session, sm_id, commit=False):
    """
    Reset the given process
    """
    sm_obj = get_process_results(db_session, sm_id)
    if (not sm_obj):
        return
    reset_event = ProcessSMResetEvent(sm_obj.id_)
    db_session.add(reset_event)
    if (commit):
        db_session.commit()
    else:
        db.session.flush()

