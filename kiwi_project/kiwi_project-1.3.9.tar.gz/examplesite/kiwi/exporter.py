#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This script is part of Kiwi.
# It requires the Sveetchies module
# See : http://svn.logicielslibres.info/bordel/sveetch/Sveetchies/
#
__title__ = "Kiwi Exporter"
__version__ = "1.0.5"
__author__ = "THENON David"
__copyright__ = "Copyright (c) 2008-2009 Sveetch.biz"
__license__ = "GPL"

import os
from Sveetchies.DocExport import DocExport
from Sveetchies.cli.ImportDjangoProject import ImportDjangoProject

class WikiXhtmlExporter(DocExport):
    """
    Class de base pour exporter le Wiki. Tel quel, elle produit du xhtml, voire 
    du xml valide en modifiant ses templates.
    """
    def __init_documents__( self, project_directory, settings_file, sitemap_metas=("index", "Sommaire"), parent_uri=None):
        """
        Méthode de récupération des documents à exporter.
        Pour générer les documents, on utilise directement les vues du site 
        en ne récupérant que le contenu de la réponse Http.
        
        @project_directory = répertoire du projet django à importer.
        
        @settings_file = fichier de settings à utiliser avec le projet.
        
        @sitemap_metas = un tuple contenant en première position le nom de 
        fichier (sans extension) pour le plan du site généré et son titre 
        en seconde position.
        
        @parent_uri = URI d'une page qui sera le point de départ du 
        site exporté, ces sous-pages seront aussi suivies.
        
        Avec tout ça vous pouvez générer un wiki consultable hors connexion, 
        un mirroir statique, une documentation, etc.
        """
        self.project_directory = project_directory
        self.settings_file = settings_file
        self.sitemap_metas = sitemap_metas
        self.parent_uri = parent_uri
        self.parent_id = None
        
        title_message = "**  %s (xhtml) v%s, started Kiwi on '%s'  **" % (__title__, __version__, self.project_directory)
        self.output_info( title_message )
            
        # Importe les settings du projet        
        self.settingsMod = ImportDjangoProject(project_directory, settings_file)
        if not self.settingsMod:
            raise "Unable to import Kiwi at directory '%s'" % project_directory
        # Attributs qui dépendent des settings
        self.module_urlpath_prefix = './'
        self.filename_format = u'%s.html'
        
        # Map des urls internes au site
        self.get_site_urls()
        
        # Collecte les documents à génèrer
        self.get_documents()
    
    def get_site_urls( self ):
        """
        Collecte toute les urls internes au site et qui sont à remplacer pour 
        pouvoir naviguer dans les documents générés.
        
        Les urls contenu dans 'self.urls' sont sous la forme (REMPLACEMENT, 
        LEVEL) où REMPLACEMENT est la chaine qui remplacera le motif, 
        LEVEL indique le niveau de profondeur du document visé par le lien 
        par rapport à la racine du sitemap.
        """
        from django.contrib.sites.models import Site
        from kiwi.models import Wikipage
        
        # Base de départ avec l'index
        root_fullurl = 'http://%s' % Site.objects.get_current().domain
        self.urls = {
            '/' : ("index.html", 0),
            root_fullurl: ("index.html", 0),
        }
        # Collecte de toute les urls de pages existantes et actives
        for item in Wikipage.objects.filter(active=True):
            url = self.filename_format%item.uri
            self.urls[ item.get_absolute_url() ] = ( url.encode('utf-8'), 1)
    
    def get_documents(self):
        """
        Groupement des méthodes de récupération des pages publiées et leur 
        contenu.
        """
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        from kiwi.models import Wikipage
        from kiwi.views.wikipage import sitemap
        self.pages = []
        
        # Création d'un faux request d'anonyme pour accéder aux view
        self.request = HttpRequest()
        self.request.user = AnonymousUser()
        
        # Limitation de l'arborescence à une page et ses enfants
        if self.parent_uri:
            try:
                parentObject = Wikipage.objects.get( uri=self.parent_uri )
            except Wikipage.DoesNotExist:
                raise " Wikipage with URI '%s' does not exist" % self.parent_uri
            else:
                self.parent_id = parentObject.id
        
        # Lookup de toute les pages du premier niveau
        if not self.parent_uri:
            queryset = Wikipage.objects.filter( parent__isnull=True, in_sitemap=True, active=True )
        # Lookup d'une page ciblée
        else:
            queryset = [parentObject]
            
        # Génération du plan du site avec la vue sitemap()
        self.pages.append({
            'title': self.sitemap_metas[1],
            'filename': self.filename_format % self.sitemap_metas[0],
            'path': "",
            'content': self.normalize_urls( sitemap(self.request).content, level=0 ),
        })
        
        # Génération des pages
        self.make_wikipage_all( queryset )
    
    def make_wikipage_all(self, queryset):
        """
        Méthode récursive de génération des pages disponibles sur le wiki
        """
        from kiwi.views.wikipage import details
        
        # Récupération de toute les pages publiés et leur sous-pages
        for page in queryset:
            self.pages.append({
                'title': page.title,
                'filename': self.filename_format % page.uri,
                'path': "",
                'content': self.normalize_urls( details(self.request, page.uri, with_history=False).content, level=0 ),
            })
            # On suit ses sous-pages éventuelles
            self.make_wikipage_all( page.child.filter(active=True) )


