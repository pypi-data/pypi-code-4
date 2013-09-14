from fanstatic import Library, Resource
from js.angular import angular
from js.bootstrap import bootstrap_css

library = Library('angularuibootstrap', 'resources')

angular_ui_bootstrap = Resource(library, 'ui-bootstrap-tpls-0.6.0.js',
                            minified='ui-bootstrap-tpls-0.6.0.min.js',
                            depends=[angular, bootstrap_css])
