from fanstatic import Library, Resource, Group
from js.jquery import jquery

library = Library('jquery_datatables', 'resources')

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')

jquery_datatables_css = Resource(
    library,
    'media/css/jquery.dataTables.css'
)

jquery_datatables_js = Resource(
    library, 'media/js/jquery.dataTables.js',
    depends=[jquery],
    minified='media/js/jquery.dataTables.min.js'
)

jquery_datatables = Group(depends=[
        jquery_datatables_css, jquery_datatables_js]
)

autofill_css = Resource(
    library, 'extras/AutoFill/media/css/AutoFill.css')

autofill = Resource(
    library, 'extras/AutoFill/media/js/AutoFill.js',
    depends=[jquery_datatables_js, autofill_css],
    minified='extras/AutoFill/media/js/AutoFill.min.js')

colreorder_css = Resource(
    library, 'extras/ColReorder/media/css/ColReorder.css')

colreorder = Resource(
    library, 'extras/ColReorder/media/js/ColReorder.js',
    depends=[jquery_datatables_js, colreorder_css],
    minified='extras/ColReorder/media/js/ColReorder.min.js')

colvis_css = Resource(
    library, 'extras/ColVis/media/css/ColVis.css')

colvis = Resource(
    library, 'extras/ColVis/media/js/ColVis.js',
    depends=[jquery_datatables_js, colvis_css],
    minified='extras/ColVis/media/js/ColVis.min.js')

fixed_columns = Resource(
    library, 'extras/FixedColumns/media/js/FixedColumns.js',
    depends=[jquery_datatables_js],
    minified='extras/FixedColumns/media/js/FixedColumns.min.js')

fixed_header = Resource(
    library, 'extras/FixedHeader/js/FixedHeader.js',
    depends=[jquery_datatables_js],
    minified='extras/FixedHeader/js/FixedHeader.min.js')

keytable = Resource(
    library, 'extras/KeyTable/js/KeyTable.js',
    depends=[jquery_datatables_js],
    minified='extras/KeyTable/js/KeyTable.min.js')

scroller_css = Resource(
    library, 'extras/Scroller/media/css/dataTables.scroller.css')

scroller = Resource(
    library, 'extras/Scroller/media/js/dataTables.scroller.js',
    depends=[jquery_datatables_js, scroller_css],
    minified='extras/Scroller/media/js/dataTables.scroller.min.js')

table_tools_css = Resource(
    library, 'extras/TableTools/media/css/TableTools.css')

table_tools = Resource(
    library, 'extras/TableTools/media/js/TableTools.js',
    depends=[jquery_datatables_js, table_tools_css],
    minified='extras/TableTools/media/js/TableTools.min.js')

