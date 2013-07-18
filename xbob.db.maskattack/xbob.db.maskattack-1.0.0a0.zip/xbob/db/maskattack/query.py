#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Mon 25 Feb 15:23:54 2013

"""This module provides the Dataset interface allowing the user to query the
replay attack database in the most obvious ways.
"""

import os
import logging
from bob.db import utils
from .models import *
from .driver import Interface
from numpy import random

INFO = Interface()

SQLITE_FILE = INFO.files()[0]

class Database(object):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self):
    # opens a session to the database - keep it open until the end
    self.connect()
    random.seed(42)

  def __del__(self):
    """Releases the opened file descriptor"""
    if self.session: self.session.bind.dispose()

  def connect(self):
    """Tries connecting or re-connecting to the database"""
    if not os.path.exists(SQLITE_FILE):
      self.session = None

    else:
      self.session = utils.session(INFO.type(), SQLITE_FILE) #DOES NOT TRY READ ONLY FIRST, LOCK SHOULD BE WORKING - GLOBALLY!!! (unlike temp)

  def is_valid(self):
    """Returns if a valid session has been opened for reading the database"""

    return self.session is not None

  def assert_validity(self):
    """Raise a RuntimeError if the database backend is not available"""

    if not self.is_valid():
      raise RuntimeError, "Database '%s' cannot be found at expected location '%s'. Create it and then try re-connecting using Database.connect()" % (INFO.name(), SQLITE_FILE)

  def check_validity(self, l, obj, valid, default):
    """Checks validity of user input data against a set of valid values"""
    if not l: return default
    elif not isinstance(l, (tuple, list)):
      return self.check_validity((l,), obj, valid, default)
    for k in l:
      if k not in valid:
        raise RuntimeError, 'Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid)
    return l

  def check_parameters_for_validity(self, parameters, parameter_description, valid_parameters, default_parameters = None):
    """Checks the given parameters for validity, i.e., if they are contained in the set of valid parameters.
    It also assures that the parameters form a tuple or a list.
    If parameters is 'None' or empty, the default_parameters will be returned (if default_parameters is omitted, all valid_parameters are returned).

    This function will return a tuple or list of parameters, or raise a ValueError.

    Keyword parameters:

    parameters
    The parameters to be checked.
    Might be a string, a list/tuple of strings, or None.

    parameter_description
    A short description of the parameter.
    This will be used to raise an exception in case the parameter is not valid.

    valid_parameters
    A list/tuple of valid values for the parameters.

    default_parameters
    The list/tuple of default parameters that will be returned in case parameters is None or empty.
    If omitted, all valid_parameters are used.
    """
    if not parameters:
      # parameters are not specified, i.e., 'None' or empty lists
      parameters = default_parameters if default_parameters is not None else valid_parameters

    if not isinstance(parameters, (list, tuple, set)):
      # parameter is just a single element, not a tuple or list -> transform it into a tuple
      parameters = (parameters,)

    # perform the checks
    for parameter in parameters:
      if parameter not in valid_parameters:
        raise ValueError, "Invalid %s '%s'. Valid values are %s, or lists/tuples of those" % (parameter_description, parameter, valid_parameters)

    # check passed, now return the list/tuple of parameters
    return parameters

  def sets(self):
    """Returns the names of all registered sets"""

    return ProtocolPurpose.set_choices # Same as Client.set_choices for this database

  def clients(self, protocol=None, sets=None):
    """Returns a set of clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('verification',)

    sets
      The sets to which the clients belong ('world', 'dev', 'test')

    Returns: A list containing all the clients which have the given properties.
    """

    self.assert_validity()
    VALID_SETS = self.sets()
    sets_ = self.check_validity(sets, "set", VALID_SETS, VALID_SETS)
    # List of the clients
    q = self.session.query(Client).filter(Client.set.in_(sets_)).\
          order_by(Client.id)
    return list(q)
    
  '''def update_set(self,cvtype='fixed',client_id=None):
    """Updates the set column for the client table based on the given cross-validation type.
       This function is removed since it causes write-access conflicts.

    Keyword Parameters:

    cvtype
      The cross validation type ('fixed','random','loo')

    client_id
      The client id to be left out (only for 'loo')

    Returns: The list of assigned sets to the cliebts
    """
    self.assert_validity()    
    cvtype = self.check_parameters_for_validity(cvtype, "cvtype", ('fixed', 'random', 'loo'))[0]
    assignment = {}

    # Update the sets for clients
    if(cvtype == 'fixed'):
        for c in self.session.query(Client).all():
            c.set = c.fixset
    elif(cvtype == 'random'):
        id_list = range(1,18)
        random.shuffle(id_list)
        assignment = {}
        for i in range(0,17):
            if i < 7: 
              set = 'world'
            elif i < 12:
              set = 'dev'
            else:
              set = 'test'
            assignment[id_list[i]] = set
        for c in self.session.query(Client).all():
            c.set = assignment[c.id]
    else:
        if(client_id not in range(1,18)):
            raise ValueError, "A valid client id is required for leave one out method."
        else:
            id_list = range(1,18)
            id_list.remove(client_id)
            #random.shuffle(id_list)
            assignment = {client_id:'test'}
            for i in range(0,16):
                if i < 8: 
                    set = 'world'
                else:
                    set = 'dev'
                assignment[id_list[i]] = set
            for c in self.session.query(Client).all():
                c.set = assignment[c.id]
        
    self.session.commit()
    
    # Delete the old file lists
    for p in self.session.query(ProtocolPurpose).all():
        p.files[:] = []
        self.session.flush()
        self.session.commit()

    # Update the files list for protocol purposes
    for p in self.session.query(ProtocolPurpose).all():
        for sid in eval(p.session_list):
            q = self.session.query(File).join(Client).filter(Client.set == p.set).filter(File.session == sid).order_by(File.id)
            for k in q:
                p.files.append(k)
    
    return assignment'''

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    self.assert_validity()
    return self.session.query(Client).filter(Client.id==id).count() != 0

  def protocols(self):
    """Returns all protocol objects.
    """

    self.assert_validity()
    return list(self.session.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    self.assert_validity()
    return self.session.query(Protocol).filter(Protocol.name==name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    self.assert_validity()
    return self.session.query(Protocol).filter(Protocol.name==name).one()

  def protocol_names(self):
    """Returns all registered protocol names"""

    return [str(p.name) for p in self.protocols()]

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.session.query(ProtocolPurpose))

  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices

  def fileID_to_clientID(self,id):
    """Returns the client ID of the given file ID"""
    
    q = self.session.query(File).filter(File.id==id)    
    return q[0].client_id
    
  def fileID_to_session(self,id):
    """Returns the client ID of the given file ID"""
    
    q = self.session.query(File).filter(File.id==id)    
    return q[0].session
    
  def fileID_to_shot(self,id):
    """Returns the client ID of the given file ID"""
    
    q = self.session.query(File).filter(File.id==id)    
    return q[0].shot

  def objects(self, protocol=None, purposes=None, client_ids=None, sets=None,
      classes=None):
    """Returns a set of filenames for the specific query by the user.
    
    Keyword Parameters:

    protocol
    One of the 3DMAD protocols ('verification', '').

    purposes
    The purposes required to be retrieved ('enrol', 'probeReal', 'probeMask', 'train') or a tuple
    with several of them. If 'None' is given (this is the default), it is
    considered the same as a tuple with all possible values. This field is
    ignored for the data from the "world" set.

    model_ids
    Only retrieves the files for the provided list of model ids (claimed
    client id). The model ids are string. If 'None' is given (this is
    the default), no filter over the model_ids is performed.

    sets
    One of the sets ('world', 'dev', 'test') or a tuple with several of them.
    If 'None' is given (this is the default), it is considered the same as a
    tuple with all possible values.

    classes
    The classes (types of accesses) to be retrieved ('client', 'impostor')
    or a tuple with several of them. If 'None' is given (this is the
    default), it is considered the same as a tuple with all possible values.

    Returns: A list of files which have the given properties.
    """

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    sets = self.check_parameters_for_validity(sets, "set", self.sets())
    classes = self.check_parameters_for_validity(classes, "class", ('client', 'impostor'))
    client_ids = self.check_parameters_for_validity(client_ids, "client_id", range(1,18))

    import collections
    if(client_ids is None):
      client_ids = ()
    elif(not isinstance(client_ids,collections.Iterable)):
      client_ids = (client_ids,)

    # Now query the database
    q = self.session.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
            filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.set.in_(sets), ProtocolPurpose.purpose.in_(purposes)))
            
    if(('probeMask' in purposes) or ('probeReal' in purposes)):
        if(classes == 'client'):
            q = q.filter(Client.id.in_(client_ids))
        elif(classes == 'impostor'):
            q = q.filter(not_(File.client_id.in_(client_ids)))
    
    q = q.order_by(File.client_id, File.session, File.shot)
    
    # To remove duplicates
    def removeDup(seq):
      seen = set()
      seen_add = seen.add
      return [ x for x in seq if x not in seen and not seen_add(x)]
      
    return removeDup(list(q)) 
