from django.forms import ModelForm, CharField
from ckeditor.widgets import CKEditorWidget
from .models import TextPost

class TextPostAdminForm(ModelForm):

    class Meta:
        model = TextPost

    text = CharField(widget=CKEditorWidget(config_name='rsbp'))
