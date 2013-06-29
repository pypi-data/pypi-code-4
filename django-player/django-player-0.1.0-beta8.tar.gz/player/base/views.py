from django.http import Http404
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist, RequestContext
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template

from configfield import params
from player.data.params import CollectionParam


DEFAULT_ITEMS_NUMBER = 20
DEFAULT_COLLECTION_TEMPLATE = 'item_list.html'
DEFAULT_ITEM_TEMPLATE = 'item_detail.html'


def render_template(request, template_name=None):
    try:
        return direct_to_template(request, template=template_name)
    except TemplateDoesNotExist:
        raise Http404()


def collection_template(request, template_name=DEFAULT_COLLECTION_TEMPLATE, collection_slug=None, items_number=DEFAULT_ITEMS_NUMBER):
    from player.data.models import Collection
    if collection_slug is None:
        raise Http404()
    collection = Collection.objects.get(slug=collection_slug)
    items = collection.item_set.all()
    if items_number != -1:
        items = items[:items_number]
    return render_to_response(template_name, {'item_list': items},
                              context_instance=RequestContext(request))


def item_template(request, template_name=DEFAULT_ITEM_TEMPLATE, item_id=None):
    from player.data.models import Item
    if item_id is None:
        raise Http404()
    item = Item.objects.get(pk=item_id)
    return render_to_response(template_name, {'item': item},
                              context_instance=RequestContext(request))


def views_to_register():
    """ returns views to be registered with dbresolver """
    return (
        {'view': render_template,
         'label': _('Generic view to render a template'),
         'params': (
             params.Template(name='template_name', label=_('Template to be rendered')),
         )},
        {'view': collection_template,
         'label': _('Generic view to render a collection'),
         'params': (
             params.Template(name='template_name', label=_('Template to be rendered'), default=DEFAULT_COLLECTION_TEMPLATE),
             CollectionParam(name='collection_slug', label=_('Collection to be rendered')),
             params.Integer(name='items_number', default=20, label=_('Number of items to be rendered')),
         )},
        {'view': item_template,
         'label': _('Generic view to render a item in a collection'),
         'params': (
             params.Template(name='template_name', label=_('Template to be rendered'), default=DEFAULT_ITEM_TEMPLATE),
         )},
    )
