from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface
from Acquisition import aq_inner
from five import grok
from Products.CMFPlone.utils import safe_unicode

def main2():
    import urllib2
    sock = urllib2.urlopen('http://biodiversity.europa.eu/AAAAAAA-News')
    return sock.read()

class ImportNews(grok.View):
    grok.context(Interface)
    grok.require('cmf.ModifyPortalContent')
    grok.name('importnews')

    def render(self):
        context = aq_inner(self.context)
        wtool = getToolByName(context, 'portal_workflow')
        from logging import getLogger
        log = getLogger('Import News')
        for item in eval(main2()):
            id = context.invokeFactory(
                id=item['id'],
                type_name='News Item',
                title=item['title'],
                )
            newsitem = context.get(id)
            text = u' '.join((safe_unicode(item['description'], 'latin-1'),
                              safe_unicode(item.get('details', ''), 'latin-1')
                              ))
            text = text.replace(u'\x96', u'').replace(u'\x92', u'').replace(u'\x93', u'').replace(u'\x94', u'')
            newsitem.text = RichTextValue(text, 'text/html', 'text/html')
            newsitem.setModificationDate(item['last_modification'])
            newsitem.setEffectiveDate(item['releasedate'])
            newsitem.resourceurl = item.get('resourceurl', '')
            newsitem.source = item.get('source', '')
            if item.get('bigpicture', None):
                data = item.get('bigpicture')
                log.info('Image for %s' % id)
                newsitem.image = NamedBlobImage(data=data)
            wtool.doActionFor(newsitem, action='publish')
            log.info('Added: %s' % id)
            try:
                newsitem.reindexObject()
            except Exception, e:
                log.exception(e)

        return 1