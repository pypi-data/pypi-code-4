#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exporteur de documents

``DocExport`` est un module permettant d'exporter du contenu. Le site est un 
ensemble de documents générés d'après leur contenu.

Ce module est une BASE pour les classes permettant de générer le 
site sous un format.

Les 'vrais' plugins d'export sont des classes d'héritages de DocExport et 
s'occupent de récupérer et générer les documents à produire.
"""
__title__ = "Documents Exporter"
__version__ = "0.5.1"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2008-2009 Sveetch.biz"
__license__ = "GPLv2"

import os, re, sys

# TODO: son utilisation n'est pas totalement implémenté
STEP_DIRS = os.path.sep

######################################################################
#                                                                    #
#               Classe de base pour l'exportation                    #
#                                                                    #
######################################################################
class DocExport(object):
    """
    Class de base pour faire un export. Elle ne se charge que de créer tout 
    les fichiers avec leur répertoires.
    """
    def __init__( self, targetDir, config={}, debug=False, verbose=True, loggingObject=False ):
        """
        Constructeur simple qui initialise 'self.__init_documents__()', LA 
        méthode à surclasser par les Classes qui hérite de MainExporter 
        pour pouvoir récupérer les documents à générer.
        
        C'est uniquement l'appel de la méthode 'self.export()' qui déclenchera 
        la génération des documents contenus dans l'attribut 'self.pages' et 
        récoltés par 'self.__init_documents__()'.
        
        @targetDir : le chemin vers le répertoire qui va recevoir le contenu 
        de l'exportation.
        
        @config : Dictionnaire python de la configuration de l'export, son 
        contenu varie selon le type d'export, seul les classes qui héritent de 
        MainExporter en ont l'usage, lui même ne l'utilise pas.
        
        @debug : booléen pour indiquer si on doit activer le mode de 
        débuggage ou non. S'il est activé, le script se contentera de procéder 
        sans rien créer.
        
        @verbose : booléen pour indiquer si on doit activer le mode verbeux ou 
        non. S'il est activé, des messages d'information seront affichés sur 
        la sortie standard.
        
        @loggingObject : objet déja initialisé du module python 'logging' pour 
        créer un fichier de log des informations. 
        """
        self.targetDir = targetDir
        self.config = config
        self.debug = debug
        self.verbose = verbose
        self.loggingObject = loggingObject
        self.pages = []
        self.urls = {}
        self.doc_level = 0
        
        # Regex de recherche de liens html et sa version compilée
        self.regex_link_match_pattern = r'href="([^>"]+)"'
        self.regex_link_match_object = re.compile(self.regex_link_match_pattern)
        # Regex de recherche de sources de médias (image, css, etc..) et sa 
        # version compilée
        self.regex_image_match_pattern = r'src="([^>"]+)"'
        self.regex_image_match_object = re.compile(self.regex_image_match_pattern)
        
        # Récupération des documents
        self.__init_documents__(**config)
    
    def __init_documents__( self ):
        """
        Méthode de récupération des documents à exporter.
        C'est la méthode à surclasser dans la class qui hérite.
        """
        self.output_info("**  "+__title__+" "+__version__+"  **")
        
        # Urls de tests
        self.get_site_urls()
        # Valeures de tests
        self.pages = [
            {
                'title': "Index",
                'filename': "index.html",
                'path': "",
                'content': self.normalize_urls( TEST_INDEX_CONTENT, level=0, withmedias=True ),
            },
            {
                'title': "Foo",
                'filename': "foo.html",
                'path': "bar/",
                'content': self.normalize_urls( TEST_PAGE1_CONTENT, level=1, withmedias=True ),
            },
            {
                'title': "Plonk",
                'filename': "plonk.html",
                'path': "bar/foo/",
                'content': self.normalize_urls( TEST_PAGE2_CONTENT, level=2, withmedias=True ),
            },
        ]
    
    def get_site_urls( self ):
        """
        Collecte toute les urls internes au site et qui sont à remplacer pour 
        pouvoir naviguer dans les documents générés.
        
        Les urls contenu dans 'self.urls' sont sous la forme (REMPLACEMENT, 
        LEVEL) où REMPLACEMENT est la chaine qui remplacera le motif, 
        LEVEL indique le niveau de profondeur du document visé par le lien 
        par rapport à la racine du sitemap.
        """
        # Valeures de tests
        self.urls = {
            '/' : ("index.html", 0),
            '/bar/' : ("index.html", 1),
            '/bar/poo/' : ("bar/poo.html", 1),
            '/bar/foo/' : ("bar/foo.html", 1),
            '/bar/foo/plonk/' : ("bar/foo/plonk.html", 2),
            '/bar/foo/plonk/meuh/' : ("bar/foo/plonk/meuh.html", 3),
        }
    
    def output_info(self, msg, methods=('verbose', 'logging')):
        """
        Gestion des informations à renvoyer à la sortie standard et l'objet 
        de logging.
        """
        if self.verbose and 'verbose' in methods:
            print msg
        if self.loggingObject and 'logging' in methods:
            self.loggingObject.info(msg)

    def normalize_urls(self, content, level=False, withmedias=False):
        """
        Méthode permettant de chercher et remplacer toute les urls d'un 
        document qui correspondent à des entrées produites par l'export.
        
        @level : le niveau relatif du répertoire de la page par rapport à la 
        racine ou se trouve l'index.
        
        @withmedias : indique si on doit utiliser la regex matchant les attributs 
        src="..." pour y remplacer des urls référencés dans self.urls
        """
        #print "_"*60
        self.doc_level = level
        content = self.regex_link_match_object.sub(self.replace_doc_link, content)
        if withmedias:
            content = self.regex_image_match_object.sub(self.replace_doc_medias, content)
        self.doc_level = False
        return content
        
    def replace_doc_link(self, matchobj, htmlattr='href="%s"'):
        """
        Fonction de remplacement pour chaque lien trouvé. On cherche si l'url 
        trouvé correspond à une entrée de 'self.urls' si oui on la remplace 
        par la valeure de la clé correspondante dans 'self.urls'.
        
        TODO: La recherche du niveau du document dans l'arborescence ne 
        vérifie pas que le document passe par le meme chemin que la cible 
        du lien. En gros cette méthode ne supporte qu'un seul et unique 
        sous-répertoire par répertoire.
        
        Type d'arborescence reconnue :
        Bar/
        |__Foo/
           |__Plonk/
        
        Type d'arborescence non reconnue :
        Bar/
        |__Foo/
           |__Plonk/
        |__Prout/
           |__Burp/
        
        """
        if matchobj.group(1) in self.urls.keys():
            url_path = self.urls[matchobj.group(1)][0]
            url_level = self.urls[matchobj.group(1)][1]
            
            # Chemin au meme niveau que le document courant ou chemin à ne 
            # pas modifier
            if not url_level:
                url_path = url_path
            # Chemin au meme niveau que le document courant ou chemin à ne 
            # pas modifier
            elif self.doc_level == url_level or not url_level:
                url_path = os.path.split(url_path)[-1]
            # Chemin sous le document courant
            elif self.doc_level > url_level:
                prefix = '../'*(self.doc_level-url_level)
                url_path = prefix+os.path.split(url_path)[-1]
            # Chemin au dessus du niveau du document courant
            elif self.doc_level < url_level:
                url_path = "/".join( url_path.split("/")[self.doc_level:] )
                
            return htmlattr % url_path
        
        return matchobj.group(0)
    
    def replace_doc_medias(self, matchobj):
        """
        Duplicata de replace_doc_link pour utiliser son attribut "htmlattr" 
        dans la méthode re.sub()
        """
        return self.replace_doc_link(matchobj, htmlattr='src="%s"')
        
    def export( self ):
        """
        Exportation de tout les objets en documents
        """
        for page in self.pages:
            self.publish(page)
    
    def publish(self, pageObject):
        """
        Création du fichier d'un document à son emplacement prévu
        """
        self.output_info( "_"*80, methods=('verbose',) )
        self.output_info(" - Document : '%s'" % pageObject['title'])
        # Chemin absolu du répertoire qui va contenir le document
        directory = os.path.join( self.targetDir, pageObject.get('path', "") )
        # Chemin absolu complet vers le fichier à créer
        fn = os.path.join( directory, pageObject['filename'] )
                
        # Si le répertoire cible n'existe pas, on tente de le créer
        if not os.path.exists(directory):
            try:
                if not self.debug:
                    os.makedirs(directory)
                else:
                    pass
            except:
                raise " ! Unable to create directory : '%s'" % directory
        
        self.doc_publisher(directory, fn, pageObject)
    
    def doc_publisher(self, directory, fn, pageObject):
        """
        Méthode de publication du fichier du document
        """
        # On tente d'écrire le fichier
        try:
            self.output_info( "   Chemin : '%s'" % directory, ('verbose',) )
            self.output_info( "   Fichier : '%s'" % fn, ('verbose',) )
            if not self.debug:
                f = open(fn, 'w')
                f.write( pageObject['content'] )
                f.close()
        except:
            raise " ! Unable to create file : %s" % fn
                
class NewDocExport(DocExport):
    """
    Nouvelle version de DocExport avec un option de "formatage" du contenu 
    qui s'occupera désormais du "normalize_url" et plus si affinités
    """
    def __init_documents__( self ):
        """
        Méthode de récupération des documents à exporter.
        C'est la méthode à surclasser dans la class qui hérite.
        """
        self.output_info("**  "+__title__+" "+__version__+"  **")
        
        # Urls de tests
        self.get_site_urls()
        # Valeures de tests
        self.pages = [
            {
                'title': "Index",
                'filename': "index.html",
                'path': "",
                'content': TEST_INDEX_CONTENT,
                'formatter': True,
            },
            {
                'title': "Foo",
                'filename': "foo.html",
                'path': "bar/",
                'content': TEST_PAGE1_CONTENT,
                'formatter': 'common',
            },
            {
                'title': "Plonk",
                'filename': "plonk.html",
                'path': "bar/foo/",
                'content': TEST_PAGE2_CONTENT,
                'formatter': True,
            },
        ]
    
    def get_site_urls( self ):
        """
        Collecte toute les urls internes au site et qui sont à remplacer pour 
        pouvoir naviguer dans les documents générés.
        
        Les urls contenu dans 'self.urls' sont sous la forme (REMPLACEMENT, 
        LEVEL) où REMPLACEMENT est la chaine qui remplacera le motif, 
        LEVEL indique le niveau de profondeur du document visé par le lien 
        par rapport à la racine du sitemap.
        """
        # Valeures de tests
        self.urls = {
            '/' : ("index.html", 0),
            '/bar/' : ("bar/index.html", 1),
            '/bar/poo/' : ("bar/poo.html", 1),
            '/bar/foo/' : ("bar/foo.html", 1),
            '/bar/foo/plonk/' : ("bar/foo/plonk.html", 2),
            '/bar/foo/plonk/meuh/' : ("bar/foo/plonk/meuh.html", 3),
            '/bar/foo/gouzi/' : ("bar/foo/gouzi.html", 2),
            # Exemple de médias
            '/medias/' : ("medias/", 1),
            '/medias/crossdomain.xml' : ("medias/crossdomain.xml", 1),
            '/medias/css/common.css' : ("medias/css/common.css", 2),
            '/medias/js/layout.js' : ("medias/js/layout.js", 2),
        }
    
    def doc_publisher(self, directory, fn, pageObject):
        """
        Méthode de publication du fichier du document
        """
        self.output_info( "   URL Path : '%s'" % os.path.join(pageObject['path'], pageObject['filename']), ('verbose',) )
        self.output_info( "   FileSystem Path : '%s'" % directory, ('verbose',) )
        self.output_info( "   Filename Path : '%s'" % fn, ('verbose',) )
        
        # Formatage optionnel du contenu
        if pageObject['formatter']:
            # Utilisation du formateur par défaut
            if pageObject['formatter'] == True:
                pageObject = self.formatter_common( pageObject )
            # Utilisation d'un formateur spécifique
            else:
                if getattr(self, 'formatter_%s'%pageObject['formatter'], None):
                    pageObject = getattr(self, 'formatter_%s'%pageObject['formatter'])( pageObject )
        
        # On tente d'écrire le fichier
        try:
            if not self.debug:
                f = open(fn, 'w')
                f.write( pageObject['content'] )
                f.close()
        except:
            raise " ! Unable to create file : %s" % fn
        
    def formatter_common(self, pageObject):
        """
        Méthode de publication du fichier du document
        """
        # Archive la source original
        pageObject['source'] = pageObject['content']
        
        # Niveau de destination du document dans l'arborescence exportée
        level = len(pageObject['path'].split(STEP_DIRS))-1
        #self.output_info( "   URL Level : '%s'" % level, ('verbose',) )
        
        # Formate le contenu pour les urls
        pageObject['content'] = self.normalize_urls( pageObject['content'], path=os.path.join(pageObject['path'], pageObject['filename']), level=level, withmedias=True )
        
        return pageObject
    
    def normalize_urls(self, content, level, path, withmedias=False):
        """
        Méthode permettant de chercher et remplacer toute les urls d'un 
        document qui correspondent à des entrées produites par l'export.
        
        @level : le niveau relatif du répertoire de la page par rapport à la 
        racine ou se trouve l'index.
        
        @path : indique le chemin prévu pour le document.
        
        @withmedias : indique si on doit utiliser la regex matchant les attributs 
        src="..." pour y remplacer des urls référencés dans self.urls
        """
        self._doc_level = level
        self._doc_path = path
        # Tout les liens 'standards'
        content = self.regex_link_match_object.sub(self.replace_doc_link, content)
        # Les liens sur les médias (balises images, css, scripts, etc..)
        if withmedias:
            content = self.regex_image_match_object.sub(self.replace_doc_medias, content)
        self._doc_level = False
        return content
        
    def replace_doc_link(self, matchobj, htmlattr='href="%s"'):
        """
        Fonction de remplacement pour chaque lien trouvé. On cherche si l'url 
        trouvé correspond à une entrée de 'self.urls' si oui on la remplace 
        par la valeure de la clé correspondante dans 'self.urls'.
        
        TODO: Ce système ne doit probablement pas fonctionner avec des urls 
        relatives pour les sources.
        """
        if matchobj.group(1) in self.urls.keys():
            url_path = self.urls[matchobj.group(1)][0]
            url_level = self.urls[matchobj.group(1)][1]
            base_path = self._doc_path.split(STEP_DIRS)[0]
            
            # Chemin avec un niveau inférieur à l'emplacement du document
            if self._doc_level > url_level:
                # Chemin sur une racine différente
                if len(os.path.dirname(url_path)) > 0 and base_path != url_path.split(STEP_DIRS)[0]:
                    prefix = '../'*self._doc_level
                    url_path = prefix+url_path
                else:
                    prefix = '../'*(self._doc_level-url_level)
                    url_path = prefix+os.path.split(url_path)[-1]
            # Chemin au meme niveau que le document courant
            elif self._doc_level == url_level or not url_level:
                # Chemin sur une racine différente
                if os.path.dirname(self._doc_path) != os.path.dirname(url_path):
                    prefix = '../'*self._doc_level
                    url_path = prefix+url_path
                else:
                    url_path = os.path.split( url_path )[-1]
            # Chemin avec un niveau supérieur à l'emplacement du document
            elif self._doc_level < url_level:
                # Chemin sur une racine différente
                if len(os.path.dirname(self._doc_path)) > 0 and base_path != url_path.split(STEP_DIRS)[0]:
                    prefix = '../'*self._doc_level
                    url_path = prefix+url_path
                else:
                    url_path = STEP_DIRS.join( url_path.split(STEP_DIRS)[self._doc_level:] )
            
            return htmlattr % url_path
        
        return matchobj.group(0)
    
    def replace_doc_medias(self, matchobj):
        """
        Duplicata de replace_doc_link pour utiliser son attribut "htmlattr" 
        dans la méthode re.sub()
        """
        return self.replace_doc_link(matchobj, htmlattr='src="%s"')
    
# Exemple de contenus pour les tests de MainExporter
TEST_INDEX_CONTENT = """<html><head><title>Doc Export</title>
    <link rel="Stylesheet" title="Normal" media="screen" type="text/css" href="/medias/css/common.css"/>
    <script type="text/javascript" src="/medias/js/layout.js"></script>
