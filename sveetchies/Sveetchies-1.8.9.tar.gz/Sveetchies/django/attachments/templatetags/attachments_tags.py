# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

from Sveetchies.django.utils import get_string_or_variable

from Sveetchies.django.attachments import ATTACHMENTS_WIDGET_TEMPLATEPATH

register = template.Library()

@register.tag(name="attachments_widget")
def do_attachments_widget(parser, token):
    """
    Lecture de préparation du Tag "attached_files_widget"
    
    Appel du tag :
    
        {% attachments_widget object %}
    
    Ou avec un template spécifique :
    
        {% attachments_widget object custom_template %}
    
    * "object" est un objet dont le modèle possède une méthode "get_attachments";
    * "templatepath" est un template sur mesure à spécifier au lieu de celui par 
      défaut.
    """
    args = token.split_contents()
    if args < 2:
        raise template.TemplateSyntaxError, "You need to specify at less an object"
    else:
        return attachments_widget_view(*args[1:])

class attachments_widget_view(template.Node):
    """
    Génération du rendu html du tag "attached_files_widget".
    """
    def __init__(self, container_object, templatepath=None):
        self.container_object = container_object
        self.templatepath = templatepath
    
    def render(self, context):
        string = ""
        
        container_object = get_string_or_variable(self.container_object, context)
        user = get_string_or_variable('user', context, safe=True)
        templatepath = ATTACHMENTS_WIDGET_TEMPLATEPATH
        if self.templatepath:
            templatepath = get_string_or_variable(self.templatepath, context, capture_none_value=True)
        
        context.update({
            'attachments_container_object': container_object,
            'attachments_object_list': container_object.get_attachments(user=user),
        })
        string = template.loader.get_template(templatepath).render(template.Context(context))
        
        return mark_safe(string)
