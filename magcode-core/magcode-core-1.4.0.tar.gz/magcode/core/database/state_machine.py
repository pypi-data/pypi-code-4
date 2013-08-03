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

import threading
import os
import sys
from functools import wraps

from sqlalchemy.orm.exc import NoResultFound

from magcode.core.logging import *
from magcode.core.globals_ import *
from magcode.core.database.event import Event
from magcode.core.database.event import SyncEvent
from magcode.core.database.event import ESTATE_SUCCESS
from magcode.core.database.event import ESTATE_RETRY
from magcode.core.database.event import ESTATE_FAILURE
from magcode.core.database.event import ESTATE_NEW
from magcode.core.database.utility import *


def sync():
    """Decorator - Places self._lock around method"""
    def _sync(func):
        @wraps(func)
        def _syncs(self, *args, **kwargs):
            lock = self.__getattribute__('_lock')
            lock.acquire()
            try:
                return func(self, *args, **kwargs)
            finally:
                lock.release()
        return _syncs
    return _sync


class StateMachineError(Exception):
    """
    Base class for all State Machine Error Exceptions
    """
    def __init__(self, *args):
        if (not len(args)):
            Exception.__init__(self, "Generic State Machine Error")
        else:
            Exception.__init__(self, *args)

        

class StateMachineFatalError(StateMachineError):
    """
    Fatal super class for all fatal State MAchine Exceptions
    """
    def __init__(self, *args):
        if (not len(args)):
            Exception.__init__(self, "Fatal State Machine Error")
        else:
            Exception.__init__(self, *args)


def smregister(class_):
    """
    State machine descedant class decorator function to register class for 
    SQL Alchemy mapping in magcode.core.database.utility.sqlalchemy_setup()
    """
    # Process _table
    if (hasattr(class_, '_table') and class_._table):
        saregister(class_)
    #register events with this SM
    for event in class_._sm_events:
        event._sm_class = class_
    return(class_)


class SMEvent(Event):
    """
    Base State Machine Event.

    Just executes state machine. Does not get mapped into sqlalchemy.
    If you modify this MODIFY SMSyncEvent as well!  Thery are both
    'photocopies' and are seperate just for inheritance reasons.
    """
    # Private parameter to pass in SM event is associated with
    _sm_class = None

    def __init__(self, sm_id, *args, **kwargs):
        """
        Initialise Event
        """
        # Make sm_id a **kwargs to be swallowed by Event.__init__
        # into the JSON parameters
        super().__init__(*args, sm_id=sm_id, **kwargs)

    def process(self):
        """
        Execute an event on the State machine
        """
        sm_obj = self._sm_class.fetch_sm_obj(self)
        if (not sm_obj):
            return RCODE_FATAL

        # Do the state machine thing...
        return_code = sm_obj.execute_state_machine(self)
        # Clean up memory
        del sm_obj
        return return_code

class SMSyncEvent(SyncEvent):
    """
    Base Syncronous State Machine Event.

    Just executes state machine. Does not get mapped into sqlalchemy.
    Photocopy of above SMEvent class, If you modify one MODIFY the OTHER!!
    """
    # Private parameter to pass in SM event is associated with
    _sm_class = None

    def __init__(self, sm_id, *args, **kwargs):
        """
        Initialise Event
        """
        # Make sm_id a **kwargs to be swallowed by Event.__init__
        # into the JSON parameters
        super().__init__(*args, sm_id=sm_id, **kwargs)

    def process(self):
        """
        Execute an event on the State machine
        """
        sm_obj = self._sm_class.fetch_sm_obj(self)
        if (not sm_obj):
            return RCODE_FATAL

        # Do the state machine thing...
        return_code = sm_obj.execute_state_machine(self)
        # Clean up memory
        del sm_obj
        return return_code


class StateMachine(object):
    """
    Base state machine object.

    Contains code that is used required by all state machines.
    """
    # Name of database table for SM
    _table = ''
    # This will be the state machine table
    _sm_table = None
    # List of events that need to have _sm_class set, ie every event
    # list in _sm_table
    _sm_events = []

    @classmethod
    def fetch_sm_obj(class_, event):
        """
        Fetchs a State Machine object given an sm_id parameter
        it an event.

        event   - event instance
        sm_type - state machine class

        returns None or sm_obj instance read in from DB.

        Note: the state machine object must have an 'id' parameter
        """
        sm_id = event.py_parameters.get('sm_id')
        if (not sm_id):
            event.state = ESTATE_FAILURE
            event.py_results['message'] = "No sm_id given"
            log_error("Event %s(%s) failed: No sm_id parameter" 
                        % (event.__class__.__name__, event.id_))
            return None

        try:
            sm_obj = event.db_session.query(class_)\
                            .with_lockmode('update')\
                            .filter("id = '%s'" % sm_id).one()
        except NoResultFound: 
            sm_obj = None

        if (not sm_obj):
            event.state = ESTATE_FAILURE
            event.py_results['message'] = ("SM object id '%s' not found in " 
                "database." % sm_id)
            # We typically delete SMs, still with events in the queue...
            log_debug(
                    "Event %s(%s) failed: no state machine sm_id %s (deleted?)"
                    % (event.__class__.__name__, event.id_, sm_id))
            return None

        return sm_obj

    def execute_state_machine(self, event):
        """
        Execute the state machine for the given event
        """
        event_id = event.id_
        event_class_name = event.__class__.__name__
        if (not self._sm_table):
            msg = ("%s - State machine event table not filled out."
                    % self.__class__.__name__)
            log_critical(msg)
            event.py_results['message'] = msg
            event.state = ESTATE_FAILURE
            return RCODE_FATAL
      
        event.py_results['pre_event_sm_state'] = self.state
        action = self._sm_table[self.state].get(event.__class__)
        if (not action):
            msg = ("Event %s(%s) no change - state '%s'" 
                    % (event_class_name, event_id, self.state))
            log_debug(msg)
            event.py_results['message'] = msg
            event.state = ESTATE_SUCCESS
            return RCODE_NOCHANGE

        try:
            (return_code, msg) = action(self, event)
        except StateMachineFatalError as exc:
            msg = ("Event %s(%s) failed - %s" 
                    % (event_class_name, event_id, str_exc(exc)))
            log_error(msg)
            event.py_results['message'] = msg
            event.py_results['sm_exception_type'] = exc.__class__.__name__
            event.py_results['sm_exception_args'] = exc.args
            event.state = ESTATE_FAILURE
            return RCODE_FATAL

        except StateMachineError as exc:
            msg = ("Event %s(%s) errored - %s"
                    % (event_class_name, event_id, str_exc(exc)))
            log_info(msg)
            event.py_results['message'] = msg
            event.py_results['sm_exception_type'] = exc.__class__.__name__
            event.py_results['sm_exception_args'] = exc.args
            event.state = ESTATE_RETRY
            return RCODE_ERROR

        msg = ("Event %s(%s) processed - %s."
                    % (event_class_name, event_id, msg))
        log_info(msg)
        event.state = ESTATE_SUCCESS
        event.py_results['message'] = msg
        event.py_results['post_event_sm_state'] = self.state
        return return_code

    

