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
"""unittests for cubicweb-processing workflow related hooks"""

import time
from contextlib import contextmanager
from functools import partial
from json import dumps

from cubicweb import Binary
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.server.session import hooks_control


class WorkflowHookTC(CubicWebTC):

    def assertInState(self, entity, statename):
        entity.cw_clear_all_caches()
        self.assertEqual(entity.cw_adapt_to('IWorkflowable').state, statename)

    def run_with_param(self, ivalue_type, ovalue_type, python_code=None):
        req = self.request()
        exe = req.create_entity('Executable', name=u'py_exe',
                                python_code=python_code)
        exe.add_input(u'p', ivalue_type)
        exe.add_output(u'o', ovalue_type)
        self.commit()
        return req.create_entity('Run', executable=exe)

    def run_with_linked_io(self, value_type, python_code=None):
        run1 = self.run_with_param(u'Int', value_type, python_code=python_code)
        run1['p'] = 1
        run2 = self.run_with_param(value_type, value_type, python_code=python_code)
        run2.link_input_to_output('p', run1, 'o')
        self.commit()
        return run1, run2

    def test_run_ready_creation_no_param(self):
        """
        A new Run that has no param should automatically pass the
        'complete params' transition.
        """
        req = self.request()
        with self.session.allow_all_hooks_but('processing.test'):
            exe = req.create_entity('Executable', name=u'e')
            run = req.create_entity('Run', executable=exe)
            self.commit()
            self.assertInState(run, 'wfs_run_ready')

    def test_run_ready_with_param(self):
        """
        A Run that is added its last missing input value should automatically
        pass the 'complete params' transition.
        """
        with self.session.allow_all_hooks_but('processing.test'):
            run = self.run_with_param(u'Int', u'Int')
            run['p'] = 1
            self.commit()
            self.assertInState(run, 'wfs_run_ready')

    def test_run_ready_last_param_set(self):
        """
        A Run that has its last input parameter linked to an output
        should automatically pass the 'complete params' transition when set.
        """
        with self.session.allow_all_hooks_but('processing.test'):
            run1, run2 = self.run_with_linked_io(u'Float')
            self.assertInState(run2, 'wfs_run_setup')
            run2.input_values[0].cw_set(value=1.)
            self.commit()
            self.assertInState(run2, 'wfs_run_ready')

    def test_run_ready_last_file_param_added(self):
        """
        A Run that is added its last missing file input value should
        automatically pass the 'complete params' transition.
        """
        with self.session.allow_all_hooks_but('processing.test'):
            run1, run2 = self.run_with_linked_io(u'File')
            self.assertInState(run2, 'wfs_run_setup')
            vfile = self.request().create_entity(
                'File', data_name=u'xxx', data=Binary('xxx'))
            run2.input_values[0].cw_set(value_file=vfile)
            self.commit()
            self.assertInState(run2, 'wfs_run_ready')

    def test_simple_run_chain(self):
        with self.session.allow_all_hooks_but('processing.test'):
            run1, run2 = self.run_with_linked_io(u'Float', python_code=u'10+run["p"]')
            self.assertInState(run1, 'wfs_run_ready')
            self.assertInState(run2, 'wfs_run_setup')
        run1.cw_adapt_to('IWorkflowable').fire_transition('wft_run_queue')
        self.commit()
        self.assertInState(run1, 'wfs_run_completed')
        self.assertInState(run2, 'wfs_run_completed')
        self.assertEqual({'o': 11.0}, run1.ovalue_dict)
        run2.input_values[0].cw_clear_all_caches()
        self.assertEqual({'p': 11.0}, run2.ivalue_dict)
        self.assertEqual({'o': 21.0}, run2.ovalue_dict)

    # runchain testing ############################################################

    def runchain(self, python_code=None):
        req = self.request()
        runchain = req.create_entity('RunChain')
        exe = req.create_entity('Executable', name=u'exe',
                                python_code=python_code)
        req.create_entity('Run', executable=exe, reverse_has_runs=runchain)
        req.create_entity('Run', executable=exe, reverse_has_runs=runchain)
        self.commit()
        return runchain

    def test_runchain_run_complete(self):
        """
        When all runs of a runchain are in the 'completed' state, the runchain must
        automatically pass the 'complete' transition.
        """
        with self.session.allow_all_hooks_but('processing.test'):
            runchain = self.runchain()
            # launch runchain
            runchain.cw_adapt_to('IWorkflowable').fire_transition('wft_runchain_run')
            self.commit()
            # check runchain and run states
            self.assertInState(runchain, 'wfs_runchain_running')
            for run in runchain.has_runs:
                self.assertInState(run, 'wfs_run_waiting')
        # complete first run and check runchain state
        runchain.has_runs[0].cw_adapt_to('IWorkflowable').fire_transition('wft_run_run')
        self.commit()
        self.assertInState(runchain.has_runs[0], 'wfs_run_completed')
        self.assertInState(runchain, 'wfs_runchain_running')
        # complete first run and check runchain state
        runchain.has_runs[1].cw_adapt_to('IWorkflowable').fire_transition('wft_run_run')
        self.commit()
        self.assertInState(runchain.has_runs[1], 'wfs_run_completed')
        self.assertInState(runchain, 'wfs_runchain_completed')

    def test_runchain_run_error(self):
        """
        When one run of a runchain passes the 'run error' transition, the runchain
        must automatically pass the 'runchain error' transition
        (XXX with a comment linking to the run that generated this error).
        """
        with self.session.allow_all_hooks_but('processing.test'):
            runchain = self.runchain()
            # launch runchain
            runchain.cw_adapt_to('IWorkflowable').fire_transition('wft_runchain_run')
            self.commit()
            # crash running run and check runchain, queue and runs states
            runchain.has_runs[0].cw_adapt_to('IWorkflowable').fire_transition('wft_run_run')
            self.commit()
            runchain.has_runs[0].cw_adapt_to('IWorkflowable').fire_transition('wft_run_error')
            self.commit()
        self.assertInState(runchain.has_runs[0], 'wfs_run_crashed')
        self.assertInState(runchain.has_runs[1], 'wfs_run_waiting')
        self.assertInState(runchain, 'wfs_runchain_crashed')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
