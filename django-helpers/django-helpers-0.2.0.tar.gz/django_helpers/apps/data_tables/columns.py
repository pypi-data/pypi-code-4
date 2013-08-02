# coding=utf-8
from django.template import Template, loader, RequestContext

__author__ = 'ajumell'

_lookups = (
    "exact",
    "iexact",
    "contains",
    "icontains",
    "in",
    "gt",
    "gte",
    "lt",
    "lte",
    "startswith",
    "istartswith",
    "endswith",
    "iendswith",
    "range",
    "year",
    "month",
    "day",
    "week_day",
    "isnull",
    "search",
    "regex",
    "iregex"
)


def get_value(instance, field, format_expression=None):
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
    if format_expression is not None:
        value = format_expression % value

    return value


class DataTableColumn(object):
    def __init__(self, field, title, searchable=False, sortable=False, title_class=None, title_width=None,
                 editable=False, annotate=None, search_lookup='contains', format_expression=None):
        self.field = field
        self.title = title
        self.searchable = searchable
        self.sortable = sortable
        self.title_class = title_class
        self.title_width = title_width
        self.editable = editable
        self.format_expression = format_expression

        if searchable and search_lookup not in _lookups:
            raise

        self.search_lookup = search_lookup

        if annotate is not None:
            from data_table import validate_annotate

            if not validate_annotate(annotate):
                raise

            if editable:
                raise

            self.field = field + "__" + annotate

        self.annotate = annotate

    def get_html(self, request, instance):
        return get_value(instance, self.field, self.format_expression)

    def need_related(self):
        return self.annotate is None and self.field.find('__') > -1


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
                 load_template=True, width=None, value_name='value', title_class=None, title_width=None, editable=False, annotate=None, search_lookup='contains', format_expression=None):
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
        DataTableColumn.__init__(self, field, title, searchable, sortable, title_class, title_width, editable, annotate, search_lookup, format_expression)
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
