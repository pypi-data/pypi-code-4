
# this is the relocatable location of the propell font for png generation demos
#propell_font_path = __path__[0]+"/data/propell.bdf"

import os 
from whiff import resolver

__wsgi_directory__ = True

resolver.publish_templates(__path__[0], globals())

