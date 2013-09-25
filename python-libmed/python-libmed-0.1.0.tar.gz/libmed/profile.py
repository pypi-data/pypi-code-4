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
MED: Profiles definition and handling interface.
"""
import numpy as np
from base import MEDFileComponents
import _profile

class MEDProfile(MEDFileComponents):
    """
    Profile in a MED file.

    Parameters
    ----------
    medfile : MEDFile
        The MED file.
    name : str
        Parameters' name.
    indices : sequence of int, optional
        Indices associated with profile to be created.
        If None, the profile is not created but just read.

    Attributes
    ----------
    medfile : MEDFile.
        The MED file.
    """
    def __init__(self, medfile, name, indices=None, **kwargs):
        super(MEDProfile, self).__init__(name=name, **kwargs)
        self.medfile = medfile
        if indices is not None:
            _profile.write_profile(medfile._fid, self.name,
                                   np.array(indices, dtype='int32'))

    def get_info(self):
        """
        Get profile info.
        """
        nprofiles = _profile.read_number_of_profiles(self.medfile._fid,
                                                     self.medfile.name)
        for iprof in xrange(nprofiles):
            name, size = _profile.read_info_from_index(self.medfile._fid,
                                                       iprof)
            if name == self.name:
                break
        return {'name': name, 'size': size}

    def indices(self, order='C'):
        """
        Retrieve profile' indices.

        Parameters
        ----------
        order : str, optional
            Data contiguity.

        Returns
        -------
        ind : array of int
            Profile array of indices.
        """
        return _profile.read_indices_from_name(self.medfile._fid, self.name,
                                               order=order)
