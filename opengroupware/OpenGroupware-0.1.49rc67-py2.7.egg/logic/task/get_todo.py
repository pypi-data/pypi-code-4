#
# Copyright (c) 2009, 2013
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
from sqlalchemy import and_, not_
from coils.foundation import apply_orm_hints_to_query
from coils.core import Task, Command
from coils.core.logic import GetCommand


class GetToDoList(GetCommand):
    __domain__ = "task"
    __operation__ = "get-todo"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

    def run(self, **params):
        #self.disable_access_check()
        self.set_multiple_result_mode()
        db = self._ctx.db_session()
        query = db.query(Task).\
            filter(
                and_(
                    Task.executor_id.in_(self._ctx.context_ids),
                    not_(
                        Task.state.in_(('30_archived', '25_done', ))
                    )
                )
            )
        query = apply_orm_hints_to_query(query, Task, self.orm_hints)
        data = query.all()
        self.log.debug('{0} tasks in result'.format(len(data), ))
        self.set_return_value(data)
