import operator
import json

import os

from clover.server.handlers.base import Base


def relative_path(path, relative_to):
    return os.path.relpath(path, relative_to)

def _GetDepsLine(path, sourcefile):
    """Get a deps.js file string for a source."""

    provides = sorted(sourcefile.get_provide_names())
    requires = sorted(sourcefile.get_require_names())
    
    return 'goog.addDependency(\'%s\', %s, %s);' % (path, json.dumps(provides), json.dumps(requires))

class Handler(Base):
    def get(self, id):
        config = self.get_config(id)
        
        self.data['config'] = config
        buildconfig = config.get_build_manifest()
        
        lines = []    
        
        for sourcefile in sorted(buildconfig.all_sourcefiles, key=operator.attrgetter('path')):
            basepath = sourcefile.path
            
            # XXX: this is hackish.. do some better calcs!
            if sourcefile.precompile:
                path = '../..%s' % self.uri_for('precompile', id=id, path=basepath)  
            else:
                path = '../../configs/%s/input/%s' % (id, basepath)
            
            lines.append(_GetDepsLine(path, sourcefile))
            
        depsjs = '\n'.join(lines )
        
        self.response.headers["Content-Type"] = "application/javascript"
        self.response.write(depsjs)