# -*- coding: utf-8 -*-
"""
Vues de rendu brut et prévisualisation
"""
from PyWiki2xhtml import __title__ as parser_name
from PyWiki2xhtml.macros.helper import Wiki2XhtmlMacrosHelper as Wiki2XhtmlHelper

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from Sveetchies.django.pywiki2xhtml import PYWIKI2XHTML_CONFIGSET, PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS
from Sveetchies.django.pywiki2xhtml.utils import configure_w2x_instance

def model_object_preview(request, model_object=None, instance_id=None, 
                        actived_macros=PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS, 
                        configset_kwargs=None, default_configset_name='standard'):
    """
    Vue pour pour la prévisualisation dans le contexte d'un document
    
    Nécessaire pour avoir une prévisualisation qui puisse utiliser correctement la macro 
    des fichiers attachés au document.
    """
    if not model_object or not instance_id:
        raise Http404
    
    contentObject = get_object_or_404(model_object, pk=instance_id)
    
    if not configset_kwargs:
        configset_kwargs = PYWIKI2XHTML_CONFIGSET[default_configset_name].copy()
    
    # Parse le texte envoyé avec les options standards
    W2Xobject = configure_w2x_instance(request, contentObject, actived_macros=actived_macros, configset_kwargs=configset_kwargs)
    
    return preview(request, W2Xobject)

def model_object_raw(request, model_object=None, instance_id=None, attr_name=None, 
                    actived_macros=PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS, 
                    configset_kwargs=None, default_configset_name='standard'):
    """
    Rendu brut
    """
    if not model_object or not instance_id or not attr_name:
        raise Http404
    
    contentObject = get_object_or_404(model_object, pk=instance_id)
    value = getattr(contentObject, attr_name)
    
    if not configset_kwargs:
        configset_kwargs = PYWIKI2XHTML_CONFIGSET[default_configset_name].copy()
    
    # Parse le texte envoyé avec les options standards
    W2Xobject = configure_w2x_instance(request, contentObject, actived_macros=actived_macros, configset_kwargs=configset_kwargs)
    
    # Renvoi directement le xhtml produit
    return HttpResponse( W2Xobject.transform( value ) )

def preview(request, W2Xobject=None,
            actived_macros=PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS, 
            configset_kwargs=None, default_configset_name='standard'):
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
        W2Xobject = configure_w2x_instance(request)
    
    # Renvoi directement le xhtml produit
    return HttpResponse( W2Xobject.transform( value ) )

def syntax_help(request, default_configset_name='standard_with_summary', accept_configset_request=True):
    """
    Vue qui contient la démonstration dynamique de la syntaxe
    """
    template = 'pywiki2xhtml/syntax_help_page.html'
    configset_name = default_configset_name
    
    if accept_configset_request and request.GET:
        configset_name = request.GET.get('configset_name', configset_name)
    elif accept_configset_request and request.POST:
        configset_name = request.POST.get('configset_name', configset_name)
    
    helperObject = Wiki2XhtmlHelper(opts=PYWIKI2XHTML_CONFIGSET[configset_name])
    object_list = helperObject.render()

    extra_context = {
        'object_list': object_list,
        'parser_name': parser_name,
        'configset_name': configset_name,
    }
    
    return render_to_response(template, extra_context, context_instance=RequestContext(request))

"""
Versions identiques mais fermés aux anonymes
"""
@login_required
def model_object_preview_login_required(*args, **kwargs):
    return model_object_preview(*args, **kwargs)

@login_required
def model_object_raw_login_required(*args, **kwargs):
    return model_object_raw(*args, **kwargs)

@login_required
def preview_login_required(*args, **kwargs):
    return preview(*args, **kwargs)

@login_required
def syntax_help_login_required(*args, **kwargs):
    return syntax_help(*args, **kwargs)

"""
Versions identiques mais limités aux admins
"""
@staff_member_required
def model_object_preview_staff_member_required(*args, **kwargs):
    return model_object_preview(*args, **kwargs)

@staff_member_required
def model_object_raw_staff_member_required(*args, **kwargs):
    return model_object_raw(*args, **kwargs)

@staff_member_required
def preview_staff_member_required(*args, **kwargs):
    return preview(*args, **kwargs)

@staff_member_required
def syntax_help_staff_member_required(*args, **kwargs):
    return syntax_help(*args, **kwargs)
