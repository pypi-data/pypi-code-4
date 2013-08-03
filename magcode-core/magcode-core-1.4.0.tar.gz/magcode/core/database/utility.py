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
Set up core database functionality.  Currently just the Event Queueing system
"""

import os
import sys
import socket
import copy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import extract
from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper

from magcode.core.globals_ import settings
from magcode.core.globals_ import debug
from magcode.core.globals_ import debug_verbose
from magcode.core.globals_ import startup_log_func
from magcode.core.logging import *


# Result codes
RCODE_FATAL = 550
_RCODE_FATAL_NAME = 'FATAL'
RCODE_FATAL_STR = 'Fatal Error'
RCODE_FATAL_LSTR = 'Fatal Error - not recoverable'
RCODE_RESET = 460
_RCODE_RESET_NAME = 'RESET'
RCODE_RESET_STR = 'Resetable Error'
RCODE_RESET_LSTR = 'Resetable Error - SM reset required'
RCODE_ERROR = 450
_RCODE_ERROR_NAME = 'ERROR'
RCODE_ERROR_STR = 'Recoverable Error'
RCODE_ERROR_LSTR = 'Recoverable Error - temporary failure'
RCODE_NOCHANGE = 220
_RCODE_NOCHANGE_NAME = 'NOCHANGE'
RCODE_NOCHANGE_STR = 'No Change'
RCODE_NOCHANGE_LSTR = 'No Change - no change to data'
RCODE_NOEFFECT = 210
_RCODE_NOEFFECT_NAME = 'NOEFFECT'
RCODE_NOEFFECT_STR = 'No Effect'
RCODE_NOEFFECT_LSTR = 'No Effect - operation happened but no change'
RCODE_OK = 200
_RCODE_OK_NAME = 'OK'
RCODE_OK_STR = 'OK'
RCODE_OK_LSTR = 'OK - success, data changed or new data'
result_error_codes = (RCODE_FATAL, RCODE_RESET, RCODE_ERROR)
result_success_codes = (RCODE_NOCHANGE, RCODE_NOEFFECT, RCODE_OK)
result_codes = result_error_codes + result_success_codes
result_code_names = (_RCODE_FATAL_NAME, _RCODE_RESET_NAME, _RCODE_ERROR_NAME,
                    _RCODE_NOCHANGE_NAME, _RCODE_NOEFFECT_NAME, _RCODE_OK_NAME)
result_code_strs = (RCODE_FATAL_STR, RCODE_RESET_STR, RCODE_ERROR_STR, 
                    RCODE_NOCHANGE_STR, RCODE_NOEFFECT_STR, RCODE_OK_STR)
result_code_lstrs = (RCODE_FATAL_LSTR, RCODE_RESET_LSTR, RCODE_ERROR_LSTR,
                        RCODE_NOCHANGE_LSTR, RCODE_NOEFFECT_LSTR,
                        RCODE_OK_LSTR)
result_code_dict =  dict(zip(result_codes, result_code_names))
result_code_str_dict = dict(zip(result_codes, result_code_strs))
result_code_lstr_dict = dict(zip(result_codes, result_code_lstrs))


# initialise settings dict so that Process.read_config() can tell that these
# are valid
settings['db_user'] = ''
settings['db_password'] = ''
settings['db_host'] = ''
settings['db_port'] = ''
settings['db_name'] = ''
settings['db_driver'] = 'psycopg2'
settings['db_type'] = ''
settings['db2_user'] = ''
settings['db2_password'] = ''
settings['db2_host'] = ''
settings['db2_port'] = ''
settings['db2_name'] = ''
settings['db2_driver'] = 'psycopg2'
settings['db2_type'] = ''
settings['db3_user'] = ''
settings['db3_password'] = ''
settings['db3_host'] = ''
settings['db3_port'] = ''
settings['db3_name'] = ''
settings['db3_driver'] = 'psycopg2'
settings['db3_type'] = ''
settings['db4_user'] = ''
settings['db4_password'] = ''
settings['db4_host'] = ''
settings['db4_port'] = ''
settings['db4_name'] = ''
settings['db4_driver'] = 'psycopg2'
settings['db4_type'] = ''

# Initialise data section
sql_data = {}
sql_data['connections'] = {}
sql_data['db_engine'] = None
sql_data['scoped_session_class'] = None
sql_data['db_session'] = None
sql_data['simple_classes'] = []
sql_data['init_list'] = []
sql_data['mappers'] = {}
sql_data['tables'] = {}
sql_data['metadata'] = None
sql_data['types'] = {}
sql_types = sql_data['types']
sql_data['events'] = {}
sql_events = sql_data['events']

# SQL alchemy/type registration functions and decorators

def typeregister(class_):
    sql_data['types'][class_.__name__] = class_
    return class_

def saregister(class_):
    db_name = class_._db_name if hasattr(class_, '_db_name') else None
    settings_db_name_key = class_._settings_db_name_key \
            if hasattr(class_, '_settings_db_name_key') else None
    reg_dict = {'class_': class_, 'table': class_._table, 
            'db_name': db_name, 'settings_db_name_key': settings_db_name_key}
    sql_data['simple_classes'].append(reg_dict)
    # also register in the types register...
    typeregister(class_)
    return class_

# Python Reserved Words
_reserved_words_to_twist = ('False', 'class', 'finally', 'is', 'return',
'None', 'continue', 'for', 'lambda', 'try', 'True', 'def', 'from', 'nonlocal',
'while', 'and', 'del', 'global', 'not', 'with', 'as', 'elif', 'if', 'or',
'yield', 'assert', 'else', 'import', 'pass', 'break', 'except', 'in', 'raise',)
# things in our code that look ugly...
_reserved_words_to_twist += ('type', 'id',)

def mapper_properties(table, class_):
    """
    Utility function to add '_' to DB column names that are reserved words
    """
    properties = {}
    if hasattr(class_, '_mapper_properties'):
        more_properties = class_._mapper_properties()
        properties.update(more_properties)
    # Work around reserved words This adds '_' to the attribute in python
    for rsrvd_word in _reserved_words_to_twist:
        if (rsrvd_word in table.c.keys()):
            properties[rsrvd_word +'_'] = table.c.get(rsrvd_word)

    return properties

def _sa_table_simple_class(class_, table, 
        db_name=None, settings_db_name_key=None):
    """
    Map a simple SQL row table
    """
    if db_name:
        db_engine = sql_data['connections'][db_name]['engine']
    elif settings_db_name_key:
        db_name = settings[settings_db_name_key]
        db_engine = sql_data['connections'][db_name]['engine']
    else:
        db_engine = sql_data['db_engine']
    table = Table(table, sql_data['metadata'],
                  autoload=True, 
                  autoload_with=db_engine)
    sql_data['tables'][class_] = table

def _sa_map_simple_class(class_, table,
        db_name=None, settings_db_name_key=None):
    """
    Map a simple SQL row table
    """
    tbl = sql_data['tables'][class_]
    sql_data['mappers'][class_] = mapper(class_, sql_data['tables'][class_], 
                            properties=mapper_properties(tbl, class_))

    # Global vars to map DB driver specific exceptions
_db_conn_exc_list = []
_db_type_dict = {'oursql': 'mysql', 'psycopg2': 'postgresql',
        'postgresql': 'postgresql'}

def is_db_connection_exception(exc):
    """
    Call back function to handle DB specific exceptions
    due to database shutdown or sudden termination.
    """
    if type(exc) in _db_conn_exc_list:
        return True
    return False


def _create_engine(db_type=None, db_driver=None, db_host=None, 
        db_port=None, db_name=None, db_user=None, db_password=None, **kwargs):
    
    # Set up some sensible defaults
    
    if not db_type:
        db_type = _db_type_dict.get(db_driver)
    if db_type == 'postgresql':
        db_port = 5432 if db_port == None else db_port
    elif db_type == 'mysql':
        db_port = 3306 if db_port == None else db_port
        db_host = 'localhost' if not db_host else db_host
    
    # Import DB driver sepecific Exceptions needed for EventQueue
    global _db_conn_exc_list

    def add_conn_exc(exc):
        if exc not in _db_conn_exc_list:
            _db_conn_exc_list.append(exc)

    if ( db_driver == 'pypostgresql'):
        import postgresql
        add_conn_exc(postgresql.exceptions.AdminShutdownError), 
        add_conn_exc(postgresql.exceptions.ConnectionFailureError)
        add_conn_exc(postgresql.exceptions.Error)
    elif (db_driver == 'psycopg2'):
        import psycopg2
        add_conn_exc(psycopg2.OperationalError)
        add_conn_exc(psycopg2.DatabaseError)
        add_conn_exc(psycopg2.InterfaceError)
    elif (db_driver == 'oursql'):
        import oursql
        add_conn_exc(oursql.OperationalError)
        add_conn_exc(oursql.DatabaseError)
        add_conn_exc(oursql.InterfaceError)
    else:
        error_str = "setup_sqlalchemy() - no 'db_driver' set, use 'psycopg2' "\
                    "or 'py-postgresql'."
        startup_log_func(error_str)
        raise RuntimeError(error_str)

    # Create connection string
    if (db_type == 'postgresql' and db_port == ''):
        # attempt to use UNIX socket...
        connect_string = ('postgresql+%(db_driver)://%(db_user)s:%(db_password)s@/%(db_name)s')
    else:
        connect_string = ('%(db_type)s+%(db_driver)s://%(db_user)s:%(db_password)s@%(db_host)s:%(db_port)s/%(db_name)s')
    connect_string = connect_string % {'db_type': db_type, 
            'db_driver': db_driver, 'db_user': db_user,
            'db_password': db_password, 'db_host': db_host,
            'db_port': db_port, 'db_name': db_name}
    if debug_verbose():
        log_debug("setup_sqlalchemy() - connect_string: %s" % connect_string)
    # Create engine
    log_info("setup_sqlalchemy() - using db_driver '%s'." % db_driver)
    engine = create_engine(connect_string)
    try:
        # Connect and test conect information 
        # otherwise get XXXX Exception traces!
        connection = engine.connect()
        error_str = None
    except DBAPIError as exc:
        error_str = str(exc)
        startup_log_func("setup_sqlalchemy() - %s" % error_str)
        raise exc
    # scoped_session() makes class Session thread local
    Session = scoped_session(sessionmaker(bind=engine))
    return(engine, Session)

def _add_connection(db_name, db_engine, Session):
    """
    Add an SA DB connection to the sql_data connections dictionary
    """
    if db_name in sql_data['connections'].keys():
        # Reasonably protected by above connect attempt - a traceback here is OK
        msg =  ("setup_sqlalchemy() - DB '%s' already exists in connections array."
                % db_name)
        startup_log_func(msg)
        raise KeyError(msg)
    sql_data['connections'][db_name] = {}
    sql_data['connections'][db_name]['session_class'] = Session
    sql_data['connections'][db_name]['engine'] = db_engine

def core_setup_sqlalchemy():
    """
    Connects to PostgreSQL, and sets up table mappings.  Can only be called
    once.  This one is made to be called from wsgi, and by wrapper below.
    """
    # Set up SQL alchemy debug
    if debug_extreme():
        logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)    
    elif debug_verbose():
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # Create DB Connections
    db_engine, Session = _create_engine(db_driver=settings['db_driver'],
            db_host=settings['db_host'], 
            db_name=settings['db_name'],  
            db_user=settings['db_user'],
            db_password=settings['db_password'])
    # Legacy sql_data entries
    sql_data['db_engine'] = db_engine
    sql_data['scoped_session_class'] = Session
    _add_connection(settings['db_name'], db_engine, Session)
    if settings['db2_name']:
        db_engine, Session = _create_engine(db_driver=settings['db2_driver'],
                db_host=settings['db2_host'], 
                db_name=settings['db2_name'],  
                db_user=settings['db2_user'],
                db_password=settings['db2_password'])
        _add_connection(settings['db2_name'], db_engine, Session)
    if settings['db3_name']:
        db_engine, Session = _create_engine(db_driver=settings['db3_driver'],
                db_host=settings['db3_host'], 
                db_name=settings['db3_name'],  
                db_user=settings['db3_user'],
                db_password=settings['db3_password'])
        _add_connection(settings['db3_name'], db_engine, Session)
    if settings['db4_name']:
        db_engine, Session = _create_engine(db_driver=settings['db4_driver'],
                db_host=settings['db4_host'], 
                db_name=settings['db4_name'],  
                db_user=settings['db4_user'],
                db_password=settings['db4_password'])
        _add_connection(settings['db4_name'], db_engine, Session)
    
    
    # Map tables and kick SQL Alchemy into gear!
    # Set up metadata
    sql_data['metadata'] = MetaData()

    try:
        # First of all, load table definitions
        # simple SQL row class tables
        for simple_class in sql_data['simple_classes']:
            _sa_table_simple_class(**simple_class)

        # Deal with other SQL classes (not so many!)
        for init in sql_data['init_list']:
            init['table']()
        
        # simple SQL row class tables
        for simple_class in sql_data['simple_classes']:
            _sa_map_simple_class(**simple_class)
    
        # Deal with other SQL classes (not so many!)
        for init in sql_data['init_list']:
            init['mapper']()

    except DBAPIError as exc:
        # Reasonably protected by above connect attempt - a traceback here is OK
        startup_log_func("setup_sqlalchemy() - %s" % sys.exc_info()[1])
        raise exc
    
    except NoSuchTableError as exc:
        startup_log_func("setup_sqlalchemy() - No such table '%s'." % exc)
        raise exc

def setup_sqlalchemy():
    """
    Connects to PostgreSQL, and sets up table mappings.  Can only be called
    once.  This one is made to be called from daemon and command line 
    applications. This one just exists to go sys.exit appropriately!
    """
    try:
        core_setup_sqlalchemy()
    except DBAPIError:
        sys.exit(os.EX_NOHOST)
    except NoSuchTableError:
        sys.exit(os.EX_NOINPUT)
    except RuntimeError:
        sys.exit(os.EX_CONFIG)

def db_clock_unixtime(db_session):
    """
    Returns database current clock time as unix timestamp
    """
    time = db_session.query(extract('epoch', func.clock_timestamp())).scalar()
    return time

def db_now_unixtime(db_session):
    """
    Returns database start of transaction clock time as unix timestamp
    """
    time = db_session.query(extract('epoch', func.now())).scalar()
    return time

def db_time(db_session):
    """
    Returns database timestamp with time zone from now(), the timestamp 
    of the current transaction.
    """
    time = db_session.execute(func.now()).scalar()
    return time

def db_clock_time(db_session):
    """
    Returns database timestamp of the current clock time
    """
    time = db_session.execute(func.clock_timestamp()).scalar()
    return time





