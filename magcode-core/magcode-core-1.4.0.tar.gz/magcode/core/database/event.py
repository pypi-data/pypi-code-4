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
"""
Event queue module  


Implents a python event queue against a SQL database table, using SQLALchemy.
"""

import sys
import os
import time
import threading
import json
import signal
from queue import Queue
from queue import Empty
from copy import copy
from traceback import format_exc

from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import make_transient
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from magcode.core import *
from magcode.core.utility import send_signal
from magcode.core.utility import get_numeric_setting
from magcode.core.database import *


# some state static constant
ESTATE_NEW = 'NEW'
ESTATE_RETRY = 'RETRY'
ESTATE_SUCCESS = 'SUCCESS'
ESTATE_FAILURE = 'FAILURE'
event_process_states = frozenset((ESTATE_NEW,ESTATE_RETRY))
event_processed_states = frozenset((ESTATE_SUCCESS, ESTATE_FAILURE))
event_states = event_process_states.union(event_processed_states)

# Lists we use in global sql_data dict
sql_data['event_subclasses'] = []
sql_data['event_type_list'] = []


def eventregister(class_):
    """
    Event descedant class decorator function to register class for SQL
    Alchemy mapping in init_event_class() below, called in 
    magcode.core.database.utility.setup_sqlalchemy()
    """
    sql_data['event_subclasses'].append(class_)
    sql_data['event_type_list'].append(class_.__name__)
    sql_data['events'][class_.__name__] = class_
    return(class_)

def synceventregister(class_):
    """
    Event descedant class decorator function to register class for SQL
    Alchemy mapping in init_event_class() below, called in 
    magcode.core.database.utility.setup_sqlalchemy()
    This one is for SyncEvent classes.
    """
    sql_data['event_subclasses'].append(class_)
    sql_data['events'][class_.__name__] = class_
    return(class_)

class EventAlreadyProcessing(Exception):
    """
    Event already processing
    """

class QueueReset(Exception):
    """
    Queue reset as DB connection loss detected
    """

class _EQueue(Queue):
    """
    Internal queue class with dictionary of events being processed

    This replaces methods on Queue so that processing array is only altered
    when mutex held to prevent races.
    """
    def __init__(self):
        """
        Special init to set queue size
        """
        self.processing = {}
        self.queue_reset = False
        super().__init__(
                maxsize=get_numeric_setting('event_queue_maxsize', int))

    def _put(self, item):
        """
        Put an event on the Queue, and record it as being processed.
        """
        if self.queue_reset:
            raise QueueReset("Event queue reset")
        if self.processing.get(item.id_):
            raise EventAlreadyProcessing("Event '%s' is already processing."
                         % item.id_)
        self.processing[item.id_] = True
        super()._put(item)

    def start_queue_reset(self):
        self.queue_reset = True
        while True:
            try:
                event = super().get_nowait()
                super().task_done()
            except Empty: 
                break

    def is_queue_reseting(self):
        return self.queue_reset

    def clean_up(self):
        """
        Cleans up after queue emptied.
        """
        self.join()
        self.queue_reset = False
        self.processing = {}

    def task_done(self, event_id):
        """
        task done
        """
        if event_id:
            self.processing.pop(event_id)
        super().task_done()



