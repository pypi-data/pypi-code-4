#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

from zopyx.smartprintng.plone.interfaces import IPPContent
from zopyx.smartprintng.plone import Transformer

_marker = object

def postEdit(event):
   
    obj = event.object
    if not IPPContent.providedBy(obj):
        return

    field = obj.Schema().getField('text')
    if not field:
        return

    # only modify text/html text fields (omit fields with reST etc.)
    if field.getContentType(obj) in ('text/html',):
        T = Transformer(('addUUIDs', 'cleanupEmptyElements'))
        html = T(obj.getText(), input_encoding='utf-8')
        obj.setText(html)
        obj.setContentType('text/html')
        obj.getField('text').setContentType(obj, 'text/html')
