#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This script is part of Kiwi.
# It requires the Sveetchies module
# See : http://svn.logicielslibres.info/bordel/sveetch/Sveetchies/
#
__title__ = "Kiwi Dumper"
__version__ = "0.0.3"
__author__ = "THENON David"
__copyright__ = "Copyright (c) 2009 Sveetch.biz"
__license__ = "GPL"

import os
from Sveetchies.DocExport import DocExport
from Sveetchies.cli.ImportDjangoProject import ImportDjangoProject

class WikiDumper(object):
    """
    Test d'utilisation du serializer pour le dump brut des modèles
    """
    def __init__( self, project_directory, settings_file):
        """
        @project_directory = répertoire du projet django à importer.
        
        @settings_file = fichier de settings à utiliser avec le projet.
        """
        self.project_directory = project_directory
        self.settings_file = settings_file
        
        title_message = "**  %s v%s, started Kiwi on '%s'  **" % (__title__, __version__, self.project_directory)
            
        # Importe les settings du projet        
        self.settingsMod = ImportDjangoProject(project_directory, settings_file)
        if not self.settingsMod:
            raise "Unable to import Kiwi at directory '%s'" % project_directory
        
        from django.core import serializers
        from kiwi.models import Template, Version, Wikipage
        
        JSONSerializer = serializers.get_serializer("json")
        json_serializer = JSONSerializer()
        out = open("file.json", "w")
        objects = []
        objects.extend( Template.objects.all() )
        objects.extend( Wikipage.objects.all() )
        objects.extend( Version.objects.all() )
        json_serializer.serialize(objects, stream=out, indent=4)


#
if __name__ == "__main__":
    #>
    #> Utilisation du dump du Wiki
    #>
    project_directory = os.path.normpath( os.path.join( os.getcwd(), "./" ) )
    config = {
        'settings_file': 'settings',
        'project_directory': project_directory,
    }
    
    o = WikiDumper( **config )
    #o.export()

