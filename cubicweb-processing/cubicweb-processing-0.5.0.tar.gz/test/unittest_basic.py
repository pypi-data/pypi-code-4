# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from cubicweb.devtools.testlib import CubicWebTC

from cubes.processing.schema import (Executable, Run, RunChain, ParameterDefinition, 
                                     ParameterValueInt, ParameterValueFloat, ParameterValueString)

class TestProcessingBasic(CubicWebTC):
    def setup_database(self):
        """Prepare two executables, each one with one input and one output 
        parameter definitions.
        """
        super(TestProcessingBasic, self).setup_database()


    def test_run_chain(self):
        with self.session.allow_all_hooks_but('processing.test'):
            my_python_code = u'"my_exe"+str(run["my_in_p"])'
            other_python_code = u'1000+int(run["other_in_p"].split("my_exe")[-1].split(".")[0])'
            my_exe = self.request().create_entity('Executable', name=u'my executable',
                                                  python_code=my_python_code)
            my_exe.add_input(u'my_in_p', u'Float')
            my_exe.add_output(u'o', u'String')
            self.commit()
            other_exe = self.request().create_entity('Executable', name=u'other executable',
                                                     python_code=other_python_code)
            other_exe.add_input(u'other_in_p', u'String')
            other_exe.add_output(u'o', u'Int')
            self.commit()
            my_run = self.request().create_entity('Run', executable=my_exe)
            my_run['my_in_p'] = 5.
            self.commit()
            other_run = self.request().create_entity('Run', executable=other_exe)
            other_run.link_input_to_output('other_in_p', my_run, 'o')
            self.commit()
        print my_run.cw_adapt_to('IWorkflowable').state
        print other_run.cw_adapt_to('IWorkflowable').state
        my_run.cw_adapt_to('IWorkflowable').fire_transition('wft_run_queue')
        self.commit()
        import ipdb; ipdb.set_trace()
        print my_run.cw_adapt_to('IWorkflowable').state
        print other_run.cw_adapt_to('IWorkflowable').state



