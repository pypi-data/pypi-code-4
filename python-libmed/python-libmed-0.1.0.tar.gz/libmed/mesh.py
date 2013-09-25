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
MED: Meshes definition and handling interface.
"""
import re

from base import MEDFileComponents
import _mesh
from _utils import MEDError

def nnodes_elements(etype):
    """ Number of nodes by element type. """
    m = re.match(r'[a-z]+(\d+)', etype)
    if m:
        return int(m.group(1))
    else:
        raise ValueError('Unsupported element type %s' % etype)

class MEDMesh(MEDFileComponents):
    """
    Mesh in a MED file.

    To retrieve an existing mesh in a MED file, simply supply its name. To
    create a new mesh, supply at least ``spacedim`` and ``meshdim`` and
    optionally the ``structured`` flag and a description comment ``desc``.
    """
    def __init__(self, medfile, name, spacedim=None, meshdim=None,
                 structured=False, desc=None, **kwargs):
        super(MEDMesh, self).__init__(name=name, **kwargs)
        self.medfile = medfile

        # mesh creation only if dims is provided
        if spacedim is not None and meshdim is not None:
            _mesh.create(self.medfile._fid, self.name, spacedim, meshdim,
                         structured, desc)
            _mesh.write_default_family(self.medfile._fid, self.name)

    def set_nodes(self, nodes, numdt=None, numit=None, dt=None):
        """
        Set nodes at a given computation sequence.

        Parameters
        ----------
        nodes : array
            Nodes as 2D array.
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.
        dt : float, optional
            Time stamp of specified time step.

        Notes
        -----
        Using the computation sequence parameters ``numdt``, ``numit`` and
        ``dt`` it is possible to create evolutive meshes. However one must
        first define an initial mesh by first adding nodes/elements without
        any sequence computation data (i.e. ``numdt``, ``numit``, ``dt``
        set to ``None``).
        """
        if _mesh.is_structured(self.medfile._fid, self.name):
            raise MEDError("Cannot write nodes coordinates for structured "
                           "mesh %s. Use set_grid() instead." % self.name)
        _mesh.write_nodes_coord(self.medfile._fid, self.name, nodes, numdt,
                                numit, dt)

    def set_grid(self, *coords, **kwargs):
        """
        Set coordinates of a grid in structured mesh.

        Parameters
        ----------
        coor1[, coor2[, ...]] : arrays
            Coordinates for each axes.
        grid_type : str
            Type structured grid: cartesian or polar.
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.
        dt : float, optional
            Time stamp of specified time step.

        Notes
        -----
        Using the computation sequence parameters ``numdt``, ``numit`` and
        ``dt`` it is possible to create evolutive meshes. However one must
        first define an initial mesh by first adding nodes/elements without
        any sequence computation data (i.e. ``numdt``, ``numit``, ``dt``
        set to ``None``).
        """
        if not _mesh.is_structured(self.medfile._fid, self.name):
            raise MEDError("Cannot write grid coordinates for unstructured "
                           "mesh %s. Use set_nodes() instead." % self.name)
        grid_type = kwargs.get("grid_type", "cartesian")
        numdt, numit, dt = map(kwargs.get, ["numdt", "numit", "dt"])
        _mesh.write_grid_type(self.medfile._fid, self.name, grid_type)
        for axis, coor in enumerate(coords):
            _mesh.write_grid_coord(self.medfile._fid, self.name, axis,
                                   coor, numdt=numdt, numit=numit, dt=dt)

    def get_info(self):
        """
        Given its name, return information about a mesh as a dictionnary
        with fields:

        - space dimension
        - mesh dimension
        - mesh type (structured or unstructured)
        - mesh description string
        - sorting sequence type
        - number of time step
        - type coordinate frame
        - axis names
        - axis units
        """
        info = _mesh.read_info_from_name(self.medfile._fid, self.name)
        dinfo = dict(zip(('spacedim', 'meshdim', 'meshtype', 'desc',
                         'sort_seq', 'nstep', 'axistype', 'axisname',
                         'axisunit', 'dtunit'), info))
        if dinfo['meshtype'] == 'structured':
            dinfo['gridtype'] = _mesh.read_grid_type(self.medfile._fid,
                                                     self.name)
        return dinfo

    def nodes(self, numdt=None, numit=None, order='C'):
        """
        Retrieve mesh nodes.

        Parameters
        ----------
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.
        order : str
            Data contiguity of the resulting array.

        Returns
        -------
        nodes : array
            Nodes' coordinates.
        """
        if self.get_info()['meshtype'] == 'structured':
            return _mesh.read_grid_coord(self.medfile._fid, self.name,
                                         numdt, numit)
        else:
            return _mesh.read_nodes_coord(self.medfile._fid, self.name,
                                          numdt, numit, order)

    def add_elements(self, etype, connects, numdt=None, numit=None, dt=None):
        """
        Add elements to a mesh.

        Parameters
        ----------
        etype : str
            Element type.
        connects : array
            Connectivity.
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.
        dt : float, optional
            Time stamp of specified time step.
        """
        _mesh.write_elements_connect(self.medfile._fid, self.name, etype,
                                     connects, numdt, numit, dt)

    def elements_types(self, numdt=None, numit=None):
        """
        Lists types of elements in a mesh.
        """
        nelm_types = _mesh.read_number_of_elements(self.medfile._fid,
                                                   self.name)
        elm_types = []
        for i in xrange(nelm_types):
            geotype = _mesh.read_entity_info_from_index(self.medfile._fid,
                                                        self.name, 'element',
                                                        i, numdt, numit)[0]
            elm_types.append(geotype)
        return elm_types

    def elements(self, etype=None, numdt=None, numit=None, order='C'):
        """
        Get elements of the mesh.

        Parameters
        ----------
        etype : str, optional
            The type of element to retrieve. If `etype is None` a dict with
            all elements by type is returned.
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.
        order : str, optional
            Data contiguity.

        Returns
        -------
        elms : array or dict of arrays
            Elements' connectivity.
            If only one ``etype`` is specified, the elements connectivity
            of that type. Otherwise a dict of elements connectivity by
            type.
        """
        if etype is None:
            etypes = self.elements_types()
            retall = True
        else:
            etypes = [etype]
            retall = False
        elms = dict()
        for etype in etypes:
            nelm = _mesh.read_number_of_elements(self.medfile._fid,
                                                 self.name, etype)
            if nelm == 0: # no element of this type
                elms[etype] = None
                continue
            nnodes = nnodes_elements(etype)
            elms[etype] = _mesh.read_elements_connect(self.medfile._fid,
                                                      self.name, etype,
                                                      nelm, nnodes,
                                                      numdt=numdt,
                                                      numit=numit,
                                                      order=order)
        if retall:
            return elms
        else:
            return elms.values()[0]
