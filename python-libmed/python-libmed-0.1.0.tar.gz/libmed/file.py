# Copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of python-libmed.
#
# python-libmed is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# python-libmed is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with python-libmed.  If not, see <http://www.gnu.org/licenses/>.

"""
MED: File objects definition and handling interface.
"""
import os
import _file
from _utils import MEDVersion, MEDError, MEDIOError, MEDVersionError
import _mesh
import _field
import _parameter
import _profile
from base import MEDObject, check_open
from mesh import MEDMesh
from field import MEDField
from parameter import MEDParameter
from profile import MEDProfile


__all__ = ['MEDFile']


class MEDFile(MEDObject):
    """
    MED file object.

    Parameters
    ----------
    path : str
        Path to the MED file.
    mode : str
        File mode. One of:

        - 'r': read-only
        - 'w': write / create
        - 'w+': read / write
        - 'a': append

    Raises
    ------
    MEDIOError, MEDError
    """
    def __init__(self, path, mode="r", **kwargs):
        super(MEDFile, self).__init__(name=path, **kwargs)
        self.mode = str(mode)
        if os.path.isfile(path):
            self._check_compat()
        self._fid = _file.open(self.mode, path)
        self._closed = False
        try:
            self._get_comment()
        except MEDError:
            if self.mode is "w":
                self._set_comment("")

    def __enter__(self):
        self._closed = False
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @check_open
    def close(self):
        """ Close a MED file. """
        try:
            _file.close(self._fid)
        except MEDIOError:
            raise MEDIOError("Error closing MED file %s." % self.name)
        self._closed = True

    def _get_closed(self):
        return self._closed

    closed = property(_get_closed, None, None,
                      "True if the MED file is closed.")

    @check_open
    def _get_comment(self):
        return _file.read_comment(self._fid)

    @check_open
    def _set_comment(self, comment):
        _file.write_comment(self._fid, comment)

    comment = property(_get_comment, _set_comment, None,
                       "MED file description header (truncated at "
                       "COMMENT_SIZE characters). Note that a \\0 ends the "
                       "string.")

    @check_open
    def _get_med_version(self):
        try:
            major, minor, release = _file.read_version(self._fid)
        except MEDError:
            raise MEDError("Could not retrieve MED version used to "
                           "create %s." % self.name)
        return MEDVersion(major, minor, release)

    med_version = property(_get_med_version, None, None,
                           "Version of the MED library used to create the file.")

    def _check_compat(self):
        try:
            hdfok, medok = _file.read_compatibility(self.name)
        except MEDError:
            raise MEDError("Could not check compatibility for %s." %
                           self.name)
        if not hdfok:
            raise MEDVersionError("%s does not follow the HDF5 format." %
                                  self.name)
        if not medok:
            raise MEDVersionError("The MED format of %s is not compatible "
                                  "with that of the MED library." % self.name)

    @check_open
    def meshes(self):
        """
        Returns the list of meshes in a MED file.
        """
        try:
            nmeshes = _mesh.read_number_of_meshes(self._fid)
        except MEDError:
            raise MEDError("Could not retrieve the number of meshes in %s."
                           % self.name)
        ask = _mesh.read_info_from_index
        build = lambda i: self.get_mesh(ask(self._fid, i)[0])
        try:
            meshes = [build(imesh) for imesh in xrange(nmeshes)]
        except MEDError:
            raise MEDError("Could not retrieve mesh infor in %s." % self.name)
        return meshes

    @check_open
    def add_mesh(self, name, spacedim, meshdim, structured=False, desc=""):
        """
        Add and create a new mesh.

        Parameters
        ----------
        name : str
            Mesh name (no longer than NAME_SIZE).
        spacedim, meshdim : int
            Dimensions of space and mesh.
        structured : bool
            Whether or not the mesh is structured.
        desc : str, optional
            Description
        """
        return MEDMesh(self, name=name, spacedim=spacedim, meshdim=meshdim,
                       structured=structured, desc=desc)

    @check_open
    def get_mesh(self, name):
        """
        Retrieve a mesh.

        Parameter
        ---------
        name : str
            Name of the mesh to retrieve.

        Returns
        -------
        mesh : MEDMesh
            The MED mesh.
        """
        return MEDMesh(self, name=name)

    @check_open
    def add_field(self, name, meshname, ncomp, dtype, compnames=None,
                  compunits=None):
        """
        Add and create a new field. A field is supported by a mesh and may
        apply to several entities of that mesh.

        Parameters
        ----------
        name : str
            Field name (no longer than NAME_SIZE)
        meshname : str
            Name of the support mesh (no longer than NAME_SIZE)
        ncomp : int
            Number of components of the field.
        dtype : numpy.dtype
            Numeric data type of field values.
        compnames : sequence of str
            Names of components.
        compunits : sequence of str
            Units of components.
        """
        return MEDField(self, name, meshname, ncomp, dtype, compnames,
                        compunits)

    @check_open
    def get_field(self, name, meshname):
        """
        Retrieve a field.

        Parameters
        ----------
        name : str
            Name of the field to retrieve.
        meshname : str
            Name of the mesh the field is attached to.

        Returns
        -------
        field : MEDField
            The MED field.
        """
        return MEDField(self, name, meshname)

    @check_open
    def fields(self):
        """
        Returns the list of fields in a MED file.
        """
        try:
            nfields = _field.read_number_of_fields(self._fid)
        except MEDError:
            raise MEDError("Could not retrieve the number of fields in %s."
                           % self.name)
        ask = _field.read_info_from_index
        build = lambda i: self.get_field(*(ask(self._fid, i)[0:2]))
        try:
            fields = [build(ifield) for ifield in xrange(nfields)]
        except MEDError:
            raise MEDError("Could not retrieve field info in %s." % self.name)
        return fields

    @check_open
    def add_parameter(self, name, value, desc="", dtunit=""):
        """
        Parameters
        ----------
        name : str
            Parameters' name.
        value : numeric
            Parameters' value.
        desc : str, optional
            Description. The string must not be longer than COMMENT_SIZE.
        dtunit : str, optional
            Time unit. The string must not be longer than SNAME_SIZE.
            return MEDParameter(name, value, desc, dtunit)

        Returns
        -------
        param : MEDParameter
            The MED parameter.
        """
        return MEDParameter(self, name, value, desc, dtunit)

    @check_open
    def get_parameter(self, name):
        """
        Retrieve a parameter.

        Parameter
        ---------
        name : str
            Name of the parameter to retrieve.

        Returns
        -------
        mesh : MEDParameter
            The MED parameter.
        """
        return MEDParameter(self, name)

    @check_open
    def parameters(self):
        """
        Returns the list of parameters in a MED file.
        """
        try:
            nparams = _parameter.read_number_of_parameters(self._fid)
        except MEDError:
            raise MEDError("Could not retrieve the number of parameters in %s."
                           % self.name)
        ask = _parameter.read_info_from_index
        build = lambda i: self.get_parameter(ask(self._fid, i)[0])
        try:
            params = [build(iparam) for iparam in xrange(nparams)]
        except:
            raise MEDError("Could not retrieve parameter info in %s." % self.name)
        return params

    @check_open
    def add_profile(self, name, indices):
        """
        Parameters
        ----------
        name : str
            Parameters' name.
        indices : array of int
            Indices of entities in the profile.

        Returns
        -------
        profile : MEDProfile
            The MED profile.
        """
        return MEDProfile(self, name, indices)

    @check_open
    def get_profile(self, name):
        """
        Retrieve a profile.

        Parameter
        ---------
        name : str
            Name of the profile to retrieve.

        Returns
        -------
        mesh : MEDProfile
            The MED profile.
        """
        return MEDProfile(self, name)

    @check_open
    def profiles(self):
        """
        Returns the list of profiles in a MED file.
        """
        nprofiles = _profile.read_number_of_profiles(self._fid, self.name)
        ask = _profile.read_info_from_index
        build = lambda i: self.get_profile(ask(self._fid, i)[0])
        try:
            profiles = [build(iprof) for iprof in xrange(nprofiles)]
        except:
            raise MEDError("Could not retrieve profile info in %s." % self.name)
        return profiles
