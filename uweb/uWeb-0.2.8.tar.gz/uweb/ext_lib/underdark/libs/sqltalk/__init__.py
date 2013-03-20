#!/usr/bin/python2.5
"""Easy use SQL abstraction module.

Returns a custom QueryResult object that holds
the result, query, used character set and various other small statistics. The
QueryResult object also support pivoting and subselects

Currently only implements a MySQL abstraction module with a stripped down
version of MySQLdb internally.

example usage:

  from sqltalk import mysql
  connection = mysql.Connect()
  with connection as cursor:
    result = cursor.RawQuery('select * from table')
"""
