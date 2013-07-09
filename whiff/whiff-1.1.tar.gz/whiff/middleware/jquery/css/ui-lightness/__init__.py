
from whiff import resolver

__wsgi_directory__ = True

resolver.publish_templates(__path__[0], globals(), mime_extensions=True)
