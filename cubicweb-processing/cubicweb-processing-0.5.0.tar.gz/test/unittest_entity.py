# copyright 2012-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from json import loads

from cubicweb.devtools.testlib import CubicWebTC

from cubes.processing.testing import RunChainTCMixin


def replace_entities_by_eids(xvaluedict):
    return dict((k, getattr(v, 'eid', v))
                for k, v in xvaluedict.iteritems())

class ProcessingRunChainTC(RunChainTCMixin, CubicWebTC):

    def test_runchain_autoname(self):
        self.assertEqual(self.runchain.name, u'<unnamed runchain %s>' % self.runchain.eid)

    def test_wiring_language(self):
        wlang = self.runchain_wlang_def(self.runchain)
        self.assertEqual(len(wlang['modules']), len(self.runchain.uses_executable))
        expected = [
            (self.exe1.dc_title(), [
                ('i11', 'number'), ('i12', 'string'),
                ('o11', 'number'), ('o12', 'string'), ('o13', 'number')]),
            (self.exe0.dc_title(), [
                ('i1', u'file'), ('i2', 'number'),
                ('o1', u'file'), ('o2', 'number')]),
            (self.exe2.dc_title(), [
                ('i21', 'number'), ('i22', 'number'), ('i23', 'string'),
                ('o21', 'string'), ('o22', 'number')]),
            ]
        self.assertEqual(self.wlang_fields_by_module(wlang), expected)

    def test_runs_from_wiring(self):
        runs = dict((run.exe.eid, run) for run in self.runchain.has_runs)
        self.assertEqual(len(runs), 3)
        run0 = runs[self.exe.eid]
        run1 = runs[self.exe2.eid]
        run2 = runs[self.exe0.eid]
        self.assertEqual(run0.ivalue_dict, dict(i11=1.1, i12=u'1.2'))
        self.assertEqual(run1.ivalue_dict['i23'], u'i23 value')
        self.assertEqual(run1.ivalue_entity('i21').from_run[0].eid, run0.eid)
        self.assertEqual(run1.ivalue_entity('i21').from_output[0].name, 'o11')
        self.assertEqual(run1.ivalue_entity('i22').from_run[0].eid, run0.eid)
        self.assertEqual(run1.ivalue_entity('i22').from_output[0].name, 'o13')
        self.assertEqual(run2.ivalue_dict['i2'], 1.0)

        self.assertFalse(run0.output_values)
        self.assertFalse(run1.output_values)
        self.assertFalse(run2.output_values)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
