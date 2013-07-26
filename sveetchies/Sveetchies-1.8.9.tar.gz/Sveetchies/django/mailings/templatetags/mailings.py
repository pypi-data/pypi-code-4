# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

from Sveetchies.django.utils import get_string_or_variable

from Sveetchies.django import mailings

register = template.Library()

@register.tag(name="template_context_help")
def do_template_context_help(parser, token):
    """
    Lecture de préparation du Tag *template_context_help*
    
    Ce tag génère juste le contenu de la cellule indiqué, sans aucun html de conteneur
    
    Arguments :
    
    key
        Clé du template dans le registre de mailings
        
    Exemples d'utilisations : ::
    
        {% template_context_help key %}
    
    :type parser: object ``django.template.Parser``
    :param parser: Objet du parser de template.
    
    :type token: object ``django.template.Token``
    :param token: Objet de la chaîne découpée du tag capturé dans le template.
    
    :rtype: object `TemplateContextHelpTagRender`
    :return: L'objet du générateur de rendu du tag.
    """
    args = token.split_contents()
    if len(args[1:]) == 1:
        return TemplateContextHelpTagRender(*args[1:])
    else:
        raise template.TemplateSyntaxError, "Tag requires exactly one argument: the key template."

class TemplateContextHelpTagRender(template.Node):
    """
    Génération du rendu html du tag *template_context_help*
    """
    def __init__(self, key):
        """
        :type key: string
        :param key: Clé du template
        """
        self.key = key
    
    def render(self, context):
        """
        Rendu de la balise
        
        :type context: object ``django.template.Context``
        :param context: Objet du contexte du tag.
        
        :rtype: string
        :return: Le rendu généré pour le tag capturé.
        """
        html = ''
        
        template_name = 'admin/mailings/template/template_context_help.html'
        key = get_string_or_variable(self.key, context)
        
        # Tente de récupérer le module du controleur du template
        try:
            tplModule = mailings.site._registry[key]
        # Controleur inconnu au registre
        except KeyError:
            return mark_safe(u"<p>Ce template n'est pas inscrit au registre de l'application, il n'y a donc aucune variable disponible pour lui.</p>")
        
        tplObject = tplModule(passive=True)
        # Liste des variables
        tags_list = []
        for k, v in tplObject.get_available_tags():
            middle = ''
            if k.strip().startswith('if'):
                middle = '{% else %}...'
            end = k.strip().split()[0]
            tag = '{%% %s %%}...%s{%% end%s %%}' % (k, middle, end)
            tags_list.append((tag, v))
        extra_context = {
            'variables': tplObject.get_available_variables(),
            'tags': tags_list,
            'usage': tplObject.help,
        }
        context.update(extra_context)
        html = template.loader.get_template(template_name).render(template.Context(context))
            
        return html
