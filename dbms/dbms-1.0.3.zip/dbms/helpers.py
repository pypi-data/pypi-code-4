#------------------------------------------------------------------------------#
#                           Connection helpers
#
#        Use this as a model and put your own connection helpers here.
#------------------------------------------------------------------------------#

import dbms

def OraConnect(user, pwd, database='bantest', host=None, port=1521):
    """Return a dbms.Connection to an Oracle database."""
    import cx_Oracle
    import os

    # If this doesn't match you'll have weird type conversion errors
    os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
    if host is None:
        host = database
    dsn = cx_Oracle.makedsn(host, port, database)
    dbc = cx_Oracle.connect(user, pwd, dsn)
    return dbms.Connection(dbc, cx_Oracle)


def PgConnect(user, pwd, database='postgres', host='localhost', port=5432):
    """Return a dmbs.Connection to a PostgreSQL database."""
    import psycopg2

    parms = {'database': database, 'user': user, 'password': pwd, 'host': host, 'port': port}
    dbc = psycopg2.connect(**parms)
    return dbms.Connection(dbc, psycopg2)


def MySQLConnect(user, pwd, database='mysql', host='localhost', port=3306):
    """Return a dmbs.Connection to a MySQL database."""
    import MySQLdb

    parms = {'db': database, 'user': user, 'passwd': pwd, 'host': host, 'port': port}
    dbc = MySQLdb.connect(**parms)
    return dbms.Connection(dbc, MySQLdb)


def MSSQLConnect(user, pwd, database, host='localhost', port=1433):
    """Return a dmbs.Connection to an MS SQL Server database."""
    import pymssql

    dbc = pymssql.connect(user=user, password=pwd, database=database, host=r'%s:%d' % (host, port))
    return dbms.Connection(dbc, pymssql)


def ODBCConnect(user, pwd, database, host='localhost', port=1433, driver='SQL Server'):
    """Return a dmbs.Connection to an ODBC database."""
    import pyodbc

    dbc = pyodbc.connect('DRIVER={%s};SERVER=%s,%d;UID=%s;PWD=%s;DATABASE=%s;' %
                         (driver, host, port, user, pwd, database))
    return  dbms.Connection(dbc, pyodbc)

