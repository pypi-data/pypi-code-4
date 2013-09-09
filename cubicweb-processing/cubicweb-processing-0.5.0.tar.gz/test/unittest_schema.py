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
"Unittests for the schema of processing cube"

from contextlib import contextmanager
from json import dumps

from cubicweb import ValidationError, Unauthorized, Binary
from cubicweb.schema import ERQLExpression
from cubicweb.devtools.testlib import CubicWebTC

from cubes.processing.testing import ProcessingTCMixin, ChainingTestMixin


class ParameterDefinitionSchemaTC(ProcessingTCMixin, CubicWebTC):

    def test_pdef_name_validity(self):
        'check parameter definition name restrictions'
        with self.assertRaises(ValidationError) as ctm:
            self.exe.add_input(name=u'p 1', value_type=u'Float')
        self.assertExcMsg(ctm, ("doesn't match the '^[a-zA-Z0-9_]+$' "
                                "regular expression"))

    def test_pdef_unique(self):
        'same parameter definition name for same executable is invalid'
        i1 = self.exe.add_input(name=u'i1', value_type=u'Float')
        with self.assertRaises(ValidationError) as ctm:
            self.exe.add_input(name=i1.name, value_type=i1.value_type)
            self.commit()
        self.assertExcMsg(ctm, 'parameter name is already used')


class ParameterValueSchemaTC(ProcessingTCMixin, CubicWebTC):

    def setup_database(self):
        super(ParameterValueSchemaTC, self).setup_database()
        self.idef = self.exe.add_input(u'p', u'Float')
        self.commit()

    def test_wrong_pval_type(self):
        'cannot assign a wrong type ParameterValue'
        run = self.request().create_entity('Run', executable=self.exe)
        with self.assertRaises(ValidationError):
            self.request().create_entity('ParameterValueString',
                                         param_def=self.idef,
                                         value=u'coucou',
                                         value_of_run=run)
            self.commit()

    def set_owner(self, user, *entities):
        for entity in entities:
            entity.cw_set(owned_by=user)

    def test_pval_perms(self):
        'cannot modify a ParameterValue if linked Run cannot be modified'
        # we use a non manager user to test: set him as owner of objects
        self.set_owner(self.create_user(self.request(), 'user'),
                       self.exe, self.idef)
        self.commit()
        # actual test
        self.login('user')
        # - add a Run with a parameter value
        with self.session.allow_all_hooks_but('processing.test'):
            run = self.request().create_entity('Run', executable=self.exe)
            run[self.idef.name] = 1.
            self.commit()
        # - check it can be modified for now
        run[self.idef.name] = 2.
        self.commit()
        # - make the run not modifiable
        with self.temporary_permissions((self.schema['Run'], dict(update=()))):
            with self.assertRaises(Unauthorized):
                run[self.idef.name] = 4.
                self.commit()


class ChainingSetupTC(ChainingTestMixin, CubicWebTC):

    def assertConstraintCrashes(self, msg):
        with self.assertRaises(ValidationError) as cm:
            self.commit()
        self.assertTrue(str(cm.exception).endswith(msg), str(cm.exception))

    def test_from_run_same_type(self):
        '''input parameter cannot be copied from a run without an output
        parameter of the same type'''
        ce = self.request().create_entity
        run_no_param = ce('Run', executable=self.exe)
        run1 = ce('Run', executable=self.exe1)
        ce('ParameterValueFloat', param_def=self.idef1_f, value=1.,
           value_of_run=run1, from_run=run_no_param)
        self.assertConstraintCrashes('specified run has no output parameter of '
                                     'the right type')

    def test_from_output_same_type(self):
        '''An input parameter definition cannot be copied from an output
        parameter with a different type'''
        ce = self.request().create_entity
        run0 = ce('Run', executable=self.exe0)
        run1 = ce('Run', executable=self.exe1)
        ce('ParameterValueFloat', param_def=self.idef1_f, value=1.,
           value_of_run=run1, from_run=run0, from_output=self.odef0_s)
        self.assertConstraintCrashes('copied output parameter has wrong value '
                                     'type')

    def test_from_output_same_run(self):
        '''An input parameter definition cannot be copied from an output
        parameter not related to the chained run'''
        ce = self.request().create_entity
        o_param_other_f = self.exe.add_output(u'f', u'Float')
        self.commit()
        run_other = ce('Run', executable=self.exe)
        run0 = ce('Run', executable=self.exe0)
        self.commit()
        run1 = ce('Run', executable=self.exe1)
        pval1_f = ce('ParameterValueFloat', param_def=self.idef1_f, value=1.,
                     value_of_run=run1, from_run=run0,
                     from_output=o_param_other_f)
        self.assertConstraintCrashes('copied output parameter is unrelated to '
                                     'source run')


