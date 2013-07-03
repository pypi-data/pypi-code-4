from zope import interface
from zope.formlib.widget import renderElement
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName

from raptus.article.listings.browser import listing

from raptus.article.core import RaptusArticleMessageFactory as _


class IAccordion(interface.Interface):
    """ Marker interface for the accordion viewlet
    """


class Component(listing.ComponentLeft):
    """ Component which lists the articles in an accordion
    """

    title = _(u'Accordion')
    description = _(u'List of the contained articles in an accordion.')
    image = '++resource++accordion.gif'
    interface = IAccordion
    viewlet = 'raptus.article.accordion'


class Viewlet(listing.ViewletLeft):
    """ Viewlet listing the articles in an accordion
    """
    type = "accordion"
    thumb_size = None
    component = "accordion"

    def _data(self, item, i, l):
        super(Viewlet, self)._data(item, i, l)
        if 'url' in item and item['url']:
            if not 'wysiwyg' in item:
                item['wysiwyg'] = ''
            item['wysiwyg'] += renderElement('p',
                                             contents=renderElement('a',
                                                                    href=item['url'],
                                                                    cssClass='button read-more',
                                                                    contents=translate(_(u'Read more'), context=self.request)))
            item['url'] = None

    @property
    def cssClass(self):
        props = getToolByName(self.context, 'portal_properties').raptus_article
        return 'accordion-listing ' + (props.getProperty('accordion_onlyone', True) and 'onlyone' or 'multiple')
