from fanstatic import Library, Resource

from js.jquery import jquery

library = Library('galleria', 'resources')

galleria = Resource(
    library, 'galleria.js',
    minified='galleria.min.js',
    depends=[jquery],
)

classic_css = Resource(
    library, 'themes/classic/galleria.classic.css',
)

classic = Resource(
    library, 'themes/classic/galleria.classic.js',
    minified='themes/classic/galleria.classic.min.js',
    depends=[galleria, classic_css],
)