</head>
<body>
    <h1><a href="/bar/">Doc Export</a></h1>
    <div>
        <h2><a href="/">Test index</a></h2>
        <ul>
            <li><a href="/bar/foo/" class="mussel" id="li_1">Foo</a></li>
            <li><a href="/bar/" class="mussel">Bar</a></li>
            <li><a href="/" id="li_3">Index</a></li>
            <li><a href="/bar/poo/">Poo</a></li>
            <li><a href="/bar/foo/plonk/" class="mussel" id="li_6">PLONK</a></li>
            <li><a href="/bar/foo/plonk/meuh/" class="mussel" id="li_7">MEUH</a></li>
        </ul>
    </div>
</body>
</html>
"""

TEST_PAGE1_CONTENT = """<html><head><title>Doc Export</title>
    <link rel="Stylesheet" title="Normal" media="screen" type="text/css" href="/medias/css/common.css"/>
    <script type="text/javascript" src="/medias/js/layout.js"></script>
</head>
<body>
    <h1><a href="/bar/">Doc Export</a></h1>
    <div>
        <h2><a href="/">Foo</a></h2>
        <ul>
            <li><a href="/bar/foo/" class="mussel" id="li_1">Foo</a></li>
            <li><a href="/bar/" class="mussel">Bar</a></li>
            <li><a href="/" id="li_3">Index</a></li>
            <li><a href="/bar/poo/">Poo</a></li>
            <li><a href="/bar/foo/plonk/" class="mussel" id="li_6">PLONK</a></li>
            <li><a href="/bar/foo/plonk/meuh/" class="mussel" id="li_7">MEUH</a></li>
        </ul>
    </div>
