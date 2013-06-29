from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from player.data.models import Item


def item_list(request):
    items = Item.objects.all()
    return render_to_response('items/item_list.html',
                              {'item_list': items},
                              context_instance=RequestContext(request))


def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render_to_response('items/item_detail.html',
                              {'item': item},
                              context_instance=RequestContext(request))


def views_to_register():
    """ returns views to be registered with dbresolver """
    return (
        (item_list, _('Item listing from all collections')),
        (item_detail, _('Item detail')),
    )
