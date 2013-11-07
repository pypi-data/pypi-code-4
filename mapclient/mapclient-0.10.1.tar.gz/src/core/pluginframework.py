'''
MAP Client, a program to generate detailed musculoskeletal models for OpenSim.
    Copyright (C) 2012  University of Auckland
    
This file is part of MAP Client. (http://launchpad.net/mapclient)

    MAP Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MAP Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MAP Client.  If not, see <http://www.gnu.org/licenses/>..
'''

'''
Inspired by Marty Alchin's Simple plugin framework.
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
'''

import os, imp

MAIN_MODULE = '__init__'

def getPlugins(pluginDirectory):
    '''
    Get all plugins from the given directory.
    '''
    plugins = []
    try:
        possibleplugins = os.listdir(pluginDirectory)
    except OSError:
        possibleplugins = []
    for i in possibleplugins:
        # print('possible plugin: ' + i)
        location = os.path.join(pluginDirectory, i)
        if not os.path.isdir(location) or not MAIN_MODULE + '.py' in os.listdir(location):
            continue
        info = imp.find_module(MAIN_MODULE, [location])
        plugins.append({'name': i, 'info': info})

    return plugins

def loadPlugin(plugin):
    return imp.load_module(MAIN_MODULE, *plugin['info'])

# class LoadDepth(object):
#    depth = 0
#
# def loadPlugins(pkgDir):
#    ii = pkgutil.ImpImporter(pkgDir)
# #    sys.path.insert(0, pkgDir)
#    LoadDepth.depth += 1
#    try:
#        for moduleName, isPkg in ii.iter_modules():
# #        projectName = os.path.basename(pkgDir)
#            if isPkg:
#                pkgPath = os.path.join(pkgDir, moduleName)
#                initPackage(pkgPath)
# #                project = __import__(moduleName)
# #                print(moduleName)
# #                sys.modules[moduleName] = project
#
#                loadPlugins(pkgPath)
#            else:
#                loadModule(moduleName, pkgDir)
# #            print(moduleName)
#    finally:
# #        print(sys.path)
# #        del sys.path[0]
#        LoadDepth.depth -= 1
# #        print(sys.path)
#
# def loadPlugins2(pkgDir):
#    ii = pkgutil.ImpImporter(pkgDir)
#    LoadDepth.depth += 1
# #    print(LoadDepth.depth)
#    for moduleName, isPkg in ii.iter_modules():
#        if isPkg:
#            pkgPath = os.path.join(pkgDir, moduleName)
#            module = initPackage(pkgPath)
# #            print(pkgPath)
#            if module and pkgDir not in sys.path and LoadDepth.depth == 1:
#                sys.path.append(pkgDir)
# #                print(pkgDir)
# #            __import__(moduleName)
#            loadPlugins(pkgPath)
#        else:
# #            print(moduleName, pkgDir)
#            loadModule(moduleName, pkgDir)
#
#    LoadDepth.depth -= 1
#
# def initPackage(pkgDir):
#    fp, path, description = imp.find_module('__init__', [pkgDir])
#    module = imp.load_module(pkgDir, fp, path, description)
# #    try:
# #        module = imp.load_module(pkgDir, fp, path, description)
# #    except:
# #        module = None
# #        print('Failed to initialise package {0}.'.format(pkgDir))
# #    finally:
# #        if fp:
# #            fp.close()
#    if LoadDepth.depth == 1:
#        print("Plugin '{0}' version {1} by {2} loaded".format(pkgDir.split(os.sep)[-1], module.__version__, module.__author__))
#    fp.close()
#
#    return module
#
# def loadModule(moduleName, moduleDir):
#    fp, path, description = imp.find_module(moduleName, [moduleDir])
#
#    print(moduleDir)
#    imp.load_module(moduleDir, fp, path, description)
# #    print('======= module', module)
#
# #    moduleVersion = '-.-.-'
# #    if hasattr(module, '__version__'):
# #        moduleVersion = module.__version__
# #    moduleAuthor = '?'
# #    if hasattr(module, '__author__'):
# #        moduleAuthor = module.__author__
# #    print("Plugin '{0}' version {1} by {2} loaded".format(moduleName, moduleVersion, moduleAuthor))
#    fp.close()
# #    try:
# #        module = imp.load_module(moduleDir, fp, path, description)
# #
# #        moduleVersion = '-.-.-'
# #        if hasattr(module, '__version__'):
# #            moduleVersion = module.__version__
# #        moduleAuthor = '?'
# #        if hasattr(module, '__author__'):
# #            moduleAuthor = module.__author__
# #        print("Plugin '{0}' version {1} by {2} loaded".format(moduleName, moduleVersion, moduleAuthor))
# #    except:
# #        # non modules will fail
# #        print("Plugin '{0}' not loaded".format(moduleName))
# #    finally:
# #        if fp:
# #            fp.close()
#
# class PluginsAt(object):
#    '''
#    Descriptor to get plugins on a given mount point.
#    '''
#    def __init__(self, mount_point):
#        '''
#        Initialise the descriptor with the mount point wanted.
#        Eg: PluginsAt(PluginFramework.MenuOption) to get extensions that change the GUI Menu.
#        '''
#        self.mount = mount_point
#
#    def __get__(self, instance, owner=None):
#        '''
#        Plugins are instantiated with the object that is calling them.
#        '''
#        return [p() for p in self.mount.plugins]


