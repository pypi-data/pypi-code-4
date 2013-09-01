"""
Created on Nov 18, 2012

@author: nibo
"""

class node(object):
    """Node is the base class for all objects in UBPM that reside in the tree.
    This class is created and populated by a factory class."""
    """nodeid is the numeric identifier of this node in the database """
    nodeid = None
    """ parentnodeid numeric identifier of the parent of this node in the database """
    parentnodeid = None
    """ nodeuuid is a globally unique identifier of this node"""
    """ It makes it possible to identify the same node in any database which is very useful """
    nodeuuid = None
    """ nodetypeid defined what type of node a node is, node types are listed in the node_type table. """
    nodetypeid = None
    """ The name of the node. Does not have do be unique from a tree standpoint.* """ 
    nodename = None
    
    
    
    """ Datamodelid is related to the node type and technically not a part of the node. 
        Used as a shorthand when loading data""" 
    datamodelid = None

    
    """ The nodename is stored in the tree itself purely for convenience reasons. 
    From experience, querying the tree is something of a pain when one always have to join a detail 
    table to get an idea of what a node is. 
    It simply is better to have it in there and have it expecially. 
    And usually, changing the name of a node has larger consequenses for users anyway.""" 
    
    def __init__(self, _nodeid = None, _parentnodeid = None, _nodeuuid = None, 
                 _nodetypeid = None, _nodename = None,_datamodelid = None, _create_original = True):
        """
        Constructor
        """
        self.nodeid = _nodeid
        self.parentnodeid = _parentnodeid
        self.nodeuuid = _nodeuuid
        self.nodetypeid = _nodetypeid
        self.nodename = _nodename
        self.datamodelid = _datamodelid
        if _create_original:
            self.__original = node(_create_original = False)
            self.reassign_properties(self, self.__original)
        
        

    def reassign_properties(self, _source, _dest):
        """Assign the properties and their valued from one node to another"""
        _source_properties = self._read_properties(_source)
        for curr_property in _source_properties:
            setattr(_dest, curr_property[0],curr_property[1]) 
        
    def _read_properties(self, _object):
        """Return a list of all properties of an object"""
        properties = list()
        for k in _object.__dict__.items():
            if not hasattr(k[1], '__call__') and k[0][0:1] != '_': 
                properties.append(k) 
                
        return properties
          
