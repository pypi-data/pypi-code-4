from __future__ import absolute_import, unicode_literals
from django.forms import *
from gollum import mixins


class Form(mixins.FormMarkupMixin, Form):
    pass


class ModelForm(mixins.FormMarkupMixin, ModelForm):
    pass
