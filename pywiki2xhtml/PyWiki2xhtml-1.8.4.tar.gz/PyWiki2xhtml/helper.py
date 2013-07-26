#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper principal
"""
from parser import Wiki2XhtmlParser
from testcases.default import *

class Wiki2XhtmlHelper(object):
    """
    Le helper permet de renvoyer une démonstration dynamique selon la syntaxe 
    employée.
    Si besoin, il est possible de lui passer des options du parser à modifier, 
    ainsi que les différentes chaînes de démonstration utilisée.
    """
    def __init__(self, opts={}, labels={ 'inline':INLINE_SYNTAX_LABELS.copy(), 'links':LINKS_SYNTAX_LABELS.copy(), 'blocks':SIMPLE_BLOCK_TEST_CASE, 'titles':TITLE_TEST_CASE, 'bulletlists':BULLETLIST_TEST_CASE}):
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
                       * links: labels et exemples de démo de la syntaxe des liens.
        """
        self.labels = labels
        self.get_parser(opts)

    def get_parser(self, opts):
        """
        Récupère et initialise le parser
        
        :type opts: dict
        :param opts: Dictionnaire des options à passer au parser pour écraser 
                     celles par défaut.
        """
        self.W2Xobject = Wiki2XhtmlParser()
        # Force l'activation du sommaires des titres pour leur aide
        self.W2Xobject.setOpt('active_menu_title', True)
        # Possibilité de changer les options
        self.W2Xobject.kwargsOpt(opts)

    def render(self):
        """
        Renvoi un dictionnaire des différentes sections de l'aide
        
        :rtype: dict
        :return: Dictionnaire des sections
        """
        return {
            'inline': self.get_inline_help(),
            'blocks': self.get_blocks_help(),
            'titles': self.get_titles_help(),
            'bulletlists': self.get_bulletlists_help(),
            'links': self.get_links_help(),
        }

    def get_inline_help(self):
        """
        Rajoute la transformation et les balises aux chaines de démonstration 
        des éléments "en ligne"
        
        :rtype: dict
        :return: Dictionnaire de toute les parties de la section
        """
        resp = {}
        for key,val in self.labels['inline'].items():
            if key in self.W2Xobject.inline_syntax.keys():
                render = val[1] % (self.W2Xobject.inline_syntax[key][0], self.W2Xobject.inline_syntax[key][1])
                resp[key] = ( val[0], render, self.W2Xobject.transform(render) )
        
        return resp
        
    def get_blocks_help(self):
        """
        Rajoute la transformation et les balises aux chaines de démonstration 
        des blocs de contenu
        
        :rtype: dict
        :return: Dictionnaire de la source des démonstrations et sa version xhtml.
        """
        return {
            'source': self.labels['blocks'],
            'xhtml': self.W2Xobject.transform( self.labels['blocks'] ),
        }
        
    def get_titles_help(self):
        """
        Rajoute la transformation et les balises aux chaines de démonstration 
        des titres et leur sommaire.
        
        :rtype: dict
        :return: Dictionnaire contenant la source (source), le xhtml (xhtml) et le 
                 sommaire des titres (summary) si il y'en a un sinon il sera vide 
                 (None).
        """
        render = self.W2Xobject.render( self.labels['titles'] )
        return render
        
    def get_bulletlists_help(self):
        """
        Rajoute la transformation et les balises aux chaines de démonstration 
        des listes à puces ou numérotés
        
        :rtype: dict
        :return: Dictionnaire de la source des démonstrations et sa version xhtml.
        """
        return {
            'source': self.labels['bulletlists'],
            'xhtml': self.W2Xobject.transform( self.labels['bulletlists'] ),
        }
        
    def get_links_help(self):
        """
        Renvoi une série de différentes démonstrations pour les liens
        
        :rtype: dict
        :return: Dictionnaire de tout les liens spéciaux supportés.
        """
        resp = {}
        for key,val in self.labels['links'].items():
            render = val[1] % (self.W2Xobject.inline_syntax['a'][0], self.W2Xobject.inline_syntax['a'][1])
            resp[key] = [ val[0], render, self.W2Xobject.transform(render) ]
            if key == "special":
                url = [item[1:item[1:].find('://')+1]+u'://MOTIF' for item in self.W2Xobject.getOpt('special_urls')]
                resp[key].append( url )
    
        return resp
        
    def title(self, title, symbol, cols=80):
        """
        Renvoi un titre justifié au centre par des caractères
        
        :type title: string
        :param title: Contenu texte du titre.
        
        :type symbol: string
        :param symbol: Caractère à employer pour justifier le texte.
        
        :type cols: int
        :param cols: (optional) Largeur complète (en nombre de caractères) alloué au 
                     titre. Sert au calcul de justification. Par défaut 80.
        
        :rtype: string
        :return: Texte justificie au centre de la largeur indiquée
        """
        return symbol*((cols-len(title))/2) + title + symbol*((cols-len(title))/2)
        
    def display(self):
        """
        Sortie d'affichage pour le terminal
        """
        s = ''
        
        print self.title(" INLINE ", "~")
        for key,val in self.get_inline_help().items():
            print self.title("%s (%s)"%(val[0], key), "-")
            print val[1]
            print val[2]
            print
        
        print self.title(" BLOCK ", "~")
        tpl = self.get_blocks_help()
        print tpl['source']
        print self.title("-", "-")
        print tpl['xhtml']
        print
        
        print self.title(" TITLE ", "~")
        tpl = self.get_titles_help()
        print tpl['source']
        print self.title("-", "-")
        print tpl['xhtml']
        print self.title("-", "-")
        print tpl['summary']
        print
        
        print self.title(" LISTS ", "~")
        tpl = self.get_bulletlists_help()
        print tpl['source']
        print self.title("-", "-")
        print tpl['xhtml']
        print
        
        print self.title(" LINKS ", "~")
        for key,val in self.get_links_help().items():
            print self.title("%s (%s)"%(val[0], key), "-")
            print val[1]
            print val[2]
            if key == "special":
                print self.title("Liste des urls spéciales possibles", "-")
                print " , ".join( val[3] )
            print

# Pour appeler ce script et tester la démonstration
if __name__ == "__main__":
    Wiki2XhtmlHelper().display()
