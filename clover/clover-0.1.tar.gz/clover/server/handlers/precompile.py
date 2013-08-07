import os

from clover.sourcefiles.soy import SoySourceFile
from clover.server.handlers.base import Base


class Handler(Base):
    def get(self, id, path):
        config = self.get_config(id)
        
        path = '/' + path
        
        if not os.path.exists(path):
            return self.error(404)
        
        # get the base path        
        basedir = config.basedir
        if not path.endswith('.soy'):
            return self.error(404)
            
        source = SoySourceFile(os.path.join(basedir, path))
        code = source.get_code_cached()
        self.response.headers['Content-Type'] = 'application/javascript'
        self.response.write(code)

        