class EventProcess(object):
    """
    Container class for event processing methods for an event.
    These are both used by queued events and synchronous events.
    """
    def _failure_results(self, db_session, reason, 
            function="event_process_wrapper" ):
        self.state = ESTATE_FAILURE
        self.result_code = RCODE_FATAL
        self.processed = db_time(db_session)
        self._clean_attrs()
        log_error("%s() - FAILING event id: '%s', "
                   "event_type: '%s', state: '%s', scheduled '%s',"
                   " created: '%s', processed: '%s' with result "
                   "'%s - %s, %s' - %s"  
                   % (function, self.id_, self.event_type, self.state,
                                self.scheduled, self.created,
                                self.processed, 
                                self.result_code,
                                result_code_dict[self.result_code],
                                result_code_lstr_dict[self.result_code],
                                reason))
        return

    def _clean_attrs(self):
        """
        Clean off attrs we don't want so event can go to DB without
        giving SQLAlchemy a headache.
        """
        if hasattr(self, 'db_session'):
            delattr(self, 'db_session')
        if hasattr(self, 'py_results'):
            delattr(self, 'py_results')
        if hasattr(self, 'py_parameters'):
            delattr(self, 'py_parameters')
        
    def _process_wrapper(self, db_session):
        """
        Setup and teardown method that wraps the 
        events process() method.

        Sets up environment, sets fields once process() finished
        and does other janitorial work.  In here rather that in 
        Event class to make Event code tidy.
        """

        # Safe guard to see if we are already processed
        if (self.state not in event_process_states):
            return

        # Set up dyanmic data for this event
        self.db_session = db_session
        # Set up results as an empty dictionary - easy for events to insert
        # results, message etc.
        self.py_results = {}

        if (self.parameters):
            # JSON decode parameters
            try:
                self.py_parameters = json.loads(self.parameters)
            except Exception:
                self._failure_results(db_session,
                        "could not decode JSON parameters.")
                return
        else:
            py_parameters = None

        # Call event state machine
        log_debug("_process_wrapper() - processing event id: '%s', "
                       "event_type: '%s', state: '%s', scheduled '%s',"
                       " created: '%s'" 
                       % (self.id_, self.event_type, self.state,
                                    self.scheduled, self.created))
        
        result_code = self.process()
        self.result_code = result_code

        # JSON encode results
        if (self.py_results):
            try:
                self.results = json.dumps(self.py_results)
            except Exception:
                self._failure_results(db_session,
                            "could not encode JSON results.")
                return

        # Check returned result code is sensible
        if (result_code not in result_codes):
            self._failure_results(db_session, 
                        "result code not recognised.")
            return
        
        # Check returned state is sensible
        if (self.state not in event_states):
            self._failure_results(db_session,
                            "new event state not recognised.")
            return
        
        # get rid of dynamic attributes we created at start of this.
        self._clean_attrs()
        
        # Only set processed_time if we are finished with this event
        if self.state in event_processed_states:
            self.processed = db_time(db_session)
        
        log_debug("_process_wrapper() - processed event id: '%s', "
                       "event_type: '%s', state: '%s', scheduled '%s',"
                       " created: '%s', processed: '%s' with result "  
                       "'%s - %s, %s'"  
                       % (self.id_, self.event_type, self.state,
                                    self.scheduled, self.created,
                                    self.processed, 
                                    self.result_code,
                                    result_code_dict[self.result_code],
                                    result_code_lstr_dict[self.result_code]))
        return

