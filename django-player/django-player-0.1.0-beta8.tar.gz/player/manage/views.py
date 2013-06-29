from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from player.crawler.models import Report
from player.data.models import Collection


@login_required
def index(request):
    collections_draft = Collection.objects.all().draft()
    reports_error = Report.objects.all().with_errors()
    return render_to_response(
        "manage/index.html",
        {'collection_list': collections_draft,
         'reports': reports_error},
        context_instance=RequestContext(request),
    )


@login_required
def generic_delete(request):
    content_type_id = request.POST.get('content_type_id', None)
    content_id = request.POST.get('content_id', None)
    if content_type_id is None or content_id is None:
        raise Http404

    content_type = ContentType.objects.get(id=int(content_type_id))
    if request.user.has_perm('delete_%s' % content_type.model) or \
       request.user.has_perm('%s.delete_%s' % (content_type.app_label, content_type.model)):
        obj = content_type.get_object_for_this_type(id=content_id)
        obj.delete()
        messages.success(request, _('%(content)s deleted successfully') % {'content': obj})
    else:
        messages.error(request, _('You do not have permission to delete %(model)s objects') % {'model': content_type.model})
    next_url = request.POST.get('next_url', request.META.get('HTTP_REFERER', '/'))
    return HttpResponseRedirect(next_url)


@login_required
def content_delete(request):
    collection_id = request.POST.get('collection_id', None)
    if not collection_id:
        collection_id = request.POST.get('content_id', None)

    if collection_id is None:
        raise Http404

    if request.user.has_perm('delete_item') or \
       request.user.has_perm('data.delete_item'):
        collection = Collection.objects.get(id=collection_id)
        for item in collection.item_set.with_invalids():
            item.delete()
        messages.success(request, _('Items removed properly'))
    else:
        messages.error(request, _('You do not have permission to delete items objects'))
    next_url = request.POST.get('next_url', request.META.get('HTTP_REFERER', '/'))
    return HttpResponseRedirect(next_url)
