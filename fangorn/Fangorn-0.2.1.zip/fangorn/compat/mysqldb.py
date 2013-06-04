'''
@author: saaj
'''


import re

import MySQLdb.cursors as cursors

from . import Abstract


class NamedCursor(cursors.Cursor):

  _placeholderRe = re.compile(':([a-zA-Z]\w+)')


  def execute(self, query, args = None):
    return super(NamedCursor, self).execute(self._placeholderRe.sub('%(\\1)s', query), args)
  

class Mysqldb(Abstract):

  _transactionLevel = 0


  def __init__(self, connection):
    super(Mysqldb, self).__init__(connection)
    
    self._connection.autocommit(True)
    
  def cursor(self):
    return self._connection.cursor(NamedCursor)
  
  def begin(self):
    if self._transactionLevel == 0:
      self.cursor().execute('START TRANSACTION')
    else:
      self.cursor().execute('SAVEPOINT LEVEL{0}'.format(self._transactionLevel))

    self._transactionLevel += 1

  def commit(self):
    self._transactionLevel -= 1

    if self._transactionLevel == 0:
      self._connection.commit()
    else:
      self.cursor().execute('RELEASE SAVEPOINT LEVEL{0}'.format(self._transactionLevel))

  def rollback(self):
    self._transactionLevel -= 1

    if self._transactionLevel == 0:
      self._connection.rollback()
    else:
      self.cursor().execute('ROLLBACK TO SAVEPOINT LEVEL{0}'.format(self._transactionLevel))
