# coding: utf-8
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django_relinking.content_types import content_types_choices, objects_choices
from django_relinking.models import Link


class LinkForm(forms.ModelForm):

    model = Link

    def __init__(self, *a, **k):
        super(LinkForm, self).__init__(*a, **k)
        types_choices = content_types_choices()
        self.fields["content_type"].widget = forms.Select(
            choices=types_choices,
            attrs=dict(get_objects_url=reverse("get_content_type_objects"))
        )
        ctype = (
            self.data.get("content_type")
            or self.initial.get("content_type")
            or self.instance.content_type
            or (types_choices and types_choices[0][0])
        )
        choices = list(objects_choices(ctype) if ctype else [])

        is_object_required = -1 not in dict(choices)

        attrs = {}
        if not is_object_required:
            attrs["disabled"] = "disabled"
        self.fields["object_pk"].widget = forms.Select(choices=choices, attrs=attrs)
        self.fields["object_pk"].required = is_object_required

    def clean_content_type(self):
        content_type = self.cleaned_data.get("content_type")
        if content_type and self.cleaned_data.get("direct_link"):
            forms.ValidationError(_(u"This field is required."))
        return content_type

    def clean_object_pk(self):
        object_pk = self.cleaned_data.get("object_pk")
        if object and self.cleaned_data.get("direct_link"):
            forms.ValidationError(_(u"This field is required."))
        return object_pk

    def clean_direct_link(self):
        if not self.cleaned_data.get("direct_link") and not self.cleaned_data.get("content_type"):
            forms.ValidationError(_(u"This field is required."))
        return self.cleaned_data.get("direct_link")

    class Media(object):
        js = ("js/django-relinking.js",)
