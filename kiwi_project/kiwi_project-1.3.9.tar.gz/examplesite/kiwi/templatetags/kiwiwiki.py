# -*- coding: utf-8 -*-
import copy

from django.conf import settings
from django.core.urlresolvers import reverse
from django import template
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe

from PyWiki2xhtml.macros.helper import Wiki2XhtmlMacrosHelper as Wiki2XhtmlHelper
from PyWiki2xhtml import __title__ as parser_name

from Sveetchies.django.utils import get_string_or_variable
from Sveetchies.django.TreeMaker import TemplatedTree

from kiwi.models import Wikipage

from kiwi import PyWiki2Xhtml_ConfigSet
from kiwi.utils import urlify_wikipage_object

register = template.Library()

@register.tag(name="treeview")
def do_treeview_tag(parser, token):
    """
    Lecture de préparation du Tag "treeview" qui créer une arborescence à 
    partir d'une liste "plane" d'éléments.
    
    Arborescence complète :
    
        {% treeview seq %}
    
    Arborescence complète avec un template customisé :
    
        {% treeview seq recursed_template %}
    
    Arborescence à partir d'une page avec un template customisé :
    
        {% treeview seq None wikipage_id %}
    
    * seq : Liste d'objets à mettre en arborescence. Pour plus d'infos sur le 
      format voir la classe de base "RawTreeMaker".
    * recursed_template : Optionnel, défini un chemin vers un template custom 
      pour chaque niveau d'arborescence. Si il est égale à None, il sera ignoré.
    * wikipage_id : identifiant de la wikipage à partir de laquelle démarrer 
      l'arborescence.
    """
    try:
        tag_name, seq, recursed_template, wikipage_id = token.contents.split(None, 3)
    except ValueError:
        try:
            tag_name, seq, recursed_template = token.contents.split(None, 2)
        except ValueError:
            try:
                tag_name, seq = token.contents.split(None, 1)
            except ValueError:
                raise template.TemplateSyntaxError, "You need to specify an item list."
            else:
                return treeview_tag(seq)
        else:
            return treeview_tag(seq, recursed_template)
    else:
        return treeview_tag(seq, recursed_template, wikipage_id)

class treeview_tag(template.Node):
    """
    Génération du rendu html du tag "treeview"
    """
    def __init__(self, seq, recursed_template=None, wikipage_id=None):
        self.seq = seq
        self.recursed_template = recursed_template
        self.wikipage_id = wikipage_id
    
    def render(self, context):
        kwargs = {}
        seq = get_string_or_variable(self.seq, context)
        wikipage_id = None
        if self.wikipage_id:
            wikipage_id = get_string_or_variable(self.wikipage_id, context)
        if self.recursed_template and self.recursed_template != "None":
            kwargs['recursed_template'] = get_string_or_variable(self.recursed_template, context)
        
        # Calcule l'arborescence
        treeobject = TemplatedTree(seq=seq, order_key='order')
        treeobject.get_tree(parent_id=wikipage_id)
        
        return treeobject.render(**kwargs)

@register.tag(name="pathline")
def do_pathline_tag(parser, token):
    """
    Lecture de préparation du Tag "pathline" qui permet de créer un chemin 
    de la page la haute dans la hiérarchie du site vers celle en cours.
    
    Appel du tag :
    
        {% pathline seq item_id %}
    
    * "seq" est une liste de toute les pages wiki.
    * "item_id" est l'identifiant de la page en cours.
    """
    try:
        tag_name, seq, item_id = token.contents.split(None, 2)
    except ValueError:
        raise template.TemplateSyntaxError, "You need to specify an item list and an item id."
    else:
        return pathline_tag(seq, item_id)

class pathline_tag(template.Node):
    """
    Génération du rendu html du tag "pathline".
    """
    def __init__(self, seq, item_id, link_template='<a href="%(uri)s">%(title)s</a>', separator='&nbsp;&gt; '):
        self.seq = seq
        self.item_id = item_id
        self.link_template = link_template
        self.separator = separator
    
    def render(self, context):
        seq = get_string_or_variable(self.seq, context, safe=True)
        # En cas d'échec de résolution, le tag reste silencieux
        if not seq:
            return ''
        item_id = get_string_or_variable(self.item_id, context)
        
        # Calcule l'arborescence
        treeobject = TemplatedTree(seq=seq)
        treeobject.get_tree()
        # Revisite chaque item pour changer l'uri par une url absolue vers la 
        # page
        pathline_list = [ urlify_wikipage_object(page) for page in treeobject.get_pathline(item_id)]
        # Renvoi chaque élément joint par un séparateur
        return self.separator.join([self.link_template%page for page in pathline_list])

