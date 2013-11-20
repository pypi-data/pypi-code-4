import re
import os.path


class Recipe(object):
    """zc.buildout recipe"""
    
    def __init__(self,buildout,name,options):
        self.buildout = buildout
        self.name = name
        self.options = options

        # We use the recipe section as it is required
        config_path = self.buildout._annotated[name]['recipe'][1]
        if not re.match("^[^:/]+://", config_path):
            config_path = "file://" + os.path.abspath(config_path)

        # Export the full path of the config and also the base path for concatenating
        # with other stuff
        self.options['config_path'] = config_path
        self.options['base'] = '/'.join(config_path.split('/')[:-1])
    
    def install(self):
        return tuple()
    
    def update(self):
        pass
