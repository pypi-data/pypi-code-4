#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper avec macros

TODO: Recherche et importation dynamique des macros activées et non pas en dur comme 
actuellement.
"""
from parser import Wiki2XhtmlMacros

from macro_attach import parse_macro_attach
from macro_pygments import parse_macro_pygments
from macro_mediaplayer import parse_macro_mediaplayer
from PyWiki2xhtml.macros.macro_gmap import parse_macro_googlemap

from PyWiki2xhtml.helper import Wiki2XhtmlHelper
from PyWiki2xhtml.testcases.default import *
from PyWiki2xhtml.testcases.macros import *

class Wiki2XhtmlMacrosHelper(Wiki2XhtmlHelper):
    """
    Dérivation du helper de base pour introduire l'aide sur les macros
    """
    def __init__(self, opts={}, labels={ 'inline':INLINE_SYNTAX_LABELS.copy(), 'links':LINKS_SYNTAX_LABELS.copy(), 'blocks':SIMPLE_BLOCK_TEST_CASE, 'titles':TITLE_TEST_CASE, 'bulletlists':BULLETLIST_TEST_CASE, 'macros':ACTIVE_MACROS}):
        """
        :type opts: dict
        :param opts: (optional) Dictionnaire des options à passer au parser pour écraser 
                     celles par défaut. Vide par défaut.
        
        :type labels: dict
        :param labels: Dictionnaire des chaines de démonstration à intégrer à l'aide, 
                       par défaut contient les éléments suivants :
                       * inline: labels et exemples de démo de la syntaxe "en ligne";
                       * blocs: exemple de démo de la syntaxe des blocs de contenus;
                       * titles: exemple de démo de la syntaxe des titres et de leur sommaire;
                       * bulletlists: exemple de démo de la syntaxe des listes;
                       * links: labels et exemples de démo de la syntaxe des liens;
                       * macros: labels et exemples de démo de la syntaxe des macros activées.
        """
        super(Wiki2XhtmlMacrosHelper, self).__init__(opts=opts, labels=labels)
    
    def get_parser(self, opts):
        """
        Récupère et initialise le parser
        
        :type opts: dict
        :param opts: Dictionnaire des options à passer au parser pour écraser 
                     celles par défaut.
        """
        self.W2Xobject = Wiki2XhtmlMacros()
        # Force l'activation du sommaires des titres pour leur aide
        self.W2Xobject.setOpt('active_menu_title', True)
        
        # Activation des macros fournies
        self.W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)
        self.W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
        self.W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
        self.W2Xobject.add_macro('googlemap', mode='post', func=parse_macro_googlemap)
        
        # Possibilité de changer les options
        self.W2Xobject.kwargsOpt(opts)
    
    def render(self):
        """
        Renvoi un dictionnaire des différentes sections de l'aide
        
        :rtype: dict
        :return: Dictionnaire des sections
        """
        render_dict = super(Wiki2XhtmlMacrosHelper, self).render()
        render_dict.update({
            'macros': self.get_macros_help(),
        })
        return render_dict

    def get_macros_help(self):
        """
        Renvoi une série de différentes démonstrations des macros activées
        
        :rtype: dict
        :return: Dictionnaire de toute les macros activées.
        """
        resp = {}
        for key,val in self.labels['macros'].items():
            resp[key] = [ val[0], val[1], self.W2Xobject.transform(val[1]) ]
    
        return resp
        
    def display(self):
        """
        Sortie d'affichage pour le terminal
        """
        super(Wiki2XhtmlMacrosHelper, self).display()
        
        print self.title(" MACROS ", "~")
        for key,val in self.get_macros_help().items():
            # Vérifie que la macro est activée
            if key in self.W2Xobject.macro_list.keys():
                print self.title("%s (%s)"%(val[0], key), "-")
                print val[1]
                print val[2]

# Pour appeler ce script et tester la démonstration
if __name__ == "__main__":
    Wiki2XhtmlMacrosHelper().display()
