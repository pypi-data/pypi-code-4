from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('namespace', 'resources')

namespace = Resource(library, 'namespace.js', depends=[jquery])
