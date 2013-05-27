from fanstatic import Library, Resource
import js.jquery
import js.jqueryui

library = Library('spiffform', 'resources')

i18n = Resource(library, 'lib/jquery.i18n.min.js',
                depends=[js.jquery.jquery])

spiffform = Resource(library, 'spiffform/spiffform.js',
                     depends=[js.jquery.jquery, js.jqueryui.jqueryui,
                              js.jqueryui.base, i18n])

spiffform_default_css = Resource(library, 'default.css',
                                 depends=[])

spiffform_css = Resource(library, 'spiffform/res/spiffform.css',
                         depends=[])

#i18n DE
spiffform_de = Resource(library, 'spiffform/spiffform-de.js',
                        depends=[spiffform, i18n,
                                 js.jqueryui.ui_datepicker_de])
