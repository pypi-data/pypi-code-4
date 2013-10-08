# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode
from django.template.loader import render_to_string
from django.forms.forms import BoundField
from django.forms.models import ModelForm, ModelChoiceField, \
    ModelMultipleChoiceField
from django.forms.widgets import Media
from django.forms.formsets import BaseFormSet
from django.conf import settings
from django.db.models import Model
from django.forms import ValidationError

try:
    from smart_selects.form_fields import ChainedModelChoiceField
except ImportError:
    ChainedModelChoiceField = None
try:
    from ajax_filtered_fields.forms.fields import AjaxForeignKeyField
except ImportError:
    AjaxForeignKeyField = None


def create_choices(cls, queryset=None, empty=False,
                   order_by=None, empty_title=u'------------',
                   extra=(), label_attr=None):
    choices = []
    if not queryset:
        objects = cls.objects.all()
    else:
        objects = queryset

    if empty:
        choices.append(('', empty_title))
    if extra:
        choices.extend(extra)
    if order_by is not None:
        objects = objects.order_by(order_by)

    if objects.exists():
        if label_attr is None:
            choices.extend([(o.id, o) for o in objects])
        else:
            if callable(getattr(objects[0], label_attr)):
                choices.extend([(o.id, getattr(o, label_attr)())
                                for o in objects])
            else:
                choices.extend([(o.id, getattr(o, label_attr))
                                for o in objects])
    return choices


class SpanWidget(forms.Widget):
    '''Renders a value wrapped in a <span> tag.

    Requires use of specific form support. (see ReadonlyForm
    or ReadonlyModelForm)
    '''

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<span%s >%s</span>' % (
            forms.util.flatatt(final_attrs), self.original_value))

    def value_from_datadict(self, data, files, name):
        return self.original_value


class SpanField(forms.Field):
    '''A field which renders a value wrapped in a <span> tag.

    Requires use of specific form support. (see ReadonlyForm
    or ReadonlyModelForm)
    '''

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', SpanWidget)
        super(SpanField, self).__init__(*args, **kwargs)


class Readonly(object):
    '''Base class for ReadonlyForm and ReadonlyModelForm which provides
    the meat of the features described in the docstings for those classes.
    '''

    class NewMeta:
        readonly = tuple()

    def __init__(self, *args, **kwargs):
        super(Readonly, self).__init__(*args, **kwargs)
        readonly = self.NewMeta.readonly
        if not readonly:
            return
        for name, field in self.fields.items():
            if name in readonly:
                field.widget = SpanWidget()
            elif not isinstance(field, SpanField):
                continue
            field.widget.original_value = unicode(getattr(self.instance, name))


class ReadonlyForm(Readonly, forms.Form):
    '''A form which provides the ability to specify certain fields as
    readonly, meaning that they will display their value as text wrapped
    with a <span> tag. The user is unable to edit them, and they are
    protected from POST data insertion attacks.

    The recommended usage is to place a NewMeta inner class on the
    form, with a readonly attribute which is a list or tuple of fields,
    similar to the fields and exclude attributes on the Meta inner class.

        class MyForm(ReadonlyForm):
            foo = forms.TextField()
            class NewMeta:
                readonly = ('foo',)
    '''
    pass


class ReadonlyModelForm(Readonly, forms.ModelForm):
    '''A ModelForm which provides the ability to specify certain fields as
    readonly, meaning that they will display their value as text wrapped
    with a <span> tag. The user is unable to edit them, and they are
    protected from POST data insertion attacks.

    The recommended usage is to place a NewMeta inner class on the
    form, with a readonly attribute which is a list or tuple of fields,
    similar to the fields and exclude attributes on the Meta inner class.

        class Foo(models.Model):
            bar = models.CharField(max_length=24)

        class MyForm(ReadonlyModelForm):
            class Meta:
                model = Foo
            class NewMeta:
                readonly = ('bar',)
    '''
    pass


class ReadOnlyWidget(forms.Widget):
    def __init__(self, original_value, display_value):

        #raise Exception(isinstance(original_value, Model))
        if isinstance(original_value, Model):
            self.original_value = original_value.pk
            self.display_value = original_value.__unicode__()
        else:
            self.original_value = original_value
            self.display_value = display_value

        super(ReadOnlyWidget, self).__init__()

    def render(self, name, value, attrs=None):
        if self.display_value is not None:
            return unicode(self.display_value)
        if self.original_value is not None:
            return unicode(self.original_value)
        else:
            return unicode(' ')

    def value_from_datadict(self, data, files, name):
        return self.original_value


