# -*- coding: utf-8 -*-
"""
Parser avec macros

C'est une "surcouche", elle hérite du parser et initie ses constantes 
internes. Lorsqu'on apelle sa méthode "transform()", elle échappe les 
macros, traite celles qui doivent l'être avant la transformation (@mode=pre) (car elles 
ne produisent pas de XHTML mais de la syntaxe wiki), fait ensuite la transformation de 
texte par le parser wiki, puis traite enfin les macros qui doivent l'être APRÈS la 
transformation (@mode=post) (car elles produisent du XHTML qui serait supprimé par le 
parser).

Les macros ne sont pas récursives, on ne peut ni les imbriquer ni les mélanger entre 
elles.

Par défaut seulement la macro "htmlpass" est disponible, pour ajouter une ou des macros, 
il suffit de les spécifier après l'instanciation du parser, par exemple : ::

    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.add_macro('mamacro', mode='post', func=ma_methode_de_traitement_de_ma_macro)

Si votre macro nécessite des paramètres particulier pour le parser, il suffit de les 
ajouter (avant ou après la définition de la macro mais toujours avant le traitement), 
par exemple : ::

    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.kwargsOpt(mon_dictionnaire_doptions)
    W2Xobject.add_macro('mamacro', mode='post', func=ma_methode_de_traitement_de_ma_macro)

"""
import re

from PyWiki2xhtml.parser import Wiki2XhtmlParser

