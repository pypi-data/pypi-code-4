# -*- encoding: utf-8 -*-
'''
Created on 27/05/2013

@author: Andrés Felipe Calderón andres.calderon@correlibre.org
@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Storage is the base of Caliope's Framework
Copyright (C) 2013 Fundación Correlibre

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import uuid
import psycopg2
import psycopg2.extras

class CaliopeGraphStoragePG:
  def __init__(self):
    self.conn = psycopg2.connect(host="localhost", database="CaliopeStorage", user="postgres", password="convectiva")
    self.cur = self.conn.cursor()
    
  def __del__(self):
    self.close()

  def close(self):
    self.commit()
    self.cur.close()
    self.conn.close()  
  
  def next_uuid(self):
    return str( uuid.uuid4() )
    #self.cur.execute("SELECT nextval('serial_caliope')")
    #return self.cur.fetchone()[0]
 
  def commit(self):  
    try:
      self.cur.execute("commit")
      
    except Exception, e:
      print e.pgerror
      
  def create_node_type(self, nodetype):  
    try:
      self.cur.execute("""INSERT INTO CALIOPE_NODE_TYPES (NAME)
         VALUES (%s)""",(nodetype,))

    except Exception, e:
      print e.pgerror

      
  def create_node(self,caliopeid, nodetype):  
    try:
      self.cur.execute("""INSERT INTO CALIOPE_NODES (NODE_TYPE, UUID_NODE)
         SELECT ID_NODE_TYPE, %s
         FROM CALIOPE_NODE_TYPES
         WHERE NAME = %s""",(str(caliopeid),nodetype))
                  
    except Exception, e:
      print e.pgerror


  def create_edge(self,from_caliopeid, to_caliopeid):  
    try:
      connection_caliopeid =  self.next_uuid()
      self.cur.execute("""INSERT INTO CALIOPE_NODES (NODE_TYPE, UUID_NODE)
         SELECT ID_NODE_TYPE, %s
         FROM CALIOPE_NODE_TYPES
         WHERE NAME = 'connection_node'""",(str(connection_caliopeid),))
                
      self.cur.execute("""INSERT INTO CALIOPE_EDGES (UUID_NODE_FROM, UUID_NODE_TO, UUID_NODE_CONNECTOR) 
         VALUES (%s,%s,%s)""", (str(from_caliopeid),str(to_caliopeid),str(connection_caliopeid)) )

    except Exception, e:
      print e.pgerror
      
    
    #except Exception, e:
      #print e.pgerror    
    
  def show_nodes(self):
    #cursor = self.conn.cursor('cursor_unique_name'+str(random.random()), cursor_factory=psycopg2.extras.DictCursor)
    self.cur.execute('SELECT * FROM CALIOPE_NODES')
  
    row_count = 0
    for row in self.cur:
      row_count += 1
      print row


  def show_edges(self):
    self.cur.execute('SELECT * FROM CALIOPE_EDGES')
  
    row_count = 0
    for row in self.cur:
      row_count += 1
      print row
      #print "row: %s    %s %s\n" % (row_count, row[1], row[2], )
      
storage = CaliopeGraphStoragePG()

storage.create_node_type('users')

for i in range(int(1e3)):
  nid = storage.next_uuid()
  storage.create_node(nid,'users')
  
#storage.create_edge(5022,5030)
 
storage.show_nodes()
  
storage.show_edges()
storage.close()