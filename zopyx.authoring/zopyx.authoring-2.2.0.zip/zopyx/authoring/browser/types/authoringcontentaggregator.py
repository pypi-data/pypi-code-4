#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

from App.class_init import InitializeClass
from Products.Five.browser import BrowserView

from zopyx.authoring.logger import LOG

class HTMLView(BrowserView):
    """ AggregatedContent proxy handler """

#    def __call__(self, *args, **kw):
#
#        result = list()
#        # get hold of the target object from the proxy's reference field
#        for d in self.context.getReferencedContent():
#            obj = d['obj']
#            # call @@asHTML view of obj
#            LOG.info('  Introspecting reference: %s' % obj.absolute_url(1))
#            view = obj .restrictedTraverse('@@asHTML')
#            result.append(view())
#        return '\n'.join(result)

    def __call__(self):
        ref = self.context.getRefersTo1()
        if ref:
            LOG.info('  Introspecting reference: %s' % ref.absolute_url(1))
            return ref.restrictedTraverse('@@asHTML')()
        return ''

InitializeClass(HTMLView)
