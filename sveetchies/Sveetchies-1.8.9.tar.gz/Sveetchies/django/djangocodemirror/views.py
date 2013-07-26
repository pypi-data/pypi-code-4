# -*- coding: utf-8 -*-
import json

from django import forms
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import BaseFormView
from django.http import HttpResponse
from django.template.loader import render_to_string

from Sveetchies.django.djangocodemirror import CODEMIRROR_SETTINGS
from Sveetchies.django.djangocodemirror.fields import CodeMirrorField, DjangoCodeMirrorField

try:
    from Sveetchies.django.documents.parser import SourceParser
except ImportError:
    # Dummy methods
    def SourceParser(source, *args, **kwargs):
        return "<p>This a dummy preview because <tt>Sveetchies.django.documents.parser</tt> is not available.</p>"

try:
    from Sveetchies.django.documents.parser import SourceReporter, map_parsing_errors
except ImportError:
    # Dummy methods
    def map_parsing_errors(error, *args, **kwargs):
        return u"Dummy"
    def SourceReporter(source, *args, **kwargs):
        return []

class DjangoCodeMirrorSampleForm(forms.Form):
    """
    Formulaire de démonstration
    """
    content = DjangoCodeMirrorField(label=u"DjangoCodeMirror", max_length=5000, required=True, codemirror_attrs=CODEMIRROR_SETTINGS['djangocodemirror_sample_demo'])
    
    def clean_content(self):
        """
        Parse le contenu pour vérifier qu'il ne contient par d'erreurs de syntaxe
        """
        content = self.cleaned_data.get("content")
        if content:
            errors = SourceReporter(content)
            if errors:
                raise forms.ValidationError(map(map_parsing_errors, errors))
        return content
    
    def save(self, *args, **kwargs):
        return

class Sample(TemplateView):
    """
    Vue de la page de démonstration
    """
    template_name = "djangocodemirror/sample.html"
    
    def get(self, request, *args, **kwargs):
        context = {
            'form' : DjangoCodeMirrorSampleForm(),
            'demo_content': render_to_string("djangocodemirror/help.rst", {}),
        }
        return self.render_to_response(context)

class SamplePreview(View):
    """
    Vue de prévisualisation
    """
    def parse_content(self, request, *args, **kwargs):
        content = request.POST.get('content', None)
        if content:
            return SourceParser(content, silent=False)
        return ''

    def get(self, request, *args, **kwargs):
        return HttpResponse('')
    
    def post(self, request, *args, **kwargs):
        content = self.parse_content(request, *args, **kwargs)
        return HttpResponse( content )

class SampleQuicksave(BaseFormView):
    """
    Exemple de sauvegarde rapide
    """
    form_class = DjangoCodeMirrorSampleForm
    
    def get(self, request, *args, **kwargs):
        return HttpResponse('')
    
    def form_valid(self, form):
        content = json.dumps({'status':'form_valid'})
        form.save()
        return HttpResponse(content, content_type='application/json')

    def form_invalid(self, form):
        content = json.dumps({
            'status':'form_invalid',
            'errors': dict(form.errors.items()),
        })
        return HttpResponse(content, content_type='application/json')
