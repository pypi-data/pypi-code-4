from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext
from django.utils import simplejson as json
from django.views.generic import list_detail

from player.crawler import get_backend
from player.crawler.models import Report
from player.crawler.exceptions import CrawlerHttpException
from player.data.forms import (CollectionGroupForm, CollectionForm,
                           ScrapAssociationWizard, CollectionCodeFormStep,
                           FieldMappingFormStep, ExtractionParamsFormStep,
                           DeleteItemsFormStep, SelectBackendFormStep)
from player.data.models import CollectionGroup, Item, Collection, CollectionField


# ----- collection group views -----

@login_required
def collectiongroup_list(request):
    return list_detail.object_list(
        request,
        queryset=CollectionGroup.objects.all(),
        template_name="data/collectiongroup_list.html",
        template_object_name="collectiongroup",
    )


@login_required
def collectiongroup_view(request, slug):
    collectiongroup = get_object_or_404(CollectionGroup, slug=slug)
    return render_to_response(
        "data/collectiongroup_view.html",
        {'collectiongroup': collectiongroup},
        context_instance=RequestContext(request),
    )


@login_required
def collectiongroup_add(request):
    if request.method == 'POST':
        form = CollectionGroupForm(request.POST)
        if form.is_valid():
            collectiongroup = form.save()
            messages.success(request, ugettext(u'The collectiongroup was successfully added'))
            return HttpResponseRedirect(reverse('collectiongroup_view', args=(collectiongroup.slug, )))
    else:
        form = CollectionGroupForm()
    return render_to_response(
        "data/collectiongroup_edit.html",
        {'form': form, 'collectiongroup': None},
        context_instance=RequestContext(request),
    )


@login_required
def collectiongroup_edit(request, slug):
    pass


# ----- Collection views -----


@login_required
def collection_add(request, collection=None):
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            newcollection = form.save()
            form.field_formset.instance = newcollection
            form.field_formset.save()
            if collection:
                messages.success(request, ugettext(u'The collection was successfully modified'))
            else:
                messages.success(request, ugettext(u'The collection was successfully added'))
            return HttpResponseRedirect(reverse('collection_view', args=(newcollection.collectiongroup.slug, newcollection.slug, )))
    else:
        form = CollectionForm(instance=collection)
    return render_to_response(
        "data/collection_edit.html",
        {'form': form, 'collection': collection},
        context_instance=RequestContext(request),
    )


@login_required
def collection_list(request):
    return list_detail.object_list(
        request,
        queryset=Collection.objects.all().order_by('collectiongroup'),
        template_name="data/collection_list.html",
        template_object_name="collection",
    )


@login_required
def collection_view(request, slug, collection_slug):
    collection = get_object_or_404(Collection.objects.select_related(),
                                   slug=collection_slug)
    return render_to_response(
        "data/collection_view.html",
        {'collection': collection,
        },
        context_instance=RequestContext(request),
    )


@login_required
def collection_edit(request, slug, collection_slug):
    collection = get_object_or_404(Collection.objects.select_related(),
                                   slug=collection_slug)
    return collection_add(request, collection)


@login_required
def collection_edit_fields(request, slug, collection_slug):
    """ used for inplace edit in collection_view """
    # TODO: adapt to model changes in #42 ticket
    field_id = request.POST['id']
    value = request.POST['value']
    collection = get_object_or_404(Collection, slug=collection_slug)
    field = CollectionField.objects.get(collection=collection, slug=value)
    if field_id == 'repr-field':
        collection.repr_field = field
    collection.save()
    return HttpResponse(value)


@login_required
def collection_fields_in_json(request, slug, collection_slug):
    """ Returns JSON format of editable fields with inplace edit. Used in collection_view """
    field_id = request.GET['id']
    collection = get_object_or_404(Collection, slug=collection_slug)
    if field_id == 'repr-field':
        fields = [field.slug for field in collection.fields.all()]
    results = {}
    for field in fields:
        results[field] = field
    json_data = json.dumps(results)
    return HttpResponse(json_data, mimetype='application/json')


