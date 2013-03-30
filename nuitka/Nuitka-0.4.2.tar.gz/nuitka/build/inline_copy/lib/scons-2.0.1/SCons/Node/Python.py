"""scons.Node.Python

Python nodes.

"""

#
# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "src/engine/SCons/Node/Python.py 5134 2010/08/16 23:02:40 bdeegan"

import SCons.Node

class ValueNodeInfo(SCons.Node.NodeInfoBase):
    current_version_id = 1

    field_list = ['csig']

    def str_to_node(self, s):
        return Value(s)

class ValueBuildInfo(SCons.Node.BuildInfoBase):
    current_version_id = 1

class Value(SCons.Node.Node):
    """A class for Python variables, typically passed on the command line 
    or generated by a script, but not from a file or some other source.
    """

    NodeInfo = ValueNodeInfo
    BuildInfo = ValueBuildInfo

    def __init__(self, value, built_value=None):
        SCons.Node.Node.__init__(self)
        self.value = value
        if built_value is not None:
            self.built_value = built_value

    def str_for_display(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

    def make_ready(self):
        self.get_csig()

    def build(self, **kw):
        if not hasattr(self, 'built_value'):
            SCons.Node.Node.build(self, **kw)

    is_up_to_date = SCons.Node.Node.children_are_up_to_date

    def is_under(self, dir):
        # Make Value nodes get built regardless of 
        # what directory scons was run from. Value nodes
        # are outside the filesystem:
        return 1

    def write(self, built_value):
        """Set the value of the node."""
        self.built_value = built_value

    def read(self):
        """Return the value. If necessary, the value is built."""
        self.build()
        if not hasattr(self, 'built_value'):
            self.built_value = self.value
        return self.built_value

    def get_text_contents(self):
        """By the assumption that the node.built_value is a
        deterministic product of the sources, the contents of a Value
        are the concatenation of all the contents of its sources.  As
        the value need not be built when get_contents() is called, we
        cannot use the actual node.built_value."""
        ###TODO: something reasonable about universal newlines
        contents = str(self.value)
        for kid in self.children(None):
            contents = contents + kid.get_contents()
        return contents

    get_contents = get_text_contents    ###TODO should return 'bytes' value

    def changed_since_last_build(self, target, prev_ni):
        cur_csig = self.get_csig()
        try:
            return cur_csig != prev_ni.csig
        except AttributeError:
            return 1

    def get_csig(self, calc=None):
        """Because we're a Python value node and don't have a real
        timestamp, we get to ignore the calculator and just use the
        value contents."""
        try:
            return self.ninfo.csig
        except AttributeError:
            pass
        contents = self.get_contents()
        self.get_ninfo().csig = contents
        return contents

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
