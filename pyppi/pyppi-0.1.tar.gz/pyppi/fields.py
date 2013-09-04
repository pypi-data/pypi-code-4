from django.db import models
import json
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import smart_unicode
from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import uuid


class PackageInfoField(models.Field):
    description = u'Python Package Information Field'
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(PackageInfoField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, basestring):
            if value:
                return MultiValueDict(json.loads(value))
            else:
                return MultiValueDict()
        if isinstance(value, dict):
            return MultiValueDict(value)
        if isinstance(value, MultiValueDict):
            return value
        raise ValueError('Unexpected value encountered when converting data to python')

    def get_prep_value(self, value):
        if isinstance(value, MultiValueDict):
            return json.dumps(dict(value.iterlists()))
        if isinstance(value, dict):
            return json.dumps(value)
        if isinstance(value, basestring) or value is None:
            return value

        raise ValueError('Unexpected value encountered when preparing for database')

    def get_internal_type(self):
        return 'TextField'

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.TextField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

# try:
#     from south.modelsinspector import add_introspection_rules
#
#     add_introspection_rules([], [r"^pyppi\.fields\.PackageInfoField"])
# except ImportError:
#     pass



class BetterJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return obj.hex
        elif not isinstance(obj, (basestring, tuple, list, dict, int, bool)):
            return unicode(obj)
        else:
            return super(BetterJSONEncoder, self).default(obj)

def json_dumps(value, **kwargs):
    return json.dumps(value, cls=BetterJSONEncoder, **kwargs)

class JSONDictWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        if not isinstance(value, basestring):
            value = json_dumps(value, indent=2)
        return super(JSONDictWidget, self).render(name, value, attrs)

class JSONDictFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', JSONDictWidget)
        super(JSONDictFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value: return
        try:
            return json.loads(value)
        except Exception, exc:
            raise forms.ValidationError(u'JSONDict decode error: %s' % (smart_unicode(exc),))

class JSONDictField(models.TextField):
    """
    Slightly different from a JSONField in the sense that the default
    value is a dictionary.
    """
    __metaclass__ = models.SubfieldBase

    def formfield(self, **kwargs):
        return super(JSONDictField, self).formfield(form_class=JSONDictFormField, **kwargs)

    def to_python(self, value):
        if isinstance(value, basestring) and value:
            value = json.loads(value)
        elif not value:
            return {}
        return value

    def get_db_prep_save(self, value, connection):
        if value is None: return
        return json_dumps(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value, None)

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.TextField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
