
# this is the relocatable location of the propell font for png generation demos
#propell_font_path = __path__[0]+"/data/propell.bdf"

import os 
from whiff import resolver

def data_file_path(filename, data_subdir="data"):
    base_dir = __path__[0]
    return os.path.join(base_dir, data_subdir, filename)

__wsgi_directory__ = True

resolver.publish_templates(__path__[0], globals())

