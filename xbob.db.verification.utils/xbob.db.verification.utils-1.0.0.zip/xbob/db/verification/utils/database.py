#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Thu Dec  6 12:28:25 CET 2012
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import abc
import six

class Database(six.with_metaclass(abc.ABCMeta, object)):
  """Abstract base class that defines the minimum required API for querying verification databases."""

  def __init__(self, original_directory = None, original_extension = None):
    """This constructor tests if all implemented functions at least take the desired arguments.
    Keyword
    The ``original_directory`` and ``original_extension`` parameters are used in the ``original_file_name`` function.
    If omitted,
    """
    # copy original file name and extension
    self.original_directory = original_directory
    self.original_extension = original_extension
    # try if the implemented model_ids() and objects() function have at least the required interface
    try:
      # create a value that is very unlikely a valid value for anything
      test_value = '#6T7+§X'
      # test if the parameters of the functions apply
      self.model_ids(groups=test_value, protocol=test_value)
      self.objects(groups=test_value, protocol=test_value, purposes=test_value, model_ids=(test_value,))
      self.annotations(file_id=test_value)
    except TypeError as e:
      # type error indicates that the given parameters are not valid.
      raise NotImplementedError(str(e) + "\nPlease implement:\n - the model_ids(...) function with at least the arguments 'groups' and 'protocol'\n - the objects(...) function with at least the arguments 'groups', 'protocol', 'purposes' and 'model_ids'\n - the annotations() function with at least the arguments 'file_id'.")
    except:
      # any other error is fine at this stage.
      pass

  #################################################################
  ###### Methods to be overwritten by derived classes #############
  #################################################################

  @abc.abstractmethod
  def model_ids(self, groups = None, protocol = None, **kwargs):
    """This function returns the ids of the models of the given groups for the given protocol.

    Keyword parameters:

    groups
      The groups of which the model ids should be returned.
      Usually, groups are one or more elements of ('world', 'dev', 'eval')

    protocol
      The protocol for which the model ids should be retrieved.
      The protocol is dependent on your database.
      If you do not have protocols defined, just ignore this field.
    """
    raise NotImplementedError("This function must be implemented in your derived class.")

  @abc.abstractmethod
  def objects(self, groups = None, protocol = None, purposes = None, model_ids = None, **kwargs):
    """This function returns lists of File objects, which fulfill the given restrictions.

    Keyword parameters:

    groups
      The groups of which the clients should be returned.
      Usually, groups are one or more elements of ('world', 'dev', 'eval')

    protocol
      The protocol for which the clients should be retrieved.
      The protocol is dependent on your database.
      If you do not have protocols defined, just ignore this field.

    purposes
      The purposes for which File objects should be retrieved.
      Usually, purposes are one of ('enrol', 'probe').

    model_ids
      The model ids for which the File objects should be retrieved.
      What defines a 'model id' is dependent on the database.
      In cases, where there is only one model per client, model ids and client ids are identical.
      In cases, where there is one model per file, model ids and file ids are identical.
      But, there might also be other cases.
    """
    raise NotImplementedError("This function must be implemented in your derived class.")


  def annotations(self, file_id):
    """This function returns the annotations for the given file id as a dictionary.

    Keyword parameters:

    file_id
      The ID of the File object you want to retrieve the annotations for,

    Return value:
      A dictionary of annotations, usually something like {'leye':(le_y,le_x), 'reye':(re_y,re_x), ...},
      or None if there are no annotations for the given file ID (which is the case in this base class implementation).
    """
    return None


  #################################################################
  ######### Methods to be used by derived classes #################
  #################################################################

  def provides_file_set_for_protocol(self, protocol = None):
    """Returns True if the given protocol specifies file sets for probes, instead of a single probe file.
    In this default implementation, False is returned, throughout.
    If you need different behavior, please overload this function in your derived class."""
    return False


  def uniquify(self, file_list):
    """Sorts the given list of File objects and removes duplicates from it.

    Keyword parameters:

    file_list
      A list of File objects to be handled.
      Also other objects can be handled, as long as they are sortable.

    Returns
      A sorted copy of the given list with the duplicated removed.
    """
    return sorted(list(set(file_list)))


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
        raise ValueError("Invalid %s '%s'. Valid values are %s, or lists/tuples of those" % (parameter_description, parameter, valid_parameters))

    # check passed, now return the list/tuple of parameters
    return parameters

  def check_parameter_for_validity(self, parameter, parameter_description, valid_parameters, default_parameter = None):
    """Checks the given parameter for validity, i.e., if it is contained in the set of valid parameters.
    If the parameter is 'None' or empty, the default_parameter will be returned, in case it is specified, otherwise a ValueError will be raised.

    This function will return the parameter after the check tuple or list of parameters, or raise a ValueError.

    Keyword parameters:

    parameter
      The single parameter to be checked.
      Might be a string or None.

    parameter_description
      A short description of the parameter.
      This will be used to raise an exception in case the parameter is not valid.

    valid_parameters
      A list/tuple of valid values for the parameters.

    default_parameters
      The default parameter that will be returned in case parameter is None or empty.
      If omitted and parameter is empty, a ValueError is raised.
    """
    if not parameter:
      # parameter not specified ...
      if default_parameter is not None:
        # ... -> use default parameter
        parameter = default_parameter
      else:
        # ... -> raise an exception
        raise ValueError("The %s has to be one of %s, it might not be 'None'." % (parameter_description, valid_parameters))

    if isinstance(parameter, (list, tuple, set)):
      # the parameter is in a list/tuple ...
      if len(parameter) > 1:
        raise ValueError("The %s has to be one of %s, it might not be more than one (%s was given)." % (parameter_description, valid_parameters, parameter))
      # ... -> we take the first one
      parameter = parameter[0]

    # perform the check
    if parameter not in valid_parameters:
      raise ValueError("The given %s '%s' is not allowed. Please choose one of %s." % (parameter_description, parameter, valid_parameters))

    # tests passed -> return the parameter
    return parameter


  #################################################################
  ######### Methods to provide common functionality ###############
  #################################################################

  def original_file_name(self, file):
    """This function returns the original file name for the given File object.

    Keyword parameters:

    file
      The File objects for which the file name should be retrieved

    Return value:
      The original file name for the given File object
    """
    # check if directory is set
    if not self.original_directory or not self.original_extension:
      raise ValueError("The original_directory and/or the original_extension were not specified in the constructor.")
    # extract file name
    file_name = file.make_path(self.original_directory, self.original_extension)
    if os.path.exists(file_name):
      return file_name
    raise ValueError("The file '%s' was not found. Please check the original directory '%s' and extension '%s'?" % (file_name, self.original_directory, self.original_extension))

  def original_file_names(self, files):
    """This function returns the list of original file names for the given list of File objects.

    Keyword parameters:

    files
      The list of File objects for which the file names should be retrieved

    Return value:
      The original file names for the given File objects, in the same order.
    """

    # extract file names
    return [self.original_file_name(f) for f in files]

  def file_names(self, files, directory, extension):
    """This function returns the list of original file names for the given list of File objects.

    Keyword parameters:

    files
      The list of File objects for which the file names should be retrieved

    directory
      The base directory where the files are stored

    extension
      The file name extension of the files

    Return value:
      The file names for the given File objects, in the same order.
    """
    # extract file names
    return [f.make_path(directory, extension) for f in files]


  def all_files(self, **kwargs):
    """Returns the list of all File objects that satisfy your query.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    return self.uniquify(self.objects(**kwargs))

  def training_files(self, protocol = None, **kwargs):
    """Returns the list of all training (world) File objects that satisfy your query.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    return self.uniquify(self.objects(protocol=protocol, groups='world', **kwargs))

  def test_files(self, protocol = None, group = 'dev', **kwargs):
    """Returns the list of all test File objects of the given group that satisfy your query.
    Test objects are all File objects that serve either for enrollment or probing.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    return self.uniquify(self.objects(protocol=protocol, groups=group, **kwargs))

  def model_ids(self, protocol = None, group = 'dev', **kwargs):
    """Returns the list of model ids of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    return sorted(self.model_ids(protocol=protocol, groups=group, **kwargs))

  def enroll_files(self, protocol = None, model_id = None, group = 'dev', **kwargs):
    """Returns the list of enrollment File objects from the given model id of the given protocol for the given group that satisfy your query.
    If the model_id is None (the default), enrollment files for all models are returned.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    if model_id:
      return self.uniquify(self.objects(protocol=protocol, groups=group, model_ids=(model_id,), purposes='enrol', **kwargs))
    else:
      return self.uniquify(self.objects(protocol=protocol, groups=group, purposes='enrol', **kwargs))

  def probe_files(self, protocol = None, model_id = None, group = 'dev', **kwargs):
    """Returns the list of probe File objects to probe the model with the given model id of the given protocol for the given group that satisfy your query.
    If the model_id is None (the default), all possible probe files are returned.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    if model_id:
      return self.uniquify(self.objects(protocol=protocol, groups=group, model_ids=(model_id,), purposes='probe', **kwargs))
    else:
      return self.uniquify(self.objects(protocol=protocol, groups=group, purposes='probe', **kwargs))