class Event(EventProcess):
    """
    Ancestor Event Class
    """

    @classmethod
    def sa_map_subclass(class_):
        sql_data['mappers'][class_] = mapper(class_,
                    inherits=sql_data['mappers'][Event], 
                    polymorphic_identity=class_.__name__)

    def __init__(self, scheduled=None, **kwargs_parameters):
        """
        Initialise the event.

        kwargs_parameters is passed to the parameters column of the database
        as a JSON encoded dict.  This is the easiest form to encode needed
        parameters, and decreases the need to override the __init__ method in
        child classes
        """
        self.state  = ESTATE_NEW
        self.scheduled = scheduled
        fkey_list = settings['event_queue_fkey_columns'].split()
        for attr in fkey_list:
            value = kwargs_parameters.pop(attr, None)
            if value == None:
                continue
            exec ("self.%s = %s" % (attr, value))
        if kwargs_parameters:
            self.parameters = json.dumps(kwargs_parameters)
        else:
            self.parameters = None

    def process(self):
        """
        Put event code here  - stub method

        attributes set up by EventQueue class:
          self.py_parameters holds decoded JSON parameters for event
          self.py_results is NONE, and you can assemble a data structure
                to be JSON encoded into the sm_event_queue results column.
          return code is one from the RCODE_s above
          self.state is the event state - adjust once process to one of the
                ESTATE_s above.
          self.customer_id - DMS customer_id from dms database.
          self.zone_id - DNS Zone zone_id from dms database.
          self.role_id - DMS role_id from dms database.
          created, scheduled,processed timestamps are attributes as well but
                DON'T TOUCH them, or DEPEND on the processed timestamp! 
        """
        log_info("Hello Good Event New World!")
        self.state = ESTATE_SUCCESS
        return RCODE_OK
    
    def set_scheduled(self, time=None, delay=None, db_session=None):
        """
        Helper function to manipulate scheduled field

        time - datetime.datetime object (Python Standard Library)
        delay - datetime.interval object (Python Standard Library)
        """
        if (not time):
            if not db_session:
                db_session = sql_data['scoped_session_class']()
            time = db_time(db_session)
        self.scheduled = time
        if (delay):
            self.scheduled += delay
        
    def get_parameters(self):
        """
        Helper function to JSON decode parameters for event
        """
        if (self.parameters):
            return json.loads(self.parameters)
        else:
            return None

    def get_results(self):
        """
        Helper function to JSON decode parameters for event
        """
        if (self.results):
            return json.loads(self.results)
        else:
            return None

    def to_engine_brief(self, time_format=None):
        """
        Supply data output in brief as a dict.  
        Just id, event_type, scheduled, processed, created, result_code.
        """
        if not time_format:
            created = self.created.isoformat(sep=' ') \
                            if self.created else None
            scheduled = self.scheduled.isoformat(sep=' ') \
                            if self.scheduled else None
            processed = self.processed.isoformat(sep=' ') \
                            if self.processed else None
        else:
            created = self.created.strftime(time_format) \
                            if self.created else None
            scheduled = self.scheduled.strftime(time_format) \
                            if self.scheduled else None
            processed = self.processed.strftime(time_format) \
                            if self.processed else None

        return {'event_id': self.id_, 'event_type': self.event_type,
                'state': self.state, 'zone_id': self.zone_id,
                'parameters': self.get_parameters(),
                'result_code': self.result_code,
                'created': created, 'scheduled': scheduled, 
                'processed': processed,}

    def to_engine(self, time_format=None):
        """
        Return all fields as a dict
        """
        if not time_format:
            created = self.created.isoformat(sep=' ') \
                            if self.created else None
            scheduled = self.scheduled.isoformat(sep=' ') \
                            if self.scheduled else None
            processed = self.processed.isoformat(sep=' ') \
                            if self.processed else None
        else:
            created = self.created.strftime(time_format) \
                            if self.created else None
            scheduled = self.scheduled.strftime(time_format) \
                            if self.scheduled else None
            processed = self.processed.strftime(time_format) \
                            if self.processed else None

        return {'event_id': self.id_, 'event_type': self.event_type,
                'state': self.state, 'zone_id': self.zone_id,
                'parameters': self.get_parameters(),
                'results': self.get_results(),
                'result_code': self.result_code,
                'created': created, 'scheduled': scheduled, 
                'processed': processed,}

class SyncEvent(Event):
    """
    Synchronous event that executes upon creation.

    Designed to be used in code that needs immediate event execution.
    Event created in event_queue table for the record and to obtain an
    event ID, but it is never executed on the queue as is it is not
    in sql_data['event_type_list']
    """
    def __init__(self, execute=False, *args, **kwargs):
        """
        Initialise synchronous event, and execute it if asked to.
        A dictionary of parameters can be passed in.
        If executing from here, use event.get_results to return
        results dictiontionary
        """
        super().__init__(*args, **kwargs)
        if execute:
            self.execute()

    def execute(self):
        """
        Execute the synchronous event. Returns results as a JSON dictionary.
        """
        # Set up environment
        db_session = sql_data['scoped_session_class']()
        db_session.add(self)
        # Execute
        self._process_wrapper(db_session)
        db_session.commit()
        # Return results
        results = self.get_results()
        results['result_code'] = self.result_code
        results['state'] = self.state
        return results

class QueueDraining(Exception):
    """
    Lost DB connection, drain queue with out processing so
    that reader loop errors on next DB query
    """

