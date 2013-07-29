from fanstatic import Library, Resource

from js.jquery import jquery

library = Library('fotorama', 'resources')

fotorama_css = Resource(
    library, 'fotorama.css',
)

fotorama = Resource(
    library, 'fotorama.js',
    depends=[
        fotorama_css,
        jquery,
    ],
)
