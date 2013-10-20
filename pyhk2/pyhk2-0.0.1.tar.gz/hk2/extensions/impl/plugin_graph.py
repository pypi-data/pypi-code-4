from hk2.extensions.interfaces import ExtParamConstraint

import logging
log = logging.getLogger('hk2.extensions') 

#===========================================================

class PluginGraph(object):
    def resolve(self, shadows):
        plugins = { shadow.name() : shadow for shadow in shadows }
        extensionPoints = { ep.fullName() : ep for p in plugins.itervalues() for ep in p.extensionPoints() }
        
        self._resolveGraph(plugins, extensionPoints)
        return (plugins, extensionPoints)
    
    def _resolveGraph(self, plugins, extensionPoints):
        
        
        extensions = ( ex for p in plugins.itervalues() for ex in p.extensions() )
        for ex in extensions:
            ep = extensionPoints.get(ex._pointName)
            if not ep:
                log.warning("Extension point '%s' targeted by '%s' not found", ex._pointName, ex.plugin().name())
            else:
                self._validateExtension(ex, ep)
                ex._point = ep
                ep._extensions.append(ex)
    
    
    def _validateExtension(self, ext, point):
        for name, constr in point.parameters().iteritems():
                if constr == ExtParamConstraint.Mandatory and name not in ext.parameters():
                    raise Exception("Extension point parameter '%s' constraint failed EP=%s, Ext=%s" \
                                    % (name, point.fullName(), ext.plugin().name()))