class EventQueue(object):
    """
    Event Queue object

    Operates on database table sm_event_queue.  
    
    The job of this class is to present a simple event class API/ABI to
    the application programmer.  SQLAlchemy gets its fingers into
    each class pie to hide the database <=> object convolution/deconvolution,
    and this class builds on top of that stack to create runable events.
    """
    def __init__(self):
        """
        Sets up queue and Threads
        """
        # This is a FIFO queue
        self._queue = _EQueue()
        self._threads = []
        self._event_count = 0
        self.event_queue_session_transactions \
                = get_numeric_setting('event_queue_session_transactions', int)
        self._thread_top_up()
        # Pause to let threads get established.
        time.sleep(3)
   
    def queue_empty(self):
        """
        check if queue is empty.  Use during sleep to help determine when to 
        garbage collect etc.
        """
        return self._queue.empty()

    def event_processor(self):
        """
        Worker thread that processes events on the queue
        """
        log_debug ("event_processor() - starting thread.")
        Session = sql_data['scoped_session_class']
        db_session = Session()
        event_count = 0

        # Loop and wait on queue
        while True:
            # Keep Session cycling to release RAM
            if (self.event_queue_session_transactions and 
                    event_count > self.event_queue_session_transactions):
                event_count = 0
                db_session.close()
                sql_data['scoped_session_class'].remove()
                db_session = Session()
            event_count += 1

            timeout = settings['event_queue_thread_timeout']
            try:
                # Balanced with finally: task-done() below.
                event = self._queue.get(timeout=timeout)
            except Empty:
                log_debug("event_processor() - exiting thread because "
                        "of Queue.get() time out %ss." % timeout) 
                Session.remove()
                return
            
            info_str = None
            error_str = None
            event_id = None
            
            try:
                if self._queue.is_queue_reseting():
                    raise QueueDraining()
                # The following replaces event with in an session event
                event = db_session.merge(event)
                event_id = event.id_
                # State machine DB locks happen in below call...
                event._process_wrapper(db_session)
                db_session.commit()
            
            except QueueDraining:
                # Finally will mark task_done
                continue
            except Exception as exc:
                # Handle error messages
                if isinstance(exc, DBAPIError):
                    if is_db_connection_exception(exc.orig):
                        info_str = ("event_processor() draining queue and exiting - PostgresQL database connection probably closed.\n" 
                                    "%s" % str_exc(exc))
                        # DB gone, drain queue
                        self._queue.start_queue_reset()
                        break
                    else:
                        error_str = ("event_processor() exiting - unexpected error\n"
                                     "%s"  % format_exc(chain=True))
                elif isinstance(exc, SQLAlchemyError):
                    error_str = ("event_processor() exiting"
                            " - unexpected error\n"
                             "%s"  % format_exc(chain=False))
                
                # Back completely out - following raise does not clear DB
                # locks!
                db_session.rollback()
                #
                # If DB stuff is corrupted, we have more to worry about
                # than this wild exception, so commit this event so it
                # is not processed again.  Record Exception information
                # along with it for fixing it up.
                #
                # The following works as event reverted to non-merged
                # due to exception processing
                event = db_session.merge(event)
                event_id = event.id_
                # capture traceback
                py_results = {}
                py_results['execption_info'] = format_exc()
                py_results['message'] = "Failing Event ID: %s due to exception.  See 'exception_info' result." % event.id_
                event.results = json.dumps(py_results)
                event._failure_results(db_session, "exception occured.",
                        function="event_processor")
                db_session.commit()

                # Terminate thread early - DB session corrupt?
                # Finally remove thread db_session
                Session.remove()
                raise

            finally:
                # Balanced with get above.  If we call too often we will
                # get an error.
                self._queue.task_done(event_id)

                # Deallocate memory
                del event
                # Process errors - avoid chained exception traces
                if (info_str):
                    log_info(info_str)
                if (error_str):
                    log_error(error_str)

        # Finally remove thread db_session
        Session.remove()

    def _thread_start(self):
        """
        Start a thread
        """
        thread = threading.Thread(target=self.event_processor)
        thread.daemon = True
        thread.start()
        self._threads.append(thread)

    def _thread_top_up(self):
        if (debug()):
            self.event_queue_threads = 1
        else:
            self.event_queue_threads = get_numeric_setting(
                                                    'event_queue_threads', int)
        # Check what threads are active, and remove those that are not
        self._threads = [thread for thread in self._threads 
                                    if thread.is_alive()]
        while (len(self._threads) < self.event_queue_threads):
            log_debug("_thread_top_up() - topping up threads")
            self._thread_start()

    def process_queue(self):
        """
        Read events from database, and place on queue, until all processed.
        """
        # top up processor threads if any have died...
        self._thread_top_up()
        # Read from sm_event_queue
        db_session = sql_data['scoped_session_class']()
        # Use flags to unchain exception handling.
        info_str = None
        error_str = None
        try:
            # Query ze events...
            for event in  db_session.query(Event)\
                    .filter(Event.processed == None)\
                    .filter(Event.event_type.in_(sql_data['event_type_list']))\
                    .filter(Event.state.in_(event_states))\
                    .filter(Event.scheduled <= func.statement_timestamp())\
                    .order_by(Event.scheduled.asc())\
                    .limit(settings['event_queue_maxsize']):
                try:
                    self._queue.put(event)
                    self._event_count += 1
                except EventAlreadyProcessing:
                    continue
                except QueueReset:
                    log_info("process_queue() - queue reset detected, cleaning up and returning to main loop.")
                    db_session.close()
                    sql_data['scoped_session_class'].remove()
                    # go back to main_process() after queue is emptied
                    self._queue.clean_up()
                    return
                log_debug("process_queue() - queueing event id:'%s', "
                          "event_type: '%s', state: '%s', scheduled '%s',"
                          " created: '%s'" 
                                % (event.id_, event.event_type, event.state,
                                    event.scheduled, event.created)) 

            db_session.commit()
            
            # Joining queue not needed as events cannot be put if they are
            # processing
        
        except DBAPIError as exc:
            if is_db_connection_exception(exc.orig):
                info_str = ("process_queue() exiting - PostgresQL database connection probably closed.\n" 
                            "         %s" 
                            % str_exc(exc))
            else:
                error_str = ("process_queue() exiting - unexpected error\n"
                             "%s"  % format_exc(chain=True))

            # close off session
            db_session.close()
        except SQLAlchemyError as exc:  
            error_str = ("process_queue() exiting - unexpected error\n"
                         "%s"  % format_exc(chain=False))
            # close off session
            db_session.rollback()
        # Unchain exception handling - Print any log messages
        if (info_str):
            log_info(info_str)
        if (error_str):
            log_error(error_str)

        # Every so often, close session
        if (self.event_queue_session_transactions 
                and self._event_count > self.event_queue_session_transactions):
            self._event_count = 0
            db_session.close()
            sql_data['scoped_session_class'].remove()
        # go back to main_process()
        return

