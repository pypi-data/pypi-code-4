# -*- coding: utf-8 -*-
"""
Vues de l'interface
"""
from Sveetchies.django.documents.models import Page, Insert
from Sveetchies.django.documents.views import RestrictedTemplateView

class BoardIndex(RestrictedTemplateView):
    """
    Gestion des documents
    """
    template_name = "documents/board.html"

    def get(self, request, *args, **kwargs):
        context = {
            'page_list' : Page.objects.filter(),
            'insert_list' : Insert.objects.filter().order_by('slug'),
        }
        return self.render_to_response(context)
