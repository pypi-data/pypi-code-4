from clover.server.handlers.base import Base

# a cache of 
cache = {}


class Handler(Base):
    def get(self, id):
        path = self.request.get('path')
        
        
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
        
        test_template = config.read_option(config.options.test_template)

        return self.render_template('templates/test_command.jinja')
            
    
        
