# -*- coding: utf-8 -*-
import django.forms
import django.utils.safestring
import django.core.urlresolvers
import StringIO
from django.utils.simplejson import dumps, loads, JSONEncoder
import dateutil.parser
import datetime
import django.db.models
import django.utils.functional
import django.db
import django.db.models.query
import django.db.models.fields.related
import django.db.models.related
try:
    import idmapper.models
except:
    pass
import base64
import jsonview
from django.utils.translation import ugettext_lazy as _, string_concat

class ModelLinkWidget(django.forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            return ''
        if hasattr(value, 'all'):
            value = value.all()
        elif not isinstance(value, (list, tuple)):
            value = [value]
        lines = ("<a href='%s'>%s</a>" % (django.core.urlresolvers.reverse('admin:%s_%s_change' % (type(obj)._meta.app_label, type(obj)._meta.module_name), args=(obj.id,)), obj)
                 for obj in value)
        out = "<ul>%s</ul>" % ('\n'.join("<li>%s</li>" % (line,) for line in lines))
        return django.utils.safestring.mark_safe(unicode(out))

class ModelLinkField(django.forms.ModelChoiceField):
    widget = ModelLinkWidget

class JsonFormField(django.forms.Field):
    default_error_messages = {
        'invalid': _(u'Enter a valid JSON expression.'),
    }

    def __init__(self, *args, **kwargs):
        super(JsonFormField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        if value is None:
            value = ""
        elif not isinstance(value, (str, unicode)):
            value = jsonview.to_json(value)
        return super(JsonFormField, self).prepare_value(value)

    def to_python(self, value):
        value = super(JsonFormField, self).to_python(value).strip()
        if not value: return None
        return jsonview.from_json(value)

class JsonField(django.db.models.Field): 
    __metaclass__ = django.db.models.SubfieldBase 
    serialize_to_string = True 
    def get_internal_type(self): 
        return "TextField" 
    def value_to_string(self, obj): 
        return self.get_prep_value(self._get_val_from_obj(obj)) 
    def get_prep_value(self, value):
        return jsonview.to_json(value) 
    def to_python(self, value):
        if isinstance(value, (str, unicode)):
            if not value.strip():
                return None
            return jsonview.from_json(value)
        return value 
    def formfield(self, **kwargs):
        kwargs['form_class'] = JsonFormField
        return super(JsonField, self).formfield(**kwargs)

class Base64Field(django.db.models.TextField):
    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.decodestring(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))


class WeakForeignKeyDescriptor(object):
    def __init__(self, related):
        self.related = related

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.related_manager_cls(instance)

    def __set__(self, instance, value):
        raise ValueError("WeakForeignKey does not support assignement; Assign to the value fields used to define it instead.")


    @django.utils.functional.cached_property
    def related_manager_cls(self):
        # Dynamically create a class that subclasses the related model's default
        # manager.
        superclass = self.related.model._default_manager.__class__
        related_object_descriptor = self

        class RelatedManager(superclass):
            def __init__(self, instance):
                super(RelatedManager, self).__init__()
                self.core_filters = {'%s__exact' % related_object_descriptor.related.to_fields[0]:
                                         getattr(instance, related_object_descriptor.related.from_fields[0])}
                self.instance = instance

            def get_queryset(self, **db_hints):
                db = django.db.router.db_for_read(related_object_descriptor.related.to, **db_hints)
                return django.db.models.query.QuerySet(related_object_descriptor.related.to).using(db).filter(**self.core_filters)

        return RelatedManager

class WeakForeignKeyRel(django.db.models.fields.related.ManyToManyRel):
    def __init__(self, to, field, *arg, **kw):
        django.db.models.fields.related.ManyToManyRel.__init__(self, to, *arg, **kw)
        self.field = field

    def get_joining_columns(self):
        return self.field.get_reverse_joining_columns()

    def get_extra_restriction(self, where_class, alias, related_alias):
        return None

class WeakForeignKey(django.db.models.ManyToManyField):
    """Defines a weak, or fake, foreign key based on existing fields.

    You must set
      from_field - the field in this model to join on
      to - the model to join to
      to_field - the field in the other model to join on

    Usefull to construct joins on non-primary keys. Note that all joins are done with equal as join condition.
    """

    def __init__(self, from_field, to, to_field, *arg, **kwargs):
        try:
            assert not to._meta.abstract, "%s cannot define a relation with abstract class %s" % (self.__class__.__name__, to._meta.object_name)
        except AttributeError:  # to._meta doesn't exist, so it must be RECURSIVE_RELATIONSHIP_CONSTANT
            assert isinstance(to, six.string_types), "%s(%r) is invalid. First parameter to ManyToManyField must be either a model, a model name, or the string %r" % (self.__class__.__name__, to, django.db.models.fields.related.RECURSIVE_RELATIONSHIP_CONSTANT)
            # Python 2.6 and earlier require dictionary keys to be of str type,
            # not unicode and class names must be ASCII (in Python 2.x), so we
            # forcibly coerce it here (breaks early if there's a problem).
            to = str(to)

        kwargs['verbose_name'] = kwargs.get('verbose_name', None)
        kwargs['rel'] = WeakForeignKeyRel(to,
            related_name=kwargs.pop('related_name', None),
            limit_choices_to=kwargs.pop('limit_choices_to', None),
            symmetrical=kwargs.pop('symmetrical', to == django.db.models.fields.related.RECURSIVE_RELATIONSHIP_CONSTANT),
            through=kwargs.pop('through', None),
            field=self
        )

        self.db_table = kwargs.pop('db_table', None)
        if kwargs['rel'].through is not None:
            assert self.db_table is None, "Cannot specify a db_table if an intermediary model is used."

        super(django.db.models.ManyToManyField, self).__init__(**kwargs)

        msg = _('Hold down "Control", or "Command" on a Mac, to select more than one.')
        self.help_text = string_concat(self.help_text, ' ', msg)

        self.from_fields = [from_field]
        self.to_fields = [to_field]

    def resolve_related_fields(self):
        if len(self.from_fields) < 1 or len(self.from_fields) != len(self.to_fields):
            raise ValueError('Foreign Object from and to fields must be the same non-zero length')
        related_fields = []
        for index in range(len(self.from_fields)):
            from_field_name = self.from_fields[index]
            to_field_name = self.to_fields[index]
            from_field = (self if from_field_name == 'self'
                          else self.opts.get_field_by_name(from_field_name)[0])
            to_field = (self.rel.to._meta.pk if to_field_name is None
                        else self.rel.to._meta.get_field_by_name(to_field_name)[0])
            related_fields.append((from_field, to_field))
        return related_fields

    @property
    def related_fields(self):
        if not hasattr(self, '_related_fields'):
            self._related_fields = self.resolve_related_fields()
        return self._related_fields

    @property
    def foreign_related_fields(self):
        return tuple([rhs_field for lhs_field, rhs_field in self.related_fields])

    @property
    def reverse_related_fields(self):
        return [(rhs_field, lhs_field) for lhs_field, rhs_field in self.related_fields]

    def get_joining_columns(self, reverse_join=False):
        source = self.reverse_related_fields if reverse_join else self.related_fields
        return tuple([(lhs_field.column, rhs_field.column) for lhs_field, rhs_field in source])

    def get_reverse_joining_columns(self):
        return self.get_joining_columns(reverse_join=True)

    def get_path_info(self):
        """
        Get path from this field to the related model.
        """
        opts = self.rel.to._meta
        from_opts = self.model._meta
        return [django.db.models.related.PathInfo(from_opts, opts, self.foreign_related_fields, self, False, True)]

    def get_reverse_path_info(self):
        """
        Get path from the related model to this field's model.
        """
        opts = self.model._meta
        from_opts = self.rel.to._meta
        pathinfos = [django.db.models.related.PathInfo(from_opts, opts, (opts.pk,), self.rel, not self.unique, False)]
        return pathinfos

    def contribute_to_class(self, cls, name):
        super(WeakForeignKey, self).contribute_to_class(cls, name)
        self.field = self
        self.to = self.rel.to
        setattr(cls, self.name, WeakForeignKeyDescriptor(self))

    def contribute_to_related_class(self, cls, related):
        related.to = self.model
        related.from_fields = self.to_fields
        related.to_fields = self.from_fields
        setattr(cls, related.get_accessor_name(), WeakForeignKeyDescriptor(related))

    def validate(self, value, model_instance):
        # Did I say this is a weak foreign key? It can't fail...
        pass
