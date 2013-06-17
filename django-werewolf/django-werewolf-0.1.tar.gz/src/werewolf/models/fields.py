__all__ = ('StatusField',)

from django.db import models

from werewolf.settings import STATUS_CHOICES


class StatusField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(StatusField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        defaults.update(choices=STATUS_CHOICES)
        return super(StatusField, self).formfield(**defaults)

# Add schema's for South
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        rules=[((StatusField,), [], {})], \
        patterns=['werewolf.models\.fields\.StatusField',]
        )
except ImportError:
    pass
