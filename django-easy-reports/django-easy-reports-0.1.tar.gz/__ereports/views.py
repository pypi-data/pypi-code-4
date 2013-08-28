# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from six import StringIO, u
import os
import datetime
import logging
import unicodecsv as csv
from ho import pisa
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.loading import get_model
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import get_standard_processors, Context, RequestContext
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from guardian.shortcuts import get_objects_for_user
from kiowa.utils import get_attr
from kiowa.utils.language import cachedproperty
from pasportng.autocache import cache
from pasportng.pasport.fields import MonthField
from pasportng.pasport.models import PasportOffice, Payslip, Payroll
from pasportng.pasport.views2 import SelectedOfficeMixin
from . import math
from .models import Report
from .templatetags.ereports import _get_field, process_queryset_field


logger = logging.getLogger("security")

PAYROLL_FIELDS_AND_LABELS = [
    {'field': 'contract.employee.index_no', 'label': 'Index', },
    {'field': 'contract.employee.first_name', 'label': 'First Name', },
    {'field': 'contract.employee.last_name', 'label': 'Last Name', },
    {'field': 'contract.type', 'label': 'Contract Type', },
    {'field': 'contract.work_level', 'label': 'Work Level', },
    {'field': 'contract.admin_duty_station', 'label': 'Duty Station', },
    {'field': 'contract.initial_eod', 'label': 'Initial EOD', },
    {'field': 'contract.eod', 'label': 'Contract EOD', },
    {'field': 'contract.nte', 'label': 'NTE', },
    {'field': 'basic_salary', 'label': 'Basic Salary', },
    {'field': 'actual_salary', 'label': 'Actual Salary', },
    {'field': 'social_insurance_wfp', 'label': 'Social Insurance (WFP-Emp)', },
    {'field': 'other_allowance', 'label': 'Other Allowances', },
    {'field': 'overtime_cash_compensation', 'label': 'Overtime', },
    {'field': 'hazard_pays_compensation', 'label': 'DDSS', },
    {'field': 'adjustment_credit', 'label': 'Adjustment Credit', },
    {'field': 'total_earning', 'label': 'Total Earning', },
    {'field': 'staff_association', 'label': 'Staff Association', },
    {'field': 'social_insurance_emp', 'label': 'Social Insurance (Emp-Plan)', },
    {'field': 'health_insurance_emp', 'label': 'Health Insurance (Emp)', },
    {'field': 'other_charges', 'label': 'Other Charges', },
    {'field': 'advance_return_amount', 'label': 'Advance return', },
    {'field': 'adjustment_debit', 'label': 'Adjustment debit', },
    {'field': 'total_deduction', 'label': 'Total Deduction', },
    {'field': 'monthly_bills', 'label': 'Bills', },
    {'field': 'net_salary_without_bills', 'label': 'Net Salary', },
    {'field': 'health_insurance_wfp', 'label': 'Health Insurance (WFP)', },
    {'field': 'social_insurance_wfp_to_plan', 'label': 'Social Insurance (WFP-Plan)', },
    {'field': 'death_disability', 'label': 'Death and Disability', },
    {'field': 'total_wfp_cost', 'label': 'Total Cost', },
    {'field': 'contract.fund_reservation', 'label': 'Fund Reservation', },
    {'field': 'contract.internal_order', 'label': 'Internal order', },
    {'field': 'contract.wbs_element', 'label': 'WBS Element', },
    {'field': 'contract.gl_account', 'label': 'GL Account', },
    {'field': 'contract.cost_category', 'label': 'Cost Category', },
    {'field': 'contract.availability_type', 'label': 'Availability Type', },
    {'field': 'starting_date', 'label': 'Salary Period', },
    {'field': 'payroll.month', 'label': 'Payment Month', },
    {'field': 'payroll.exchange_rate', 'label': 'Exchange Rate', },
]

PAYROLL_FIELDS = [x['field'] for x in PAYROLL_FIELDS_AND_LABELS]
PAYROLL_LABELS = [x['label'] for x in PAYROLL_FIELDS_AND_LABELS]


class ProtectedViewMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)


class OfficeMixin(object):
    @cachedproperty
    def office(self):
        param = self.kwargs.get('office', None)
        user = self.request.user
        if param:
            try:
                office = PasportOffice.objects.get(pk=int(param))
            except ValueError:
                office = PasportOffice.objects.get(code=param)
            if not self.request.user.is_superuser:
                all_perms = self.request.user.get_all_permissions()
                if not bool(all_perms.intersection(['ereports.run_report', 'pasport.can_administer_pasport'])):
                    logger.error("Error on permissions")
                    raise PermissionDenied("No permissions")

                if user.office != office and not user.aditional_offices.filter(pk=office.pk).exists():
                    logger.error("No access to office: %s", office)
                    raise PermissionDenied("No access to office: %s", office)
        else:
            raise Http404
        return office


