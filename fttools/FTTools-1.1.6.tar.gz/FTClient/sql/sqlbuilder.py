#!/usr/bin/python
#
# Copyright (C) 2010 Google Inc.

""" Builds SQL strings.

Builds SQL strings to pass to FTClient query method.
"""

__author__ = 'kbrisbin@google.com (Kathryn Brisbin)'


import re

class SQL:
  """ Helper class for building SQL queries """

  def showTables(self):
    """ Build a SHOW TABLES sql statement.

    Returns:
      the sql statement
    """
    return 'SHOW TABLES'

  def describeTable(self, table_id):
    """ Build a DESCRIBE <tableid> sql statement.

    Args:
      table_id: the ID of the table to describe

    Returns:
      the sql statement
    """
    return 'DESCRIBE %s' % (table_id)

  def createTable(self, table):
    """ Build a CREATE TABLE sql statement.

    Args:
      table: a dictionary representing the table. example:
        {
          "tablename":
            {
            "col_name1":"STRING",
            "col_name2":"NUMBER",
            "col_name3":"LOCATION",
            "col_name4":"DATETIME"
            }
        }

    Returns:
      the sql statement
    """

    table_name = table.keys()[0]
    cols_and_datatypes = ",".join(["'%s': %s" % (col[0], col[1]) 
                                   for col in table.get(table_name).items()])
    return "CREATE TABLE '%s' (%s)" % (table_name, cols_and_datatypes)


  def select(self, table_id, cols=None, condition=None):
    """ Build a SELECT sql statement.

    Args:
      table_id: the id of the table
      cols: a list of columns to return. If None, return all
      condition: a statement to add to the WHERE clause. For example,
        "age > 30" or "Name = 'Steve'". Use single quotes as per the API.

    Returns:
      the sql statement
    """
    stringCols = "*"
    if cols: stringCols = ("'%s'" % ("','".join(cols))) \
                          .replace("\'rowid\'", "rowid") \
                          .replace("\'ROWID\'", "ROWID")

    if condition: select = 'SELECT %s FROM %s WHERE %s' % (stringCols, table_id, condition)
    else: select = 'SELECT %s FROM %s' % (stringCols, table_id)
    return select


  def update(self, table_id, values, row_id):
    """ Build an UPDATE sql statement.

    Args:
      table_id: the id of the table
      values: dictionary of column to value. Example:
        {
        "col_name1":12,
        "col_name2":"mystring",
        "col_name3":"Mountain View",
        "col_name4":"9/10/2010"
        }
      row_id: the id of the row to update

    Returns:
      the sql statement
    """

    return "UPDATE %s SET %s WHERE ROWID = '%d'" % (table_id, 
        ", ".join(["%s=%s" % (k, self._get_str_value(v)) for k,v in values.iteritems()]), 
        row_id)

  def delete(self, table_id, row_id):
    """ Build DELETE sql statement.

    Args:
      table_id: the id of the table
      row_id: the id of the row to delete

    Returns:
      the sql statement
    """
    return "DELETE FROM %s WHERE ROWID = '%d'" % (table_id, row_id)


  def insert(self, table_id, row):
    """ Build an INSERT sql statement.

    Args:
      table_id: the id of the table
      row: dictionary of column to value. Example:
        {
        "col_name1":12,
        "col_name2":"mystring",
        "col_name3":"Mountain View",
        "col_name4":"9/10/2010"
        }

    Returns:
      the sql statement
    """

    keys = []
    values = []
    for k,v in row.items():
        if v is not None:
            keys.append(k)
            values.append(v)
                    
    return 'INSERT INTO %s (%s) VALUES (%s)' % \
      (table_id, 
        ','.join(["'%s'" % k for k in keys]), 
        ','.join([self._get_str_value(v) for v in values]))
#      (int(table_id), 

  def dropTable(self, table_id):
    """ Build DROP TABLE sql statement.

    Args:
      table_id: the id of the table

    Returns:
      the sql statement
    """
    return "DROP TABLE %s" % (table_id)


  def _get_str_value (self, value):
    """ Get a string value usable in an FT query. Enclose in sing;e quotes if necessary

    Args:
      value: the value to be converted

    Returns:
      stringified version of the value suitable fo use in an insert or update statement
    
    """
    if type(value).__name__=='int':
      stringValue = '%d' % (value)
    if type(value).__name__=='long':
      stringValue = '%d' % (value)
    elif type(value).__name__=='float':
      stringValue = '%f' % (value)
    elif type(value).__name__=='unicode':
      stringValue = "'%s'" % (value.encode('ascii', 'xmlcharrefreplace').encode('string-escape'))                              
    elif value is None:
      stringValue = "''" 
    else:
      stringValue = "'%s'" % (str(value).encode('string-escape'))                              
    return stringValue
  
if __name__ == '__main__':
    pass



