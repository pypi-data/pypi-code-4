"""timesheet hooks: compute progress, completing what's already done in
workorder.
"""

__docformat__ = "restructuredtext en"

from cubicweb.predicates import is_instance
from cubicweb.server import hook

from cubes.workorder.hooks import UpdateProgressOp


class UpdateProgressOnActivityModification(hook.Hook):
    __regid__ = 'timesheet.progress.activity'
    __select__ = hook.Hook.__select__ & is_instance('Activity')
    events = ('after_update_entity', )

    def __call__(self):
        if 'duration' in self.entity.cw_edited:
            for workorder in self.entity.done_for:
                UpdateProgressOp.get_instance(self._cw).add_data(
                    (workorder.eid, True) )


class UpdateProgressOnDoneForChange(hook.Hook):
    __regid__ = 'timesheet_update_done_for'
    __select__ = (hook.Hook.__select__
                  & hook.match_rtype('done_for', toetypes=('WorkOrder',)))
    events = ('after_add_relation', 'after_delete_relation',)

    def __call__(self):
        UpdateProgressOp.get_instance(self._cw).add_data(
            (self.eidto, True))
