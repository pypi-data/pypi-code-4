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
MED: Numerical parameters definition and handling interface.
"""
import numpy as np
from base import MEDFileComponents
import _parameter

class MEDParameter(MEDFileComponents):
    """
    Numerical parameter in a MED file.

    Parameters
    ----------
    medfile : MEDFile
        The MED file.
    name : str
        Parameters' name.
    value : numeric, optional
        Parameters' value. If value is None, the parameter is not actually
        created.
    desc : str, optional
        Description. The string must not be longer than COMMENT_SIZE.
    dtunit : str, optional
        Time unit. The string must not be longer than SNAME_SIZE.

    Attributes
    ----------
    medfile : MEDFile.
        The MED file.
    """
    def __init__(self, medfile, name, value=None, desc="", dtunit="",
                 **kwargs):
        super(MEDParameter, self).__init__(name=name, **kwargs)
        self.medfile = medfile
        if value is not None:
            _parameter.create(medfile._fid, self.name,
                              np.asarray(value).dtype, desc, dtunit)
            self.set_value(value)

    def set_value(self, value, numdt=None, numit=None, dt=None):
        """
        Set a parameter value.

        Parameters
        ----------
        value : numeric
            Parameter value.
        numdt : int, optional
            Time step index in the computation sequence.
        numit : int, optional
            Iteration index in the computation sequence.
        dt : float, optional
            Time stamp of specified time step.
        """
        vals = np.asarray(value)
        _parameter.write_value(self.medfile._fid, self.name, vals, numdt,
                               numit, dt)

    def get_info(self):
        """
        Get parameter info.
        """
        info = _parameter.read_info_from_name(self.medfile._fid, self.name)
        return dict(zip(['dtype', 'nstep', 'desc', 'dtunit'], info))

    def value(self, steps=None):
        """
        Return the parameters' value at time steps.

        Parameters
        ----------
        steps : sequence
            Time steps.

        Returns
        -------
        vals : recarray
            Parameter's value and computation step information (numdt,
            numit, dt).
        """
        dtype, nstep = map(self.get_info().get, ['dtype', 'nstep'])
        if steps is None:
            steps = xrange(nstep)
        vals = np.zeros(len(steps),
                        dtype=[('numdt', int), ('numit', int),
                               ('dt', float), ('value', dtype)])
        for i, csit in enumerate(steps):
            vals[i] = _parameter.read_value(self.medfile._fid, self.name,
                                           csit, dtype)
        return vals
