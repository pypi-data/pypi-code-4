from hk2.extensions.interfaces import IPluginManager, ExtParamConstraint, PluginBase

from hk2.extensions.impl.plugin_shadow import PluginShadow
from hk2.extensions.impl.extension_point import ExtensionPoint
from hk2.extensions.impl.plugin_graph import PluginGraph

from hk2.utils.version import Version

import logging
log = logging.getLogger('hk2.extensions') 

#===========================================================

class PluginManager(IPluginManager):
    def __init__(self, scanner):
        self._scanner = scanner
        self._plugins = {}
        self._extensionPoints = {}
        self._resolvedModules = set()
        
        self._loadGraph()
    
    def plugins(self):
        return self._plugins
    
    def extensionPoints(self):
        return self._extensionPoints
    
    def createInstance(self, ext):
        ep = ext.extensionPoint()
        
        try:
            ep_mod, iface = self._scanner.getType(ep.plugin(), ep.interfaceName())
            ext_mod, clazz = self._scanner.getType(ext.plugin(), ext.className())
            
            self._prepareModule(ep_mod, ep.plugin())
            self._prepareModule(ext_mod, ext.plugin())
            
            inst = clazz()
        except:
            log.exception("Extension instantiation failed EP=%s, Ext=%s" \
                          % (ext.extensionPoint().fullName(), ext.plugin().name()))
            raise
        
        if not isinstance(inst, iface):
            import inspect
            base = inspect.getmro(inst.__class__)
            raise Exception("Extension does not implement required interface EP=%s, Ext=%s Iface=%s Cls=%s Base=%s" \
                            % (ext.extensionPoint().fullName(), ext.plugin().name(), iface, inst, base))
        
        return inst
    
    def start(self, args=None):
        log.info("Running hk2::start_listeners extensions")
        
        stl = self._extensionPoints['hk2::start_listeners']
        exts = list(stl.extensions())
        exts.sort(key = lambda x: x.parameters().get('priority', 50))
        
        for ext in exts:
            inst = self.createInstance(ext)
            inst.start(args)
        
        log.info("Shutting down hk2")
    
    def _getKernelPlugin(self):
        kpl = PluginShadow()
        kpl._name = 'hk2'
        kpl._desc = 'pyhk2 kernel plugin'
        kpl._author = 'Sergii Mikhtoniuk (mikhtoniuk@gmail.com)'
        kpl._version = Version('1.0.0')
        
        stl = ExtensionPoint()
        stl._plugin = kpl
        stl._name = 'start_listeners'
        stl._interface = 'hk2.extensions.IStartListener'
        stl._params = { "priority" : ExtParamConstraint.Optional }
        
        kpl._extensionPoints.append(stl)
        return kpl
    
    def _loadGraph(self):
        log.info("Loading plugins")
        shadows = self._scanner.scan()
        shadows.append(self._getKernelPlugin())
        
        unique_plugins = set()
        for s in shadows:
            if s.name() in unique_plugins:
                raise Exception("Plugin name collision '%s'" % (s.name()))
            unique_plugins.add(s.name())
        
        log.info("Resolving plugin graph")
        pg = PluginGraph()
        self._plugins, self._extensionPoints = pg.resolve(shadows)
    
    def _prepareModule(self, mod, shadow):
        if mod not in self._resolvedModules:
            pl_t = self._findSubclass(PluginBase, mod)
            if pl_t:
                pl = pl_t()
                pl.init(shadow, self)
            
            self._resolvedModules.add(mod)
        
        return mod
    
    def _findSubclass(self, base, mod):
        mn = mod.__name__
        sc = base.__subclasses__()
        for c in sc:
            if c.__module__ == mn:
                return c
        return None