class CsvViewMixin(object):
    list_display = []

    def render_to_csv(self, context, **response_kwargs):
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment;filename="%s.csv"' % self.get_filename()

        writer = csv.writer(response, escapechar="\\", delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow([h for h in context['headers']])
        ctx = RequestContext(self.request, {})
        for obj in context['queryset']:
            ctx['obj'] = obj
            row = []
            for fieldname in context['columns']:
                row.append(process_queryset_field(ctx, obj, fieldname))
            writer.writerow(row)
        return response


class PdfViewMixin(object):
    list_display = []

    def render_to_pdf(self, context, **response_kwargs):
        context = self.get_context_data(pagesize='A0', object_list=self.get_queryset())
        html = loader.render_to_string(self.template_name, context)
        result = StringIO.StringIO()
        pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result)
        if not pdf.err:
            response = HttpResponse(mimetype='application/pdf')
            response['Content-Disposition'] = 'attachment;filename="payroll_%(office)s_%(year)s_%(month)s.pdf"' % self.kwargs
            response.write(result.getvalue())
            return response


class ExcelViewMixin(object):
    list_display = []

    def _get_style_for_field(self, fieldname):
        field = _get_field(self.model, fieldname)

        FORMATS = {
            models.fields.DateField: 'DD MMM-YY',
            MonthField: 'DD MMM-YY',
            datetime.datetime.date: 'DD MMM-YY',
            datetime.date: 'DD MMM-YY',
            datetime: 'DD MMM-YY',
            models.fields.DateTimeField: 'DD MMD YY hh:mm',
            models.fields.IntegerField: '#,##',
            models.fields.DecimalField: '#,##0.00',
        }

        default = FORMATS.get(type(field), 'general')
        CUSTOM = {'basic_salary': '#,##0.00'}
        return '', CUSTOM.get(fieldname, default)

    def render_to_xls(self, context, **response_kwargs):
        from xlwt import Workbook, XFStyle, easyxf

        response = HttpResponse(mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename="%s.xls"' % self.get_filename()

        w = Workbook(encoding='utf-8')
        w.owner = b'UN World Food Programme'

        ws = w.add_sheet('Payroll')
        style = XFStyle()

        row = 0
        heading_xf = easyxf('font:height 200; font: bold on; align: wrap on, vert centre, horiz center')
        ws.write(row, 0, '#', style)

        for col, fieldname in enumerate(context['headers'], start=1):
            ws.write(row, col, fieldname, heading_xf)
            ws.col(col).width = 5000
        ws.row(row).height = 500

        # we have to prepare all the styles before going into the loop
        # to avoid the "More than 4094 XFs (styles)" Error
        styles = {fieldname: easyxf(*self._get_style_for_field(fieldname)) for fieldname in context['columns']}
        ctx = RequestContext(self.request, {})
        for row, obj in enumerate(context['queryset'], start=row + 1):
            ws.write(row, 0, row)
            ctx['obj'] = obj
            for col, fieldname in enumerate(context['columns'], start=1):
                value = process_queryset_field(ctx, obj, fieldname, raw=True)
                style = styles[fieldname]
                try:
                    ws.write(row, col, value, style=style)
                except Exception:
                    ws.write(row, col, smart_str(value), style=style)

        w.save(self.get_filename())
        response.write(open(self.get_filename()).read())

        return response


class OfficeList(ListView):
    model = PasportOffice
    template_name = 'ereports/payroll/office.html'


class PayrollTemplateResponse(TemplateResponse):
    def __init__(self, request, template, context=None, mimetype=None, status=None, content_type=None, current_app=None):
        super(PayrollTemplateResponse, self).__init__(request, template, context, mimetype, status, content_type, current_app)

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)
        content = template.render(context)
        return content