def queue_event(event, db_session=None, commit=False, time=None, delay=None,
                coalesce_period=None, signal_queue_daemon=False):
    """
    Given a newly created event instance, queue it for processing
    """
    if not db_session:
        db_session = sql_data['scoped_session_class']()
    # Given a db_session, queue a created event
    event.set_scheduled(time, delay, db_session=db_session)
    events_to_coalesce = []
    if coalesce_period:
        events_iterator = db_session.query(Event)\
                .filter(Event.processed == None)\
                .filter(Event.event_type == event.event_type)\
                .filter(Event.scheduled <= event.scheduled)\
                .filter(Event.scheduled > (event.scheduled - coalesce_period))\
                .order_by(Event.scheduled)
        events_to_coalesce = [e for e in events_iterator 
                                if e.get_parameters() == event.get_parameters()]
    if events_to_coalesce:
        # first event in list is earliest equivalent
        earlist_event = events_to_coalesce.pop(0)
        earlist_event.scheduled = event.scheduled
        for e in events_to_coalesce:
            db_session.delete(e)
        event = earlist_event
    else:
        db_session.add(event)
    if commit:
        db_session.commit()
    else:
        db_session.flush()
    if signal_queue_daemon:
        send_signal(settings['event_queue_pid_file'], signal.SIGUSR1)
    return event
 
def create_event(event_type, db_session=None, commit=False,
                    time=None, delay=None, coalesce_period=None,
                    signal_queue_daemon=False,
                    *args, **kwargs):
    """
    Create and then queue an event for processing. *args and **kwargs
    are passed into the event constructor
    """
    event = event_type(*args, **kwargs)
    event = queue_event(event, db_session, commit, time, delay,
                coalesce_period, signal_queue_daemon)
    return event

