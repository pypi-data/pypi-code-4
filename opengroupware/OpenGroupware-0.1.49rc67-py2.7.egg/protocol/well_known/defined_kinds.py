#
# Copyright (c) 2013
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
import json
import yaml
from datetime import datetime
from coils.core import \
    NotImplementedException, \
    NoSuchPathException, \
    BLOBManager, \
    CoilsException
from coils.net import Protocol, PathObject
from namedpathobject import NamedPathObject
from utility import get_object_from_project7000_path


class DefinedKindsList(NamedPathObject):

    def __init__(self, parent, name, **params):
        NamedPathObject.__init__(self, parent, name, **params)

    def _encode(self, o):
        if (isinstance(o, datetime)):
            return  o.strftime('%Y-%m-%dT%H:%M:%S')
        raise TypeError()

    def do_GET(self):

        result = None
        obj = get_object_from_project7000_path(
            self.context,
            '/DefinedKinds.yaml', )

        if obj:
            rfile = self.context.run_command('document::get-handle',
                                             document=obj, )
            content = yaml.load(rfile)
            BLOBManager.Close(rfile)

            '''
            If there is any need to transform the content - that code
            goes here
            '''

            result = content

            if result:

                if self.name.endswith('.json'):

                    content_type = 'application/json'
                    result = json.dumps(result, default=self._encode, )

                elif self.name.endswith('.yaml'):

                    content_type = 'application/yaml'
                    result = yaml.dump(result)

                else:

                    self.no_such_path()

                self.request.simple_response(
                    200,
                    data=result,
                    mimetype=content_type, )

            else:

                raise CoilsException(
                    'Unable to marshall handle to defined properties '
                    'document; corrupted permissions?')

        else:
            raise NoSuchPathException(
                'The defined kinds document in Project 7000 '
                '(/DefinedKinds.yaml) has not been provisioned')
