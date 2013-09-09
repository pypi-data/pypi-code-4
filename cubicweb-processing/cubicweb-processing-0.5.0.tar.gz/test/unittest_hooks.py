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


from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC

from cubes.processing.testing import ProcessingTCMixin, ChainingTestMixin


class UsesExecutableHookTC(ProcessingTCMixin, CubicWebTC):

    def setup_database(self):
        super(UsesExecutableHookTC, self).setup_database()
        ce = self.request().create_entity
        self.exe1 = self.exe
        self._add_iset_1(self.exe1)
        self._add_oset_1(self.exe1)
        self.exe2 = ce('Executable', name=u'e2')
        self._add_iset_2(self.exe2)
        self._add_oset_2(self.exe2)
        self.commit()

    def test_wiring_language(self):
        # test creation
        req = self.request()
        ce = req.create_entity
        runchain = ce('RunChain', uses_executable=(self.exe1, self.exe2))
        self.commit()
        self.assertEqual(len(self.runchain_wlang_def(runchain)['modules']), 2)
        # test edition
        req.execute('DELETE S uses_executable E WHERE S eid %(s)s, '
                    'E eid %(e)s', {'s': runchain.eid, 'e': self.exe1.eid})
        self.commit()
        self.assertEqual(len(self.runchain_wlang_def(runchain)['modules']), 1)
        # test deletion
        req.execute('DELETE RunChain S WHERE S eid %(s)s', {'s': runchain.eid})
        self.commit()


class ParameterOfHookTC(ProcessingTCMixin, CubicWebTC):

    def setup_database(self):
        super(ParameterOfHookTC, self).setup_database()
        ce = self.request().create_entity
        self._add_iset_1(self.exe)
        self._add_oset_1(self.exe)
        self.runchain = ce('RunChain', uses_executable=(self.exe,))
        self.commit()
        # check tests prerequisites
        fields = self.wlang_fields_by_module(self.runchain_wlang_def(self.runchain))
        self.assertEqual(len(fields), 1) # one exe
        self.assertEqual(len(fields[0][1]), 5) # 2 inputs, 3 outputs

    def test_input_parameter_of(self):
        '''Adding an input parameter to an executable should regenerate runchain's
        wiring language'''
        self.exe.add_input(u'pnew', u'String')
        self.commit()
        fields = self.wlang_fields_by_module(self.runchain_wlang_def(self.runchain))
        self.assertEqual(len(fields), 1)
        self.assertEqual(len(fields[0][1]), 6)

    def test_output_parameter_of(self):
        '''Adding an output parameter to an executable should regenerate runchain's
        wiring language'''
        self.exe.add_output(u'onew', u'String')
        self.commit()
        fields = self.wlang_fields_by_module(self.runchain_wlang_def(self.runchain))
        self.assertEqual(len(fields), 1)
        self.assertEqual(len(fields[0][1]), 6)


class InputParameterValueOrFromOutputRequiredTC(ChainingTestMixin, CubicWebTC):
    '''test hook part of the ParameterValue coherency checks
    -see also unittest_schema.py for constraint part-'''

    def test_value_required(self):
        'ParameterValue value is required when no link to an output is setup'
        ce = self.request().create_entity
        run1 = ce('Run', executable=self.exe1)
        with self.assertRaises(ValidationError) as cm:
            ce('ParameterValueFloat', param_def=self.idef1_f,
               value_of_run=run1)
            self.commit()
        self.assertExcMsg(cm, 'value is required for parameter "f"')

    def test_from_output_required(self):
        '''removing from_output relation is not possible when no value was
        specified'''
        pval = self.chaining_setup()
        with self.assertRaises(ValidationError) as cm:
            pval.cw_set(from_output=None)
            self.commit()
        self.assertExcMsg(cm, 'value is required for parameter "f"')

    def _file_pvalue(self, with_value=True):
        ce = self.request().create_entity
        exe = ce('Executable', name=u'e')
        pdef = exe.add_input(u'fp', u'File')
        self.commit()
        run = ce('Run', executable=exe)
        pval = self.new_file_pval(pdef, run, with_value=with_value)
        self.commit()
        return pval

    def test_file_value_required(self):
        pval = self._file_pvalue()
        with self.assertRaises(ValidationError) as ctm:
            pval.value.cw_delete()
            self.commit()
        self.assertExcMsg(ctm, 'value is required for parameter "fp"')

    def _file_odef_setup(self):
        ce = self.request().create_entity
        exe1 = ce('Executable', name=u'e1')
        odef = ce('ParameterDefinition',
                  name=u'fo',
                  value_type=u'File',
                  param_type=u'output',
                  parameter_of=exe1)
        self.commit()
        return ce('Run', executable=exe1), odef

    def test_file_value_from_output_required(self):
        run, odef = self._file_odef_setup()
        pval = self._file_pvalue(with_value=False)
        pval.cw_set(from_run=run, from_output=odef)
        self.commit()
        with self.assertRaises(ValidationError) as cm:
            pval.cw_set(from_output=None)
            self.commit()
        self.assertExcMsg(cm, 'value is required for parameter "fp"')


class RunChainingTC(ChainingTestMixin, CubicWebTC):

    def test_output_copy(self):
        '''When a Run receives an output value linked to a input value,
        the value is copied from the output into the input.
        '''
        pval = self.chaining_setup()
        ce = self.request().create_entity
        obj = ce('ParameterValueFloat',
                 value=3.7,
                 param_def=pval.from_output,
                 value_of_run=pval.from_run[0])
        self.commit()
        self.assertEqual(pval.value, obj.value)


class RunChainRunsGenerationHooksTC(CubicWebTC):

    def test_new_linked_wiring(self):
        self.skipTest('to be implemented soon')

    def test_updated_wiring(self):
        self.skipTest('to be implemented soon')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