class PayrollView(SelectedOfficeMixin, CsvViewMixin, ExcelViewMixin, OfficeMixin, ListView):
    """ Payroll report in XLS, CSV, HTML
    """
    template_name = 'ereports/payroll/payroll2.html'
    permissions = []
    model = Payslip
    context_object_name = "payslips"
    allow_empty = True
    list_display = PAYROLL_FIELDS
    response_class = PayrollTemplateResponse

    def get_filename(self):
        import tempfile

        return os.path.join(tempfile.gettempdir(), 'payroll_%(office)s_%(year)s_%(month)s.%(format)s' % self.kwargs)

    def get_cache_key(self, prefix='qs'):
        return "%s_%s" % (prefix, ('payroll_%(office)s_%(year)s_%(month)s_%(format)s' % self.kwargs))

    def get_queryset(self):
        office = self.selected_office
        month = self.kwargs['month']
        year = self.kwargs['year']
        key = self.get_cache_key()
        self.payroll = Payroll.objects.get(office=office, month__month=month, month__year=year)

        if key in cache.cache:
            ret = cache.cache.get(key, version=1)
        else:
            ret = Payslip.nopartial.select_related().filter(payroll=self.payroll)
        cache.cache.set(key, ret, cache.YEAR)
        return ret

    def render_to_response(self, context, **response_kwargs):
        format = self.kwargs.get('format', 'html')
        SUMMARY_FIELDS = ['social_insurance_wfp',
                          'other_allowance', 'overtime_cash_compensation', 'hazard_pays_compensation', 'adjustment_credit',
                          'actual_salary',
                          'total_earning', 'staff_association', 'social_insurance_emp', 'health_insurance_emp', 'other_charges',
                          'advance_return_amount', 'adjustment_debit', 'total_deduction', 'monthly_bills',
                          'net_salary_without_bills', 'health_insurance_wfp', 'social_insurance_wfp_to_plan', 'death_disability',
                          'total_wfp_cost']

        SUBTOTAL_FIELDS = SUMMARY_FIELDS
        context.update({'queryset': self.get_queryset().order_by('contract__actual_duty_station__name'),
                        'headers': PAYROLL_LABELS,
                        'payroll': self.payroll,
                        'SUMMARY_FIELDS': SUMMARY_FIELDS,
                        'SUBTOTAL_FIELDS': SUBTOTAL_FIELDS,
                        'columns': PAYROLL_FIELDS})

        regrouped = math.Regrouper()
        totals = math.Totalizer()
        if format == 'html':
            for record in self.get_queryset():
                ds = record.contract.actual_duty_station.name
                regrouped[ds].append(record)

                for f in SUMMARY_FIELDS:
                    attr = get_attr(record, f)
                    if callable(attr):
                        totals[f].append(attr())
                    else:
                        totals[f].append(attr)

            context.update({'regrouped': regrouped.items(),
                            'totals': totals})

            return self.response_class(request=self.request,
                                       template=self.get_template_names(),
                                       context=context,
                                       **response_kwargs)
        elif format == 'csv':
            return self.render_to_csv(context, **response_kwargs)
        elif format == 'xls':
            return self.render_to_xls(context, **response_kwargs)
            # elif format == 'pdf':
        #     return self.render_to_pdf(context, **response_kwargs)
        return HttpResponseServerError(format)


class ReportIndex(SelectedOfficeMixin, TemplateView):
    """ Index of all available reports for an office
    """
    template_name = 'ereports/index.html'
    permissions = ['ereports.read_report', 'ereports.run_report']

    def get_context_data(self, **kwargs):
        user = self.request.user
        return dict(payrolls=Payroll.objects.select_related().filter(office=self.selected_office).order_by('-month'),
                    reports=get_objects_for_user(user, 'ereports.run_report', Report).filter(published=True).order_by('name'))


class ReportConfigView(SelectedOfficeMixin, DetailView):
    template_name = 'ereports/configure.html'
    permissions = ['ereports.read_report']
    model = Report
    pk_url_kwarg = 'report'


class ReportView(SelectedOfficeMixin, TemplateView, CsvViewMixin, ExcelViewMixin):
    template_name = 'ereports/report.html'
    permissions = ['ereports.read_report']

    def get_filename(self):
        return self.report.name

    def get_report(self):
        pk = self.kwargs.get('report', None)
        return Report.objects.get(pk=pk)

    def get_context_data(self, **kwargs):
        return kwargs

    def render_to_response(self, context, **response_kwargs):
        if self.report.template:
            template = loader.get_template_from_string(self.report.template.body)
            return HttpResponse(template.render(RequestContext(self.request, context)))
        return super(ReportView, self).render_to_response(context, **response_kwargs)

    def render_to_raw(self, context):
        template = loader.get_template('ereports/raw.html')
        return HttpResponse(template.render(RequestContext(self.request, context)), mimetype='text/plain')

    def get(self, request, *args, **kwargs):
        format = self.kwargs.get('format', 'html')
        self.report = self.get_report()
        self.model = self.report.target_model.model_class()
        ctx = {}
        for cp in get_standard_processors():
            ctx.update(**cp(request))
        ctx.update(**self.report.get_extra_context())

        cols, titles = self.report.get_columns()

        context = self.get_context_data(
            selected_office=self.selected_office,
            headers=titles,
            model=str(self.model.__name__),
            columns=cols,
            filters=self.report.get_target_filtering(**ctx),
            queryset=self.report.get_target_queryset(**ctx).all(),
            report=self.report
        )

        if format == 'html':
            return self.render_to_response(context)
        elif format == 'csv':
            return self.render_to_csv(context)
        elif format == 'xls':
            return self.render_to_xls(context)
        # elif format == 'pdf':
        #     return self.render_to_pdf(context)
        elif format == 'raw':
            return self.render_to_raw(context)
        return HttpResponseServerError(format)


def get_model_meta(request, owner, app_name, model_name):
    model = get_model(app_name, model_name)
    fields = sorted(model._meta.fields, key=lambda x: x.verbose_name)
    return render_to_response('ereports/meta_info.html', Context({'owner': owner, 'fields': fields}))
