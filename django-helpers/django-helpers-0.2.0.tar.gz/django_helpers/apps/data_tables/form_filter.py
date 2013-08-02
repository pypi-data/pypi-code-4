__author__ = 'ajumell'


class DataTableFormFilter(object):
    form_id = None
    field_connection = {}

    def filter(self, query, DICT):
        fields = self.field_connection
        filter_dict = {}
        for field in fields:
            val = DICT.get(field, '')
            if val is not None:
                filter_dict[fields[field]] = val
        query = query.filter(**filter_dict)
        return query
