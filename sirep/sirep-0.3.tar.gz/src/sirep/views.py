from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.template.defaultfilters import slugify
from django.http import HttpResponse

import sirep
from sirep.constants import GET_PARAM_DATE_LOWER, GET_PARAM_DATE_UPPER, GET_PARAM_PAGE, GET_PARAM_PER_PAGE
from sirep.conf import get_setting
from sirep.forms import ReportForm
from sirep.writers import UnicodeWriter

REPORT_NUMBER_OF_ITEMS_PER_PAGE = get_setting('REPORT_NUMBER_OF_ITEMS_PER_PAGE')

@staff_member_required
def reports_list(request):
    """
    List of all reports registered.

    :param django.http.HttpRequest request:
    :return django.http.HttpResponse:
    """
    reports = sirep.all_reports()
    all_reports = []
    for slug, report in reports:
        all_reports.append(sirep.base.ReportContainer(slug, report))
    context = {'reports': all_reports, 'GET_PARAM_PER_PAGE': GET_PARAM_PER_PAGE}
    return render_to_response('sirep/list.html', context, context_instance=RequestContext(request))

@staff_member_required
def view_report(request, slug):
    """
    Report (sirep.base.Report)

    :param django.http.HttpRequest request:
    :param str slug: Report slug.
    :return django.http.HttpResponse:
    """
    report = sirep.get_report(slug)(request) # Getting report by slug
    report_form = ReportForm(request.GET, report=report) # Getting the report form
    data = {
        'report_form': report_form,
        'report': report,
        'title': report.verbose_name,
        'slug': slug,
        'GET_PARAM_DATE_LOWER': GET_PARAM_DATE_LOWER,
        'GET_PARAM_DATE_UPPER': GET_PARAM_DATE_UPPER,
        'GET_PARAM_PAGE': GET_PARAM_PAGE,
        'GET_PARAM_PER_PAGE': GET_PARAM_PER_PAGE,
        'REPORT_NUMBER_OF_ITEMS_PER_PAGE': REPORT_NUMBER_OF_ITEMS_PER_PAGE,
        }

    return render_to_response('sirep/view.html', data, context_instance=RequestContext(request))

@staff_member_required
def view_csv_report(request, slug):
    """
    CSV report (sirep.base.Report).

    :param django.http.HttpRequest request:
    :param str slug: Report slug.
    :return django.http.HttpResponse:
    """
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s_%s_report.csv' % (slug, slugify(request.GET.urlencode()))

    report = sirep.get_report(slug)(request)

    writer = UnicodeWriter(response)
    writer.writerow([h for h in report.get_headers()])

    for item in report.items:
        try:
            writer.writerow(item)
        except:
            pass
    return response
