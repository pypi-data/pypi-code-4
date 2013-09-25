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
libmed: manipulation `MED`_ files
=================================

The ``libmed`` package provides a wrapper to the `libmed`_ C library. The API
consists of pure Python modules that allow manipulation of fundamental
components of a MED file (the file itself, meshes, fields, numerical
parameters, etc.). The main entry point is the ``MEDFile`` class which
provides an interface to a MED file and to its components.

.. _MED: http://www.salome-platform.org/about/med
.. _libmed: http://www.salome-platform.org/about/med

Examples
--------

Create a MED file, set its description comment string:

>>> with MEDFile('myfile.med', 'w') as fw:
...     fw.comment = "This is a MED file."

Open it in read-only mode:

>>> with MEDFile('myfile.med', 'r') as fr:
...     print fr.comment
This is a MED file.

Add simple 2D mesh with nodes and elements:

>>> import numpy as np
>>> with MEDFile('myfile.med', 'w+') as f:
...     m = f.add_mesh(name='Simple mesh', spacedim=2, meshdim=2)
...     m.set_nodes(np.array([[0, 0], [0, 1],
...                           [1, 0], [1, 1],
...                           [2, 0], [2, 1.]]))
...     m.add_elements('Quad4', np.array([[1, 2, 3, 4],
...                                       [3, 4, 5, 6]]))
...     print m.nodes(), m.elements()
[[ 0.  0.]
 [ 0.  1.]
 [ 1.  0.]
 [ 1.  1.]
 [ 2.  0.]
 [ 2.  1.]] {'quad4': array([[1, 2, 3, 4],
       [3, 4, 5, 6]])}

Add a cartesian structured mesh:

>>> with MEDFile('myfile.med', 'w+') as f:
...     ms = f.add_mesh(name='structured mesh', structured=True,
...                     spacedim=3, meshdim=3)
...     ms.set_grid(np.arange(2), np.arange(3), np.arange(4))
...     print ms.nodes()
[array([ 0.,  1.]), array([ 0.,  1.,  2.]), array([ 0.,  1.,  2.,  3.])]

Add a scalar field:
>>> with MEDFile('myfile.med', 'w+') as f:
...     m = f.get_mesh('Simple mesh')
...     fd = f.add_field('Random field', m.name, ncomp=1,
...                      dtype=np.dtype('float64'))
...     fd.set_values('quad4', np.array([[0.1], [2.58]]))

Read the field:
>>> with MEDFile('myfile.med', 'r') as f:
...     print f.fields()[0].values()
{'quad4': array([[ 0.1 ],
       [ 2.58]])}
"""
from file import *
from _utils import *
