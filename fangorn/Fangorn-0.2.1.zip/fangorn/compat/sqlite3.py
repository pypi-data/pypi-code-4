'''
@author: saaj
'''


from . import Abstract


class Sqlite3(Abstract):

  _transactionLevel = 0


  def __init__(self, connection):
    super(Sqlite3, self).__init__(connection)
    
    self._connection.isolation_level = None
    self._connection.execute('PRAGMA foreign_keys = 1')

  def cursor(self):
    return self._connection.cursor()
  
  def begin(self):
    if self._transactionLevel == 0:
      self.cursor().execute('BEGIN TRANSACTION')
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
