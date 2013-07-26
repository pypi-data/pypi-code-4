# -*- coding: utf-8 -*-
import difflib

from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.list_detail import object_list

from Sveetchies.django.autobreadcrumbs.decorators import autobreadcrumb_add

from kiwi.models import Wikipage, Version

from kiwi.utils import get_root_element

@autobreadcrumb_add(u'Historique des versions de "{{ wikipageObject.title }}"')
def history(request, uri):
    """
    Historique des versions d'une page
    """
    template = 'kiwi/version_history.html'

    wikipageObject = get_object_or_404(Wikipage, uri=uri, in_sitemap=True, active=True)

    # Récupère l'arborescence complète des pages
    wikipageAll = Wikipage.objects.get_active_menu()

    extra_context = {
        'user': request.user,
        'wikipageTopParent': get_root_element(wikipageAll, wikipageObject.id),
        'wikipageObject': wikipageObject,
        'wikipageAll': wikipageAll,
    }
    response = object_list(
        request,
        queryset = wikipageObject.version.all().order_by('-rev_number'),
        paginate_by = 4,
        template_name = template,
        extra_context = extra_context,
        allow_empty = True
    )
    return response

@autobreadcrumb_add(u"Version n°{{ versionObject.rev_number }}")
def details(request, uri, version_id):
    """
    Affichage d'une version archivée d'une page wiki
    """
    template = 'kiwi/version_details.html'

    wikipageObject = get_object_or_404(Wikipage, uri=uri, in_sitemap=True, active=True)
    versionObject = get_object_or_404(Version, wikipage=wikipageObject, rev_number=version_id)
    
    # Récupère l'arborescence complète des pages
    wikipageAll = Wikipage.objects.get_active_menu()

    extra_context = {
        'user': request.user,
        'wikipageTopParent': get_root_element(wikipageAll, wikipageObject.id),
        'wikipageObject': wikipageObject,
        'wikipageAll': wikipageAll,
        'wikipageAllPub': Wikipage.objects.get_active_dict(),
        'versionObject': versionObject,
        'attachment_items': wikipageObject.get_attachments(user=request.user),
    }
    
    return render_to_response(template, extra_context, context_instance=RequestContext(request))

@autobreadcrumb_add(u"Différence entre la version n°{{ versionObject.rev_number }} et la version n°{{ wikipageObject.rev_number }}")
def diff(request, uri, version_id):
    """
    Différence entre une version d'une page et celle actuelle
    """
    template = 'kiwi/version_diff.html'

    wikipageObject = get_object_or_404(Wikipage, uri=uri, in_sitemap=True, active=True)
    versionObject = get_object_or_404(Version, wikipage=wikipageObject, rev_number=version_id)
    
    label_from = u"N°%s" % versionObject.rev_number
    label_to = u"N°%s" % wikipageObject.rev_number()
    diffObject = difflib.HtmlDiff().make_table(versionObject.text.splitlines(1), wikipageObject.text.splitlines(1), fromdesc=label_from, todesc=label_to, context=True)
    diffObject = diffObject.replace('&nbsp;',' ').replace(' nowrap="nowrap"','')
    
    # Récupère l'arborescence complète des pages
    wikipageAll = Wikipage.objects.get_active_menu()

    extra_context = {
        'user': request.user,
        'wikipageTopParent': get_root_element(wikipageAll, wikipageObject.id),
        'wikipageObject': wikipageObject,
        'wikipageAll': wikipageAll,
        'versionObject': versionObject,
        'diffObject': diffObject,
    }
    
    return render_to_response(template, extra_context, context_instance=RequestContext(request))
