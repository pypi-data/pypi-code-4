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

from unittest import TestCase, main
import tempfile
import shutil
import os
import os.path as osp
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal

import libmed

TEST_DATADIR = osp.join(osp.dirname(osp.abspath(__file__)), 'data')

class _MEDTest(TestCase):
    " Base test class "
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="temp-med-")
        self.pwd = osp.abspath(os.curdir)
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.pwd)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

class _DocTestMixin(object):
    def test_doctests(self):
        import doctest
        nfailures = doctest.testmod(self.mod)[0]
        self.assertEqual(nfailures, 0, "%d doctest(s) failed." % nfailures)

class TestDocTests(_DocTestMixin, _MEDTest):
    mod = libmed

class TestMEDString(_DocTestMixin, TestCase):
    mod = libmed._medtypes

class TestMEDFile(_MEDTest):
    " Tests for MED file manipulation "
    def test_openclose_success(self):
        " Check open/close operation "
        with libmed.MEDFile('a', 'w') as f:
            self.assertEqual(f.name, 'a')
            self.assertEqual(f.mode, 'w')
            self.assertFalse(f.closed)
        self.assertTrue(osp.exists('a'))

    def test_open_read_missing(self):
        " Check that opening a MED file read-only raises an error "
        self.assertRaises(libmed.MEDIOError, libmed.MEDFile, 'z', 'r')

    def test_comment(self):
        " Check various operations on comment "
        with libmed.MEDFile('c', 'w') as f:
            self.assertEqual(f.comment, "")
            f.comment = "a"*301
            self.assertEqual(f.comment, "a"*200)
            f.comment = "b"
            self.assertEqual(f.comment, "b")
            f.comment = "b "+ chr(0) * 4
            self.assertEqual(f.comment, "b")
            f.comment = "b\0c"
            self.assertEqual(f.comment, "b")

    def test_version(self):
        " Check that file MED version and MED library version are the same "
        with libmed.MEDFile('v', 'w') as f:
            self.assertEqual(f.med_version, libmed.medlib_version())

    def test_compatibility(self):
        " Check incompatibility with an old MED file "
        self.assertRaises(libmed.MEDVersionError, libmed.MEDFile,
                          osp.join(TEST_DATADIR, 'legacy.med'))

    def test_unusable_closed_file(self):
        " Test that operation on closed files are disabled "
        with libmed.MEDFile('u', 'w') as f:
            pass
        self.assertRaises(libmed.MEDIOError, f.close)

class _MedTestWith2DMesh(_MEDTest):
    def mesh2d(self):
        " A 2D mesh "
        # nodes coordinates
        coord = np.array([(2., 1.), (7., 1.), (12., 1.), (17., 1.),
                          (22., 1.), (2., 6.), (7., 6.), (12., 6.),
                          (17., 6.), (22., 6.), (2., 11.), (7., 11.),
                          (12., 11.), (17., 11.), (22., 11.)])
        # quad elements
        connect4 = np.array([(3, 4, 9, 8), (4, 5, 10, 9),
                             (15, 14, 9, 10), (13, 8, 9, 14)])
        # tria elements
        connect3 = np.array([(1, 7, 6), (2, 7, 1), (3, 7, 2),
                             (8, 7, 3), (13, 7, 8), (12, 7, 13),
                             (11, 7, 12), (6, 7, 11)])
        return coord, connect3, connect4

