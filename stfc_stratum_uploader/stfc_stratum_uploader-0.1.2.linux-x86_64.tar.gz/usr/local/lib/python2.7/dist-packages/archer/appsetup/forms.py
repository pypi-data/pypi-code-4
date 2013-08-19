from django import forms
from archer.projects.models import FileSystem


class GrantAdminForm(forms.Form):
    pass


class FileSystemForm(forms.ModelForm):
    class Meta:
        model = FileSystem
        fields = ['alias', 'mount_point']
