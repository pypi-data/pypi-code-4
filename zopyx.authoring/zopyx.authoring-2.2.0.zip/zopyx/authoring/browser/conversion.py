
#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

from zope.interface import implements
from ..interfaces import IConversionView

class SupplConversionView(object):
    implements(IConversionView)

    def __call__(self):
        return dict(tab_text= u'Custom', 
                    tab_content='<h2>Just a test</h2>')
