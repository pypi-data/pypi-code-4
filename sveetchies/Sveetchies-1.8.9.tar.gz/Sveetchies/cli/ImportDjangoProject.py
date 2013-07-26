#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This script provide a short method to import any Django's project from 
# anywhere, no matter that you are or not under the path's project.
# 
# Requires :
# * Python >= 2.5
# * Django >= 0.96
#
#
__title__ = "Django's project anywhere importer"
__version__ = "0.2.0"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2008 Sveetch.biz"
__license__ = "GPL"

import imp, os, sys

def ImportDjangoProject(projectDir, settingsFile, djangoPath=None):
    """
    Import module @settingsFile from the directory @projectDir given. The 
    @settingsFile is imported as a python module, so it must be his filename 
    without the ".py" extension.
    
    For specific case where django is not in the python_path of the shell, you 
    can specify it with @djangoPath in an absolute path to the Django directory
    
    If the import is a success, the method return the settings file as a 
    Settings object. If not return False.
    
    :type projectDir: string
    :param projectDir: Project directory to import.
    
    :type settingsFile: string
    :param settingsFile: Settings module name of the projet.
    
    :type djangoPath: string
    :param djangoPath: (optional) Specific path to the install of Django.
    """
    # Tente d'importer Django
    if not djangoPath:
        import django
    else:
        Django_fp, Django_pathname, Django_desc = imp.find_module("django", [djangoPath])
        imp.load_module("django", Django_fp, Django_pathname, Django_desc)
    # Django est bien installé, tout se passe normalement
    django_install_fullpath = sys.modules['django'].__path__[0]
    
    # Get the project name
    project_name = os.path.basename( os.path.abspath( projectDir ) )
    
    # Export DJANGO_SETTINGS_MODULE in the user shell so Django can 
    # retreive it
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.%s' % ( project_name, settingsFile )
    
    # Import the settings file from the project directory.
    fp, pathname, description = imp.find_module(settingsFile, [projectDir])
    try:
        settings_mod = imp.load_module(settingsFile, fp, pathname, description)
    except:
        return False
    finally:
        # Close fp explicitly.
        if fp:
            fp.close()
    
    # Add the project to the sys.path
    project_name = os.path.basename( os.path.abspath( projectDir ) )
    sys.path.append( os.path.normpath( os.path.join(projectDir, '..') ) )
    # Sys.path is ok, we can import the project
    project_module = __import__(project_name, '', '', [''])
    # Cleanup the sys.path of the project path
    sys.path.pop()
    
    return settings_mod

## Import example with the Shoop project
#if __name__ == "__main__":
    #o = ImportDjangoProject(projectDir="/home/django/projects/shoop", settingsFile="prod_settings")
    #print o
    ## Sample test of the imported project
    ##from django.shortcuts import get_object_or_404
    ##from shoop.wiki.models import Wikipage, Version, Backlink
    ##print get_object_or_404(Wikipage, uri="Accueil")
