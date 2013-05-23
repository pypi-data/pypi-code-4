##############################################################################
#
# Copyright (c) 2013 Christopher Lozinski (lozinski@freerecruiting.com).
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""TTW Python Script
"""
import types
from persistent import Persistent
from cStringIO import StringIO

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.security.untrustedpython import interpreter
from zope.size.interfaces import ISized

from zope.container.contained import Contained
from zope.app.publication.interfaces import IFileContent

from zopache.pythonscript.interfaces import IPythonScript

SOURCE_TEMPLATE = '''\
def %s(%s):
    %s
'''

def evalModule(source):
    """Evaluate module and return a pair: collected symbols and execution
    output.
    """
    module = types.ModuleType('pythonscript', "TTW Python Script")
    if not source:
        return module

    prog = interpreter.CompiledProgram(source)
    f = StringIO()
    # Collect a few more builtins that the untrusted Python interpreter does
    # not declare.
    ns = {'sum': sum}
    prog.exec_(ns, output=f)

    module.__dict__.update(ns)
    return module


class PythonScript(Persistent, Contained):
    implements(IPythonScript, IFileContent)
    _v_module = None
    _v_sourceHash = None

    signature = FieldProperty(IPythonScript['signature'])
    source = FieldProperty(IPythonScript['source'])

    def getModule(self):
        source = SOURCE_TEMPLATE %(
            self.__name__, self.signature,
            self.source.replace('\n', '\n    '))
        if self._v_module is None or self._v_sourceHash != hash(source):
            self._v_module = evalModule(source)
            self._v_sourceHash = hash(source)
        return self._v_module

    def __call__(self, *args, **kw):
        module = self.getModule()
        return getattr(module, self.__name__)(*args, **kw)


class Sized(object):
    implements(ISized)

    def __init__(self, script):
        self.num_lines = len(script.source.splitlines())

    def sizeForSorting(self):
        'See ISized'
        return ('line', self.num_lines)

    def sizeForDisplay(self):
        'See ISized'
        if self.num_lines == 1:
            return u'1 line'
        return u'%s lines' % str(self.num_lines)
