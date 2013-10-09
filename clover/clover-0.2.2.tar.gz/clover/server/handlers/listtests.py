from clover.server.handlers.base import Base
import os

class Handler(Base):
    def get(self, id):
        config = self.get_config(id)
        
        self.data['config'] = config
        self.data['config_id'] = id
        
        test_files = sorted(config.find_tests())
        test_files = [(file, os.path.relpath(file, config.basedir)) for file in test_files]
        
            
        # search the paths for _test.js/html
        self.data['test_files'] = test_files
        
        return self.render_template('templates/list_tests.jinja')