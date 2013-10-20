# -*- coding: utf-8 -*-
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from Sveetchies.django.autobreadcrumbs.decorators import autobreadcrumb_add

from kiwi import WIKIPAGE_ENABLE_ARCHIVE
from kiwi.models import Wikipage

from kiwi.utils import get_root_element

@autobreadcrumb_add(u"Plan du wiki")
def sitemap(request):
    """
    Plan d'arborescence des pages
    """
    template = 'kiwi/sitemap.html'
    object_list = Wikipage.objects.get_active_menu()

    extra_context = {
        'user': request.user,
        'object_list': object_list,
    }
    return render_to_response(template, extra_context, context_instance=RequestContext(request))

@autobreadcrumb_add(u"Document")
def details(request, uri, with_history=True):
    """
    Affichage d'une page wiki
    
    @with_history : désactive le mode avec historique. Utile 
    principalement à l'outil d'exportation pour ne pas afficher le lien de 
    l'historique des pages.
    """
    template = 'kiwi/details.html'

    wikipageObject = get_object_or_404(Wikipage, uri=uri, in_sitemap=True, active=True)
    
    # Template spécifique à la wikipage
    if wikipageObject.template:
        template = wikipageObject.template.path
    
    # On note l'URI dans l'objet de la requete pour qu'il soit utilisable 
    # directement par n'importe quelle appli/plugin tierce sans bidouilles
    request.wikipage_uri = wikipageObject.uri
    
    # Récupère l'arborescence complète des pages
    wikipageAll = Wikipage.objects.get_active_menu()
    
    extra_context = {
        'user': request.user,
        'wikipageTopParent': get_root_element(wikipageAll, wikipageObject.id),
        'wikipageObject': wikipageObject,
        'wikipageAll': wikipageAll,
        'wikipageAllPub': Wikipage.objects.get_active_dict(),
        'with_history': (with_history and WIKIPAGE_ENABLE_ARCHIVE),
        'attachment_items': wikipageObject.get_attachments(user=request.user),
    }
    
    return render_to_response(template, extra_context, context_instance=RequestContext(request))

@autobreadcrumb_add(u"Recherche")
def search(request):
    """
    Recherche sur les Wikipage
    """
    template = 'kiwi/search.html'
    
    # Récupération du motif dans POST et GET, GET écrase POST
    search_pattern = None
    if request.POST:
        search_pattern = request.POST.get('search_pattern', None)
    if request.GET:
        search_pattern = request.GET.get('search_pattern', None)
    
    # Si on a bien un motif on renvoi sa requête sinon un queryset vide
    if search_pattern:
        queryset = Wikipage.objects.filter( Q(text__icontains=search_pattern) | Q(title__icontains=search_pattern), in_sitemap=True, active=True )
        
    else:
        queryset = Wikipage.objects.none()

    extra_context = {
        'user': request.user,
        'object_list': queryset,
        'search_pattern': search_pattern,
    }
    return render_to_response(template, extra_context, context_instance=RequestContext(request))
