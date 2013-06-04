'''
@author: saaj
'''


class Abstract(object):
  '''Abstract wrapper for connection object. Declares the API subset Fangorn uses.
  Constructor must set auto-commit mode on provided connection. Cursors must implement 
  'named' DB-API paramstyle. Transaction control methods are recommended to implement 
  nested transaction support. However testsuite requires nested transactions to run.'''

  _connection = None


  def __init__(self, connection):
    self._connection = connection

  def cursor(self):
    raise NotImplementedError()
  
  def begin(self):
    raise NotImplementedError()
  
  def commit(self):
    raise NotImplementedError()
  
  def rollback(self):
    raise NotImplementedError()
