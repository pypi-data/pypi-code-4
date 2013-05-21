""" Alchemy controllers
"""
import logging
import transaction
from zope.component import queryUtility, queryAdapter
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from Products.statusmessages.interfaces import IStatusMessage

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from eea.alchemy.interfaces import IDiscoverGeoTags
from eea.alchemy.interfaces import IDiscoverTags
from eea.alchemy.interfaces import IDiscoverTime

logger = logging.getLogger('eea.alchemy.tool')

DISCOVER = (
    ('location', 'Geographical coverage'),
    ('temporalCoverage', 'Temporal coverage'),
    ('subject', 'Keywords'),
)

class Alchemy(BrowserView):
    """ Main Controller

        >>> self.loginAsPortalOwner()
        >>> from zope.component import getMultiAdapter
        >>> view = getMultiAdapter((portal, portal.REQUEST),
        ...                         name=u'alchemy-tags.html')

        >>> print view()
        <...Auto-discover geographical coverage, temporal coverage and...

    """

class Search(BrowserView):
    """ Search View

        >>> self.loginAsPortalOwner()
        >>> from zope.component import getMultiAdapter
        >>> view = getMultiAdapter((portal, portal.REQUEST),
        ...                         name=u'alchemy.search')

        >>> print view()
        <...Portal types... ...Look in... ...Discover...

    """
    @property
    def portal_types(self):
        """ Available portal types
        """
        voc = queryUtility(IVocabularyFactory,
                           name=u"eea.faceted.vocabularies.FacetedPortalTypes")

        for term in voc(self.context):
            yield term

    @property
    def atschema(self):
        """ Archetypes base schema
        """
        voc = queryUtility(IVocabularyFactory,
                           name=u"eea.faceted.vocabularies.CatalogIndexes")

        for term in voc(self.context):
            if not term.value:
                continue
            yield term

    @property
    def discover(self):
        """ Discoverable tags
        """
        for term in DISCOVER:
            yield SimpleTerm(term[0], term[0], term[1])

class Update(BrowserView):
    """ Results View

        >>> self.loginAsPortalOwner()
        >>> from zope.component import getMultiAdapter
        >>> view = getMultiAdapter((portal, portal.REQUEST),
        ...                         name=u'alchemy.update')

        >>> print view()
        Auto-discover complete

    """

    def __init__(self, context, request):
        super(Update, self).__init__(context, request)
        self._form = {}

    def _redirect(self, msg='', to=''):
        """ Return or redirect
        """
        if not to:
            return msg

        if not self.request:
            return msg

        if msg:
            IStatusMessage(self.request).addStatusMessage(str(msg), type='info')
        self.request.response.redirect(to)
        return msg

    @property
    def form(self):
        """ Request form
        """
        if not self._form:
            self._form = self.request.form
        return self._form

    def discover(self, brain, interface=None, preview=False):
        """ Discover tags in brain
        """
        discover = queryAdapter(brain, interface)
        if not discover:
            logger.warn('No adapter found for %s, %s', brain, interface)
            return

        lookin = self.form.get('lookin', [])
        discover.metadata = lookin
        if preview:
            discovery_data = discover.preview
            if discovery_data:
                return discovery_data[1]
            else:
                return
        else:
            discover.tags = 'Update'

    def save(self):
        """ Auto-discover tags and persist them in ZODB
        """
        ctool = getToolByName(self.context, 'portal_catalog')
        ptype = self.form.get('portal_type', None)
        brains = ctool(Language='all', portal_type=ptype)
        batch = self.form.get('alchemy-batch', '0-0')
        lookfor = self.form.get('discover', [])
        lookin = self.form.get('lookin', [])

        logger.info('Applying alchemy %s auto-discover on %s %s objects. '
                    'Looking in %s', lookfor, len(brains), ptype, lookin)

        count = 0
        for brain in brains[int(batch.split('-')[0]):int(batch.split('-')[1])]:
            count += 1
            if "location" in lookfor:
                self.discover(brain, IDiscoverGeoTags)
            if 'temporalCoverage' in lookfor:
                self.discover(brain, IDiscoverTime)
            if 'subject' in lookfor:
                self.discover(brain, IDiscoverTags)
            if not (count % 10):
                transaction.commit()

        return 'Auto-discover complete'

    def preview(self):
        """ Preview auto-discovered tags
        """
        ctool = getToolByName(self.context, 'portal_catalog')
        ptype = self.form.get('portal_type', None)
        brains = ctool(Language='all', portal_type=ptype)
        batch = self.form.get('alchemy-batch', '0-0')
        lookfor = self.form.get('discover', [])
        lookin = self.form.get('lookin', [])

        preview_report = ('<strong>Applying alchemy %s auto-discover on %s %s '
                          'objects. Looking in %s:</strong><ol>' % (
                              lookfor, len(brains), ptype, lookin))
        count = 0
        for brain in brains[int(batch.split('-')[0]):int(batch.split('-')[1])]:
            count += 1

            if "location" in lookfor:
                data = self.discover(brain, IDiscoverGeoTags, True)
            if 'temporalCoverage' in lookfor:
                data = self.discover(brain, IDiscoverTime, True)
            if 'subject' in lookfor:
                data = self.discover(brain, IDiscoverTags, True)

            if data:
                preview_report += '<li>%s</li>' % data
            if not (count % 10):
                transaction.commit()
        preview_report += '</ol>'

        return preview_report

    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)
        self._form = kwargs
        redirect = kwargs.get('redirect', '@@alchemy-tags.html')
        preview = kwargs.get('preview', None)
        try:
            if preview:
                msg = self.preview()
            else:
                msg = self.save()
            return self._redirect(msg, redirect)
        except Exception, err:
            logger.exception(err)
            return self._redirect(err, redirect)

class Batch(BrowserView):
    """ Batch info
    """

    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)
        ptype = kwargs.get('portal_type', '')
        ctool = getToolByName(self.context, 'portal_catalog')
        brains = ctool(Language='all', portal_type=ptype)
        return len(brains)
