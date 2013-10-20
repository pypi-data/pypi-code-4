# -*- coding: utf-8 -*-
from PyWiki2xhtml.macros.parser import Wiki2XhtmlMacros as Wiki2XhtmlParser
from PyWiki2xhtml.macros.macro_attach import parse_macro_attach
from PyWiki2xhtml.macros.macro_pygments import parse_macro_pygments
from PyWiki2xhtml.macros.macro_mediaplayer import parse_macro_mediaplayer
from PyWiki2xhtml.macros.macro_gmap import parse_macro_googlemap
from PyWiki2xhtml.macros.helper import Wiki2XhtmlMacrosHelper as Wiki2XhtmlHelper
from PyWiki2xhtml import __title__ as parser_name

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from Sveetchies.django.autobreadcrumbs.decorators import autobreadcrumb_add

from kiwi import PyWiki2Xhtml_ConfigSet

from kiwi.models import Wikipage

from kiwi.utils import get_attachment_items_from_list

@login_required
def wikipage_preview(request, uri):
    """
    Vue pour pour la prévisualisation dans le contexte d'un document
    
    TODO: Dans l'admin la preview d'une macro googlemap ne fonctionne pas, probablement 
    parce que le js dans le html n'est pas exécuté après son insertion. Vérifiez mais ça 
    doit etre pareil pour la macro mediaplayer;
    """
    wikipageObject = get_object_or_404(Wikipage, uri=uri)
    
    kwargs = PyWiki2Xhtml_ConfigSet['standard'].copy()
    kwargs.update({'published_wikipage': Wikipage.objects.get_active_dict()})
    # Parse le texte envoyé avec les options standards
    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.kwargsOpt(kwargs)
    W2Xobject.setOpt('attached_items', get_attachment_items_from_list(wikipageObject.get_attachments(user=request.user)))
    W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)
    W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
    W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
    W2Xobject.add_macro('googlemap', mode='post', func=parse_macro_googlemap)
    
    return preview(request, W2Xobject)

def preview(request, W2Xobject=None):
    """
    Vue pour prévisualiser la transformation d'un texte.
    Recois un texte dans un attribut "source" d'une requête POST et renvoi 
    directement sa transformation en xhtml
    """
    value = ""
    if request.POST:
        value = request.POST.get('source', value)
    
    # Si aucun objet de parser instancié n'est passé en argument, on en instancie un 
    # par défaut
    if not W2Xobject:
        kwargs = PyWiki2Xhtml_ConfigSet['standard'].copy()
        kwargs.update({'published_wikipage': Wikipage.objects.get_active_dict()})
        # Parse le texte envoyé avec les options standards
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.kwargsOpt(kwargs)
        W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
        W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
        W2Xobject.add_macro('googlemap', mode='post', func=parse_macro_googlemap)
    
    # Renvoi directement le xhtml produit
    return HttpResponse( W2Xobject.transform( value ) )

@autobreadcrumb_add(u"Aide de la syntaxe Wiki")
def help(request, default_configset_name='standard_with_summary', accept_configset_request=True):
    """
    Vue qui contient la démonstration dynamique de la syntaxe
    """
    template = 'kiwi/syntax_help_page.html'
    configset_name = default_configset_name
    
    if accept_configset_request and request.GET:
        configset_name = request.GET.get('configset_name', configset_name)
    elif accept_configset_request and request.POST:
        configset_name = request.POST.get('configset_name', configset_name)
    
    helperObject = Wiki2XhtmlHelper(opts=PyWiki2Xhtml_ConfigSet[configset_name])
    object_list = helperObject.render()

    extra_context = {
        'object_list': object_list,
        'parser_name': parser_name,
        'configset_name': configset_name,
    }
    
    return render_to_response(template, extra_context, context_instance=RequestContext(request))
