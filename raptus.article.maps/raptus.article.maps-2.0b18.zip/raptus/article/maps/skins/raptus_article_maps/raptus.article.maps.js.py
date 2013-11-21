## Script (Python) "raptus.article.maps.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=foo=None,bar=None
##title=
##

from raptus.article.maps.interfaces import IMaps, IMarkers

# LinguaPlone needs this to get the preferred language
context.REQUEST.environ['PATH_TRANSLATED'] = '/'.join(context.getPhysicalPath())
maps = IMaps(context).getMaps(path={'query': '/'})
if not len(maps):
    return ''

template = """
(function($) {

  function init(e) {
    var container = $(this);
    %(wrap)s
    %(maps)s
    %(hide)s
  }

  $(document).ready(function(e) {
    $.proxy(init, $('body'))(e);
    $('.viewletmanager').on('viewlets.updated', init);
  });

})(jQuery);
"""

wrap_template = """container.find('%(all_markers)s').wrapInner('<div class="gmnoprint"></div>');"""

hide_template = """container.find('%(all_markers)s').hide();"""

map_template = """
var props = {};
%(props)s%(markers)s
container.find('.map.%(id)s').each(function() {
  $(this).goMap(props);
  %(center)s
});
"""

markers_template = """props['markers'] = [
%(markers)s
];"""

marker_template = """{
 %(props)s,
 'html': {
   'id': '.%(map_id)s + .markers .%(marker_id)s'
 }
}"""


all_markers = []
map_templates = []
for map in maps:
    center = ''
    obj = map.getObject()
    props = {}
    if obj.getLatitude():
        props['latitude'] = obj.getLatitude()
    if obj.getLongitude():
        props['longitude'] = obj.getLongitude()
    if obj.getDepth():
        props['zoom'] = obj.getDepth()
    props['mapTypeControl'] = obj.getHideControls() and 'false' or 'true'
    props['navigationControl'] = obj.getHideControls() and 'false' or 'true'
    props['scrollwheel'] = obj.getEnableScrollZoom() and 'true' or 'false'
    props['streetViewControl'] = obj.getEnableStreetView() and 'true' or 'false'
    props['maptype'] = '"%s"' % obj.getMapType()
    if obj.getLayer():
        props['layer'] = '"%s"' % obj.getLayer()
    if obj.getEnableCenteredView():
        center = """$.goMap.fitBounds('visible');"""



    marker_brains = IMarkers(obj).getMarkers()
    markers = []
    for marker in marker_brains:
        marker_obj = marker.getObject()
        all_markers.append('.%s' % marker.UID)
        marker_props = {}
        # default icon override it in portal_skin
        marker_props['icon'] = '"%s/googlemaps_marker.png"' % context.absolute_url()
        if marker_obj.getLatitude():
            marker_props['latitude'] = marker_obj.getLatitude()
        if marker_obj.getLongitude():
            marker_props['longitude'] = marker_obj.getLongitude()
        markers.append(marker_template % dict(props=',\n '.join(["'%(name)s': %(value)s" % dict(name=name, value=value) for name, value in marker_props.items()]),
                                              map_id=map.UID,
                                              marker_id=marker.UID))
    map_templates.append(map_template % dict(id=map.UID,
                                             props=''.join(['props["%(name)s"] = %(value)s;\n' % dict(name=name, value=value) for name, value in props.items()]),
                                             markers=markers and markers_template % dict(markers=',\n'.join(markers)) or '',
                                             center=center))
all_markers = ', '.join(all_markers)

wrap = ''
hide = ''
if all_markers:
    wrap = wrap_template % dict(all_markers=all_markers)
    hide = hide_template % dict(all_markers=all_markers)

return template % dict(maps='\n'.join(map_templates), wrap=wrap, hide=hide)
