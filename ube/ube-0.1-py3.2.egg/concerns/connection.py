"""
Created on Nov 6, 2012

@author: Nicklas Boerjesson
@note: This is an decorator that adds a connection property to the decorated class 
"""


from decorator import decorator
from .aspect_utilities import alter_function_parameter_and_call

db_connection = None 

def set_connection(connection):
    global db_connection
    db_connection = connection

def get_connection():
    global db_connection
    return db_connection

def _connection(func, *args, **kwargs):
    """The connection aspect code"""
    global db_connection
    if db_connection == None:
        raise Exception('Connection aspect for "' + func.__name__ +'": No connection set.')
    
    return alter_function_parameter_and_call(func, args, kwargs, '_connection', db_connection, 
        'Connection aspect for "' + func.__name__ +'": No _connection argument set.')


def connection(f):
    """The connection decorator requires a _connection argument in the decorated function.
    It assigns a DAL instance to that argument"""
    return decorator(_connection, f)

def connection_c(obj):
    """The c_connection decorator. It assigns a DAL instance to the classes' _dal-property."""
    global db_connection
    if db_connection == None:
        raise Exception('Connection aspect for "' + obj.__name__ +'": No connection set.')
    
    obj._dal = db_connection
    return obj
