# coding=utf-8
from django.utils.safestring import mark_safe
from django_helpers import add_app_url, get_settings_val
import urls

from django.core.urlresolvers import reverse

from django.db.models import Q
from django.conf.urls import url
from django.http import HttpResponse
from json import dumps
from django.template import Template, loader, RequestContext, Context

from django_helpers.templatetags.static_manger import add_css_file, add_js_file, require_jquery

__author__ = "ajumell"

tables = dict()


def get_table(name):
    return tables[name]()

def get_value(instance, field):
    try:
        value = getattr(instance, field)
    except Exception:
        if field.find('__') > 0:
            fields = field.split('__')
        elif field.find('.') > 0:
            fields = field.split('.')
        else:
            raise
        value = instance
        for field in fields:
            value = getattr(value, field)
    return value

class DataTableColumn(object):
    def __init__(self, field, title, searchable, sortable, title_class=None, title_width=None):
        self.field = field
        self.title = title
        self.searchable = searchable
        self.sortable = sortable
        self.title_class = title_class
        self.title_width = title_width

    def get_html(self, request, instance):
        return get_value(instance, self.field)

    def need_related(self):
        return self.field.find('__') > -1


class DataTableClientRenderedColumn(DataTableColumn):
    """
    This class is still under planning.
    """
    pass


class DataTableTemplateColumn(DataTableColumn):
    """
    A Data table column which will return a rendered
    a template instead of a database field.
    """

    def __init__(self, field, title, searchable, sortable, template,
                 load_template=True, width=None, value_name='value', title_class=None, title_width=None):
        """
        @param field: The name of the field to be passed to the template.
        @param title: Title of the column which will be displayed in the table header.
        @param searchable: jQuery data table option searchable
        @param sortable: jQuery data table option sortable
        @param template: Template to be rendered as the return value.
        This can be either a django.template.Template object or a sting.
        If a string is passed then that template has to be loaded by give
        load_template parameter as True.
        @param load_template: If this parameter is true the template will
        be loaded.
        @param width: Width of the column
        @param value_name: name of the variable that has to be passed to the template.
        Its default value is "value"
        """
        DataTableColumn.__init__(self, field, title, searchable, sortable, title_class, title_width)
        if load_template:
            template = loader.get_template(template)
        self.template = template
        self.width = width
        self.value_name = value_name

    def get_html(self, request, instance):
        value = getattr(instance, self.field)
        template = self.template

        if not isinstance(template, Template):
            template = Template(self.template)

        context = RequestContext(request, {
            self.value_name: value,
            "width": self.width
        })

        return template.render(context)


