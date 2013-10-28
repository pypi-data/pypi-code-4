from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_timeago_plugin', 'resources')
timeago = Resource(library, 'jquery.timeago.js', depends=[jquery])
