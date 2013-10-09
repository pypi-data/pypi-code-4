import os
from clover.server.handlers.base import Base
from clover.sourcefiles.javascript import JavascriptSourceFile

# a cache of 
cache = {}


class Handler(Base):
    def get(self, id, path):
        #path = self.request.get('path')
        
        
        config = self.get_config(id)
        if not path.startswith('/'):
            path = config.abspath(path)
        
        self.data['base_js_url'] = '/library/goog/base.js'
        
        if not path.endswith('.js'):
            return 
            
        
        self.data['test_js_url'] = self.uri_for('input', id=id, path=path)
        self.data['goog_base_js'] = '/library/goog/base.js'
        self.data['goog_deps_js'] = '/library/goog/deps.js'
        self.data['test_deps_js'] = self.uri_for('deps', id=id)
        self.data['test_title'] = path
        
        #test_template = config.read_option(config.options.test_template)
        
        
        sourcefile = JavascriptSourceFile(path)
        self.data['test_requires'] = sourcefile.get_require_names()
        
        if not os.path.exists(path):
            self.response.out.write('Test %s is missing' % path)
            self.response.set_status(404)
            return
        
        #if test_template:
        #    test_template = config.abspath(test_template)
        #    return self.render_template_string(open(test_template).read())
        #else:
        # use the default test template
        return self.render_template('templates/test_template.jinja')
    
        
