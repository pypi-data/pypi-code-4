#
# Copyright (c) 1019 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core           import *
from coils.core.logic     import CreateCommand
from keymap               import COILS_COLLECTION_KEYMAP

from command import CollectionAssignmentFlyWeight

class CreateCollection(CreateCommand):
    __domain__ = "collection"
    __operation__ = "new"

    def __init__(self):
        CreateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap =  COILS_COLLECTION_KEYMAP
        self.entity = Collection
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        self.membership = params.get('membership', None)

    def do_assignments(self):
        if not self.membership:
            self.membership = KVC.subvalues_for_key( self.values, [ '_MEMBERSHIP', 'membership' ] )
        if self.membership:
            self._ctx.run_command( 'collection::set-assignments', insert=self.membership,
                                                                  collection=self.obj )

    def run(self, **params):
        CreateCommand.run(self, **params)
        self.do_assignments()
        self.save()
