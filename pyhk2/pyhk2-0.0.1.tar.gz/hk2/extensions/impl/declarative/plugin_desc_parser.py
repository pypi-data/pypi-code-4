from hk2.extensions.impl.plugin_shadow import PluginShadow
from hk2.extensions.impl.extension import Extension
from hk2.extensions.impl.extension_point import ExtensionPoint
from hk2.utils.version import Version

import imp
from hk2.extensions.interfaces import ExtParamConstraint

#===========================================================

class PluginDescParser(object):
    def __init__(self, config):
        self.shadow = PluginShadow()
        self._validate(config)
        
        self._loadDescription(config)
        
        provides_sec = config.get('provides', [])
        if isinstance(provides_sec, dict):
            provides_sec = [provides_sec]
        self._loadProvides(provides_sec)
        
        extends_sec = config.get('extends', [])
        if isinstance(extends_sec, dict):
            extends_sec = [extends_sec]
        self._loadExtends(extends_sec)
    
    @staticmethod
    def parse(stream):
        loader = imp.new_module('hk2.extensions.loader')
        exec 'from hk2.extensions import *' in loader.__dict__
        exec stream.read() in loader.__dict__
        if 'plugin' not in loader.__dict__:
            raise Exception('Declarative config not found')
        return PluginDescParser(loader.plugin).shadow
    
    @staticmethod
    def parse_file(filename):
        with open(filename, 'r') as f:
            return PluginDescParser.parse(f)
    
    def _validate(self, config):
        root_els = ['name', 'desc', 'version', 'author', 'extends', 'provides']
        unknown = [k for k in config if k not in root_els]
        
        if len(unknown):
            raise Exception('Unknown root parameters: %s' % (', '.join(unknown)))
    
    def _loadDescription(self, config):
        self.shadow._name = config['name']
        self.shadow._desc = config.get('desc')
        self.shadow._version = Version(config.get('version', '0.0.0'))
        self.shadow._author = config.get('author', None)
    
    def _loadProvides(self, prv):
        for ep in prv:
            epd = ExtensionPoint()
            epd._plugin = self.shadow
            epd._name = ep['point']
            epd._interface = ep['interface']
            epd._params = self._loadProvidesParams(ep.get('params', {}))
            
            self.shadow._extensionPoints.append(epd)
    
    def _loadProvidesParams(self, params):
        for _, prop in params.iteritems():
            assert prop in ExtParamConstraint.values
        
        return params
    
    def _loadExtends(self, exts):
        for ext in exts:
            etd = Extension()
            etd._plugin = self.shadow
            etd._pointName = ext['point']
            etd._className = ext['class']
            etd._params = ext.get('params', {})
            
            self.shadow._extensions.append(etd)
    
    