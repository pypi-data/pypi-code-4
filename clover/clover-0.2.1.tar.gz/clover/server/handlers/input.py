from clover.server.handlers.base import Base
import os

# TODO: send proper cache headers

class Handler(Base):
    def get(self, id, path):
        self.data['config_id'] = id
        config = self.get_config(id)
        
        if not path.startswith('/'):
            path = '/' + path
        
        if os.path.isdir(path):
            self.data['parent_path'] = os.path.abspath(os.path.join(path, '..'))
            entries = sorted(list(os.listdir(path)))
            files = []
            directories = []
            for entry in entries:
                abspath = os.path.join(path, entry)
                if os.path.isdir(abspath):
                    directories.append((entry, abspath))
                else:
                    files.append((entry, abspath))
            
            self.data['directories'] = directories
            self.data['files'] = files
            return self.render_template('templates/list_directory.jinja')
            
        code = open(path).read()

        if path.endswith('.js'):
            self.response.headers['Content-Type'] = 'application/javascript; charset=UTF-8'
            code += '\n//# sourceURL=file://%s\n' % path
            code += '//@ sourceURL=file://%s\n' % path
        if path.endswith('.css'):
            self.response.headers['Content-Type'] = 'text/css; charset=UTF-8'
       
        self.response.write(code)


        