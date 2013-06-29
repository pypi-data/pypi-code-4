from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from player.crawler.models import Report
from player.data.models import Collection


@login_required
def report_index(request):
    reports = Report.objects.all()
    return render_to_response(
        "crawler/report_index.html",
        {'reports': reports},
        context_instance=RequestContext(request),
    )


@login_required
def report_view(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    collections = Collection.objects.filter(crawler_collection=report.crawler_collection)
    return render_to_response(
        "crawler/report_view.html",
        {'report': report,
         'collections': collections,
         'added_items': report.added_items.all().order_by('collection'),
         'updated_items': report.updated_items.all().order_by('collection'),
        },
        context_instance=RequestContext(request),
    )


@login_required
def crawled_view(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    return render_to_response(
        "crawler/crawled_view.html",
        {'report': report},
        context_instance=RequestContext(request),
    )
