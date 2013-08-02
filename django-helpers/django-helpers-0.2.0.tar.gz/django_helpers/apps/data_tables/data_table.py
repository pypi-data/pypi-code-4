# coding=utf-8
from json import dumps
from math import ceil
from types import StringTypes, TypeType

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum, Avg, Min, Max, Count
from django.http import HttpResponse
from django.template import loader, Context

from django_helpers.apps.static_manager import jQueryURL, AjaxCsrfURL
from django_helpers.utils.models import last_query


__author__ = 'ajumell'

_annotates = {
    'sum': Sum,
    'avg': Avg,
    'min': Min,
    'max': Max,
    'count': Count,
}


def validate_annotate(name):
    return name in _annotates


# noinspection PyMethodParameters
class DataTableMeta(type):
    def __new__(cls, name, bases, attrs):
        from columns import DataTableColumn

        new_class = type.__new__(cls, name, bases, attrs)

        # This can be done now. Now think about a better syntax.
        fields = []
        for attr_name, attr in attrs.iteritems():
            if isinstance(attr, DataTableColumn):
                fields.append(attr)

        # no_columns = '___no_columns___'
        # old_columns = getattr(new_class, 'columns', no_columns)

        # if old_columns not in (old_columns, None):
        #     warn(DeprecationWarning('New Columns methods should be used now.'))
        # elif len(fields) > 0:
        #     new_class.columns = fields

        return new_class


