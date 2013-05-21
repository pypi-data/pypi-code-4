import fanstatic
import js.jquery

library = fanstatic.Library('jquery_placeholder', 'resources')

jquery_placeholder = fanstatic.Resource(
    library,
    'jquery.placeholder.js',
    minified='jquery.placeholder.min.js',
    depends=[js.jquery.jquery]
)
