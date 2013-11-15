#
# Copyright (c) 2010, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
# LIABILITY, WHETHER I89N AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
from sqlalchemy import and_
from coils.core import Command, Task, Project, CoilsException
from coils.core.logic import GetCommand
from coils.foundation import apply_orm_hints_to_query


class GetProjectTasks(GetCommand):
    __domain__ = "project"
    __operation__ = "get-tasks"

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):

        Command.parse_parameters(self, **params)

        self._include_archived = bool(params.get('included_archived', True))

        if ('id' in params):
            self.project_id = int(params['id'])
        elif ('project' in params):
            self.project_id = params['project'].object_id
        else:
            raise CoilsException(
                'No project or project id provided to project::get-tasks')

    def run(self, **params):
        self.set_multiple_result_mode()
        query = self._ctx.db_session().query(Task)
        if not self._include_archived:
            query = query.\
                filter(
                    and_(
                        Task.project_id == self.project_id,
                        Task.state != '30_archived',
                    )
                )
        else:
            query = query.filter(Task.project_id == self.project_id)
        apply_orm_hints_to_query(query, Task, self.orm_hints)
        self.set_return_value(query.all())
