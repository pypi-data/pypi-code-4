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
import os

from PySide import QtCore

from core.workflow import WorkflowManager
from core.undomanager import UndoManager
from core.threadcommandmanager import ThreadCommandManager

class MainApplication(object):
    '''
    This object is the main application object for the framework.
    '''


    def __init__(self):
        '''
        Constructor
        '''

        self._size = QtCore.QSize(600, 400)
        self._pos = QtCore.QPoint(100, 150)
        self._pluginManager = PluginManager()
        self._workflowManager = WorkflowManager()
        self._undoManager = UndoManager()
        self._threadCommandManager = ThreadCommandManager()

    def setSize(self, size):
        self._size = size

    def size(self):
        return self._size

    def setPos(self, pos):
        self._pos = pos

    def pos(self):
        return self._pos

    def undoManager(self):
        return self._undoManager

    def workflowManager(self):
        return self._workflowManager

    def pluginManager(self):
        return self._pluginManager

    def threadCommandManager(self):
        return self._threadCommandManager

    def writeSettings(self):
        settings = QtCore.QSettings()
        settings.beginGroup('MainWindow')
        settings.setValue('size', self._size)
        settings.setValue('pos', self._pos)
        settings.endGroup()
        self._pluginManager.writeSettings(settings)
        self._workflowManager.writeSettings(settings)
#        for stackedWidgetPage in self.stackedWidgetPages:
#            stackedWidgetPage.writeSettings(settings)

    def readSettings(self):
        settings = QtCore.QSettings()
        settings.beginGroup('MainWindow')
        self._size = settings.value('size', self._size)
        self._pos = settings.value('pos', self._pos)
        settings.endGroup()
        self._pluginManager.readSettings(settings)
        self._workflowManager.readSettings(settings)
#        for stackedWidgetPage in self.stackedWidgetPages:
#            stackedWidgetPage.readSettings(settings)

from core.pluginframework import getPlugins, loadPlugin

class PluginManager(object):


    def __init__(self):
        self._directories = []
        self._loadDefaultPlugins = True
        self._pluginsChanged = False

    def directories(self):
        return self._directories

    def setDirectories(self, directories):
        if self._directories != directories:
            self._directories = directories
            self._pluginsChanged = True

    def loadDefaultPlugins(self):
        return self._loadDefaultPlugins

    def setLoadDefaultPlugins(self, loadDefaultPlugins):
        if self._loadDefaultPlugins != loadDefaultPlugins:
            self._loadDefaultPlugins = loadDefaultPlugins
            self._pluginsChanged = True

    def allDirectories(self):
        plugin_dirs = self._directories[:]
        if self._loadDefaultPlugins:
            file_dir = os.path.dirname(os.path.abspath(__file__))
            inbuilt_plugin_dir = os.path.realpath(os.path.join(file_dir, '..', '..', 'plugins'))
            plugin_dirs.insert(0, inbuilt_plugin_dir)

        return plugin_dirs

    def pluginsModified(self):
        return self._pluginsChanged

    def load(self):
        self._pluginsChanged = False
        for directory in self.allDirectories():
            for p in getPlugins(directory):
                try:
                    loadPlugin(p)
                except:
                    print('Plugin \'' + p['name'] + '\' not loaded')

    def readSettings(self, settings):
        self._directories = []
        settings.beginGroup('Plugins')
        self._loadDefaultPlugins = settings.value('load_defaults', 'true') == 'true'
        directory_count = settings.beginReadArray('directories')
        for i in range(directory_count):
            settings.setArrayIndex(i)
            self._directories.append(settings.value('directory'))
        settings.endArray()
        settings.endGroup()

    def writeSettings(self, settings):
        settings.beginGroup('Plugins')
        settings.setValue('load_defaults', self._loadDefaultPlugins)
        settings.beginWriteArray('directories')
        directory_index = 0
        for directory in self._directories:
            settings.setArrayIndex(directory_index)
            settings.setValue('directory', directory)
            directory_index += 1
        settings.endArray()
        settings.endGroup()
