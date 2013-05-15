from fanstatic import Library, Resource
from js.namespace import namespace
from js.jquery import jquery

library = Library('fanstatictools', 'resources')

lib_url = Resource(library, 'url.js', depends=[jquery, namespace])
