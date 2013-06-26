__title__ = 'slim.models.fields'
__version__ = '0.4'
__build__ = 0x000004
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('LanguageField', 'SimpleLanguageField')

from django.db import models
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

from slim import get_languages, default_language


class LanguageField(models.CharField):
    """
    LanguageField model. Stores language string in a ``CharField`` field.

    Using `contrib_to_class` melthod adds `translation_of` field, which is simply a ``ForeignKey``
    to the same class.
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        """
        Create new field. Argument ``populate`` will be sent as-is to the form field.
        """
        defaults = {
            'verbose_name': _('Language'),
            'populate': None,
            'max_length': 10,
            'choices': get_languages(),
            'default': default_language
        }
        defaults.update(kwargs)
        self.populate = defaults.pop('populate', None)
        super(LanguageField, self).__init__(*args, **defaults)

    def contribute_to_class(self, cls, name):
        """
        Language field consists of more than one database record. We have ``lanaguage`` (CharField)
        and ``translation_of`` (ForeignKey to ``cls``) in order to identify translated and
        primary objects.

        We have a set of very useful methods implemented in order to get translations easily.
        """
        self.name = name
        self.translation_of = models.ForeignKey(cls, blank=True, null=True, verbose_name=_('Translation of'), \
                                                related_name='translations', \
                                                limit_choices_to={'language': default_language}, \
                                                help_text=_('Leave this empty for entries in the primary language.'))
        cls.add_to_class('translation_of', self.translation_of)
        super(LanguageField, self).contribute_to_class(cls, name)

    def formfield(self, **kwargs):
        """
        Returns best form field to represent this model field
        """
        defaults = {
            'form_class': LanguageField,
            'populate': self.populate,
        }
        defaults.update(kwargs)
        return super(models.CharField, self).formfield(**defaults)

    def validate(self, value, model_instance):
        """
        Validating the field.

        We shall make sure that there are double translations for the same language for the same object. That's
        why, in case if model is not yet saved (``translated_object`` does not yet have a primary key), we check
        if there are already translations of the same object in the language we specify now.

        Otherwise, if ``model_instance`` already has a primary key, we anyway try to get a ``translated_object``
        and compare it with our ``model_instance``. In case if ``translated_object`` exists and not equal to our
        ``model_instance`` we raise an error.

        NOTE: This has nothing to do with unique fields in the original ``model_instance``. Make sure you have
        properly specified all unique attributes with respect to ``LanguageField` of your original
        ``model_instance`` if you need those records to be unique.
        """
        if model_instance.original_translation:
            translated_object = model_instance.original_translation.get_translation_for(value)
        else:
            translated_object = None
        if not model_instance.pk:
            if translated_object and translated_object.pk:
                raise exceptions.ValidationError("Translation in language %s for this object already exists." % value)
        else:
            if translated_object and translated_object.pk and model_instance != translated_object:
                raise exceptions.ValidationError("Translation in language %s for this object already exists." % value)
        super(LanguageField, self).validate(value, model_instance)


class SimpleLanguageField(models.CharField):
    """
    SimpleLanguageField model. Stores language string in a ``CharField`` field.
    """

    def __init__(self, *args, **kwargs):
        """
        Create new field. Argument ``populate`` will be sent as-is to the form field.
        """
        defaults = {
            'verbose_name': _('Language'),
            'populate': None,
            'max_length': 10,
            'choices': get_languages(),
            'default': default_language
        }
        defaults.update(kwargs)
        self.populate = defaults.pop('populate', None)
        super(SimpleLanguageField, self).__init__(*args, **defaults)

    def formfield(self, **kwargs):
        """
        Returns best form field to represent this model field
        """
        defaults = {
            'form_class': SimpleLanguageField,
            'populate': self.populate,
        }
        defaults.update(kwargs)
        return super(models.CharField, self).formfield(**defaults)

# Add schema's for South
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        rules=[((LanguageField,), [], {'populate': ('populate', {'default':None}),})], \
        patterns=['slim.models\.fields\.LanguageField', 'slim.models\.fields\.SimpleLanguageField']
        )
except ImportError:
    pass
