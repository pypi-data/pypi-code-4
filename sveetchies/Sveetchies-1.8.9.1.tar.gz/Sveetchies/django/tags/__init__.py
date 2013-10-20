# -*- coding: utf-8 -*-
from django.conf import settings
from django import template
from django.utils.safestring import mark_safe

from Sveetchies.django.utils import get_string_or_variable

register = template.Library()

@register.tag(name="common_tabs_menu")
def do_common_tabs_menu(parser, token):
    """
    Tag de génération d'un menu d'onglets à partir d'un schéma
    
    Le schéma des onglets prends la forme suivante : ::
    
        TABS = (
            '/url/de/base/pour/tout/onglet/',
            (
                ('key1', 'Onglet 1'),
                ('key2', 'Onglet 2'),
            )
        )
    
    Le dernier élément de la liste est optionnel et contient un template 
    du HTML de la ligne de l'onglet.
    L'id de l'onglet est ajouté à chaque fois à la fin de son url de base 
    dans le template.
    
    Appel avec le schéma des onglets et l'onglet actif courant : ::
    
        {% common_tabs_menu schema active_tab %}
    
    Appel avec le schéma des onglets et l'onglet actif courant, plus un 
    template HTML customisé : ::
    
        {% common_tabs_menu schema active_tab custom_template_tab %}
    
    schema
        une liste python contenant le schéma
    active_tab
        une chaine de texte contenant l'id dans le schéma de 
        l'onglet actif. Cet argument peut etre passé dans le template directement
        commune une chaîne ou comme une variable présente dans le context.
    custom_template_tab
        une chaine de texte contenant le template HTML de 
        la ligne de l'onglet. Peut contenir jusqu'à 4 motifs de substitution 
        qui désignent dans l'ordre le lien, la class css "active", le titre.
        Cet argument peut etre passé dans le template directement commune une 
        chaîne ou comme une variable présente dans le context.
    
    Exemple : ::
    
        <div class="tab %(active_class)s"><a href="%(link_url)s">%(link_title)s</a></div>
    
    Ou bien : ::
    
        <li%(html_active_class)s><a href="%(link_url)s">%(link_title)s</a></li>
    """
    # Tente avec la totale
    try:
        tag_name, schema, active_tab, custom_template_tab = token.contents.split(None, 3)
    except ValueError:
        # Échec, on essaye sans le template customisé
        try:
            tag_name, schema, active_tab = token.contents.split(None, 2)
        except ValueError:
            raise template.TemplateSyntaxError, "You need to specify at less 'schema' and 'active_tab' value."
        else:
            return common_tabs_menu_render(schema, active_tab)
    else:
        return common_tabs_menu_render(schema, active_tab, custom_template_tab)

class common_tabs_menu_render(template.Node):
    """
    Génération du rendu html du tag
    """
    def __init__(self, schema, active_tab, custom_template_tab=None):
        self.schema = schema
        self.active_tab = active_tab
        self.template_tab = '<a href="%(link_url)s" class="tab%(active_class)s">%(link_title)s</a>'
        self.custom_template_tab = custom_template_tab
    
    def render(self, context):
        """
        Générateur du menu de tabulation à partir du schéma compressé 
        dans une liste/tuple.
        """
        self.schema = get_string_or_variable(self.schema, context)
        self.active_tab = get_string_or_variable(self.active_tab, context)
        self.custom_template_tab = get_string_or_variable(self.custom_template_tab, context)
        # Le template custom donné dans le tag peut prendre le dessus sur celui 
        # par défaut du tag
        if self.custom_template_tab:
            self.template_tab = self.custom_template_tab
        menu = []
        # On fait une liste simple en fonction du nombre de pages
        for url, key, title in self.schema[1]:
            # Classe css qui désigne l'onglet en cours ("actif")
            active = ''
            html_active = ''
            if self.active_tab != None and key == self.active_tab:
                active = ' active'
                html_active = ' class="active"'
            # Forme l'url
            if self.schema[0]:
                link = "%s%s" % (self.schema[0], url)
            else:
                link = "%s" % url
            # Substitutions dans le template
            row = self.template_tab % {
                'id':key,
                'link_url':link,
                'active_class':active,
                'html_active_class':html_active,
                'link_title':title
            }
            menu.append( row )
        
        return mark_safe( "".join(menu) )
