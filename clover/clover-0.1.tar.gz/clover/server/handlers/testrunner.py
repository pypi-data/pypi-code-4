from clover.server.handlers.base import Base


class Handler(Base):
    def get(self, id):
        config = self.get_config(id)
        self.data['config'] = config 
        self.data['config_id'] = id
        testfiles = config.find_tests()
                
        self.data['testfiles'] = [self.uri_for('test', id=id, path=f) for f in testfiles]
        
        if not config.read_option(config.options.closure_library):
            self.data['base_js_url'] = '/library/goog/base.js'
        else:
            # TODO: handle not included library
            pass
        
        return self.render_template('templates/test_runner.jinja')