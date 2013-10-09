import json
import logging
from clover.server.handlers.base import Base
from clover.builder import Builder


# XXX: a global used as a compilation cache
CACHE = {}

LOGGING_TEMPLATE = '''\
var CLOVER_ERRORS = %s;
var CLOVER_WARNINGS = %s;

clover = {};

clover.htmlEscape = function(str) {
  return str.replace(/[&<"]/g, function(ch) {
    switch (ch) {
      case '&': return '&amp;';
      case '<': return '&lt;';
      case '"': return '&quot;';
    }
  });
};

clover.ERROR_STYLE = 1;
clover.WARNING_STYLE = 2;
clover.addslashes = function ( str ) {
    return (str + '').replace(/[\\\\"']/g, '\\\\$&').replace(/\\u0000/g, '\\\\0');
}
/**
 * @param {Array.<clover.CompilationError>} errors
 * @param {string} style
 */
clover.writeErrors_ = function(errors, style) {
  for (var i = 0, len = errors.length; i < len; i++) {
    var error = errors[i];
    var message = error['description'];
    var htmlMessage = clover.htmlEscape(message);
    
    if(style == clover.ERROR_STYLE) {
      console.error(error['input'], error['line'], error['column'], message);
    }
    else {
      console.warn(error['input'], error['line'], error['column'], message);
    }
  }
};

clover.writeErrorsOnLoad = function() {
  clover.writeErrors_(CLOVER_ERRORS, clover.ERROR_STYLE);
  clover.writeErrors_(CLOVER_WARNINGS, clover.WARNING_STYLE);
};

clover.writeErrorsOnLoad();

'''

HEADER = '''\
var CLOSURE_NO_DEPS = true;

'''

FATAL_ERROR = '''\
console.error('%s')
'''
import re

def fatal_error(message):
    return FATAL_ERROR % re.escape(message)
    
    
def build_warning_log(compilation):
    args = (
        json.dumps(compilation.errors),
        json.dumps(compilation.warnings),
    )
    template = LOGGING_TEMPLATE % args
    return template

from clover.solver import SolverError

class Handler(Base):
    def render_raw(self, config):
        id = config.get_id()
        buildconfig = config.get_build_manifest()
        
        # paths in deps.js must be relative to the base.js
        
        paths = []
        deps = buildconfig.get_sorted_deps()
        
        for sourcefile in deps:
            basepath = sourcefile.path
            
            if sourcefile.precompile:
                path = self.uri_for('precompile', id=id, path=basepath)  
            else:
                path = '/configs/%s/input%s' % (id, basepath)
            
            paths.append(path)
            
        base_js_path = buildconfig.get_base_js().path
        paths.insert(0, '/configs/%s/input%s' % (id, base_js_path))
        
        self.data['files'] = ['%s%s' % ("http://localhost:2323", path) for path in paths]
        
        return self.render_template('templates/raw_template.jinja')
    
    def get(self, id):
        config = self.get_config(id)
        
        self.data['config'] = config
        
        if config.read_option(config.options.mode) != 'WHITESPACE':
            pass
        
        try:
            self.response.headers["Content-Type"] = "application/javascript"
            
            if config.read_option(config.options.mode) == 'RAW':
                return self.render_raw(config)
            
            
            # compile and cache the result for other handlers...
            
            builder = Builder(config)
            builder.compiler.location_prefix = "http://localhost:2323/configs/%s/input" % id
            compilation = builder.build()
            code = compilation.source
            
            if code is None:
                code = ""
            else:
                sourcemap = self.uri_for('sourcemap', id=id)
                self.response.headers["SourceMap"] = sourcemap
                self.response.headers["X-SourceMap"] = sourcemap
        except SolverError as e:
            logging.error('Error compiling: %s', e)
            self.response.write(fatal_error(str(e)))
            return
            


        code = compilation.wrap_source(config.read_option(config.options.output_wrapper))

        CACHE[id] = compilation
        # prepend no deps for any compilation
        self.response.write(HEADER + code + build_warning_log(compilation))
