# -*- coding: utf-8 -*-
"""
Template tags de pagination pour Django

Exemple d'un template "pagination.html" à intégrer dans le projet pour la pagination : ::

    {% comment %} Template d'inclusion utilisé par Sveetchies.django.tags.pagination {% endcomment %}
    {% load i18n %}
    <div class="pagination ui-corner-all">
        <p class="resume">
            {% trans 'global.page' %} {{ page }} {% trans 'global.on' %} {{ pages }}
            {% trans 'global.for' %} {{ hits }} {% trans 'global.totalresults' %}.
        </p>
        {% if has_previous %}<p class="previous"><a href="{{ url_arg }}{{ previous }}">Précédent</a></p>
        {% else %}<p class="disabled previous"><span>Précédent</span></p>
        {% endif %}
        
        <p class="index">{{ index|safe }}</p>
        
        {% if has_next %}<p class="next"><a href="{{ url_arg }}{{ next }}">Suivant</a></p>
        {% else %}<p class="disabled next"><span>Suivant</span></p>
        {% endif %}
        
        <div class="cale"></div>
    </div>
    <div class="cale"></div>
"""
from django.conf import settings
from django import template

import datetime

register = template.Library()

# Paramètres par défauts optionnels qui peuvent être surchargés dans les settings
DEFAULT_PAGINATION_TEMPLATE = getattr(settings, 'PAGINATION_TEMPLATE', 'pagination.html')
DEFAULT_PAGINATION_MAX_INDEX_DISPLAY = getattr(settings, 'PAGINATION_MAX_INDEX_DISPLAY', None)
DEFAULT_PAGINATION_INDEX_LINK_HTML = getattr(settings, 'PAGINATION_INDEX_LINK_HTML', '<a href="%s%d">%d</a>')
DEFAULT_PAGINATION_INDEX_CURRENT_HTML = getattr(settings, 'PAGINATION_INDEX_CURRENT_HTML', '<span class="active">%d</span>')

@register.tag(name="pagination_tag")
def do_pagination_tag(parser, token):
    """
    Lecture de préparation du Tag de pagination des résultats
    
    Appel du tag simplement : ::
    
        {% pagination_tag %}
    
    Appel du tag avec une url customisée : ::
    
        {% pagination_tag url_arg %}
    
    Appel avec un nom de template : ::
    
        {% pagination_tag url_arg pagination_template %}
    
    url_arg
        Chaînes de caractères contenant une chaîne d'arguments d'URL à adjoindre aux 
        liens de navigation dans les résultats.
    pagination_template
        Chemin d'un template particulier à utiliser.
    
    À noter que pour passer le nom de template, il faut aussi passer ``url_arg``, 
    même vide.
    """
    args = token.split_contents()
    return PaginationResultsIndex(*args[1:])

class PaginationResultsIndex(template.Node):
    """
    Génération du rendu html du tag de pagination des résultats
    Prends un nombre de page, le numéro de la page actuelle et l'argument 
    d'url pour former les liens et produit une liste de numéro de page 
    cliquable séparé par un tiret
    """
    def __init__(self, url_arg='?page=', template_pagination=DEFAULT_PAGINATION_TEMPLATE, max_index_display=DEFAULT_PAGINATION_MAX_INDEX_DISPLAY):
        self.url_arg = url_arg
        self.custom_template = template_pagination
        self.common_template = DEFAULT_PAGINATION_TEMPLATE
        self.max_index_display = max_index_display
        self.span = DEFAULT_PAGINATION_INDEX_CURRENT_HTML
        self.link = DEFAULT_PAGINATION_INDEX_LINK_HTML
    
    def render(self, context):
        """
        Rendu du tag
        """
        # Si le context est paginé, on peut continuer et récupérer le 
        # nécessaire sinon on renvoi une chaine vide
        if not context.get('is_paginated', False):
            return ''
        # Class based view don't return a verbose context, 
        # only a "page_obj"
        page_obj = context['page_obj']
        paginator = context['paginator']
        self.p_context = {
            'results_per_page': paginator.per_page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page': page_obj.number,
            'next': page_obj.next_page_number(),
            'previous': page_obj.previous_page_number(),
            'pages': paginator.num_pages,
            'hits': paginator.count,
            'max_index_display': self.max_index_display,
        }
        # Tente de récupérer les arguments d'url optionnels, on peut y rajouter 
        # des arguments pour des formulaires de recherches, l'url doit comprendre 
        # l'argument du numéro de page à la fin
        try:
            self.p_context['url_arg'] = template.resolve_variable(self.url_arg, context)
        except template.VariableDoesNotExist:
            self.p_context['url_arg'] = "?page="
        # Tente de récupérer le nom de template optionnel
        try:
            self.template = template.resolve_variable(self.custom_template, context)
        except template.VariableDoesNotExist:
            self.template = self.common_template
        
        self.p_context['index'] = self.__make_index()
        return template.loader.get_template( self.template ).render( template.Context(self.p_context) )

    def __make_index(self):
        """
        Génération de l'index des pages disponibles
        
        L'index peut être limité à une tranche de pages à afficher, de façon à ne pas 
        générer un pavé d'index par exemple dans le cas de 500pages, n'afficher qu'une 
        tranche de 10pages dont la page courante se trouve au milieu.
        
        :rtype: string
        :return: Liens des pages de résultats.
        """
        index_range = self.__get_index_range()
        
        # On fait une liste simple en fonction du nombre de pages
        seq = []
        for p in index_range:
            html = self.link % (self.p_context['url_arg'], p, p)
            if self.p_context['page'] and self.p_context['page']==p:
                html = self.span % p
            seq.append( html )
        
        # Joint la liste avec séparateur
        resp = ' - '.join(seq)
        return resp
        
    def __get_index_range(self):
        """
        Calcul de la rangée d'index selon les limites si il y'en a sinon renvoi 
        simplement la rangée complète de toute les pages
        
        :rtype: list
        :return: Liste des numéros de pages de résultats dans la rangée courante.
        """
        if self.p_context['max_index_display'] and self.p_context['max_index_display'] > 0:
            if self.p_context['pages'] > self.p_context['max_index_display']:
                # Début de rangée
                left_slice = self.p_context['max_index_display']/2
                if left_slice >= self.p_context['page']:
                    left_slice = self.p_context['page']-1
                start = self.p_context['page'] - left_slice
                # Fin de la rangée
                end = start+self.p_context['max_index_display']
                if (end-1) > self.p_context['pages']:
                    end = self.p_context['pages']+1
                # Rangée calculée
                index_range = range(start, end)
                # Correction
                if len(index_range) < self.p_context['max_index_display']:
                    reserve = self.p_context['max_index_display'] - len(index_range)
                    # Ajout au début uniquement sans tenir compte de end
                    index_range = range(start-reserve, end)
                return index_range
        
        return range( 1, self.p_context['pages']+1 )
