#
# Copyright (c) 2010, 2011, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import uuid
from datetime import timedelta, datetime
from sqlalchemy import and_
from coils.core import \
    Task, \
    Command, \
    CoilsException, \
    AccessForbiddenException, \
    OGO_ROLE_SYSTEM_ADMIN, \
    Project
from command import TaskCommand


class BatchArchive(Command, TaskCommand):
    __domain__ = "task"
    __operation__ = "batch-archive"

    def check_run_permissions(self):
        if self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN):
            return
        raise AccessForbiddenException(
            'Context lacks role; cannot perform batch archive')

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self._age = int(params.get('age', 0))
        self._owner = int(params.get('owner_id', 0))
        if not self._age and not self._owner:
            raise CoilsException(
                'Neither owner nor age specified for batch archive.')

        self.project = params.get('project', None)
        if self.project:
            if not isinstance(self.project, Project):
                raise CoilsException(
                    'Entity provided by project parameter must be a Project'
                )

        # Determine if we should fix the completion dates of tasks with
        # NULL completion dates.
        fix_completion_dates = params.get('fix_completion_dates', None)
        if fix_completion_dates:
            if isinstance(fix_completion_dates, basestring):
                fix_completion_dates = \
                    (fix_completion_dates.upper() == 'YES')
            elif isinstance(fix_completion_dates, bool):
                pass
            else:
                fix_completion_dates = False
        else:
            fix_completion_dates = False
        self._fix_completion_date = fix_completion_dates

    def _do_completion_date_fix(self, admin_event_id):
        db = self._ctx.db_session()
        query = db.query(Task).\
            filter(
                and_(Task.state.in_(['25_done', '02_rejected', ]),
                     Task.completed is None, )
            )
        for task in query.all():
            completed = None
            for action in task.actions:
                if action.action in ['25_done', '02_rejected', ]:
                    if not completed or action.action_date > completed:
                        completed = action.action_date
            if completed:
                task.completed = completed
                comment = \
                    'Completion date of task corrected to {0}.\n' \
                    'Administrative event {{{1}}}'.\
                    format(completed, admin_event_id, )
                self._ctx.run_command('task::comment',
                                      task=task,
                                      values={'comment': comment,
                                              'action': 'archive', }, )

    def run(self):

        admin_event_id = str(uuid.uuid4())

        if self._fix_completion_date:
            self._do_completion_date_fix(admin_event_id)

        counter = 0
        db = self._ctx.db_session()
        comment = \
            'Auto-archived by administrative event {{{0}}}'.\
            format(admin_event_id, )

        clause = and_()
        clause.append(Task.state.in_(['25_done', '02_rejected', ]))
        if self._age:
            # Assuming Age (archive old tasks) mode
            now = datetime.now()
            span = timedelta(days=self._age)
            clause.append(Task.completed != None)
            clause.append(Task.completed < (now - span))
        if self._owner:
            clause.append(Task.owner_id == self._owner)
        if self.project:
            clause.append(Task.project_id == self.project.object_id)
        query = db.query(Task).filter(clause)
        for task in query.all():
            self._ctx.run_command('task::comment',
                                  task=task,
                                  values={'comment': comment,
                                          'action': 'archive', }, )
            counter += 1
            # TODO: Perform notification of event
        self._result = counter
