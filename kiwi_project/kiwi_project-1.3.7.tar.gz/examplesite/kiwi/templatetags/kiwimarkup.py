# -*- coding: utf-8 -*-
#
# This script is part of Kiwi.
#
from django.conf import settings
from django import template
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

from PyWiki2xhtml.macros.parser import Wiki2XhtmlMacros as Wiki2XhtmlParser
from PyWiki2xhtml.macros.macro_attach import parse_macro_attach
from PyWiki2xhtml.macros.macro_pygments import parse_macro_pygments
from PyWiki2xhtml.macros.macro_mediaplayer import parse_macro_mediaplayer
from PyWiki2xhtml.macros.macro_gmap import parse_macro_googlemap

from Sveetchies.django.utils import get_string_or_variable

from kiwi import PyWiki2Xhtml_ConfigSet
from kiwi.utils import get_attachment_items_from_list

register = template.Library()

@register.tag(name="wiki2xhtml")
def do_wiki2xhtml_transform(parser, token):
    """
    Lecture de préparation du Tag de transformation de texte par PyWiki2Xhtml
    
    Appel du tag simplement : ::
    
        {% wiki2xhtml text %}
    
    Appel du tag en indiquant les pages publiés pour les Wikiword : ::
    
        {% wiki2xhtml text published_wikipage %}
    
    Appel du tag en indiquant les pages publiés pour les Wikiword et en indiquant la 
    liste des fichiers attachés au document : ::
    
        {% wiki2xhtml text published_wikipage attachment_items %}
    
    Appel du tag en indiquant uniquement la liste des fichiers attachés au document : ::
    
        {% wiki2xhtml text None attachment_items %}
    
    * 'text' est le texte du document à transformer;
    * (optionnel) 'published_wikipage' est un dictionnaire sous la forme uri=>titre des 
      pages publiés qui va permettre le remplacement des mots Wiki par leur lien;
    * (optionnel) 'attachment_items' est un dictionnaire des fichiers attachés au document 
      disponibles. 
    """
    args = token.split_contents()
    if args < 2:
        raise template.TemplateSyntaxError, "You need to specify a text value."
    else:
        return wiki2xhtml_transform(*args[1:])

class wiki2xhtml_transform(template.Node):
    """
    Génération du rendu html du tag "wiki2xhtml"
    """
    def __init__(self, value, published_wikipage=None, attachment_items=None):
        self.value = value
        self.published_wikipage = published_wikipage
        self.attachment_items = attachment_items
    
    def render(self, context):
        string = ''
        value = get_string_or_variable(self.value, context, capture_none_value=False)
        
        # Liste des Wikipage publiés pour les Wikiword
        if self.published_wikipage:
            published_wikipage = get_string_or_variable(self.published_wikipage, context)
            if published_wikipage:
                PyWiki2Xhtml_ConfigSet['standard'].update({'published_wikipage': published_wikipage})
        
        # Dictionnaire des fichiers attachés au document disponibles
        attachment_items = {}
        if self.attachment_items:
            attachment_items = get_attachment_items_from_list(get_string_or_variable(self.attachment_items, context, safe=True, default=[], capture_none_value=False))
        
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.kwargsOpt(PyWiki2Xhtml_ConfigSet['standard'])
        W2Xobject.setOpt('attached_items', attachment_items)
        W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)
        W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
        W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
        W2Xobject.add_macro('googlemap', mode='post', func=parse_macro_googlemap)
        string = mark_safe(W2Xobject.transform( force_unicode(value) ))
            
        return string

@register.tag(name="wiki2xhtml_render")
def do_wiki2xhtml_render(parser, token):
    """
    Lecture de préparation du Tag de transformation de texte par PyWiki2Xhtml
    
    Contraire au tag "wiki2xhtml", celui ci n'est pas remplacé directement par 
    la transformation de la source wiki en xhtml. En fait ce tag, insère dans 
    le context courant (du template) plusieurs nouvelles variables :
    
    * W2X_Xhtml : Le rendu xhtml de la source wiki
    * W2X_Summary : Un sommaire du document calculé à partir de ses titres. 
      S'il n'en possède pas 'None' sera renvoyé.
    
    Exemple : ::
    
        {% wiki2xhtml_render text published_wikipage attachment_items %}
        {% if W2X_Summary %}<div class="summary">{{ W2X_Summary }}</div>{% endif %}
        <div class="xhtml_render">{{ W2X_Xhtml }}</div>
    
    Les arguments sont les mêmes et fonctionnent comme avec son homologue (le tag 
    "wiki2xhtml").
    """
    args = token.split_contents()
    if args < 2:
        raise template.TemplateSyntaxError, "You need to specify a text value."
    else:
        return wiki2xhtml_render(*args[1:])

class wiki2xhtml_render(template.Node):
    """
    Génération du rendu html du tag "wiki2xhtml_render"
    """
    def __init__(self, value, published_wikipage=None, attachment_items=None):
        self.value = value
        self.published_wikipage = published_wikipage
        self.attachment_items = attachment_items
    
    def render(self, context):
        # Résolution de la variable donnée pour la source wiki
        value = get_string_or_variable(self.value, context, capture_none_value=False)
        
        # Liste des Wikipage publiés pour les Wikiword
        if self.published_wikipage:
            published_wikipage = get_string_or_variable(self.published_wikipage, context)
            if published_wikipage:
                PyWiki2Xhtml_ConfigSet['standard_with_summary'].update({'published_wikipage': published_wikipage})
        
        # Dictionnaire des fichiers attachés au document disponibles
        attachment_items = {}
        if self.attachment_items:
            attachment_items = get_attachment_items_from_list(get_string_or_variable(self.attachment_items, context, safe=True, default=[], capture_none_value=False))
        
        # Init le parser avec ses options
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.kwargsOpt(PyWiki2Xhtml_ConfigSet['standard_with_summary'])
        W2Xobject.setOpt('attached_items', attachment_items)
        W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)
        W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
        W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
        W2Xobject.add_macro('googlemap', mode='post', func=parse_macro_googlemap)
        
        # Rendu complet de la source
        W2X_Render = W2Xobject.render( force_unicode(value) )
        
        # Insertion dans le context des résultats
        context['W2X_Xhtml'] = mark_safe(W2X_Render['xhtml'])
        if W2X_Render['summary']:
            context['W2X_Summary'] = mark_safe(W2X_Render['summary'])
        else:
            context['W2X_Summary'] = None
        
        return ''
