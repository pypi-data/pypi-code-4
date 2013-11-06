from StringIO import StringIO
import greplin.scales
import greplin.scales.formats
import greplin.scales.util


def scales_stats(request):
    parts = request.matchdict.get('prefix')
    path = '/'.join(parts)
    stats = greplin.scales.util.lookup(greplin.scales.getStats(), parts)

    output = StringIO()
    outputFormat = request.params.get('format', 'html')
    query = request.params.get('query', None)
    if outputFormat == 'json':
        request.response.content_type = 'application/json'
        greplin.scales.formats.jsonFormat(output, stats, query)
    elif outputFormat == 'prettyjson':
        request.response.content_type = 'application/json'
        greplin.scales.formats.jsonFormat(output, stats, query, pretty=True)
    else:
        request.response.content_type = 'text/html'
        # XXX Dear pyramid.renderers.string_renderer_factory,
        # you can't be serious
        request.response.default_content_type = 'not-text/html'
        output.write('<html>')
        greplin.scales.formats.htmlHeader(output, '/' + path, __name__, query)
        greplin.scales.formats.htmlFormat(output, tuple(parts), stats, query)
        output.write('</html>')

    return output.getvalue()


def includeme(config):
    config.add_route('scales', '/scales/*prefix')
    config.add_view(scales_stats, route_name='scales', renderer='string')
