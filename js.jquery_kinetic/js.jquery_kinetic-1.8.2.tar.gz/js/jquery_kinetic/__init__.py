from fanstatic import Library, Resource
from js.jquery import jquery
from js.jqueryui import jqueryui

library = Library('jquery_kinetic', 'resources')

jquery_kinetic = Resource(
    library, 
    'jquery.kinetic.js',
    minified='jquery.kinetic.min.js',
    depends=[jquery, jqueryui],
    bottom=True,
)
