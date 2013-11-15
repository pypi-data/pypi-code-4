#
# Copyright (c) 2010, 2013
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
# THE SOFTWARE.
#
from lxml import etree
from coils.core import Task, OGO_ROLE_SYSTEM_ADMIN, CoilsException
from coils.core.logic import ActionCommand


class ArchiveOldTasksAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "archive-old-tasks"
    __aliases__ = ['archiveOldTasks', "archiveOldTasksAction", ]

    def __init__(self):
        ActionCommand.__init__(self)

    def parse_action_parameters(self):
        self._do_completion_date_fix = False
        do_completion_date_fix = \
            self.action_parameters.get('doCompletionDaysFix', 'NO')
        do_completion_date_fix = \
            self.process_label_substitutions(do_completion_date_fix)
        do_completion_date_fix = \
            do_completion_date_fix.upper()
        if do_completion_date_fix == 'YES':
            self._do_completion_date_fix = True

        self._project = None
        project_number = \
            self.action_parameters.get('project', None)
        if project_number:
            project_number = \
                self.process_label_substitutions(project_number)
            self._project = \
                self._ctx.run_command('project::get', number=project_number, )
            if not self._project:
                raise CoilsException(
                    'Unable to marshall project for number "{0}"'.
                    format(project_number, ))

        age_days = self.action_parameters.get('days', '187', )
        self._age_days = int(self.process_label_substitutions(age_days))

    def check_run_permissions(self):
        if self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN):
            return
        raise CoilsException(
            'Insufficient privilages to invoke archiveAccountTasksAction')

    def do_action(self):
        result = self._ctx.run_command(
            'task::batch-archive',
            age=self._age_days,
            fix_completion_dates=self._do_completion_date_fix,
            project=self._project, )
        self.wfile.write(unicode(result))