class SQLiteDatabase(Database):
  """This class can be used for handling SQL databases.
  It opens an SQL database in a read-only mode and keeps it opened during the whole session.
  Since this class is based on the :py:class:`Database` class, it is abstract and you have to implement the abstract methods of that class."""

  def __init__(self, sqlite_file, file_class, **kwargs):
    """Opens a connection to the given SQLite file and keeps it open through the whole session."""
    self.m_sqlite_file = sqlite_file
    if not os.path.exists(sqlite_file):
      self.m_session = None
    else:
      import bob.db.utils
      self.m_session = bob.db.utils.session_try_readonly('sqlite', sqlite_file)
    # call base class constructor
    Database.__init__(self, **kwargs)
    # also set the File class that is used (needed for a query)
    from .file import File
    # assert the given file class is derived from the File class
    assert issubclass(file_class, File)
    self.m_file_class = file_class

  def __del__(self):
    """Closes the connection to the database when it is not needed any more."""
    if self.is_valid():
      # do some magic to close the connection to the database file
      try:
        # Since the dispose function re-creates a pool
        #   which might fail in some conditions, e.g., when this destructor is called during the exit of the python interpreter
        self.m_session.bind.dispose()
      except TypeError:
        # ... I can just ignore the according exception...
        pass

  def is_valid(self):
    """Returns if a valid session has been opened for reading the database."""
    return self.m_session is not None

  def assert_validity(self):
    """Raise a RuntimeError if the database back-end is not available."""
    if not self.is_valid():
      raise RuntimeError("Database of type 'sqlite' cannot be found at expected location '%s'." % self.m_sqlite_file)

  def query(self, *args):
    """Creates a query to the database using the given arguments."""
    self.assert_validity()
    return self.m_session.query(*args)

  def paths(self, ids, prefix=None, suffix=None, preserve_order = True):
    """Returns a full file paths considering particular file ids, a given
    directory and an extension

    Keyword Parameters:

    id
      The ids of the object in the database table "file". This object should be
      a python iterable (such as a tuple or list).

    prefix
      The bit of path to be prepended to the filename stem

    suffix
      The extension determines the suffix that will be appended to the filename
      stem.

    preserve_order
      If True (the default) the order of elements is preserved, but the
      execution time increases.

    Returns a list (that may be empty) of the fully constructed paths given the
    file ids.
    """

    file_objects = self.query(self.m_file_class).filter(self.m_file_class.id.in_(ids))
    if not preserve_order:
      return [f.make_path(prefix, suffix) for f in file_objects]
    else:
      # path_dict = {f.id : f.make_path(prefix, suffix) for f in file_objects}  <<-- works fine with python 2.7, but not in 2.6
      path_dict = {}
      for f in file_objects: path_dict[f.id] = f.make_path(prefix, suffix)
      return [path_dict[id] for id in ids]

  def reverse(self, paths, preserve_order = True):
    """Reverses the lookup: from certain paths, return a list of
    File objects

    Keyword Parameters:

    paths
      The filename stems to query for. This object should be a python
      iterable (such as a tuple or list)

    preserve_order
      If True (the default) the order of elements is preserved, but the
      execution time increases.

    Returns a list (that may be empty).
    """

    file_objects = self.query(self.m_file_class).filter(self.m_file_class.path.in_(paths))
    if not preserve_order:
      return file_objects
    else:
      # path_dict = {f.path : f for f in file_objects}  <<-- works fine with python 2.7, but not in 2.6
      path_dict = {}
      for f in file_objects: path_dict[f.path] = f
      return [path_dict[path] for path in paths]


