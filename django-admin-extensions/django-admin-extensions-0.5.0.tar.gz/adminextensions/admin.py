from adminextensions.shortcuts import print_link
from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.timezone import now


def extend(base, extra):
    if extra is None:
        return base

    base = base or {}
    base.update(extra)
    return base


class ExtendedModelAdmin(admin.ModelAdmin):

    object_tools = {
        'add': [],
        'change': [],
        'changelist': [],
    }

    add_form_template = 'adminextensions/change_form.html'
    change_form_template = 'adminextensions/change_form.html'
    change_list_template = 'adminextensions/change_list.html'

    valid_lookups = ()

    def get_object_tools(self, request, method):
        return self.object_tools.get(method, None)

    def add_view(self, request, form_url='', extra_context=None):
        object_tools = self.get_object_tools(request, 'add')
        extra_context = extend(extra_context, {'object_tools': object_tools})
        return super(ExtendedModelAdmin, self).add_view(
            request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        object_tools = self.get_object_tools(request, 'change')
        extra_context = extend(extra_context, {'object_tools': object_tools})
        return super(ExtendedModelAdmin, self).change_view(
            request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        object_tools = self.get_object_tools(request, 'changelist')
        extra_context = extend(extra_context, {'object_tools': object_tools})
        return super(ExtendedModelAdmin, self).changelist_view(
            request, extra_context)

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup.startswith(self.valid_lookups):
            return True
        return super(ExtendedModelAdmin, self).lookup_allowed(
            lookup, *args, **kwargs)

    def construct_changelist(self, request, method):
        from django.contrib.admin.views.main import ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label

        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)
        if actions:
            # Add the action checkboxes if there are any actions available.
            list_display = ['action_checkbox'] + list(list_display)

        ChangeList = self.get_changelist(request)
        cl = ChangeList(
            request, self.model, list_display, list_display_links, list_filter,
            self.date_hierarchy, self.search_fields, self.list_select_related,
            self.list_per_page, self.list_max_show_all, self.list_editable,
            self)

        return cl


def export_tool(context):
    request = context['request']
    model = context['cl'].model

    url = reverse('admin:{0}_{1}_export'.format(
        model._meta.app_label, model._meta.module_name))

    return print_link("Export", url, "model_search")


class ExportableModelAdmin(ExtendedModelAdmin):

    EXPORT_IDS_KEY = 'export_ids'

    object_tools = {
        'changelist': [export_tool],
    }

    def get_actions(self, request):
        actions = super(ExportableModelAdmin, self).get_actions(request)
        actions['export'] = (
            self.__class__.export_action,  # Grab the unbound method
            'export',
            'Export selected {0}'.format(
                unicode(self.model._meta.verbose_name_plural)))
        return actions

    def get_urls(self):
        urls = super(ExportableModelAdmin, self).get_urls()

        app_label = self.model._meta.app_label
        module_name = self.model._meta.module_name
        my_urls = patterns(
            '',
            url(r'^export/$', self.admin_site.admin_view(self.export),
                name='{0}_{1}_export'.format(app_label, module_name)),
        )
        return my_urls + urls

    def export_action(self, request, queryset):
        export_ids = ','.join(map(str, (i.id for i in queryset)))

        export_url = reverse('admin:{0}_{1}_export'.format(
            self.model._meta.app_label, self.model._meta.module_name))

        return redirect('{0}?{1}={2}'.format(
            export_url, self.EXPORT_IDS_KEY, export_ids))

    def export(self, request):
        if 'export_ids' in request.GET:
            export_ids = request.GET[self.EXPORT_IDS_KEY].split(',')
            query_set = self.model.objects.filter(id__in=export_ids)
        else:
            changelist = self.construct_changelist(request, 'export')
            query_set = changelist.query_set

        data = self.make_export_data(request, query_set)
        return self.make_export_response(request, data)

    def make_export_data(self, request, query_set):
        raise NotImplementedError

    def make_export_response(self, request, data):
        response = HttpResponse(data.xls,
                                content_type='application/vnd.ms-excel')

        filename = '{0} - {1}.xls'.format(
            self.model._meta.verbose_name_plural.title(),
            now().date().isoformat())
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            filename)

        return response
