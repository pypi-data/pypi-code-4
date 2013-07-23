from fanstatic import Library, Resource

library = Library('css3mediaqueries', 'resources')


def renderer(url):
    return """
<!--[if lt IE 9 ]>
  <script src="%s"></script>
<![endif]-->""" % url


css3mediaqueries = Resource(
    library, 'css3-mediaqueries.js',
    bottom=True,
    renderer=renderer,
)
