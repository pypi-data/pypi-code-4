from fanstatic import Library, Resource

from js.jquery import jquery

library = Library('jquery_autosize', 'resources')

jquery_autosize = Resource(
    library, 'jquery.autosize.js',
    minified='jquery.autosize.min.js',
    depends=[jquery],
)