def cancel_event(event_id, db_session=None, commit=False, log_to_info=False):
    """
    Cancel an unprocessed event given an event_id
    """
    if not db_session:
        db_session = sql_data['scoped_session_class']()

    # get event
    event = db_session.query(Event)\
                    .filter(Event.id_ == event_id).one()
    if event.processed:
        return
    
    # Cancel Event
    time = db_time(db_session)
    event.state = ESTATE_FAILURE
    event.processed = time
    msg = ("Event %s(%s) canceled." 
            % (event.__class__.__name__, event.id_))
    if log_to_info:
        log_info(msg)
    else:
        log_debug(msg)
    results = {'message': msg}
    event.results = json.dumps(results) 

    # put it out to database
    if commit:
        db_session.commit()
    else:
        db_session.flush()


def reschedule_event(event_id, db_session=None, commit=False, time=None,
        delay=None, signal_queue_daemon=False):
    """
    Coalesce an event with one already existing in the event queue.
    Event is coalesced with one within coalesce_time seconds of its 
    scheduled time.  Event to be claesced has to be exactly the same 
    apart from id - ie same type State has to be NEW or RETRY, and same
    params 
    """
    if not db_session:
        db_session = sql_data['scoped_session_class']()

    # get event
    try:
        event = db_session.query(Event)\
                    .filter(Event.id_ == event_id).one()
    except NoResultFound:
        return None
    if event.processed:
        return None

    # reschedule it
    event.set_scheduled(time, delay, db_session=db_session)
    
    # put it out to database
    if commit:
        db_session.commit()
    else:
        db_session.flush()
    if signal_queue_daemon:
        send_signal(settings['event_queue_pid_file'], signal.SIGUSR1)
    return event

def find_events(event_type, db_session=None, 
                    from_time=None, before_time=None, period=None,
                    processed=False, **kwargs_fkey):
    """
    Search for events.

    This function works on time boundaries exactly as per time around midnight
    ie 0 seconds on the hour is within the hour commencing.
    """
    if not db_session:
        db_session = sql_data['scoped_session_class']()

    # Get list of events
    events_query = db_session.query(Event)\
            .filter(Event.event_type == event_type.__name__)\
            .order_by(Event.scheduled)
    fkey_list = settings['event_queue_fkey_columns'].split()
    for attr in fkey_list:
        value = kwargs_fkey.pop(attr, None)
        if value == None:
            continue
        events_query = events_query.filter(getattr(Event, attr) == value) 
    # processed is boolean - else condition needed
    if processed:
        events_query = events_query.filter(Event.processed != None)
    else:
        events_query = events_query.filter(Event.processed == None)
    if from_time:
        events_query = events_query.filter(Event.scheduled >= from_time)
    if before_time:
        events_query = events_query.filter(Event.scheduled < before_time)
    if period:
        if from_time and not before_time:
            before_time = from_time + period
            events_query = events_query.filter(Event.scheduled < before_time)
        if before_time and not from_time:
            from_time = before_time - period
            events_query = events_query.filter(Event.scheduled >= from_time)
        if not before_time and not from_time:
            before_time = db_time(db_session)
            from_time = before_time - period
            events_query = events_query.filter(Event.scheduled >= from_time)
    return events_query.all()

# SQL Alchemy hooks
def init_event_table():
    table = Table('sm_event_queue', sql_data['metadata'],
                        autoload=True, 
                        autoload_with=sql_data['db_engine'])
    sql_data['tables'][Event] = table

def init_event_mappers():
    table = sql_data['tables'][Event]
    sql_data['mappers'][Event] = mapper(Event, table,
            polymorphic_on=table.c.event_type, 
            polymorphic_identity=Event.__name__,
            properties=mapper_properties(table, Event))
    sql_data['event_type_list'].append(Event.__name__)
    # Map all the event subclasses
    for class_ in sql_data['event_subclasses']:
        class_.sa_map_subclass()

sql_data['init_list'].append({'table': init_event_table, 'mapper': init_event_mappers})