@login_required
def collection_publish(request, slug, collection_slug):
    collection = get_object_or_404(Collection, slug=collection_slug)
    collection.status = 'published'
    collection.save()
    collection.item_set.with_invalids().delete()
    messages.success(request, ugettext('Collection published successfully'))
    return HttpResponseRedirect(collection.get_absolute_url())


@login_required
def collection_unpublish(request, slug, collection_slug):
    collection = get_object_or_404(Collection, slug=collection_slug)
    collection.status = 'draft'
    collection.save()
    messages.success(request, ugettext('Collection unpublished successfully'))
    return HttpResponseRedirect(collection.get_absolute_url())


@login_required
def collection_crawl(request, slug, collection_slug):
    """ Launch a crawling job for a collection """
    collection = get_object_or_404(Collection.objects.select_related(), slug=collection_slug)
    if not collection.is_mapped():
        raise Http404('Collection %s is not mapped.' % collection)
    get_backend(collection.crawler_collection.backend).extract_collection_data(collection.crawler_collection)
    try:
        report = Report.objects.filter(crawler_collection=collection.crawler_collection).latest()
        code_str = report.get_return_code_display()
        if report.return_code == 'suc':
            inform = messages.success
        else:
            inform = messages.error
        message = u'<a href="%s">%s</a>' % (reverse('report_view', args=(report.id, )),
                                            ugettext('Collection crawled report: %(code)s') % {'code': code_str})
        inform(request, message)
    except Report.DoesNotExist:
        messages.error(request, ugettext('Collection crawled report not found. Probably an error has occurred'))
    except CrawlerHttpException, excp:
        messages.error(request,
                       ugettext('Crawler connection failed: [%(code)s]: %(error)s') %
                           {'code': excp.http_code, 'error': excp.error})
    return HttpResponseRedirect("%s#elements-tab" % collection.get_absolute_url())


@login_required
def collection_toggle_crawling_checked(request, slug, collection_slug):
    collection = get_object_or_404(Collection, slug=collection_slug)
    if request.method == "POST":
        collection.crawling_checked = not collection.crawling_checked
        collection.save()
    return HttpResponseRedirect(reverse("collection_view", None,
                                        kwargs={'slug': slug,
                                                'collection_slug': collection_slug}) + "#steps-tab")


@login_required
def scrap_association(request, slug, collection_slug):
    """ Map a collection with a crawler collection """
    collection = get_object_or_404(Collection.objects.select_related(), slug=collection_slug)
    if not bool(collection.fields.all()):
        raise Http404('Collection %s have no fields defined so it can not be mapped.' % collection)
    if not collection.crawler_collection:
        wizard = ScrapAssociationWizard((SelectBackendFormStep, CollectionCodeFormStep, FieldMappingFormStep, ExtractionParamsFormStep), collection=collection)
    else:
        wizard = ScrapAssociationWizard((SelectBackendFormStep, CollectionCodeFormStep, FieldMappingFormStep, ExtractionParamsFormStep, DeleteItemsFormStep), collection=collection)
    if collection.crawler_collection:
        collection_code = collection.crawler_collection.collection_code
    else:
        collection_code = None
    return wizard(request, extra_context={'collection_code': collection_code})


# ----- Item views -----


@login_required
def item_view(request, slug, item_id):
    item = get_object_or_404(Item.objects.with_deleted(), pk=item_id)
    if not item.is_valid:
        messages.error(request,
                       ugettext(u'This item is not valid.'))
    return render_to_response(
        "data/item_view.html",
        {'item': item},
        context_instance=RequestContext(request),
    )


@login_required
def item_validate(request, slug, item_id):
    item = get_object_or_404(Item.objects.with_deleted(), pk=item_id)
    if item.content:
        if len(Item.objects.filter(uid=item.uid, collection=item.collection,
                                   is_valid=True, is_deleted=False)):
            Item.objects.get(uid=item.uid, collection=item.collection,
                             is_valid=True, is_deleted=False).delete()
        item.is_valid = True
        item.save()
    else:
        Item.objects.get(uid=item.uid, collection=item.collection,
                         is_valid=True, is_deleted=False).delete()
        item.delete()
    messages.success(request, ugettext(u'This items has been validate'))

    return HttpResponseRedirect(reverse('player.data.views.item_view', args=(slug, item_id)))