class RunSchemaTC(ProcessingTCMixin, CubicWebTC):

    def test_input_values_pdef_exists_ok(self):
        'can add parameter if it corresponds to a param def of the executable'
        ce = self.request().create_entity
        p = self.exe.add_input(u'p', u'Float')
        self.commit()
        run = ce('Run', executable=self.exe)
        run[p.name] = 1.
        self.commit()

    def test_input_values_pdef_exists_error(self):
        '''cannot add parameter value which does not correspond to a parameter
        definition of the executable'''
        ce = self.request().create_entity
        exe2 = ce('Executable', name=u'e2')
        pexe2 = exe2.add_input(u'p', u'Float')
        self.commit()
        with self.assertRaises(ValidationError) as ctm:
            run = ce('Run', executable=self.exe)
            ce('ParameterValueFloat', param_def=pexe2, value=1.,
               value_of_run=run)
            self.commit()
        self.rollback()
        self.assertExcMsg(ctm,
                          'cannot find such a parameter for this executable')

    def test_executable_constraint(self):
        '''cannot link run to executable with param defs without defining
        corresponding param values'''
        ce = self.request().create_entity
        self.exe.add_input(u'p', u'Float')
        self.commit()
        with self.assertRaises(ValidationError) as ctm:
            ce('Run', executable=self.exe)
            self.commit()
        self.rollback()
        self.assertExcMsg(ctm, 'missing input parameter values')

    def test_input_values_unique(self):
        'cannot add 2 input param values for the same definition on same run'
        ce = self.request().create_entity
        p = ce('ParameterDefinition',
               name=u'p',
               value_type=u'Float',
               param_type=u'input',
               parameter_of=self.exe)
        self.commit()
        run = ce('Run', executable=self.exe)
        ce('ParameterValueFloat', param_def=p, value=1., value_of_run=run)
        self.commit()
        with self.assertRaises(ValidationError) as ctm:
            ce('ParameterValueFloat', param_def=p, value=1., value_of_run=run)
            self.commit()
        self.assertExcMsg(ctm, 'this parameter has several values')

    def test_output_values_odef_exists_ok(self):
        '''can add output parameter value if it corresponds to an output
        parameter definition of the executable'''
        ce = self.request().create_entity
        p = ce('ParameterDefinition',
               name=u'p',
               value_type=u'Float',
               param_type=u'output',
               parameter_of=self.exe)
        self.commit()
        run = ce('Run', executable=self.exe)
        ce('ParameterValueFloat', param_def=p, value=1., value_of_run=run)
        self.commit()

    def test_output_values_odef_exists_error(self):
        '''cannot add an output parameter value which does not correspond to an
        output parameter definition of the executable'''
        ce = self.request().create_entity
        exe2 = ce('Executable', name=u'e2')
        pexe2 = ce('ParameterDefinition',
                   name=u'p',
                   value_type=u'Float',
                   param_type=u'output',
                   parameter_of=exe2)
        self.commit()
        with self.assertRaises(ValidationError) as ctm:
            run = ce('Run', executable=self.exe)
            ce('ParameterValueFloat', param_def=pexe2, value=1.,
               value_of_run=run)
            self.commit()
        self.rollback()
        self.assertExcMsg(ctm,
                          'cannot find such a parameter for this executable')

    def test_output_values_unique(self):
        'cannot add 2 output param values for the same definition on same run'
        ce = self.request().create_entity
        p = ce('ParameterDefinition',
               name=u'p',
               value_type=u'Float',
               param_type=u'output',
               parameter_of=self.exe)
        self.commit()
        run = ce('Run', executable=self.exe)
        ce('ParameterValueFloat', param_def=p, value=1., value_of_run=run)
        self.commit()
        with self.assertRaises(ValidationError) as ctm:
            ce('ParameterValueFloat', param_def=p, value=1., value_of_run=run)
            self.commit()
        self.assertExcMsg(ctm, 'this parameter has several values')


