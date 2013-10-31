#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later
#
#
# XXX: This module is some kind of experimental.
#
# the reason for using this module is the need of rendering lots (100+) browser
# views in one request. when doing this via bound templates we have a huge
# overhead with page templates due to parsing and restricted python
#

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts

from interfaces import ISelectionVocab
from interfaces import IHTMLRenderer

class SelectionVocabBase(object):
    """ISelectionVocab implementation
    """
    
    implements(ISelectionVocab)
    adapts(Interface)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self):
        raise NotImplementedError(u"``__call__()`` must be implemented by "
                                  "subclass")

class HTMLRendererMixin(object):
    """IHTMLRenderer implementation
    """
    
    implements(IHTMLRenderer)
    
    def _tag(self, name_, *args, **kw):
        attrlist = list()
        for key, value in kw.items():
            if value is None:
                continue
            if not isinstance(value, unicode):
                value = str(value).decode('utf-8')
            attrlist.append((key, value))
        attrs = u' '.join(u'%s="%s"' % (key.strip('_'), value) \
                                          for key, value in attrlist)
        attrs = attrs and u' %s' % attrs or u''
        arglist = list()
        for arg in args:
            if not isinstance(arg, unicode):
                arg = str(arg).decode('utf-8')
            arglist.append(arg)
        if not arglist:
            return u'<%(name)s%(attrs)s />' % {
                'name': name_,
                'attrs': attrs,
            }
        return u'<%(name)s%(attrs)s>%(value)s</%(name)s>' % {
            'name': name_,
            'attrs': attrs,
            'value': u''.join(c for c in arglist),
        }
    
    def _selection(self, vocab_, **kw):
        options = list()
        for term in vocab_:
            optkw = {'value': term[0]}
            if term[2]:
                optkw['selected'] = 'selected'
            option = self._tag('option', term[1], **optkw)
            options.append(option)
        return self._tag('select', *options, **kw)
