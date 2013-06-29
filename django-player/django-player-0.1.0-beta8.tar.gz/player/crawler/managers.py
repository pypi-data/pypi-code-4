from django.db.models import Manager
from django.db.models.query import QuerySet


class ReportQuerySet(QuerySet):

    def by_return_code(self, code):
        return self.filter(return_code=code)

    def except_return_code(self, code):
        return self.exclude(return_code=code)

    def success(self):
        """ only success objects """
        return self.by_return_code('suc')

    def with_errors(self):
        """ exclude success objects """
        return self.except_return_code('suc')


class ReportManager(Manager):

    def get_query_set(self):
        return ReportQuerySet(self.model)