class Wiki2XhtmlMacros(Wiki2XhtmlParser):
    """
    Dérivation du parser PyWiki2Xhtml pour y ajouter un système de macros.
    """
    def __init__(self):
        # Initialisation de l'__init__ original
        super(Wiki2XhtmlMacros, self).__init__()
        # D'office on active les macros
        self.setOpt('active_macros', True)
        # Liste des macros intégrés
        self.macro_list = {
            'htmlpass': ('post',),
        }
        # Option pour "avaler" le contenu" des macros sans méthodes de rendus
        self.macro_eat_orphelin = False
        # template syntax constants
        self._macro_BLOCK_TAG_START = '{%'
        self._macro_BLOCK_TAG_END = '%}'
        # Template des noms de méthodes des macros
        self._macro_funcname = 'parse_macro_%s'
        # Template des code d'échappement des macros
        self._macro_safe_template = u'{%%{M%sM}%%}'
        # Schéma des macros activés
        self._macro_schema = {}
    
    def add_macro(self, name, mode='post', func=None):
        """
        Ajout d'une macro externe
        
        La méthode de traitement donnée de la macro dans l'argument "func" doit posséder 
        plusieurs arguments :
        
        * source: la source complète à renvoyer sans l'échappement de la macro;
        * opts: transmet les options du parser, cet attribut est seulement 
          passé aux méthodes externes;
        * source: la source complète à renvoyer sans l'échappement de la macro;
        * macro_serial: l'id de la macro;
        * macro_value: le contenu à traiter;
        * macro_args: une liste d'arguments si il y en avait, sinon None.
        
        Une méthode de macro doit s'occuper de remplacer son échappement dans 
        le document et doit le modifier puis le retourner. Le document est 
        donc à sa charge le temps du traitement.
        
        :type name: string
        :param name: Nom clé de la macro
        
        :type mode: string
        :param mode: (optional) 'pre' pour être traité avant la transformation wiki, 
                     'post' pour être traité après. Par défaut le mode est 'post'.
        
        :type func: function
        :param func: (optional) Méthode à passer qui s'occupera du traitement. Si cet 
                     argument est vide ou que la méthode n'existe pas non plus dans la 
                     classe, le contenu sera nettoyé (voir 
                     `Wiki2XhtmlMacros.macro_eat_orphelin`).
        """
        if name not in self.macro_list.keys():
            self.macro_list[name] = (mode, func)
    
    def remove_macro(self, name):
        """
        Supprime une macro du registre si elle existe.
        
        :type name: string
        :param name: Nom clé de la macro
        """
        if name in self.macro_list.keys():
            del self.macro_list[name]
    
    def init_macros(self):
        """
        Schémas des macros avec leur nom clé, et leurs balises à chercher
        
        :rtype: dict
        :return: Dictionnaire de schéma des macros et leur composition (tags et regex 
                 de match).
        """
        macro_schema = {}
        for macroname in self.macro_list.keys():
            # Tag d'ouverture de la macro avec OU sans attributs
            o1 = '%s %s %s' % (re.escape(self._macro_BLOCK_TAG_START), re.escape(macroname), re.escape(self._macro_BLOCK_TAG_END))
            o2 = '%s %s[ ](.*?)[ ]%s' % (re.escape(self._macro_BLOCK_TAG_START), re.escape(macroname), re.escape(self._macro_BLOCK_TAG_END))
            opener = '%s|%s' % (o1, o2)
            # Tag de fermeture de la macro
            closer = re.escape('%s end%s %s' % (self._macro_BLOCK_TAG_START, macroname, self._macro_BLOCK_TAG_END))
            # Schéma de la macro
            macro_schema[macroname] = (
                opener,
                closer,
                # Regex de recherche
                re.compile( '(%s)(.*?)(%s)' % (opener, closer), re.M|re.S ),
            )
        
        return macro_schema

    def safe_macros(self, source):
        """
        Échappe les macros dans le document et les stockent en vue d'un traitement 
        ultérieur
        
        :type source: string
        :param source: Source du document complet
        
        :rtype: string
        :return: Source du document avec toute les macros échappés
        """
        self._macro_escaped_content = {}
        rendered = source
        for k, v in self._macro_schema.items():
            rendered = v[2].sub(self.__replace_with_safe_macro, rendered)
        
        return rendered
    
    def __replace_with_safe_macro(self, matchobj):
        """
        Remplacement d'une macro par sa version d'échappement
        
        :type matchobj: MatchObject
        :param matchobj: Objet de match de la macro détectée.
        
        :rtype: string
        :return: Version "échappée" de la macro.
        """
        # Nom de la macro
        macro_name = matchobj.group(1).strip().split(' ')[1]
        
        # Identifiant de l'entrée de la macro
        serial = len(self._macro_escaped_content)
        
        # Arguments optionnels de certaines macros
        args = matchobj.group(2)
        if args:
            # Argument unique dans une chaine quotée
            if args[0] == args[-1] and args[0] in ['"', "'"]:
                args = args[1:-1]
            else:
                # Arguments par mots clés
                args = args.split(' ')
        
        # Stockage pour un futur traitement
        self._macro_escaped_content[ serial ] = (macro_name, matchobj.group(3), args)
        
        # Renvoi l'échappement temporaire
        return self._macro_safe_template % serial
    
    def _parse_all_macros(self, source, mode):
        """
        Remplace tout les échappement de macros par leur traitement
        
        :type source: string
        :param source: Source du document complet.
        
        :type mode: string
        :param mode: 'pre' ou 'post' pour respectivement chercher les macros à traiter 
                     AVANT et APRES le rendu par le parser wiki.
        
        :rtype: string
        :return: Source du document avec le contenu des macros traitées.
        """
        rendered = source
        
        # Cherche les macros affectés au @mode en cours
        macro_active_mode = [k for k,v in self.macro_list.items() if v[0]==mode]
        
        # Traite tout les contenus des macros du mode en cours
        for macroserial,macrovalue in self._macro_escaped_content.items():
            if macrovalue[0] in macro_active_mode:
                macro_escaped = self._macro_safe_template % macroserial
                # Utilise la méthode forcée dans le schéma si elle existe
                if len(self.macro_list[macrovalue[0]])>1 and self.macro_list[macrovalue[0]][1]:
                    rendered = self.macro_list[macrovalue[0]][1](rendered, self.opt, macro_escaped, macroserial, macrovalue[1], macrovalue[2])
                # Sinon vérifie que la méthode de rendu existe dans la classe
                elif hasattr(self, self._macro_funcname%macrovalue[0]):
                    rendered = getattr(self, self._macro_funcname%macrovalue[0])(rendered, macro_escaped, macroserial, macrovalue[1], macrovalue[2])
                # Méthode de rendu par défaut pour nettoyer les échappements
                else:
                    rendered = self.clean_macros(rendered, macro_escaped, macroserial, macrovalue[1])
        
        return rendered

    def clean_macros(self, source, macro_escaped, macro_serial, macro_value):
        """
        Nettoit une macro annulée (sans méthode de rendu valable)
        
        Utilise l'attribut `Wiki2XhtmlMacros.macro_eat_orphelin` pour savoir si il faut 
        "avaler" le contenu d'une macro sans méthode.
        
        :type source: string
        :param source: Source du document complet.
        
        :type macro_escaped: string
        :param macro_escaped: Version d'échappement de la macro qui sert à sa recherche 
                              pour remplacement.
        
        :type macro_serial: string
        :param macro_serial: Clé unique de la macro.
        
        :type macro_value: string
        :param macro_value: Valeur source de la macro.
        
        :rtype: string
        :return: Source du document avec la macro supprimée.
        """
        if self.macro_eat_orphelin:
            macro_value = ''
        return source.replace(macro_escaped, macro_value)

    def parse_macro_htmlpass(self, source, macro_escaped, macro_serial, macro_value, macro_args=None):
        """
        Méthode de traitement de la macro 'htmlpass', qui permet de passer du 
        html tel quel sans aucune retouche ni contrôle.
        Encercle juste le contenu dans un div.macro_htmlpass. À activer 
        prudemment.
        
        :type source: string
        :param source: Source du document complet.
        
        :type macro_escaped: string
        :param macro_escaped: Version d'échappement de la macro qui sert à sa recherche 
                              pour remplacement.
        
        :type macro_serial: string
        :param macro_serial: Clé unique de la macro.
        
        :type macro_value: string
        :param macro_value: Valeur source de la macro.
        
        :type macro_args: list or None
        :param macro_args: (optional) Liste des arguments inclus dans la macro, None si il 
                           n'y en avait pas.
        
        :rtype: string
        :return: Source du document avec le contenu de la macro remplacée par le rendu de 
                 son traitement.
        """
        return source.replace(macro_escaped, u'<div class="macro_htmlpass">%s</div>' % macro_value)

    def transform(self, source):
        """
        Surcouche de la méthode transform() originale pour y introduire 
        l'échappement et le traitement des macros reconnues.
        
        :type source: string
        :param source: Source du document complet.
        
        :rtype: string
        :return: Texte transformé en XHTML avec les macros traitées (ou nettoyées).
        """
        if self.getOpt('active_macros'):
            # Verifie les macros activés
            self._macro_schema = self.init_macros()
            
            # Echappement des macros
            rendered = self.safe_macros( source )
            
            # Traitement des macros AVANT transformation
            rendered = self._parse_all_macros(rendered, 'pre')
            
            # Traitement de transformation du document
            rendered = super(Wiki2XhtmlMacros, self).transform( rendered )

            # Traitement des macros APRÈS transformation
            rendered = self._parse_all_macros(rendered, 'post')
            
            return rendered
        
        return super(Wiki2XhtmlMacros, self).transform( source )
