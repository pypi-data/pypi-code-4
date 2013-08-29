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
import json, yaml
from coils.core          import NotImplementedException, \
                                NoSuchPathException, \
                                BLOBManager, \
                                AdministrativeContext
from coils.net           import Protocol, PathObject
from namedpathobject     import NamedPathObject
from utility             import get_object_from_project7000_path

class OpenSearch(NamedPathObject):

    def __init__(self, parent, name, **params):
        NamedPathObject.__init__(self, parent, name, **params)

    def do_GET(self):

        ctx = AdministrativeContext( )

        try:
            result = None
            obj = get_object_from_project7000_path( ctx, '/OpenSearch.xml' )
            if obj:
                rfile = ctx.run_command( 'document::get-handle', document=obj )
                if rfile:
                    self.request.simple_response( 200, stream=rfile, mimetype='application/opensearchdescription+xml' )
                    BLOBManager.Close( rfile )
                    return
        finally:
            ctx.close( )

        raise NoSuchPathException( 'OpenSearch specification not provisioned' )

