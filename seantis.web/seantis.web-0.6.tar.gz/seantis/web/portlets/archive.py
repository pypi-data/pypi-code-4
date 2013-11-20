from collective.blogging.portlets.archive import Renderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class MyRenderer(Renderer):
    """Portlet renderer.

    Fixes the broken sorting.
    """

    render = ViewPageTemplateFile('archive.pt')

    def archives(self):
        result = super(MyRenderer, self).archives()
        return sorted(result, key=lambda archive: archive['year'], reverse=True)