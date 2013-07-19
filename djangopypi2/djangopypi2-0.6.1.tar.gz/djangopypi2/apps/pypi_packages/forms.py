import logging
from os.path import basename
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from ..pypi_metadata.definitions import METADATA_VERSIONS
from ..pypi_metadata.models import Classifier
from .models import Package, Release, Distribution

log = logging.getLogger(__name__)

class SearchCharField(forms.CharField):
    def __init__(self, **options):
        super(SearchCharField, self).__init__(**options)
        self.widget.attrs['class'] = 'search-query'
        self.widget.attrs['placeholder'] = 'Search'

class SimplePackageSearchForm(forms.Form):
    query = SearchCharField(max_length=255)

class AdvancedPackageSearchForm(forms.Form):
    name = forms.CharField(required = False, label = 'Name', max_length = 255)
    summary = forms.CharField(required = False, label = 'Summary', max_length = 255)
    description = forms.CharField(required = False, label = 'Description', max_length = 255)
    classifier = forms.ModelMultipleChoiceField(required=False, label = 'Classifiers', queryset=Classifier.objects.all(), widget = forms.SelectMultiple(attrs = {'size': 15}))
    keywords = forms.CharField(required=False, label = 'Keywords', help_text = 'Space-separated words')

class DistributionUploadForm(forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ('content','comment','filetype','pyversion',)
        
    def clean_content(self):
        content = self.cleaned_data['content']
        storage = self.instance.content.storage
        field = self.instance.content.field
        
        name = field.generate_filename(instance=self.instance,
                                       filename=content.name)
        
        if not storage.exists(name):
            log.error('%s does not exist', name)
            return content
        
        if settings.DJANGOPYPI_ALLOW_VERSION_OVERWRITE:
            raise forms.ValidationError('Version overwrite is not yet handled')
        
        raise forms.ValidationError('That distribution already exists, please '
                                    'delete it first before uploading a new '
                                    'version.')

class ReleaseForm(forms.ModelForm):
    metadata_version = forms.CharField(widget=forms.Select(choices=zip(METADATA_VERSIONS.keys(),
                                                                       METADATA_VERSIONS.keys())))
    
    class Meta:
        model = Release
        exclude = ['package', 'version', 'package_info']
