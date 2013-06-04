'''
@author: saaj
'''

import sqlite3

from compat.sqlite3 import Sqlite3 as Wrapper
from base import Tree, NotFoundError, IntegrityError


class NestedSetsTree(Tree):
  
  def _getMeta(self, prefix = ''):
    return dict(self.columns, **{
      'table'  : self._table,
      'fields' : ','.join('{0}{1}'.format(prefix, f) for f in self.columns.values())
    })
    
  def _nameColumns(self, row):
    return dict(zip(self.columns.keys(), row))
  
  def _updateMarkup(self, prev, width):
    meta   = self._getMeta()
    cursor = self._db.cursor()
    values = dict(prev = prev, width = width)
    
    sql = '''
      UPDATE {table}
      SET {left} = {left} + :width
      WHERE {left} > :prev
    '''
    cursor.execute(sql.format(**meta), values)
    
    sql = '''
      UPDATE {table}
      SET {right} = {right} + :width
      WHERE {right} > :prev
    '''
    cursor.execute(sql.format(**meta), values)
    
  def add(self, values, parentId = None, prevId = None):
    self._db.begin()
    try:
      # if neither then it's root adding 
      if parentId or prevId:
        if prevId:
          target = self.getNode(prevId)
          if target['parentId'] is None:
            raise IntegrityError('Cannot add node behind root')
          
          parentId = target['parentId']
          prev     = target['right']
        else:
          target = self.getNode(parentId)
          prev   = target['left']
        
        self._updateMarkup(prev, 2)
      else:
        prev = 0
        
      values['parentId'] = parentId
      values['left']     = prev + 1;
      values['right']    = prev + 2;
      
      sql = '''
        INSERT INTO {table}({fields}) 
        VALUES({values})
      '''
      
      meta           = self._getMeta()
      meta['fields'] = ','.join(v for k, v in self.columns.items() if k in values)
      meta['values'] = ','.join(':{0}'.format(k) for k in self.columns.keys() if k in values)
      
      cursor = self._db.cursor()
      cursor.execute(sql.format(**meta), values)
      
      self._db.commit()
      
      return cursor.lastrowid
    except:
      self._db.rollback()
      raise

  def edit(self, id, values):
    sql = '''
      UPDATE {table}
      SET {values}
      WHERE {nodeId} = :id
    '''
    
    meta           = self._getMeta()
    meta['values'] = ','.join('{0} = :{1}'.format(v, k) for k, v in self.valueColumns.items() if k in values)

    self._db.cursor().execute(sql.format(**meta), dict(values, id = id))
  
  def remove(self, id):
    self._db.begin()
    try:
      target = self.getNode(id)
      
      sql = '''
        DELETE FROM {table}
        WHERE {left} BETWEEN :left AND :right
      '''
      self._db.cursor().execute(sql.format(**self._getMeta()), target)

      self._updateMarkup(target['right'], target['left'] - target['right'] - 1)
      
      self._db.commit()
    except:
      self._db.rollback()
      raise
  
  def move(self, id, parentId = None, prevId = None):
    self._db.begin()
    try:
      if prevId:
        if prevId == id:
          return
        target   = self.getNode(prevId)
        parentId = target['parentId'] 
        prev     = target['right']
      else:
        target = self.getNode(parentId)
        prev   = target['left']

      if parentId == id:
        raise IntegrityError('Cannot move node into self')
      if self.isDescendantOf(id, parentId):
        raise IntegrityError('Cannot move node under its own descendant')
      
      node = self.getNode(id)
      # shift nodes on the width of moving subtree, like in add()
      self._updateMarkup(prev, node['right'] - node['left'] + 1)
      
      cursor = self._db.cursor()
      meta   = self._getMeta()
      
      sql = '''
        UPDATE {table}
        SET {parentId} = :parentId
        WHERE {nodeId} = :id
      '''
      cursor.execute(sql.format(**meta), dict(id = id, parentId = parentId))
      
      # re-fetch node and prev value since could be changed  
      node = self.getNode(id)
      if prevId:
        target = self.getNode(prevId)
        prev   = target['right']
      else:
        target = self.getNode(parentId)
        prev   = target['left']
      
      sql = '''
        UPDATE {table}
        SET {right} = {right} + :offset, 
            {left}  = {left} + :offset
        WHERE {left} > :left - 1 AND {right} < :right + 1
      '''
      cursor.execute(sql.format(**meta), dict(node, offset = prev - node['left'] + 1))
      
      # shift nodes on the width of moving subtree, like in remove()
      self._updateMarkup(node['right'], node['left'] - node['right'] - 1)
      
      self._db.commit()
    except:
      self._db.rollback()
      raise
  
  def getRoot(self):
    sql = '''
      SELECT {fields}
      FROM {table}
      WHERE {left} = 1
    '''
    
    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta()))
    result = cursor.fetchone()
    
    if not result:
      raise NotFoundError('No root node')
    else:
      return self._nameColumns(result)
  
  def getNode(self, id):
    sql = '''
      SELECT {fields}
      FROM {table}
      WHERE {nodeId} = :id
    '''
    
    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta()), {'id' : id})
    result = cursor.fetchone()
    
    if not result:
      raise NotFoundError('No node with id:{0}'.format(id))
    else:
      return self._nameColumns(result)
  
  def getParent(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} p ON n.{parentId} = p.{nodeId}
      WHERE n.{nodeId} = :id
    '''
    
    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('p.')), {'id' : id})
    result = cursor.fetchone()
    
    if not result:
      raise NotFoundError('No parent node for id:{0}'.format(id))
    else:
      return self._nameColumns(result)
  
  def getNext(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} s ON n.{right} + 1 = s.{left} AND n.{parentId} = s.{parentId}
      WHERE n.{nodeId} = :id
    '''
    
    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('s.')), {'id' : id})
    result = cursor.fetchone()
    
    if not result:
      raise NotFoundError('No right sibling node for id:{0}'.format(id))
    else:
      return self._nameColumns(result)
  
  def getPrevious(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} s ON n.{left} - 1 = s.{right} AND n.{parentId} = s.{parentId}
      WHERE n.{nodeId} = :id
    '''
    
    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('s.')), {'id' : id})
    result = cursor.fetchone()
    
    if not result:
      raise NotFoundError('No left sibling node for id:{0}'.format(id))
    else:
      return self._nameColumns(result)
  
  def getPath(self, id):
    node = self.getNode(id)
    
    sql = '''
      SELECT {fields}
      FROM {table}
      WHERE {left} <= :left AND {right} >= :right
      ORDER BY {left} ASC
    '''
    
    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta()), node)
    
    return map(self._nameColumns, cursor)
  
  def getChildren(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} c ON n.{nodeId} = c.{parentId}
      WHERE n.{nodeId} = :id
      ORDER BY c.{left}
    '''
    
    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('c.')), {'id' : id})
    
    return map(self._nameColumns, cursor)
  
  def getDescendants(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} d
      JOIN {table} n ON d.{left} BETWEEN n.{left} + 1 AND n.{right} - 1
      WHERE n.{nodeId} = :id
      ORDER BY d.{left}
    '''
    
    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('d.')), {'id' : id})
    
    return map(self._nameColumns, cursor)
  
  def isDescendantOf(self, parentId, descendantId):
    parent     = self.getNode(parentId)
    descendant = self.getNode(descendantId)

    return parent['left'] < descendant['left'] and parent['right'] > descendant['right']
  
  def isLeaf(self, id):
    node = self.getNode(id)
      
    return node['right'] - node['left'] == 1
  
  def validate(self, edges = False):
    cursor = self._db.cursor()
    meta   = self._getMeta()
    first  = lambda rows: tuple(r[0] for r in rows)
    
    sql = '''
      SELECT COUNT(*)
      FROM {table} 
    '''
    cursor.execute(sql.format(**meta))
    stats = cursor.fetchone()
    if stats[0] == 0:
      return 
    
    sql = '''
      SELECT {nodeId} 
      FROM {table} 
      WHERE {left} >= {right}
    '''
    cursor.execute(sql.format(**meta))
    broken = cursor.fetchall() 
    if broken:
      raise IntegrityError('Left must always be less than right: {0}'.format(first(broken)))
    
    sql = '''
      SELECT {nodeId} 
      FROM {table} 
      WHERE {parentId} = {nodeId}
    '''
    cursor.execute(sql.format(**meta))
    broken = cursor.fetchall()
    if broken:
      raise IntegrityError('Tree must have no loops: {0}'.format(first(broken)))
    
    sql = '''
      SELECT MIN({left}), MAX({right}), COUNT(*)  
      FROM {table}
    '''
    cursor.execute(sql.format(**meta))
    stats = cursor.fetchone()
    if stats[0] != 1:
      raise IntegrityError('Min left must always be 1')
    if stats[1] / 2 != stats[2]:
      raise IntegrityError('Max right must always be number of nodes / 2')

    sql = '''
      SELECT {parentId}
      FROM {table} 
      WHERE {left} = :left AND {right} = :right
    '''
    cursor.execute(sql.format(**meta), dict(left = stats[0], right = stats[1]))
    stats = cursor.fetchone()
    if not stats:
      raise IntegrityError('Tree must have one root')
    elif stats[0] is not None:
      raise IntegrityError('Parent of root must be none')
    
    sql = '''
      SELECT {nodeId} 
      FROM {table}
      WHERE ({right} - {left}) %  2 != 1 
    '''
    cursor.execute(sql.format(**meta))
    broken = cursor.fetchall()
    if broken:
      raise IntegrityError('Right - left must always be odd: {0}'.format(first(broken)))
    
    sql = '''
      SELECT GROUP_CONCAT(a.{nodeId}), a.m
      FROM (
          SELECT {nodeId}, {left} m
          FROM {table}
        UNION ALL
          SELECT {nodeId}, {right} m
          FROM {table}
      ) a
      GROUP BY a.m
      HAVING COUNT(*) != 1
    '''
    cursor.execute(sql.format(**meta))
    broken = cursor.fetchall()
    if broken:
      raise IntegrityError('Markup must be unique: {0}'.format(tuple(broken)))
    
    if edges:
      # Few minutes for 40K-row tree
      sql = '''
        SELECT a.nid, a.pid
        FROM (
            SELECT n.{nodeId} `nid`, p.{nodeId} `pid`
            FROM {table} n  
            LEFT JOIN (
              SELECT {nodeId}, {left}, {right}
              FROM {table}
              ORDER BY {left} {parentJoinOrder}
            ) p ON p.{left} < n.{left} AND p.{right} > n.{right}
            GROUP BY n.{nodeId}
          UNION ALL
            SELECT {nodeId} nid, {parentId} pid
            FROM {table}
        ) a
        GROUP BY a.nid, a.pid
        HAVING COUNT(*) != 2
      '''
      
      # strange that sqlite reverses the order of joined select 
      # so it needs ASC socrting to produce same GROUP BY result as mysql 
      try:
        cursor.execute('SELECT sqlite_version()')
        meta['parentJoinOrder'] = 'ASC'
      except:
        meta['parentJoinOrder'] = 'DESC'
      
      cursor.execute(sql.format(**meta))
      broken = tuple(cursor.fetchall())
      if broken:
        raise IntegrityError('Adjacency list edges do not match nested sets edges: {0}'.format(broken))

  def memorize(self, chunk = 4096, index = True):
    connection   = Wrapper(sqlite3.connect(':memory:'))
    targetCursor = connection.cursor()
    meta         = self._getMeta()
    
    sql = '''
      CREATE TABLE {table} (
        {nodeId}   INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        {parentId} INTEGER DEFAULT NULL REFERENCES {table}({nodeId}) 
          ON DELETE CASCADE ON UPDATE CASCADE,
        {left}     INTEGER NOT NULL,
        {right}    INTEGER NOT NULL
        {valueColumns}
      )
    '''
    valueColumns = ''
    if self.valueColumns:
      root         = self.getRoot()
      valueColumns = ', ' + ','.join(
        '{0} {1}'.format(v, 'INTEGER' if isinstance(root[k], int) else 'TEXT') 
        for k, v in self.valueColumns.items()
      )
    sql = sql.format(**dict(meta, valueColumns = valueColumns))
    
    targetCursor.execute(sql)

    meta['values'] = ','.join(':{0}'.format(k) for k in self.columns.keys())
    def insert(values):
      sql = '''
        INSERT INTO {table}({fields}) 
        VALUES({values})
      '''
      targetCursor.executemany(sql.format(**meta), values)
      return targetCursor.rowcount 
      
    sourceCursor = self._db.cursor()
    if chunk:
      index    = 0
      inserted = 0
      while not index or inserted > 0:
        sql = '''
          SELECT {fields}
          FROM {table}
          LIMIT {offset}, {limit}
        '''
        sourceCursor.execute(sql.format(offset = chunk * index, limit = chunk, **meta))
        inserted = insert(sourceCursor)
        index += 1
    else:
      sql = '''
        SELECT {fields}
        FROM {table}
      '''
      sourceCursor.execute(sql.format(**meta))
      insert(sourceCursor)
      
    if index:
      targetCursor.execute('CREATE INDEX {left} ON {table}({left})'.format(**meta))
      targetCursor.execute('CREATE INDEX {right} ON {table}({right})'.format(**meta))
      targetCursor.execute('CREATE INDEX {parentId} ON {table}({parentId})'.format(**meta))
    
    memorized         = self.__class__(connection, self._table, self.valueColumns)
    memorized.columns = self.columns
    
    return memorized 
