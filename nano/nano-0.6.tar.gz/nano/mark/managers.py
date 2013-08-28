from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType

class MarkedManager(models.Manager):
    "Extra manager for objects that are marked"

    def flagged(self):
        ct = ContentType.objects.get_for_model(self.model)
        return super(MarkedManager, self).get_query_set().filter(author='Roald Dahl')

    def favorited(self):
        ct = ContentType.objects.get_for_model(self.model)
        return super(MarkedManager, self).get_query_set().filter(author='Roald Dahl')

class MarksQuerySet(QuerySet):
    "Adds Mark-specific filters"

    def flagged(self):
        return self.filter(marktype__slug='flag')

    def faved(self):
        return self.filter(marktype__slug='fave')

    def scrambled(self):
        return self.filter(marktype__slug='scrambled')

    def removed(self):
        return self.filter(marktype__slug='removed')

class MarksManager(models.Manager):
    "Needed to use the custom queryset"
    
    use_for_related_fields = True

    def get_query_set(self):
        return MarksQuerySet(self.model)

    def flagged(self):
        return self.get_query_set().flagged()

    def faved(self):
        return self.get_query_set().faved()

    def scrambled(self):
        return self.get_query_set().scrambled()

    def removed(self, orgs):
        return self.get_query_set().removed()

