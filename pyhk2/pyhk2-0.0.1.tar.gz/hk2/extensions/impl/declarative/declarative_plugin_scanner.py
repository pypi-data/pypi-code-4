from hk2.extensions.interfaces import IPluginScanner

from hk2.extensions.impl.declarative.plugin_desc_parser import PluginDescParser
from hk2.utils.pathutil import listdir_recursive

import os, sys
import logging
log = logging.getLogger('hk2.extensions')

#===========================================================

class DeclarativePluginScanner(IPluginScanner):
    PLUGIN_DESC_FILE = '__plugin__.py'
    
    def __init__(self):
        self.plugin_dirs = []
        self.resolvedModules = set()
    
    def addDir(self, path, recursive=False):
        self.plugin_dirs.append((os.path.abspath(path), recursive))
    
    def scan(self):
        candidates = self._scanDirs()
        all_descs = ( self._loadPluginDesc(c) for c in candidates )
        plugin_descs = [ d for d in all_descs if d ]
        
        paths = [p[0] for p in self.plugin_dirs]
        paths = [os.path.abspath(p) for p in paths or ["."]]
        roots = [p for p in paths for pp in paths if not p.startswith(pp)]
        for p in roots:
            sys.path.insert(0, d)
        
        return plugin_descs
    
    def getType(self, shadow, typeName):
        module, clazz = self._splitTypeName(typeName)
        
        log.debug("Importing module '%s'", module)
        mod = __import__(module, {}, {}, ['*'])
        typ = mod.__dict__.get(clazz)
        
        if not typ:
            raise Exception("Type '%s' not found in module '%s'" % (clazz, module))
        
        return mod, typ
    
    def _scanDirs(self):
        candidates = []
        plugin_dirs = self.plugin_dirs or [('.', None, False)]
        
        for path, recursive in plugin_dirs:
            ld = os.listdir if not recursive else listdir_recursive
            listdir = ( os.path.join(p) for p in ld(path) )
            plugindirs = ( p for p in listdir if self._isPlugin(p) )
            
            candidates.extend(plugindirs)
        
        return candidates
    
    def _isPlugin(self, path):
        return os.path.isdir(path) and os.path.isfile(os.path.join(path, DeclarativePluginScanner.PLUGIN_DESC_FILE))
    
    def _loadPluginDesc(self, path):
        try:
            desc_path = os.path.join(path, DeclarativePluginScanner.PLUGIN_DESC_FILE)
            desc = PluginDescParser.parse_file(desc_path)
            desc._path = path
            log.debug("Loaded plugin desc '%s'", desc.name())
            return desc
        except:
            log.exception("Failed to load plugin desc in '%s'", path)
    
    def _splitTypeName(self, typeName):
        p = typeName.split('.')
        module = '.'.join(p[:-1])
        clazz = p[-1]
        return module, clazz