class ZTDatabase(Database):
  """This class defines another set of abstract functions that need to be implemented if your database provides the interface for computing scores used for ZT-normalization."""

  def __init__(self, **kwargs):
    """This constructor tests if all implemented functions take the correct arguments."""
    # call base class constructor
    Database.__init__(self, **kwargs)
    # try if the implemented tmodel_ids(), tobjects() and zobjects() function have at least the required interface
    try:
      # create a value that is very unlikely a valid value for anything
      test_value = '#F9S%3*Y'
      # test if the parameters of the functions apply
      self.tmodel_ids(groups=test_value, protocol=test_value)
      self.tobjects(groups=test_value, protocol=test_value, model_ids=test_value)
      self.zobjects(groups=test_value, protocol=test_value)
    except TypeError as e:
      # type error indicates that the given parameters are not valid.
      raise NotImplementedError(str(e) + "\nPlease implement:\n - the tmodel_ids(...) function with at least the arguments 'groups' and 'protocol'\n - the tobjects(...) function with at least the arguments 'groups', 'protocol' and 'model_ids'\n - the zobjects(...) function with at least the arguments 'groups' and 'protocol'")
    except:
      # any other error is fine at this stage.
      pass

  @abc.abstractmethod
  def tmodel_ids(self, groups = None, protocol = None, **kwargs):
    """This function returns the ids of the T-Norm models of the given groups for the given protocol.

    Keyword parameters:

    groups
      The groups of which the model ids should be returned.
      Usually, groups are one or more elements of ('dev', 'eval')

    protocol
      The protocol for which the model ids should be retrieved.
      The protocol is dependent on your database.
      If you do not have protocols defined, just ignore this field.
    """
    raise NotImplementedError("This function must be implemented in your derived class.")

  @abc.abstractmethod
  def tobjects(self, groups = None, protocol = None, model_ids = None, **kwargs):
    """This function returns the File objects of the T-Norm models of the given groups for the given protocol and the given model ids.

    Keyword parameters:

    groups
      The groups of which the model ids should be returned.
      Usually, groups are one or more elements of ('dev', 'eval')

    protocol
      The protocol for which the model ids should be retrieved.
      The protocol is dependent on your database.
      If you do not have protocols defined, just ignore this field.

    model_ids
      The model ids for which the File objects should be retrieved.
      What defines a 'model id' is dependent on the database.
      In cases, where there is only one model per client, model ids and client ids are identical.
      In cases, where there is one model per file, model ids and file ids are identical.
      But, there might also be other cases.
    """
    raise NotImplementedError("This function must be implemented in your derived class.")

  @abc.abstractmethod
  def zobjects(self, groups = None, protocol = None, **kwargs):
    """This function returns the File objects of the Z-Norm impostor files of the given groups for the given protocol.

    Keyword parameters:

    groups
      The groups of which the model ids should be returned.
      Usually, groups are one or more elements of ('dev', 'eval')

    protocol
      The protocol for which the model ids should be retrieved.
      The protocol is dependent on your database.
      If you do not have protocols defined, just ignore this field.
    """
    raise NotImplementedError("This function must be implemented in your derived class.")


  def t_model_ids(self, protocol, group = 'dev', **kwargs):
    """Returns the list of model ids used for T-Norm of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    return self.uniquify(self.tmodel_ids(protocol=protocol, groups=group, **kwargs))

  def t_enroll_files(self, protocol, model_id, group = 'dev'):
    """Returns the list of T-Norm model enrollment File objects from the given model id of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    return self.uniquify(self.tobjects(protocol=protocol, groups=group, model_ids=(model_id,), **kwargs))

  def z_probe_files(self, protocol, model_id, group = 'dev'):
    """Returns the list of Z-Norm probe File objects to probe the model with the given model id of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the implementation of the derived class Database.objects() function."""
    return self.uniquify(self.zobjects(protocol=protocol, groups=group, model_ids=(model_id,), purposes='probe', **kwargs))