class TestMEDMesh(_MedTestWith2DMesh):
    " Tests for MED mesh manipulation "
    def _test_mesh_contiguity(self, order):
        """
        Base test for C or Fortran contiguous meshes.

        Meshes are created using specified order and then read using the
        other one.
        """
        coord, connect3, connect4 = self.mesh2d()
        with libmed.MEDFile('msh.med', 'w') as f:
            mc = f.add_mesh(name=order +" mesh",
                            spacedim=2, meshdim=2,
                            desc="Nodes coordinates %s contiguous." % order)
            mc.set_nodes(np.asarray(coord, order=order))
            mc.add_elements('Quad4', np.asarray(connect4, order=order))
            mc.add_elements('tria3', np.asarray(connect3, order=order))
        # read the meshes
        with libmed.MEDFile('msh.med', 'r') as f:
            mc = f.get_mesh(order +" mesh")
            self.assertEqual(mc.get_info()['meshtype'], 'unstructured')
            self.assertEqual(mc.elements_types(), ['quad4', 'tria3'])
            order = {'C': 'F', 'F': 'C'}[order]
            assert_array_equal(mc.nodes(order=order), coord)
            assert_array_equal(mc.elements(order=order)['quad4'],
                               connect4)
            assert_array_equal(mc.elements('tria3', order=order),
                               connect3)

    def test_C_mesh(self):
        " Test C-contiguous mesh "
        self._test_mesh_contiguity('C')

    def test_Fortran_mesh(self):
        " Test Fortran-contiguous mesh "
        self._test_mesh_contiguity('F')

    def test_mesh_int(self):
        " Test mesh with integer coordinates "
        nodes = np.array([[1, 2]], dtype=int)
        with libmed.MEDFile('myfile.med', 'w') as f:
            m = f.add_mesh(name='mesh with int coordinates', spacedim=2,
                           meshdim=2)
            m.set_nodes(nodes)
            assert_array_equal(m.nodes(), nodes)

    def test_mesh_sequence(self):
        " Test mesh with varying sequence "
        nodes = [np.array([[0, 0], [0, 1], [1, 0], [1, 1]])]
        elms = [np.array([[0, 1, 2], [1, 2, 3]])]
        elms1 = np.array([[0, 1, 3], [0, 2, 3]])
        nnodes, dim = nodes[0].shape
        ndt = 4
        with libmed.MEDFile('seq-mesh.med', 'w') as f:
            m = f.add_mesh(name='mesh', spacedim=dim, meshdim=dim)
            m.set_nodes(nodes[0])
            m.add_elements('tria3', elms[0])
            # move nodes randomly
            for idt in xrange(ndt):
                nodes.append(nodes[0] + np.random.rand(nnodes, dim))
                m.set_nodes(nodes[idt+1], numdt=idt)
                # change elements for some time steps
                if idt >= ndt - 2:
                    elms.append(elms1)
                    m.add_elements('tria3', elms[idt+1], numdt=idt)
                else:
                    elms.append(elms[0])
        with libmed.MEDFile('seq-mesh.med', 'r') as f:
            m = f.meshes()[0]
            assert_array_equal(nodes[0], m.nodes())
            assert_array_equal(elms[0], m.elements('tria3'))
            for idt in xrange(ndt):
                assert_array_equal(nodes[idt+1], m.nodes(numdt=idt))
                assert_array_equal(elms[idt+1], m.elements('tria3', numdt=idt))

    def test_structured_cartesian(self):
        " Test structured cartesian mesh "
        # X, Y, Z grid coordinates, mixing int and float
        coords = (np.arange(4), np.arange(3), np.arange(1, 3, 0.2))
        with libmed.MEDFile('struct-mesh.med', 'w') as f:
            m = f.add_mesh(name='struct. mesh', spacedim=3, meshdim=3,
                           structured=True)
            # writting nodes coordinates should fail
            self.assertRaises(libmed.MEDError,
                              m.set_nodes, np.random.rand(2, 3, 4))
            m.set_grid(*coords)
        with libmed.MEDFile('struct-mesh.med', 'r') as f:
            m = f.meshes()[0]
            self.assertEqual(m.get_info()['meshtype'], 'structured')
            self.assertEqual(m.get_info()['gridtype'], 'cartesian')
            for c, cr in zip(m.nodes(), coords):
                assert_array_equal(c, cr)


