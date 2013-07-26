# -*- coding: utf-8 -*-
"""
Vues des documents à insérer
"""
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse

from Sveetchies.django.utils.objects import get_instance_children

from Sveetchies.django.documents.models import Insert
from Sveetchies.django.documents.parser import SourceParser
from Sveetchies.django.documents.forms import InsertForm, InsertQuickForm
from Sveetchies.django.documents.views import RestrictedCreateView, RestrictedUpdateView, RestrictedDeleteView

class InsertCreate(RestrictedCreateView):
    """
    Vue du formulaire de création d'une insert
    """
    model = Insert
    context_object_name = "insert_instance"
    template_name = "documents/insert_form.html"
    form_class = InsertForm
    _redirect_to_self = False

    def post(self, request, *args, **kwargs):
        # Mark to go back to the form page after save, triggered by special submit
        if request.POST and request.POST.get('submit', False):
            if request.POST['submit'] == u"Enregistrer et continuer":
                self._redirect_to_self = True
        return super(InsertCreate, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if self._redirect_to_self:
            return reverse('documents-insert-edit', args=[self.object.slug])
        return reverse('documents-board')
    
    def get_form_kwargs(self):
        kwargs = super(InsertCreate, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
        })
        return kwargs

class InsertEdit(RestrictedUpdateView):
    """
    Vue du formulaire d'édition d'une insert
    """
    model = Insert
    context_object_name = "insert_instance"
    template_name = "documents/insert_form.html"
    form_class = InsertForm
    _redirect_to_self = False

    def post(self, request, *args, **kwargs):
        # Mark to go back to the form page after save, triggered by special submit
        if request.POST and request.POST.get('submit', False):
            if request.POST['submit'] == u"Enregistrer et continuer":
                self._redirect_to_self = True
        return super(InsertEdit, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if self._redirect_to_self:
            return reverse('documents-insert-edit', args=[self.object.slug])
        return reverse('documents-board')
    
    def get_form_kwargs(self):
        kwargs = super(InsertEdit, self).get_form_kwargs()
        kwargs.update({'author': self.request.user})
        return kwargs

class InsertQuicksave(InsertEdit):
    """
    Sauvegarde rapide du contenu d'un Insert
    
    Uniquement le contenu et seulement pour un objet qui existe déjà (donc édition 
    uniquement, pas pour la création)
    """
    form_class = InsertQuickForm
    
    def get_object(self, queryset=None):
        if self.request.POST.get('slug', False):
            self.kwargs['slug'] = self.request.POST['slug']
        return super(InsertQuicksave, self).get_object(queryset=queryset)

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

class InsertDelete(RestrictedDeleteView):
    """
    Vue du formulaire de suppression d'une insert
    
    Supprime l'objet ciblé, la insert de confirmation affiche une arborescence recursive 
    des relations de l'objet qui seront aussi supprimés.
    """
    model = Insert
    context_object_name = "insert_instance"
    template_name = "documents/insert_delete.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context.update({'relations': get_instance_children(self.object)})
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('documents-board')
