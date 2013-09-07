from fanstatic import Library, Resource


library = Library('pure', 'resources')

# Pure with the responsive bits
pure = Resource(library, 'pure-min.css')

# Pure without the responsive bits
purenr = Resource(library, 'pure-nr-min.css')