class DataTable(object):
    __metaclass__ = DataTableMeta

    send_sql = True

    aggregate_fields = []
    has_js = True
    query = None
    url_search_parameters = None

    width = None
    class_name = ""
    name = None
    columns = []
    table_id = None
    display_length = 10
    display_lengths = [2, 3, 5, 10, 25, 50, 100]
    loading_message = 'Please wait while data is loading'

    ui_themes = False
    bootstrap_theme = True

    scroller = False
    scroller_height = 200

    info_empty = None
    info_loading = None
    info_processing = None

    row_id = None

    dom = None
    template = 'data-tables/table-html.html'
    js_template = 'data-tables/table-js.js'

    render_initial = False

    form_filter = None

    def __init__(self, request=None):

        if len(self.columns) is 0:
            raise Exception('There are no columns.')

        self.request = request

        js_files = [
            jQueryURL,
            AjaxCsrfURL,
            'data-tables/js/jquery-data-tables-min.1.9.4.js'
        ]

        if self.bootstrap_theme:
            js_files.append('data-tables/js/DT_bootstrap.js')

        self.columns = self.columns[:]

        if self.scroller:
            js_files.append('data-tables/js/dataTables.scroller.min.js')

        if self.scroller:
            js_files.append('data-tables/js/dataTables.scroller.min.js')

        if self.is_editable():
            js_files.append('js/jquery.jeditable.js')
            js_files.append('data-tables/js/dataTable.editable.js')

        if self.send_sql:
            js_files.append('data-tables/js/dataTable.sql.js')
            js_files.append('js/prettify.min.js')

        self.js_files = js_files

        self._data = None

        filter_form = self.form_filter
        if filter_form is not None:
            if type(filter_form) is TypeType:
                filter_form = filter_form()
                self.form_filter = filter_form

            if filter_form.form_id is None:
                raise

    def __unicode__(self):
        return self.render()

    def is_editable(self):
        if not hasattr(self, '_is_editable'):
            is_editable = False
            editable_columns = []
            i = 0
            for column in self.columns:
                i += 1
                if column.editable is True:
                    is_editable = True
                    editable_columns.append(i)
            self._is_editable = is_editable
            self._editable_columns = editable_columns
        return self._is_editable

    def generate_render_data(self, kwargs=None, args=None):
        if self._data is None:

            render_initial = self.render_initial
            if render_initial and args is not None:
                raise Exception('Arguments cannot be used when using initial data')

            is_editable = self.is_editable()
            table_id = self.table_id
            try:
                ajax_source = reverse(self.table_id, kwargs=kwargs, args=args)
                save_source = reverse(self.table_id + '_save', kwargs=kwargs, args=args)
            except Exception:
                from views import has_registered

                if not has_registered(table_id):
                    t = type(self)
                    m = t.__module__
                    n = t.__name__
                    raise Exception('This table "%s.%s" is not registered.' % (m, n))
                raise Exception('Django helpers is not added in root urls.')

            self._data = {
                'display_length': self.display_length,
                'display_lengths': self.display_lengths,
                'dom': self.dom,
                'ajax_source': ajax_source,
                'save_source': save_source,
                'columns': self.columns,
                "table_id": table_id,
                'width': self.width,
                'loading_message': self.loading_message,

                "ui_themes": self.ui_themes,
                "bootstrap_theme": self.bootstrap_theme,

                'is_editable': is_editable,

                'scroller': self.scroller,
                'scroller_height': self.scroller_height,

                'info_loading': self.info_loading,
                'info_processing': self.info_processing,
                'info_empty': self.info_empty,

                'initial_data': render_initial
            }

            filter_form = self.form_filter
            if filter_form is not None:
                self._data['has_form'] = True
                self._data['form_id'] = filter_form.form_id

            if is_editable:
                self._data['editable_columns'] = self._editable_columns

            if render_initial:
                self.initial_data(kwargs)

        return self._data

    def render_template(self, template, kwargs=None, args=None):
        template = loader.get_template(template)
        context = Context(self.generate_render_data(kwargs, args))
        return template.render(context)

    def render_js(self):
        return self.render_template(self.js_template)

    def render(self):
        return self.render_template(self.template)

    def safe_string(self, kwargs=None, args=None):
        self.generate_render_data(kwargs, args)
        return mark_safe(self.render())

    # noinspection PyUnusedLocal
    def get_query(self, request, kwargs=None):
        if hasattr(self, 'query'):
            return self.query

    def process_extra_params(self, query, kwargs):
        extra_params = self.url_search_parameters
        if extra_params is not None:
            filter_dict = {}
            for param_name in extra_params:
                param_value = kwargs.get(param_name, '')
                if param_value != '':
                    filter_dict[param_name] = param_value
            query = query.filter(**filter_dict)
        return query

    def annotate(self, query):
        columns = self.columns
        for column in columns:
            field = column.field
            annotate = column.annotate

            if annotate is not None:
                i = field.rfind('__')
                field = field[:i]
                fn = _annotates[annotate]
                query = query.annotate(fn(field))
        return query

    def _get_query(self, request, kwargs=None):
        query = self.get_query(request, kwargs)
        query = self.process_extra_params(query, kwargs)
        query = self.annotate(query)
        return query

    def sort_first_column(self, query):
        column = self.columns[0]
        if column.sortable is False:
            return query
        return self.sort(query, sortings=[column.field])

    def sort(self, query, DICT=None, sortings=None):
        if sortings is None and DICT is not None:
            gt = DICT.get
            sortings = []
            columns = self.columns
            total_sort_columns = gt('iSortingCols')
            total_sort_columns = int(total_sort_columns)

            if total_sort_columns is 0:
                return None

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
            sortings.reverse()

        if sortings is not None:
            query = query.order_by(*sortings)

        return query

    def page_data(self, query, DICT=None, start=None, max_items=None):
        if start is None and max_items is None:
            gt = DICT.get
            start = int(gt('iDisplayStart'))
            max_items = int(gt('iDisplayLength'))

        if max_items is None:
            max_items = self.display_length

        return query[start:start + max_items]

    def search(self, query, DICT=None, search_term=None):
        columns = self.columns

        if DICT is not None and search_term is None:
            gt = DICT.get
            search_term = gt('sSearch')

        search = None
        for column in columns:
            if column.searchable and search_term != "":
                field = column.field + "__" + column.search_lookup
                kwargs = {field: search_term}
                if search is None:
                    search = Q(**kwargs)
                else:
                    search = search | Q(**kwargs)

        if search is not None:
            query = query.filter(search)

        return query

    def only(self, query):
        columns = self.columns
        row_id = self.row_id
        fields = []
        need_related = False
        aggregate_fields = self.aggregate_fields
        related_fields = []
        for column in columns:
            column_related = column.need_related()
            need_related = need_related or column_related

            get_fields = getattr(column, 'get_fields', None)
            if get_fields is None:
                field = column.field
                annotate = column.annotate

                if annotate is None and field not in aggregate_fields:
                    fields.append(field)
                    if column_related:
                        related_fields.append(field)
            else:
                column_fields = get_fields()
                typ = type(column_fields)
                if typ in StringTypes:
                    fields.append(column_fields)
                elif typ in (tuple, list):
                    for column_field in column_fields:
                        fields.append(column_field)
                        if column_related:
                            related_fields.append(column_field)

        if row_id is not None:
            fields.insert(0, row_id)

        fields = tuple(fields)
        related_fields = tuple(related_fields)

        if need_related:
            query = query.select_related(*related_fields)

        query = query.only(*fields)
        return query

    #
    #   Initial Data For Table rendering
    #
    def initial_data(self, kwargs):
        request = self.request

        if self.request is None:
            raise Exception('Request is required for rendering initial data')

        query = self._get_query(request, kwargs)

        search_term = self.initial_search_term(request)
        prev_total = None
        if search_term:
            prev_total = query.count()
            query = self.search(query, search_term=search_term)

        query = self.sort_first_column(query)
        total_length = query.count()
        paginator = self.initial_pagination(request, total_length)
        query = self.only(query)
        query = self.page_data(query, start=paginator['from'] - 1)

        data = self._data

        data['rows'] = self.generate_initial_data_dict(query, request)
        data['total'] = total_length
        data['qs'] = paginator['qs']
        data['request'] = request
        data['paginator'] = paginator
        data['search_term'] = search_term
        data['prev_total'] = prev_total

        if self.send_sql:
            data['sql'] = last_query()

    def generate_initial_data_dict(self, query, request):
        rows = []
        row_id = self.row_id
        columns = self.columns
        for record in query:
            row = {}
            if row_id is not None:
                row['row_id'] = getattr(record, row_id)
            cells = []
            row['cells'] = cells
            for column in columns:
                cells.append(mark_safe(column.get_html(request, record)))
            rows.append(row)

        return rows

    # noinspection PyShadowingBuiltins
    def initial_pagination(self, request, count, page=None):
        qs = self.table_id + '-page'

        if page is None:
            try:
                page = request.GET.get(qs, 1)
                page = int(page)
            except:
                page = 1

        per_page = self.display_length
        hits = max(1, count)
        num_pages = int(ceil(hits / float(per_page)))
        prev_pages = []
        next_pages = []

        next_count = 4
        prev = page - 1

        while len(prev_pages) < 2 and prev > 0:
            if prev == 1:
                prev_pages.append((prev, None))
                break
            prev_pages.append((prev, prev))
            next_count -= 1
            prev -= 1
        prev_pages.reverse()

        next = page + 1
        while len(next_pages) < next_count and next <= num_pages:
            next_pages.append((next, next))
            next += 1

        paginator = {
            'from': per_page * (page - 1) + 1,
            'to': count if page == num_pages else page * per_page,
            'has_next': page < num_pages,
            'has_prev': page > 1,

            'current': page,

            'next_page': page + 1,
            'next_pages': next_pages,

            'prev_pages': prev_pages,
            'prev_page': None if page - 1 == 1 else page - 1,

            'qs': qs
        }

        return paginator

    def initial_search_term(self, request):
        search_key = self.table_id + '-search'
        search_term = request.GET.get(search_key, None)
        return search_term

    def initial_search(self, request, query):
        search_key = self.table_id + '-search'
        search_term = request.GET.get(search_key, None)
        if search_term is not None:
            query = self.search(query, search_term=search_term)
        return search_term, query

    def do_form_filter(self, query, DICT):
        form_filter = self.form_filter
        if form_filter is not None:
            query = form_filter.filter(query, DICT)
        return query

    #
    #   AJAX Table Rendering
    #
    def get_data(self, request, kwargs):
        DICT = request.GET
        query = self._get_query(request, kwargs)
        total_length = query.count()
        query = self.search(query, DICT)
        query = self.do_form_filter(query, DICT)
        query = self.sort(query, DICT)
        query = self.only(query)
        current_length = query.count()
        query = self.page_data(query, DICT)
        result = self.generate_ajax_json(query, request, DICT, total_length, current_length)
        return HttpResponse(dumps(result))

    def generate_ajax_json(self, query, request, DICT, total_length, current_length):
        datas = []
        row_id = self.row_id
        columns = self.columns
        gt = DICT.get
        echo = gt('sEcho')

        for record in query:
            data = {}

            if row_id is not None:
                data['DT_RowId'] = getattr(record, row_id)

            i = 0
            for column in columns:
                data[str(i)] = unicode(column.get_html(request, record))
                i += 1
            datas.append(data)

        data = {
            "aaData": datas,
            "sEcho": echo,
            "iTotalRecords": total_length,
            "iTotalDisplayRecords": current_length
        }

        if self.send_sql:
            data['sql'] = last_query()

        return data

    #
    #   Editable Data Table
    #
    def save_object(self, query, value, row_id, field):
        query = query.filter(**{
            self.row_id: row_id
        })

        query.update(**{
            field: value
        })

        return HttpResponse(value + ' - Saved')

    def save(self, request, kwargs=None):
        query = self.get_query(request, kwargs)
        query = self.process_extra_params(query, kwargs)

        gt = request.POST.get
        value = gt('value')
        row_id = gt('row_id')
        column = int(gt('column'))
        column = self.columns[column]
        field = column.field

        if field is None:
            raise Exception('Data cannot be saved in a column with out field')

        if row_id is None:
            raise Exception('Data cannot be saved with out row ID')

        if value is not None and row_id is not None:
            return self.save_object(query, value, row_id, field)
