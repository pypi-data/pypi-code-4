from django.db.models import Manager
from player.logicaldelete.models import LogicalDeletedManager
from django.db.models.query import QuerySet


class ItemQuerySet(QuerySet):

    def contents(self):
        for item in self:
            yield item.content


class ItemManager(LogicalDeletedManager):
    use_for_related_fields = True

    def all(self):
        return self.get_query_set().filter(is_valid=True)

    def with_invalids(self):
        return self.get_query_set()

    def invalids(self):
        return self.get_query_set().filter(is_valid=False)

    def contents(self):
        return self.get_query_set().contents()

    def get_query_set(self):
        """ by default we will do joins with Collection for reduce SQL sentences """
        return ItemQuerySet(self.model).filter(is_deleted=False).select_related('collection')


class CollectionManager(Manager):

    def get_query_set(self):
        return CollectionQuerySet(self.model)


class CollectionQuerySet(QuerySet):

    def by_status(self, status):
        return self.filter(status=status)

    def published(self):
        """ only published objects """
        return self.by_status('published')

    def draft(self):
        """ only draft objects """
        return self.by_status('draft')


class CollectionFieldQuerySet(QuerySet):

    def is_mapped(self):
        return self.filter(mapped_field__isnull=False)


class CollectionFieldManager(Manager):
    use_for_related_fields = True

    def is_mapped(self):
        return self.get_query_set().is_mapped()

    def get_query_set(self):
        return CollectionFieldQuerySet(self.model)