class WikiPlainExporter(DocExport):
    """
    Class pour exporter les sources du Wiki
    """
    def __init_documents__( self, project_directory, settings_file, sitemap_metas=("index", "Sommaire"), parent_uri=None):
        """
        Méthode de récupération des documents à exporter.
        
        @project_directory = répertoire du projet django à importer.
        
        @settings_file = fichier de settings à utiliser avec le projet.
        
        @sitemap_metas = un tuple contenant en première position le nom de 
        fichier (sans extension) pour le plan du site généré et son titre 
        en seconde position.
        
        @parent_uri = URI d'une page qui sera le point de départ du 
        site exporté, ces sous-pages seront aussi suivies.
        """
        self.project_directory = project_directory
        self.settings_file = settings_file
        self.sitemap_metas = sitemap_metas
        self.parent_uri = parent_uri
        self.parent_id = None
        
        title_message = "**  %s (plain) v%s, started Kiwi on '%s'  **" % (__title__, __version__, self.project_directory)
        self.output_info( title_message )
            
        # Importe les settings du projet        
        self.settingsMod = ImportDjangoProject(project_directory, settings_file)
        if not self.settingsMod:
            raise "Unable to import Kiwi at directory '%s'" % project_directory
        # Attributs qui dépendent des settings
        self.module_urlpath_prefix = './'
        self.filename_format = u'%s'
        
        # Map des urls internes au site
        self.get_site_urls()
        
        # Collecte les documents à génèrer
        self.get_documents()
    
    def get_site_urls( self ):
        """
        Collecte toute les urls internes au site et qui sont à remplacer pour 
        pouvoir naviguer dans les documents générés.
        
        Les urls contenu dans 'self.urls' sont sous la forme (REMPLACEMENT, 
        LEVEL) où REMPLACEMENT est la chaine qui remplacera le motif, 
        LEVEL indique le niveau de profondeur du document visé par le lien 
        par rapport à la racine du sitemap.
        """
        from django.contrib.sites.models import Site
        from kiwi.models import Wikipage
        
        # Base de départ avec l'index
        root_fullurl = 'http://%s' % Site.objects.get_current().domain
        self.urls = {
            '/' : ("index.html", 0),
            root_fullurl: ("index.html", 0),
        }
        # Collecte de toute les urls de pages existantes et actives
        for item in Wikipage.objects.filter(active=True):
            url = self.filename_format%item.uri
            self.urls[ item.get_absolute_url() ] = ( url.encode('utf-8'), 1)
    
    def get_documents(self):
        """
        Groupement des méthodes de récupération des pages publiées et leur 
        contenu.
        """
        from kiwi.models import Wikipage
        self.pages = []
        
        # Limitation de l'arborescence à une page et ses enfants
        if self.parent_uri:
            try:
                parentObject = Wikipage.objects.get( uri=self.parent_uri )
            except Wikipage.DoesNotExist:
                raise " Wikipage with URI '%s' does not exist" % self.parent_uri
            else:
                self.parent_id = parentObject.id
        
        # Lookup de toute les pages du premier niveau
        if not self.parent_uri:
            queryset = Wikipage.objects.filter( in_sitemap=True, active=True )
        # Lookup d'une page ciblée
        else:
            queryset = [parentObject]
            
        # Récupération de toute les pages publiés et leur sous-pages
        for page in queryset:
            self.pages.append({
                'title': page.title,
                'filename': self.filename_format % page.uri,
                'path': "",
                'content': page.text.encode('utf-8'),
            })

#
if __name__ == "__main__":
    #>
    #> Utilisation de l'export du Wiki
    #>
    # Configuration contenant le nécessaire pour importer et accéder 
    # à Kiwi.
    #
    # Pour certains, on peut avoir besoin d'utiliser des templates, url des 
    # médias, etc.. différents de ceux utilisé sur le site en prod. Pour cela 
    # il suffirait alors d'indiquer un fichier settings différent conçu 
    # spécialement pour l'exportation.
    #
    # Les attributs de configuration, sont commentés dans la méthode 
    # '__init_documents__' de la classe 'WikiXhtmlExporter'
    project_directory = os.path.normpath( os.path.join( os.getcwd(), "./" ) )
    config = {
        'settings_file': 'export_settings',
        'project_directory': project_directory,
        'parent_uri': None,
    }
    targetDir = "/home/django/projects/kiwi_project/documentation"
    
    o = WikiXhtmlExporter( targetDir=targetDir, config=config, debug=False, verbose=True )
    #o = WikiPlainExporter( targetDir=targetDir, config=config, debug=False, verbose=True )
    o.export()

