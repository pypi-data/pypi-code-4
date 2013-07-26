# -*- coding: utf-8 -*-
"""
Vues des pages
"""
import json
from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from Sveetchies.django.utils.objects import get_instance_children

from Sveetchies.django.documents.models import Page
from Sveetchies.django.documents.parser import SourceParser
from Sveetchies.django.documents.forms import PageForm, PageQuickForm
from Sveetchies.django.documents.views import RestrictedView, RestrictedCreateView, RestrictedUpdateView, RestrictedDeleteView

class PageIndex(TemplateView):
    """
    Arborescence des pages
    """
    template_name = "documents/page_index.html"
    
    def get(self, request, *args, **kwargs):
        context = {'page_list' : Page.objects.filter(visible=True)}
        return self.render_to_response(context)

class HelpPage(TemplateView):
    """
    Page d'aide à l'utilisation
    """
    template_name = "documents/help.html"
    
    def get(self, request, *args, **kwargs):
        content = render_to_string("documents/help.rst", {})
        #print content
        context = {'content' : SourceParser(content, silent=False)}
        return self.render_to_response(context)

class PagePreview(RestrictedView):
    """
    Vue de prévisualisation ReST
    
    Procède au rendu par le parser d'un contenu soumis par POST dans un argument "data", 
    une requête GET renvoi toujours un document complètement vide, de même si le contenu 
    est vide.
    
    Le contenu du parser est seulement un "fragment" de page et non une page complète, 
    en clair uniquement le rendu HTML du contenu à placer quelque part dans le <body/>.
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

class PageDetails(DetailView):
    """
    Vue d'une page
    """
    model = Page
    context_object_name = "page_instance"
    template_name = "documents/page_details.html"
    
    def get_template_names(self):
        return [self.object.get_template()]

class PageSource(PageDetails):
    """
    Source 'brute' d'une page
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.content, content_type="text/plain; charset=utf-8")

class PageCreate(RestrictedCreateView):
    """
    Vue du formulaire de création d'une page
    """
    model = Page
    context_object_name = "page_instance"
    template_name = "documents/page_form.html"
    form_class = PageForm
    _redirect_to_self = False

    def get(self, request, *args, **kwargs):
        self.parent_page_instance = self._get_parent(**kwargs)
        return super(PageCreate, self).get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        self.parent_page_instance = self._get_parent(**kwargs)
        # Mark to go back to the form page after save, triggered by special submit
        if request.POST and request.POST.get('submit', False):
            if request.POST['submit'] == u"Enregistrer et continuer":
                self._redirect_to_self = True
        return super(PageCreate, self).post(request, *args, **kwargs)
        
    def get_success_url(self):
        if self._redirect_to_self:
            return reverse('documents-page-edit', args=[self.object.slug])
        return reverse('documents-board')

    def _get_parent(self, **kwargs):
        if 'slug' in kwargs:
            return get_object_or_404(Page, slug=kwargs['slug'])
        return None
        
    def get_context_data(self, **kwargs):
        context = super(PageCreate, self).get_context_data(**kwargs)
        context.update({
            'parent_page_instance': self.parent_page_instance,
        })
        return context
    
    def get_form_kwargs(self):
        kwargs = super(PageCreate, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
            'parent': self.parent_page_instance,
            'initial': {'published': datetime.today()},
        })
        return kwargs

class PageEdit(RestrictedUpdateView):
    """
    Vue du formulaire d'édition d'une page
    """
    model = Page
    context_object_name = "page_instance"
    template_name = "documents/page_form.html"
    form_class = PageForm
    _redirect_to_self = False
        
    def post(self, request, *args, **kwargs):
        # Mark to go back to the form page after save, triggered by special submit
        if request.POST and request.POST.get('submit', False):
            if request.POST['submit'] == u"Enregistrer et continuer":
                self._redirect_to_self = True
        return super(PageEdit, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if self._redirect_to_self:
            return reverse('documents-page-edit', args=[self.object.slug])
        return reverse('documents-board')

    def get_form_kwargs(self):
        kwargs = super(PageEdit, self).get_form_kwargs()
        kwargs.update({'author': self.request.user})
        return kwargs

class PageQuicksave(PageEdit):
    """
    Sauvegarde rapide du contenu d'une Page
    
    Uniquement le contenu et seulement pour un objet qui existe déjà (donc édition 
    uniquement, pas pour la création)
    """
    form_class = PageQuickForm
    
    def get_object(self, queryset=None):
        if self.request.POST.get('slug', False):
            self.kwargs['slug'] = self.request.POST['slug']
        return super(PageQuicksave, self).get_object(queryset=queryset)

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

class PageDelete(RestrictedDeleteView):
    """
    Vue du formulaire de suppression d'une page
    
    Supprime l'objet ciblé, la page de confirmation affiche une arborescence recursive 
    des relations de l'objet qui seront aussi supprimés.
    
    NOTE: On pourrait optimiser largement les perfs d'accès BDD de cette vue en 
          utilisant ``mptt`` pour les pages liés, mais on perd la possibilité de voir 
          d'éventuels autre objets liés.
    """
    model = Page
    context_object_name = "page_instance"
    template_name = "documents/page_delete.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context.update({'relations': get_instance_children(self.object)})
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('documents-board')
