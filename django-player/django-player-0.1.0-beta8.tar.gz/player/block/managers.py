from django.db import models
from django.db.models.query import QuerySet


class BlockQuerySet(QuerySet):

    def actives(self):
        return self.filter(is_active=True)


class PlacedBlockManager(models.Manager):
    """ Block manager """

    def get_query_set(self):
        return BlockQuerySet(self.model)

    def actives(self):
        return self.get_query_set().actives()
