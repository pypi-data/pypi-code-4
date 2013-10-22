from codemirror.widgets import CodeMirrorTextarea
from django import forms
from django.contrib import admin
from django_diazo.models import SingleRule, CompoundRule
from django.utils.translation import ugettext_lazy as _


class SingleRuleForm(forms.ModelForm):
    rule = forms.CharField(required=True, widget=CodeMirrorTextarea())


class SingleRuleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    form = SingleRuleForm


class CompoundRuleForm(forms.ModelForm):
    prefix = forms.CharField(required=True, widget=CodeMirrorTextarea())
    suffix = forms.CharField(required=True, widget=CodeMirrorTextarea())


class CompoundRuleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    form = CompoundRuleForm
    filter_horizontal = ('rules',)


# admin.site.register(SingleRule, SingleRuleAdmin)
# admin.site.register(CompoundRule, CompoundRuleAdmin)