</body>
</html>
"""

TEST_PAGE2_CONTENT = """<html><head><title>Doc Export</title>
    <link rel="Stylesheet" title="Normal" media="screen" type="text/css" href="/medias/css/common.css"/>
    <script type="text/javascript" src="/medias/js/layout.js"></script>
</head>
<body>
    <h1><a href="/bar/">Doc Export</a></h1>
    <div>
        <h2><a href="/">Plonk</a></h2>
        <ul>
            <li><a href="/bar/foo/" class="mussel" id="li_1">Foo</a></li>
            <li><a href="/bar/" class="mussel">Bar</a></li>
            <li><a href="/" id="li_3">Index</a></li>
            <li><a href="/bar/poo/">Poo</a></li>
            <li><a href="/bar/foo/plonk/" class="mussel" id="li_6">PLONK</a></li>
            <li><a href="/bar/foo/plonk/meuh/" class="mussel" id="li_7">MEUH</a></li>
        </ul>
    </div>
</body>
</html>
"""

#
if __name__ == "__main__":
    #>
    #> Test de la classe de base
    #>
    #o = DocExport( targetDir=os.path.join( os.getcwd(), "test" ), debug=True, verbose=True )
    o = NewDocExport( targetDir=os.path.join( os.getcwd(), "test" ), debug=False, verbose=True )
    o.export()
