import fanstatic
import js.jquery

library = fanstatic.Library('ember', 'resources')

handlebars = fanstatic.Resource(
    library,
    'handlebars-1.0.0.js',
    minified='handlebars-1.0.0.min.js')

ember = fanstatic.Resource(
    library,
    'ember-1.0.0-rc.8.js',
    minified='ember-1.0.0-rc.8.min.js',
    depends=[js.jquery.jquery, handlebars])

ember_data = fanstatic.Resource(
    library,
    'ember-data-0.13-108.js',
    minified='ember-data-0.13-108.min.js',
    depends=[ember])
