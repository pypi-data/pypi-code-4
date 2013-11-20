from fanstatic import Library, Resource, Group
from js.bootstrap import bootstrap

library = Library('fuelux', 'resources')

fuelux_css = Resource(library, 'css/fuelux.css',
                      minified='css/fuelux.min.css')

fuelux_responsive_css = Resource(library, 'css/fuelux-responsive.css')

loader = Resource(library, 'js/loader.js',
                  minified='js/loader.min.js')

fuelux_js = Resource(library, 'js/all.js',
                     minified='js/all.min.js',
                     depends=[bootstrap, ])

fuelux = Group([fuelux_css, fuelux_js])
