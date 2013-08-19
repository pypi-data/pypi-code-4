import os
import re

from bootstrap_toolkit.widgets import BootstrapFileInput
from django import forms
from django.utils.translation import ugettext_lazy as _

from archer.packages.models import Package
from models import Project


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['file']
        widgets = {
            'file': BootstrapFileInput(format_type='simple'),
        }


class RemoveDirectoryForm(forms.Form):
    pass


class RemoveFileForm(forms.Form):
    pass


class MakeDirectoryForm(forms.Form):
    new_directory = forms.CharField(max_length=200, required=True)

    def __init__(self, parent_directory, *args, **kwargs):
        self.parent_directory = parent_directory
        super(MakeDirectoryForm, self).__init__(*args, **kwargs)

    def clean_new_directory(self):
        new_directory = self.cleaned_data['new_directory']
        if not len(new_directory) > 0:
            raise forms.ValidationError('Directory name cannot be empty!')
        if not re.match('^([\.\-]|\w)+$', new_directory):
            raise forms.ValidationError(_('Directory name must consist of ' +
                                          'alphanumeric characters, hyphens, ' +
                                          'dots or underscores only! (([\.\-]|\w)+)'), code='dir_name')

        dir_full_path = os.path.join(self.parent_directory, new_directory)
        if os.path.exists(dir_full_path):
            # raise forms.ValidationError(_('Directory "%(dir)s" already exists!'),
            #                             params={'dir': new_directory},) # Django 1.6 only
            raise forms.ValidationError(_('Directory "%s" already exists!') % new_directory,)
        return new_directory