class DataTable(object):
    query = None
    url_search_parameters = None

    width = None
    class_name = ""
    name = None
    columns = []
    table_id = None
    display_length = 10
    ajax_source = ''
    loading_message = 'Please wait while data is loading'

    ui_themes = False
    bootstrap_theme = True

    scroller = False
    scroller_height = 200

    info_empty = None
    info_loading = None
    info_processing = None

    dom = '<f>t<plir>'
    template = 'data-tables/table.html'

    def __init__(self):
        require_jquery()
        add_js_file('data-tables/js/jquery.dataTables.min.js')

        if not get_settings_val('DATA_TABLES_INCLUDE_CSS', True) and not self.bootstrap_theme:
            add_css_file('data-tables/css/jquery.dataTables.css')

        if get_settings_val('DATA_TABLES_INCLUDE_UI_CSS', self.ui_themes) is True:
            add_css_file('data-tables/css/demo_table_jui.css')

        if self.bootstrap_theme:
            if get_settings_val('BOOTSTRAP_INCLUDE_CSS', False):
                add_css_file('django-helpers/bootstrap/css/bootstrap.min.css')

            add_css_file('data-tables/css/DT_bootstrap.css')
            add_js_file('data-tables/js/DT_bootstrap.js')

        if self.scroller:
            add_css_file('data-tables/css/dataTables.scroller.css')
            add_js_file('data-tables/js/dataTables.scroller.min.js')

    def render(self, kwargs=None, args=None):
        template = loader.get_template(self.template)

        #        if self.bootstrap_theme:
        #            self.dom = False

        #        if self.scroller:
        #            self.dom = 'frtiS'

        context = Context({
            'display_length': self.display_length,
            'dom': self.dom,
            'ajax_source': reverse(self.table_id, kwargs=kwargs, args=args),
            'columns': self.columns,
            "table_id": self.table_id,
            'width': self.width,
            'loading_message': self.loading_message,

            "ui_themes": self.ui_themes,
            "bootstrap_theme": self.bootstrap_theme,

            'scroller': self.scroller,
            'scroller_height': self.scroller_height,

            'info_loading': self.info_loading,
            'info_processing': self.info_processing,
            'info_empty': self.info_empty
        })
        return template.render(context)

    def safe_string(self, kwargs=None, args=None):
        return mark_safe(self.render(kwargs, args))

    def __unicode__(self):
        return self.render()

    def get_query(self, request, kwargs=None):
        if hasattr(self, 'query'):
            return self.query

    def get_data(self, request, kwargs):
        GET = request.GET
        gt = GET.get

        columns = self.columns
        query = self.get_query(request, kwargs)

        extra_params = self.url_search_parameters
        if extra_params is not None:
            filter_dict = {}
            for param_name in extra_params:
                param_value = kwargs.get(param_name, '')
                if param_value != '':
                    filter_dict[param_name] = param_value
            query = query.filter(**filter_dict)

        echo = gt('sEcho')
        start_pos = int(gt('iDisplayStart'))
        max_items = int(gt('iDisplayLength'))
        search_term = gt('sSearch')

        total_length = query.count()
        need_related = False

        fields, sortings, search, i = [], [], None, -1
        for column in columns:
            fields.append(column.field)
            i += 1
            need_related = need_related or column.need_related()

            if column.searchable and search_term != "":
                field = column.field + "__contains"
                kwargs = {field: search_term}
                if search is None:
                    search = Q(**kwargs)
                else:
                    search = search | Q(**kwargs)

        # Sorting
        total_sort_columns = gt('iSortingCols')
        total_sort_columns = int(total_sort_columns)
        while total_sort_columns:
            total_sort_columns -= 1
            column_number = int(gt('iSortCol_%d' % total_sort_columns))
            sort_order = gt('sSortDir_%d' % total_sort_columns)
            column = columns[column_number]
            if column.sortable:
                field = column.field
                if sort_order == 'desc':
                    field = '-' + field
                sortings.append(field)

        fields = tuple(fields)
        if need_related:
            query = query.select_related()
        query = query.order_by(*sortings)
        if search is not None:
            query = query.filter(search)
        query = query.only(*fields)

        current_length = query.count()
        query = query[start_pos:start_pos + max_items]
        datas = []

        for record in query:
            data = []
            for column in columns:
                data.append(column.get_html(request, record))
            datas.append(data)

        result = {
            "aaData": datas,
            "sEcho": echo,
            "iTotalRecords": total_length,
            "iTotalDisplayRecords": current_length,
        }
        return HttpResponse(dumps(result))


def get_data(request, name, **kwargs):
    if not tables.has_key(name):
        return HttpResponse()

    table = tables[name]()

    results = table.get_data(request, kwargs)
    return results


def create_reg(name):
    return "(?P<%s>.*)/" % name


url_prefix = 'data-table-'


def register(data_table):
    add_app_url('data-table', urls)

    if isinstance(data_table, DataTable):
        raise Exception("DataTable class is required not instance.")

    if not issubclass(data_table, DataTable):
        raise Exception("A Sub class of DataTable is required.")

    name = getattr(data_table, 'table_id', None)
    if name is None:
        raise Exception("Table ID is needed.")

    if not name.startswith(url_prefix):
        name = url_prefix + name

    if name in tables:
        raise Exception("A Data table with the given ID already exists.")

    setattr(data_table, 'table_id', name)
    tables[name] = data_table
    reg = "%s/" % name
    extra_url_parameters = data_table.url_search_parameters
    if extra_url_parameters is not None:
        for parameter in extra_url_parameters:
            reg += create_reg(parameter)
    reg += "$"

    pattern = url(r"%s" % reg, get_data, name=name, kwargs={
        "name": name
    })

    urls.urlpatterns.append(pattern)
    return data_table
