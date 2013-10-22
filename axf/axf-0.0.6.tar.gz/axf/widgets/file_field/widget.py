from tw2 import forms
from tw2.core import Param


class AvatarFileField(forms.FileField):
    template = 'axf.widgets.file_field.templates.avatar_file_field'
    avatar = Param('Url of the avatar image', default='http://placehold.it/128x128')
    avatar_attrs = Param('Extra attributes to include in the img tag.', default={})
