from fanstatic import Library, Resource

from js.jquery import jquery

library = Library('jquery_interdependencies', 'resources')

jquery_interdependencies = Resource(
    library, 'jquery.interdependencies.js',
    depends=[jquery],
)
