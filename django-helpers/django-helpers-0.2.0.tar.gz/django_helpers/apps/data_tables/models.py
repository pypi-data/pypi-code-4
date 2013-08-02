from django.utils.text import capfirst
from data_table import DataTable
from columns import DataTableColumn


class ModelDataTable(DataTable):
    model = None
    fields = None

    default_editable = False
    default_searchable = True
    default_sortable = True

    searchable = []
    sortable = []
    editable = []
    types = {}

    def __init__(self, request=None):
        if self.model is None:
            raise

        model = self.model
        model_fields = model._meta.fields

        if self.fields is None:
            fields = [model_field.name for model_field in model_fields]
        else:
            fields = self.fields

        columns = []
        types = self.types

        searchable = self.searchable
        sortable = self.sortable
        editable = self.editable
        need_related = False

        for model_field in model_fields:
            field = model_field.name
            if field in fields:
                Column = types.get(model_field, DataTableColumn)
                related = hasattr(model_field, 'related')

                need_related = need_related or related

                is_sortable = field in sortable or self.default_sortable
                is_editable = not related and (field in editable or self.default_editable)
                is_searchable = not related and (field in searchable or self.default_searchable)

                params = {
                    'searchable': is_searchable,
                    'sortable': is_sortable,
                    'editable': is_editable,
                    'title': capfirst(model_field.verbose_name),
                    'field': field,

                }
                columns.append(Column(**params))

        self.columns = columns
        self.query = model.objects.all()

        if need_related:
            self.query = self.query.select_related()

        DataTable.__init__(self, request)