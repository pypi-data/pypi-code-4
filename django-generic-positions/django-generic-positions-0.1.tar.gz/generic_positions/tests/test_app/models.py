"""Dummy models to be used in test cases of the ``generic_positions`` app."""
from django.contrib.contenttypes import generic
from django.db import models


class DummyModel(models.Model):
    """Dummy to be used in test cases of the ``generic_positions`` app."""
    name = models.CharField(max_length=256, blank=True)

    def __unicode__(self):
        return self.name


# We are just monkeypatching here for testing purposes. Of course you would add
# the GenericRelation directly to your model if it is part of your own app.
# The monkeypatching will only be used for models of third party apps.
DummyModel.add_to_class(
    'generic_position',
    generic.GenericRelation('generic_positions.ObjectPosition'),
)
