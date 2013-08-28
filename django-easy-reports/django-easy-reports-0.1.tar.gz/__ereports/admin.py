import json
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.models import ModelForm
from django.template.context import get_standard_processors
from pasportng.ng.admin import NGModelAdmin
from .models import Report, ReportGroup, ReportTemplate, ReportPermission
from pasportng.pasport.models import PasportOffice
from pasportng.shortcuts.iguardian import GroupObjectPermissionAdmin


class ReportForm(ModelForm):
#    manager = forms.ChoiceField()
    manager = forms.CharField(initial='filter')

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['target_model'].queryset = ContentType.objects.order_by('name')
        if 'instance' in kwargs:
            try:
                extras = json.loads(kwargs['instance'].extras)
                self.fields['manager'].initial = extras['manager']
            except ValueError:
                extras = ''

    class Meta:
        model = Report

    def clean(self):
        self.cleaned_data['extras'] = json.dumps({'manager': self.cleaned_data['manager']})
        return super(ReportForm, self).clean()


def publish(modeladmin, request, queryset):
    queryset.update(published=True)


def unpublish(modeladmin, request, queryset):
    queryset.update(published=False)

#class ReportPermission(GroupObjectPermission):
#    pass


class IReport(NGModelAdmin):
    save_on_top = True
    list_display = ('name', 'target_model', 'datasource', 'published', 'template', 'group', 'preview')
    list_filter = cell_filter = ('target_model', 'published', 'template', 'group')
    form = ReportForm
    actions = [publish, unpublish]
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea({'cols': '20', 'rows': '20'})}, }

    search_fields = ('name', )
    fieldsets = [
        (None, {'fields': (('name', 'target_model', 'published', 'select_related', 'use_distinct'),
                           ('ttl', 'cache_key', 'template', 'group', 'datasource', 'manager'))}),
        ('Columns', {'classes': ['ollapse', 'textarea-fields', ],
                     'fields': [('columns', 'filtering', 'ordering', 'groupby', 'extras'), ]}),
        ('Extra', {'classes': ('collapse textarea-fields',), 'fields': [('rawsql',), ]}),

    ]

    def preview(self, u):
        url = reverse('ereports.do_report', args=[PasportOffice.objects.get(pk=1).code, u.pk, 'html'])
        return '<a target="_new" href="%s">HTML</a>' % url

    preview.allow_tags = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        object = Report.objects.get(pk=object_id)
        import sqlparse

        ctx = {}
        for cp in get_standard_processors():
            ctx.update(**cp(request))
        ctx.update(**object.get_extra_context())
        try:
            qs = object.get_target_queryset(**ctx)
        except ValidationError:
            qs = object.target_model.model_class().objects.all()

        context = {'qs': qs,
                   'fields': sorted(qs.model._meta.fields, key=lambda x: x.verbose_name),
                   'query': sqlparse.format(str(qs.query), reindent=True, keyword_case='upper')}
        if extra_context:
            context.update(extra_context)

        return super(IReport, self).change_view(request, object_id, form_url, context)


class ReportPermissionForm(ModelForm):
#    content_type = forms.ModelChoiceField( ContentType.objects.all(), initial="something")

    def __init__(self, *args, **kwargs):
        super(ReportPermissionForm, self).__init__(*args, **kwargs)
        self.fields['content_type'].initial = ContentType.objects.get_for_model(Report)
        self.fields['permission'].initial = Permission.objects.get(content_type__app_label='ereports', codename='run_report')

    class Meta:
        model = ReportPermission

class ReportPermissionAdmin(GroupObjectPermissionAdmin):
#    readonly_fields = ['content_type', ]

    form = ReportPermissionForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs.get("request", None)
        formfield = super(ReportPermissionAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        ct = ContentType.objects.get_for_model(Report)
        if db_field.name == 'permission':
            formfield.queryset = Permission.objects.filter(content_type=ct)
        elif db_field.name == 'object_pk':
            formfield = forms.ChoiceField(Report.objects.values_list('id', 'name'))
        elif db_field.name == 'content_type':
            formfield.queryset = ContentType.objects.filter(pk=ct.pk)

        return formfield

    def queryset(self, request):
        ct = ContentType.objects.get_for_model(Report)
        return super(ReportPermissionAdmin, self).queryset(request).filter(content_type=ct)


admin.site.register(Report, IReport)
admin.site.register(ReportPermission, ReportPermissionAdmin)
admin.site.register(ReportTemplate, NGModelAdmin)
admin.site.register(ReportGroup, NGModelAdmin)

__iadmin__ = ((Report, IReport), (ReportTemplate, NGModelAdmin), (ReportGroup, NGModelAdmin), (ReportPermission, ReportPermissionAdmin))
