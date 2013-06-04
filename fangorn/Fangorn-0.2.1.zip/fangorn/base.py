'''
@author: saaj
'''


class NotFoundError(Exception):
  ''''Raised when node was not found'''
  
class IntegrityError(Exception):
  '''Raised when tree is broken'''


class Tree(object):
  
  _table = None
  '''Name of tree-holding table'''
  _db  = None
  '''Database connection object'''
  columns = None
  '''Tree table columns'''
  valueColumns = None
  '''Non-system tree table columns'''
  
  
  def __init__(self, db, table, valueColumns = None):
    self._table = table
    self._db    = db
   
    if isinstance(valueColumns, dict):
      self.valueColumns = valueColumns
    elif valueColumns:
      self.valueColumns = dict(zip(valueColumns, valueColumns))
    else:
      self.valueColumns = {}
    
    self.columns = dict(self.valueColumns, **{
      'nodeId'   : '{0}_id'.format(table),
      'parentId' : 'parent_id',
      'left'     : 'l',
      'right'    : 'r'
    })
    
  def add(self, values, parentId = None, prevId = None):
    raise NotImplementedError()

  def edit(self, id, values):
    raise NotImplementedError()

  def remove(self, id):
    raise NotImplementedError()

  def move(self, id, parentId = None, prevId = None):
    raise NotImplementedError()  
  
  def getRoot(self):
    raise NotImplementedError()
  
  def getNode(self, id):
    raise NotImplementedError()
  
  def getParent(self, id):
    raise NotImplementedError()
  
  def getNext(self, id):
    raise NotImplementedError()
  
  def getPrevious(self, id):
    raise NotImplementedError()
  
  def getPath(self, id):
    raise NotImplementedError()
  
  def getChildren(self, id):
    raise NotImplementedError()
  
  def getDescendants(self, id):
    raise NotImplementedError()
  
  def isDescendantOf(self, parentId, descendantId):
    raise NotImplementedError()
  
  def isLeaf(self, id):
    raise NotImplementedError()
  
  def validate(self):
    raise NotImplementedError()
  
  def memorize(self, chunk = None, index = True):
    raise NotImplementedError()
