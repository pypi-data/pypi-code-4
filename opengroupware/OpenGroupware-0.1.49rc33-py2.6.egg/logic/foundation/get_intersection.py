#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy       import *
from coils.core       import *

class GetIntersectingEntities(Command):
    __domain__ = "collection"
    __operation__ = "get-intersection"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.collections         = params.get('collections',None)
        self.entity_name      = params.get('entity_name',None)

    def run(self):
        query_list = []
        db = self._ctx.db_session()
        for collection in self.collections:
            query_list.append(db.query(CollectionAssignment.assigned_id).\
                                        filter(CollectionAssignment.collection_id == collection.object_id))
        intersect_query = db.execute(intersect(*query_list)).fetchall()
        ids = []
        for id in intersect_query:
            ids.append(id[0])
        if (len(ids) > 0):
            result = self._ctx.type_manager.group_ids_by_type(ids)
            if (self.entity_name is None):
                self.set_return_value(result)
                return
            else:
                self.set_return_value(result.get(self.entity_name, [] ))
                return
        else:
            self.set_return_value([])
