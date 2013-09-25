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
MED: Fields definition and handling interface.
"""
import numpy as np
from base import MEDFileComponents
import _field
import _profile
from profile import MEDProfile

class MEDField(MEDFileComponents):
    """
    Field in a MED file.
    """
    def __init__(self, medfile, name, meshname, ncomp=None, dtype=None,
                 compnames=None, units=None, **kwargs):
        super(MEDField, self).__init__(name=name, **kwargs)
        self.medfile = medfile
        self.meshname = meshname

        # create the field only if values are provided
        if ncomp is not None and dtype is not None:
            if compnames is None:
                compnames = []
            if units is None:
                units = []
            dtunit = ""
            _field.create(self.medfile._fid, self.name, self.meshname,
                          ncomp, dtype, compnames, units, dtunit)

    def set_values(self, entity_type, values, profile=None,
                   numdt=None, numit=None, dt=None):
        """
        Add values to a field for a given entity type.

        Parameters
        ----------
        entity_type : str
            Type of mesh entity. For nodal fields, use 'node'. Otherwise,
            use the type of elements (e.g. 'tria3', 'hexa8').
        values : array
            Field values as a 2D NumPy array.
        profile : array, optional
            Sequence of entity indices for which to define field values.
            Use this option when the field does not have values for all
            entities on which it applies. This will create a specific
            *profile* in the MED file.
            This option is subject to changes.
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.
        dt : float, optional
            Time stamp of specified time step.
        """
        if values.ndim == 1:
            values = values[:, np.newaxis]
        if profile is None:
            _field.write_values(self.medfile._fid, self.name, entity_type,
                                values, numdt, numit, dt)
        else:
            if profile.shape[0] != values.shape[0]:
                raise ValueError("The shapes of values and profile do not "
                                 "match")
            # define a new profile, accounting for existing ones
            nprof = _profile.read_number_of_profiles(self.medfile._fid,
                                                     self.medfile.name)
            p = MEDProfile(self.medfile, "profile #%d for %s in field %s" %
                           (nprof+1, entity_type, self.name), profile)
            # write field values using this profile
            _field.write_values_with_profile(self.medfile._fid, self.name,
                                             entity_type, values, p.name,
                                             numdt, numit, dt)

    def get_info(self):
        """
        Get field info.
        """
        info = _field.read_info_from_name(self.medfile._fid, self.name)
        return dict(zip(['meshname', 'compnames', 'units', 'nstep',
                         'dtype', 'on_local_mesh', 'dtunit'], info))

    def entities(self, numdt=None, numit=None):
        """
        List entities on which the field applies.

        Parameters
        ----------
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.

        Returns
        -------
        ents : list
            List of mesh entities.
        """
        msh = self.medfile.get_mesh(self.meshname)
        # use read_number_of_values_with_profile with first profile instead
        # of read_number_of_values which fails if there's a profile
        filter_func = lambda x: \
            _field.read_number_of_values_with_profile(self.medfile._fid,
                                                      self.name, x, 1, numdt,
                                                      numit)
        return filter(filter_func, ['node'] + msh.elements_types())

    def values(self, etype=None, numdt=None, numit=None, dt=None, order='C'):
        """
        Retrieve field values by mesh entities.

        Parameters
        ----------
        etypes : str, optional
            Type of mesh entity to retrive the field values of. For nodal
            fields, use 'node'. Otherwise, use the type of elements (e.g.
            'tria3', 'hexa8'). If None, all mesh entities with field values
            with be returned.
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.
        dt : float, optional
            Time stamp of specified time step.
        order : str, optional
            Data contiguity of the resulting array.

        Returns
        -------
        vals : array or dict
            Fields values.
        """
        if etype is None:
            etypes = self.entities()
            retall = True
        else:
            etypes = [etype]
            retall = False
        values = dict()
        for etype in etypes:
            (nprofiles,
             defaultprof,
             defaultloc) = _field.read_number_of_profiles(self.medfile._fid,
                                                          self.name, etype,
                                                          numdt=numdt,
                                                          numit=numit, dt=dt)
            if nprofiles == 1 and defaultprof == "":
                values[etype] = _field.read_values(self.medfile._fid,
                                                   self.name, etype,
                                                   numdt=numdt, numit=numit,
                                                   dt=dt, order=order)
            else:
                for iprof in xrange(nprofiles):
                    values[etype] = \
                        _field.read_values_with_profile(self.medfile._fid,
                                                        self.name, etype,
                                                        iprof + 1,
                                                        numdt=numdt,
                                                        numit=numit, dt=dt,
                                                        order=order)
        if retall:
            return values
        else:
            return values.values()[0]
