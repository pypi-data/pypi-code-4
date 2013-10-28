from fanstatic import Library, Resource

library = Library('icanhaz.js', 'resources')
icanhaz = Resource(library, 'ICanHaz.min.js', debug='ICanHaz.js')
icanhaz_no_mustache = Resource(library, 'ICanHaz-no-mustache.min.js',
    debug='ICanHaz-no-mustache.js')
