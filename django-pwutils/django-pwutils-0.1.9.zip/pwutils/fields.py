# -*- coding: utf-8 -*-

try:
    from django.utils.timezone import now as datetime_now
    datetime_now  # workaround for pyflakes
except ImportError:
    from datetime import datetime
    datetime_now = datetime.now

from django.db.models import DateTimeField
from django.db.models.fields import FilePathField
from django.db.models.loading import get_model
from django.contrib.contenttypes import generic
from django.forms.fields import ChoiceField

try:
    from south.modelsinspector import introspector  # @UnresolvedImport
except:
    introspector = None


class CreationDateTimeField(DateTimeField):
    """ CreationDateTimeField

    By default, sets editable=False, default=timezone aware datetime.now
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        kwargs.setdefault('default', datetime_now)
        DateTimeField.__init__(self, *args, **kwargs)

    def south_field_triple(self):
        args, kwargs = introspector(self)
        return ("django.db.models.DateTimeField", args, kwargs)


class ModificationDateTimeField(CreationDateTimeField):
    """ ModificationDateTimeField

    By default, sets editable=False, default=datetime.now

    Sets value to datetime.now() on each save of the model.
    """

    def pre_save(self, model, add):
        value = datetime_now()
        setattr(model, self.attname, value)
        return value


class DeletionDateTimeField(DateTimeField):
    """ DeletionDateTimeField

    By default, sets editable=False, blank=True
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        kwargs.setdefault('null', True)
        DateTimeField.__init__(self, *args, **kwargs)

    def south_field_triple(self):
        args, kwargs = introspector(self)
        return ("django.db.models.DateTimeField", args, kwargs)


class FilterChoiceField(ChoiceField):

    def __init__(self, *args, **kwagrs):
        choices = kwagrs.pop('choices', ())
        kwagrs['choices'] = [(i, choice[0])
                             for i, choice in enumerate(choices)]
        self.values = [(i, choice[1]) for i, choice in enumerate(choices)]
        self.values = dict(self.values)
        super(FilterChoiceField, self).__init__(*args, **kwagrs)

    def clean(self, value):
        value = super(FilterChoiceField, self).clean(value)
        return (value, self.values[int(value)]())


class CustomGenericForeingKey(generic.GenericForeignKey):

    def get_content_type(self, obj=None, id=None, using=None):
        ''' Convenience function using get_model avoids
            a circular import when using this model

        TODO this method in 1.2 differs from 1.1,
             cause of multydbs, had to rewrite it
        '''
        ContentType = get_model("contenttypes", "contenttype")
        if obj:
            f = self.model._meta.get_field(self.ct_field)
            model = getattr(obj, 'ct_exception_model', None)
            needed_models = f.rel.limit_choices_to.get('model__in', [])
            if model and model.__name__.lower() in needed_models:
                return ContentType.objects.db_manager(obj._state.db)\
                                          .get_for_model(model)
            else:
                return ContentType.objects.db_manager(obj._state.db)\
                                          .get_for_model(obj)
        elif id:
            return ContentType.objects.db_manager(using).get_for_id(id)
        else:
            # This should never happen.
            raise Exception("Impossible arguments to GFK.get_content_type!")

if introspector is not None:
    class SouthFilePathField(FilePathField):

        def south_field_triple(self):
            "Returns a suitable description of this field for South."
            args, kwargs = introspector(self)
            kwargs.update({'path': None})
            return ('pwutils.models.SouthFilePathField', args, kwargs)
else:
    SouthFilePathField = FilePathField