# import traceback
class MetaPluginMountPoint(type):
    '''
    * A way to declare a mount point for plugins. Since plugins are an example 
      of loose coupling, there needs to be a neutral location, somewhere between
      the plugins and the code that uses them, that each side of the system can
      look at, without having to know the details of the other side. Trac calls
      this an 'extension point'.
    * A way to register a plugin at a particular mount point. Since internal code
      can't (or at the very least, shouldn't have to) look around to find plugins 
      that might work for it, there needs to be a way for plugins to announce their
      presence. This allows the guts of the system to be blissfully ignorant of 
      where the plugins come from; again, it only needs to care about the mount point.
    * A way to retrieve the plugins that have been registered. Once the plugins 
      have done their thing at the mount point, the rest of the system needs to
      be able to iterate over the installed plugins and use them according to its need.

    For compatibility across python 2.x and python 3.x we must construct the PluginMountPoint
    classes like so:
    MyPlugin = MetaPluginMountPoint('MyPlugin', (object, ), {})
    '''

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)

#        traceback.print_stack()
#        for item in sys.modules:
#            print(item)
#        print('=========', cls, name)

    def getPlugins(self, *args, **kwargs):
        return [p(*args, **kwargs) for p in self.plugins]


# Plugin mount points are defined below.
# For running in both python 2.x and python 3.x we must follow the example found
# at http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/
from PySide.QtCore import QObject

MetaQObject = type(QObject)

# For multiple inheritance in classes we also need to create a metaclass that also
# inherits from the metaclasses of the inherited classes
class MetaQObjectPluginMountPoint(MetaQObject, MetaPluginMountPoint):

    def __init__(self, name, bases, attrs):
        MetaPluginMountPoint.__init__(self, name, bases, attrs)
        MetaQObject.__init__(self, name, bases, attrs)


#
# Template plugin comment:
#
# '''
# Plugins can inherit this mount point to extend
#
# A plugin that registers this mount point must have attributes
# * None
#
# A plugin that registers this mount point could have attributes
# * None
#
# It must implement
# * pass
#
# '''
#

'''
Plugins can inherit this mount point to add a tool to the tool menu.  It is passed two 
keyword arguments, the tool menu ('menu_Tool') and the parent widget ('parent').

 A plugin that registers this mount point must have attributes
 * None
 
 A plugin that registers this mount point could have attributes
 * None
 
 It must implement
 * pass 
 
'''
ToolMountPoint = MetaPluginMountPoint('ToolMountPoint', (object,), {})

