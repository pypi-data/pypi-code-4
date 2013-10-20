# -*- coding: utf-8 -*-
from PyWiki2xhtml.macros.parser import Wiki2XhtmlMacros as Wiki2XhtmlParser
from PyWiki2xhtml.macros.macro_attach import parse_macro_attach
from PyWiki2xhtml.macros.macro_pygments import parse_macro_pygments
from PyWiki2xhtml.macros.macro_mediaplayer import parse_macro_mediaplayer
from PyWiki2xhtml.macros.macro_gmap import parse_macro_googlemap

from Sveetchies.django.pywiki2xhtml import PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS
from Sveetchies.django.attachments.utils import get_attachment_items_from_list

def configure_w2x_instance(request, instance=None, actived_macros=PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS, configset_kwargs=None):
    """
    Instanciation du parser
    """
    W2Xobject = Wiki2XhtmlParser()
    
    if configset_kwargs:
        W2Xobject.kwargsOpt(configset_kwargs)
        
    if 'attach' in PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS and instance and hasattr(instance, 'get_attachments'):
        W2Xobject.setOpt('attached_items', get_attachment_items_from_list(instance.get_attachments(user=request.user)))
        W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)
    if 'mediaplayer' in PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS:
        W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
    if 'pygments' in PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS:
        W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
    if 'googlemap' in PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS:
        W2Xobject.add_macro('googlemap', mode='post', func=parse_macro_googlemap)
    
    return W2Xobject