@register.tag(name="wikidocument")
def do_wikipage_document(parser, token):
    """
    Lecture de préparation du Tag "wikidocument". Il permet d'insérer une page 
    wiki bien définie dans un template.
    
    Appel du tag : ::
    
        {% wikidocument wikipage_uri %}
    
    Appel du tag avec un template customisé : ::
    
        {% wikidocument wikipage_uri custom_template %}
    
    * wikipage_uri: variable qui indique l'uri de la page wiki à insérer;
    * custom_template: Chemin d'un template spécifique qui prendra la main sur celui 
      configuré sur le document.
    """
    try:
        tag_name, wikipage_uri, custom_template = token.contents.split(None, 2)
    except ValueError:
        try:
            tag_name, wikipage_uri = token.contents.split(None, 1)
        except ValueError:
            raise template.TemplateSyntaxError, "You need to specify a wikipage uri."
        else:
            return wikipage_document_view(wikipage_uri)
    else:
        return wikipage_document_view(wikipage_uri, custom_template)

class wikipage_document_view(template.Node):
    """
    Génération du rendu html du tag "wikidocument".
    
    TODO: ce tag utilise un chemin de template en dur alors qu'il devrait utiliser le 
    chemin du template associé au document. Par contre je ne vois pas encore le 
    comportement à adopter si le gabarit n'est pas du type document intégré 
    (included=True), lever une erreur ? échec silencieux ?
    TODO: En fait le problème vient du fait qu'une wikipage peut ne pas avoir de template 
    spécifié.
    """
    def __init__(self, wikipage_uri, custom_template=None):
        self.wikipage_uri = wikipage_uri
        self.custom_template = custom_template
    
    def render(self, context):
        string = ""
        # Résolutions des variables
        if self.custom_template:
            self.custom_template = get_string_or_variable(self.custom_template, context)
        self.wikipage_uri = get_string_or_variable(self.wikipage_uri, context)
        # Document wiki à afficher
        try:
            wikipageObject = Wikipage.objects.get(uri=self.wikipage_uri, active=True)
        except Wikipage.DoesNotExist:
            wikipageObject = None
        
        # Forme la sortie html
        if wikipageObject:
            template_name = 'kiwi/document.html'
            # Le template spécifique du document prends la main sur celui par 
            # défaut
            if wikipageObject.template:
                template_name = wikipageObject.template.path
            # Le template donné dans le tag prends la main sur tout les autres
            if self.custom_template:
                template_name = self.custom_template
            
            context.update({
                'wikipageObject' : wikipageObject,
                'wikipageAllPub': Wikipage.objects.get_active_dict(),
                'attachment_items': wikipageObject.get_attachments(user=context['user']),
            })
            string = template.loader.get_template(template_name).render(template.Context(context))
        
        return mark_safe( string )

@register.tag(name="attached_files_widget")
def do_attached_files_widget(parser, token):
    """
    Lecture de préparation du Tag "attached_files_widget". Qui intègre le widget de la 
    liste des fichiers attachés à une Wikipage.
    
    Appel du tag :
    
        {% attached_files_widget wikipage_object %}
    
    Ou avec un template spécifique :
    
        {% attached_files_widget wikipage_object custom_template %}
    
    * "wikipage_object" est un objet d'une Wikipage.
    * "custom_template" est un template sur mesure à spécifier au lieu de celui par 
      défaut.
    """
    args = token.split_contents()
    if args < 2:
        raise template.TemplateSyntaxError, "You need to specify at less a Wikipage object"
    else:
        return attached_files_widget_view(*args[1:])

class attached_files_widget_view(template.Node):
    """
    Génération du rendu html du tag "attached_files_widget".
    """
    def __init__(self, wikipage_object, widget_template='kiwi/attached_files_widget.html'):
        self.wikipage_object = wikipage_object
        self.widget_template = widget_template
    
    def render(self, context):
        string = ""
        
        wikipage_object = get_string_or_variable(self.wikipage_object, context)
        user = get_string_or_variable('user', context, safe=True)
        
        widget_context = {
            'wikipageObject': wikipage_object,
            'attachment_items': wikipage_object.get_attachments(user=user),
            'user': user,
        }
        string = template.loader.get_template(self.widget_template).render(template.Context(widget_context))
        
        return mark_safe( string )

@register.tag(name="wikisyntax")
def do_wikipage_syntax(parser, token):
    """
    Lecture de préparation du Tag "wikisyntax". Il permet d'insérer la vue de 
    la démonstration dynamique de la syntaxe du parser.
    
    Appel du tag :
    {% wikisyntax %}
    """
    return wikipage_syntax_view()

class wikipage_syntax_view(template.Node):
    """
    Génération du rendu html du tag "wikisyntax".
    """
    def render(self, context):
        template_name = 'kiwi/syntax_help_content.html'
        
        opts = copy.deepcopy(PyWiki2Xhtml_ConfigSet['standard'])
        # Liste bidon de fichiers attachés pour tester la macro 'attach'
        opts['attached_items'] = {
            '1': ("http://perdu.com/prout.pdf", "Prout !"),
            '11': "http://perdu.com/plouf.pdf",
            '42': "http://sveetch.net/download.py?coco|file=cocolapin.xls&validate=true",
            'totoz': "http://sveetch.net/download.py?file=totoz.gif",
        }
        
        helperObject = Wiki2XhtmlHelper(opts=opts)
        object_list = helperObject.render()
        extra_context = {
            'object_list': object_list,
            'parser_name': parser_name,
        }
        
        string = template.loader.get_template(template_name).render(template.Context(extra_context))
        
        return mark_safe( string )
