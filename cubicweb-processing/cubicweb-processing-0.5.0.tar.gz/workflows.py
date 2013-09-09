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

def define_run_workflow(add_workflow):
    run_wf = add_workflow(u'Run workflow', 'Run')
    run_wf_perms = ('managers',)
    addtrans = run_wf.add_transition
    addstate = run_wf.add_state

    setup     = addstate(_('wfs_run_setup'), initial=True)
    ready     = addstate(_('wfs_run_ready'))
    waiting   = addstate(_('wfs_run_waiting'))
    running   = addstate(_('wfs_run_running'))
    completed = addstate(_('wfs_run_completed'))
    crashed   = addstate(_('wfs_run_crashed'))

    addtrans(_('wft_run_complete_params'), (setup,), ready, run_wf_perms)
    addtrans(_('wft_run_queue'), (ready,), waiting, run_wf_perms + ('owners',))
    addtrans(_('wft_run_run'), (waiting,), running, run_wf_perms)
    addtrans(_('wft_run_error'), (waiting, running,), crashed, run_wf_perms)
    addtrans(_('wft_run_complete'), (running,), completed, run_wf_perms)


def define_runchain_workflow(add_workflow):
    runchain_wf = add_workflow(u'RunChain workflow', 'RunChain')
    runchain_wf_perms = ('managers',)
    addtrans = runchain_wf.add_transition
    addstate = runchain_wf.add_state

    setup     = addstate(_('wfs_runchain_setup'), initial=True) # ui-building time, without runs
    ready     = addstate(_('wfs_runchain_ready'))
    running   = addstate(_('wfs_runchain_running'))
    completed = addstate(_('wfs_runchain_completed'))
    crashed   = addstate(_('wfs_runchain_crashed'))

    addtrans(_('wft_runchain_generate'), (setup,), ready, runchain_wf_perms)
    addtrans(_('wft_runchain_run'), (ready,), running, runchain_wf_perms + ('owners',))
    addtrans(_('wft_runchain_complete'), (running,), completed, runchain_wf_perms)
    addtrans(_('wft_runchain_error'), (running,), crashed, runchain_wf_perms)
