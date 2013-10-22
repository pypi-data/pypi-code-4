from fanstatic import Library, Resource
from js.jquery import jquery
from js.jquery_datatables import jquery_datatables, fixed_header

library = Library('namespace', 'resources')

tableselect_css = Resource(library, 'tableselect.css')

tableselect = Resource(library, 'tableselect.js',
                       depends=[
                           jquery, jquery_datatables, fixed_header,
                           tableselect_css])
