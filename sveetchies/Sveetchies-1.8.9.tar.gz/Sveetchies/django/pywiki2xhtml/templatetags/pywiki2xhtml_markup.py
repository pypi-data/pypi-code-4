# -*- coding: utf-8 -*-
#
# Template tags pour utiliser PyWiki2Xhtml
#
from django import template
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

from PyWiki2xhtml.macros.parser import Wiki2XhtmlMacros as Wiki2XhtmlParser
from PyWiki2xhtml.macros.macro_attach import parse_macro_attach
from PyWiki2xhtml.macros.macro_pygments import parse_macro_pygments
from PyWiki2xhtml.macros.macro_mediaplayer import parse_macro_mediaplayer
from PyWiki2xhtml.macros.macro_gmap import parse_macro_googlemap

from Sveetchies.django.attachments.utils import get_attachment_items_from_list
from Sveetchies.django.utils import get_string_or_variable

from Sveetchies.django.pywiki2xhtml import PYWIKI2XHTML_CONFIGSET, PYWIKI2XHTML_CONTAINER

register = template.Library()

@register.tag(name="wiki2xhtml")
def do_wiki2xhtml_transform(parser, token):
    """
    Lecture de préparation du Tag de transformation de texte par PyWiki2Xhtml
   
   {% wiki2xhtml text[ configset_name[ published_wikipage[ attachment_items]]] %}
    
    Appel du tag simplement : ::
    
        {% wiki2xhtml text %}
    
    Appel du tag en spécifiant un nom de schéma d'options particulier : ::
    
        {% wiki2xhtml text 'myschema' %}
    
    Appel du tag en indiquant les pages publiés pour les Wikiword : ::
    
        {% wiki2xhtml text None published_wikipage %}
    
    Appel du tag en indiquant les pages publiés pour les Wikiword et en indiquant la 
    liste des fichiers attachés au document : ::
    
        {% wiki2xhtml text published_wikipage attachment_items %}
    
    Appel du tag en indiquant uniquement la liste des fichiers attachés au document : ::
    
        {% wiki2xhtml text None attachment_items %}
    
    * 'text' est le texte du document à transformer;
    * (optionnel) 'configset_name' est un nom clé de schéma d'options pour PyWiki2Xhtml 
      configuré dans settings.PYWIKI2XHTML_CONFIGSET. Si cette variable vaut ``None`` le 
      schéma ``standard`` (livré dans PyWiki2Xhtml) est utilisé par défaut.
    * (optionnel) 'published_wikipage' est un dictionnaire sous la forme uri=>titre des 
      pages publiés qui va permettre le remplacement des mots Wiki par leur lien;
    * (optionnel) 'attachment_items' est un dictionnaire des fichiers attachés au document 
      disponibles.
    
    Le rendu final de la conversion est intégré dans ``settings.PYWIKI2XHTML_CONTAINER`` 
    si il est rempli. Il doit contenir au moins la variable ``{content}`` qui sera le 
    résultat de conversion, pour désactiver ce conteneur, mettez simplement 
    ``settings.PYWIKI2XHTML_CONTAINER`` à ``None``.
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
    def __init__(self, value, configset_name=None, published_wikipage=None, attachment_items=None):
        self.value = value
        self.configset_name = configset_name
        self.published_wikipage = published_wikipage
        self.attachment_items = attachment_items
    
    def render(self, context):
        string = ''
        value = get_string_or_variable(self.value, context, capture_none_value=False)
        
        # Schéma d'options pour pywiki2xhtml
        configset_name = "standard"
        if self.configset_name:
            name = get_string_or_variable(self.configset_name, context, capture_none_value=True)
            if name:
                configset_name = name
        
        # Liste des Wikipage publiés pour les Wikiword
        if self.published_wikipage:
            published_wikipage = get_string_or_variable(self.published_wikipage, context)
            if published_wikipage:
                PYWIKI2XHTML_CONFIGSET[configset_name].update({'published_wikipage': published_wikipage})
        
        # Dictionnaire des fichiers attachés au document disponibles
        attachment_items = {}
        if self.attachment_items:
            attachment_items = get_attachment_items_from_list(get_string_or_variable(self.attachment_items, context, safe=True, default=[], capture_none_value=False))
        
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.kwargsOpt(PYWIKI2XHTML_CONFIGSET[configset_name])
        W2Xobject.setOpt('attached_items', attachment_items)
        W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)
        W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
        W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
        W2Xobject.add_macro('googlemap', mode='post', func=parse_macro_googlemap)
        string = mark_safe(W2Xobject.transform( force_unicode(value) ))
        
        if PYWIKI2XHTML_CONTAINER:
            return PYWIKI2XHTML_CONTAINER.format(content=string)
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
    
    De ce fait, il n'utilise pas le conteneur automatique 
    ``settings.PYWIKI2XHTML_CONTAINER``.
    
    Exemple : ::
    
        {% wiki2xhtml_render text configset_name published_wikipage attachment_items %}
        {% if W2X_Summary %}<div class="summary">{{ W2X_Summary }}</div>{% endif %}
        <div class="xhtml_render">{{ W2X_Xhtml }}</div>
    
    Les arguments sont les mêmes et fonctionnent comme avec son homologue (le tag 
    "wiki2xhtml") à la différence que si l'argument ``configset_name`` vaut ``None`` le 
    schéma ``standard_with_summary`` (livré dans PyWiki2Xhtml) est utilisé par défaut au 
    lieu de ``standard``.
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
    def __init__(self, value, configset_name=None, published_wikipage=None, attachment_items=None):
        self.value = value
        self.configset_name = configset_name
        self.published_wikipage = published_wikipage
        self.attachment_items = attachment_items
    
    def render(self, context):
        # Résolution de la variable donnée pour la source wiki
        value = get_string_or_variable(self.value, context, capture_none_value=False)
        
        # Schéma d'options pour pywiki2xhtml
        configset_name = "standard_with_summary"
        if self.configset_name:
            configset_name = get_string_or_variable(self.configset_name, context, capture_none_value=False)
        
        # Liste des Wikipage publiés pour les Wikiword
        if self.published_wikipage:
            published_wikipage = get_string_or_variable(self.published_wikipage, context)
            if published_wikipage:
                PYWIKI2XHTML_CONFIGSET[configset_name].update({'published_wikipage': published_wikipage})
        
        # Dictionnaire des fichiers attachés au document disponibles
        attachment_items = {}
        if self.attachment_items:
            attachment_items = get_attachment_items_from_list(get_string_or_variable(self.attachment_items, context, safe=True, default=[], capture_none_value=False))
        
        # Init le parser avec ses options
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.kwargsOpt(PYWIKI2XHTML_CONFIGSET[configset_name])
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