class FileValueFunctionalTC(ProcessingTCMixin, CubicWebTC):

    def setup_database(self):
        super(FileValueFunctionalTC, self).setup_database()
        # data setup : executable and parameters
        pdef1 = self.exe.add_input(u'i1', u'File')
        pdef2 = self.exe.add_input(u'i2', u'Float')
        self.commit()
        # data setup : run and parameter values
        ce = self.request().create_entity
        self.run = ce('Run', executable=self.exe)
        self.pv1 = self.new_file_pval(pdef1, self.run, with_value=True)
        self.fval = self.pv1.value_file[0]
        self.pv2 = ce('ParameterValueFloat', value=1., param_def=pdef2,
                      value_of_run=self.run)
        self.commit()

    def assertExists(self, entity, false_true=True):
        rql = 'Any X WHERE X eid %(x)s'
        self.assertEqual(self.execute(rql, dict(x=entity.eid)).rowcount,
                         int(false_true))

    def assertNotExists(self, entity):
        self.assertExists(entity, false_true=False)

    def test_remove_input_values(self):
        '''Parameter values must be deleted as soon as the Run is.
        File parameters are special in that we authorize sharing them between
        Run instances, but removing the only Run linked to a File value must
        remove it too.'''
        self.run.cw_delete()
        self.commit()
        self.assertNotExists(self.pv1)
        self.assertNotExists(self.pv2)
        self.assertNotExists(self.fval)

    def test_wiring_update(self):
        '''Updating the Wiring of a RunChain regenerates the Run instances.
        During this operation, we do not want the File instances linked to
        ParameterValueFile instances of the Run to be removed, but reused
        by the new Run if applicable.
        This functional (yet simple) test intends to demonstrate this.'''
        # create test data
        ce = self.request().create_entity
        runchain = ce('RunChain', uses_executable=(self.exe))
        self.commit()
        json = (u'{"modules":[{"eid":%(exe)s,"value":{"i1":%(f)s, "i2":1.0}}],"wires":[]}'
                % {'exe':self.exe.eid, 'f':dumps(self.fval.eid)})
        ce('Wiring', json=json, reverse_wiring=runchain, language=runchain.wlang)
        self.commit()
        # record values before wiring update
        old_run = runchain.has_runs[0]
        old_pval = old_run.ivalue_entity('i1')
        fval = old_pval.value_file[0]
        # dummy yet sufficient wiring update
        runchain.wiring[0].cw_set(json=json+u' ')
        self.commit()
        # check everything happened as expected
        runchain.cw_clear_all_caches()
        self.assertTrue(old_run.eid != runchain.has_runs[0].eid)
        self.assertTrue(old_pval.eid != runchain.has_runs[0].ivalue_entity('i1').eid)
        self.assertEqual(runchain.has_runs[0].ivalue_entity('i1').value_file[0].eid,
                         fval.eid)
        # remove one reference to the file, and check it still exists
        self.run.cw_delete()
        self.commit()
        self.assertExists(fval)
        # remove the other and check it was removed
        runchain.cw_delete()
        self.commit()
        self.assertNotExists(fval)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