class TestMEDField(_MedTestWith2DMesh):
    " Tests for MED field manipulation "
    def _test_fields_contiguity(self, order):
        """
        Base test for C or Fortran contiguous fields.

        Fields are created using specified order and then read using the
        other one.
        """
        # 2D mesh
        coord, connect3, connect4 = self.mesh2d()
        # field values for each entity type
        fentities = ['node', 'tria3', 'quad4']
        efields = [10 * (1 - np.random.rand(coord.shape[0], 2)),
                   100 * (1 - np.random.rand(connect3.shape[0], 2)),
                   1000 * (1 - np.random.rand(connect4.shape[0], 2))]
        # names and units of components
        compnames, units = ['r1', 'r2'], ['u1', 'u2']
        fields = [(k, np.asarray(v, order=order))
                  for k, v in zip(fentities, efields)]
        # create MED file with a mesh and a field
        mesh_name = '2D mesh with tria and quad.'
        field_name = 'Random field, %s contiguous' % order
        with libmed.MEDFile('fld.med', 'w') as f:
            m = f.add_mesh(name=mesh_name, spacedim=2, meshdim=2)
            m.add_elements('tria3', connect3)
            m.add_elements('quad4', connect4)
            # create field with nodal values
            fd = f.add_field(field_name, m.name, ncomp=2,
                             dtype=np.dtype('float'), compnames=compnames,
                             compunits=units)
            # add values at elements
            for enttype, val in fields:
                fd.set_values(enttype, val)
        # read the field in the MED file, check consistency with input data
        with libmed.MEDFile('fld.med', 'r') as f:
            order = {'C': 'F', 'F': 'C'}[order]
            fd = f.get_field(field_name, mesh_name)
            fd_info = fd.get_info()
            cnames, cunits = fd_info['compnames'], fd_info['units']
            self.assertEqual(cnames, compnames)
            self.assertEqual(cunits, units)
            self.assertEqual(sorted(fd.entities()), sorted(fentities))
            for fn, ff in zip(fentities, efields):
                assert_array_equal(fd.values(fn, order=order), ff,
                                   '%s fields do not match' % fn)

    def test_C_fields(self):
        " Test fields with C contiguity "
        self._test_fields_contiguity('C')

    def test_Fortran_fields(self):
        " Test fields with Fortran contiguity "
        self._test_fields_contiguity('F')

    def test_field_int32(self):
        " Test scalar field with int32 values "
        coord, connect3 = self.mesh2d()[:2]
        field_int = np.asarray(np.random.random_integers(1, 10,
                                                         coord.shape[0]),
                               dtype=np.dtype('int32'))
        mesh_name = 'mesh'
        field_name = 'nodal integer field'
        with libmed.MEDFile('fld.med', 'w') as f:
            m = f.add_mesh(name=mesh_name, spacedim=2, meshdim=2)
            m.set_nodes(coord)
            m.add_elements('tria3', connect3)
            fd = f.add_field(field_name, m.name, ncomp=1,
                             dtype=np.dtype('int32'))
            fd.set_values('node', field_int)
        with libmed.MEDFile('fld.med', 'r') as f:
            fd = f.get_field(field_name, mesh_name)
            assert_array_equal(fd.values('node').ravel(), field_int)

    def test_field_structured_mesh(self):
        " Test field on a structured mesh "
        dims, fdim = (3, 2), 2
        fvals = np.random.rand(sum(dims), 2)
        with libmed.MEDFile('field+structmesh.med', 'w') as f:
            m = f.add_mesh('smesh', spacedim=2, meshdim=2, structured=True)
            m.set_grid(*map(np.arange, dims))
            fd = f.add_field('field on struct. mesh', m.name, ncomp=2,
                             dtype=np.dtype('float'))
            fd.set_values('node', fvals)
        with libmed.MEDFile('field+structmesh.med', 'r') as f:
            fd = f.fields()[0]
            assert_array_almost_equal(fd.values()['node'], fvals)

    def test_field_profile(self):
        " Test field with profile "
        coord, connect3 = self.mesh2d()[:2]
        mesh_name = 'mesh'
        field_name = 'nodal field with profile'
        nodes_in_prof = np.array([2, 4, 7, 11])
        field_on_all = np.random.random((coord.shape[0], 1))
        field_with_prof = np.random.random((nodes_in_prof.shape[0], 2))
        with libmed.MEDFile('field+profile.med', 'w') as f:
            m = f.add_mesh(mesh_name, spacedim=2, meshdim=2)
            m.set_nodes(coord)
            m.add_elements('tria3', connect3)
            fd = f.add_field(field_name, m.name, ncomp=2,
                             dtype=field_with_prof.dtype)
            fd.set_values('node', field_with_prof, profile=nodes_in_prof)
            fe = f.add_field('another field, on all entities', m.name,
                             ncomp=1, dtype=np.dtype('float'))
            fe.set_values('node', field_on_all)
        with libmed.MEDFile('field+profile.med', 'r') as f:
            fe, fd = f.fields()
            assert_array_almost_equal(fd.values('node'),
                                      field_with_prof)
            assert_array_almost_equal(fe.values()['node'], field_on_all)

class TestMEDparameter(_MEDTest):
    " Tests for MED numerical parameter manipulation "
    def test_parameter(self):
        " Test parameter "
        pars = {'a': 1, 'b': -0.2}
        with libmed.MEDFile('mpar.med', 'w') as f:
            for n, v in pars.iteritems():
                f.add_parameter(n, v)
        with libmed.MEDFile('mpar.med', 'r') as f:
            for p in f.parameters():
                self.assertEqual(p.value([0])['value'], pars[p.name])

class TestMEDProfile(_MEDTest):
    def test_profile(self):
        " Test profile "
        prof = {'profile 1': np.random.random_integers(1, 10, 4),
                'profile 2': np.random.random_integers(1, 10, 4)}
        with libmed.MEDFile('mprof.med', 'w') as f:
            for pname, pval in prof.iteritems():
                f.add_profile(pname, pval)
        with libmed.MEDFile('mprof.med', 'r') as f:
            for p in f.profiles():
                assert_array_equal(p.indices(), prof[p.name])

if __name__ == '__main__':
    main()
