from fanstatic import Library, Resource

library = Library('log4javascript', 'resources')

log4javascript = Resource(library,
    'log4javascript_uncompressed.js',
    minified='log4javascript.js')