class ReadOnlyAdminFields(object):

    """typical admin.py file:
    from django.contrib import admin
    from foo.bar import ReadOnlyAdminFields

    class MyModelAdmin(ReadOnlyAdminFields, admin.ModelAdmin):
        readonly = ('field1', 'field2',)"""

    def get_form(self, request, obj=None):
        form = super(ReadOnlyAdminFields, self).get_form(request, obj)

        if hasattr(self, 'readonly'):
            for field_name in self.readonly:
                if field_name in form.base_fields:

                    if hasattr(obj, 'get_%s_display' % field_name):
                        display_value = getattr(obj,
                                                'get_%s_display' % field_name)
                        display_value = display_value()
                    else:
                        display_value = None

                    field = form.base_fields[field_name]

                    field.widget = ReadOnlyWidget(getattr(obj, field_name, ''),
                                                  display_value)
                    field.required = False

        return form


def f(render_f, link_add):
    def wrap(name, value, attrs=None, choices=()):
        res = render_f(name, value, attrs=attrs, choices=choices)
        popupplus = render_to_string("popups/popupplus.html",
            {'field': name, 'link_add': link_add})
        return res + popupplus
    return wrap


def popup(render_f, link_add):
    def wrap(*args, **kwargs):
        kwargs['link_add'] = link_add
        res = render_f(*args, **kwargs)
        return res
    return wrap


if AjaxForeignKeyField is not None:

    class PopupAjaxForeignKeyField(AjaxForeignKeyField):

        def __init__(self, *args, **kwargs):
            link_add = kwargs.pop('link_add')
            super(PopupAjaxForeignKeyField, self).__init__(*args, **kwargs)
            self.widget.render = f(self.widget.render, link_add=link_add)

    class AjaxModelForm(ModelForm):
        class Media:
            js = (
                    settings.STATIC_URL + "admin/js/SelectBox.js",
                    settings.STATIC_URL + "admin/js/SelectFilter2.js",
                    settings.STATIC_URL + \
                        "ajax-filtered-fields/js/ajax_filtered_fields.js",
                 )


class PopupModelChoiceField(ModelChoiceField):

    def __init__(self, *args, **kwargs):
        link_add = kwargs.pop('link_add')
        super(PopupModelChoiceField, self).__init__(*args, **kwargs)
        self.widget.render = popup(self.widget.render, link_add=link_add)


class PopupModelMultipleChoiceField(ModelMultipleChoiceField):

    def __init__(self, *args, **kwargs):
        link_add = kwargs.pop('link_add')
        super(PopupModelMultipleChoiceField, self).__init__(*args, **kwargs)
        self.widget.render = popup(self.widget.render, link_add=link_add)


if ChainedModelChoiceField is not None:
    class PopupChainedModelChoiceField(ChainedModelChoiceField):

        def __init__(self, *args, **kwargs):
            link_add = kwargs.pop('link_add')
            super(PopupChainedModelChoiceField, self).__init__(*args, **kwargs)
            self.widget.render = f(self.widget.render, link_add=link_add)


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
        """Outputs radios"""
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class EmptyField(forms.CharField):
    def clean(self, value):
        if value != '':
            raise ValidationError('Please DO NOT fill this field!')


# MultipleForm inspired by
# http://www.slideshare.net/kingkilr/forms-getting-your-moneys-worth

class MultipleFormBase(StrAndUnicode):
    def __init__(self, *args, **kwargs):
        super(StrAndUnicode, self).__init__(*args, **kwargs)

    def __iter__(self):
        for field in self.fields:
            for form in self.forms:
                for inner_field in form:
                    if inner_field.name == field:
                        yield inner_field

    def save(self, commit=True):
        result = list()
        for form in self.forms:
            result.append(form.save(commit) if hasattr(form, 'save') else None)
        return tuple(result)

    def is_valid(self):
        return bool(1 for form in self.forms if form.is_valid())

    def _media(self):
        media = Media()
        for form in self.forms:
            media += form.media
        return media
    media = property(_media)

    def __getitem__(self, name):
        if name == 'media':
            return self.media

        field = None
        for form in self.forms:
            if isinstance(form, BaseFormSet) and form.name == name:
                field = form
            else:
                try:
                    field = form.fields[name]
                except KeyError:
                    pass
                else:
                    field = BoundField(self, field, name)
        if not field:
            raise KeyError('Key %r not found in Form' % name)

        return field


def multipleform_factory(forms, fields=None):
    attrs = dict(forms=forms,
                 fields=fields)
    return type('MultipleForm', (MultipleFormBase,), attrs)
