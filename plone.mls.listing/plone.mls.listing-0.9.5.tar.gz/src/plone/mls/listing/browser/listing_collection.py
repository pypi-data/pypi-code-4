# -*- coding: utf-8 -*-
"""MLS Listing collection."""

# zope imports
from plone.app.layout.viewlets.common import ViewletBase
from plone.directives import form
from plone.memoize.view import memoize
from z3c.form import field, button
from z3c.form.browser import checkbox
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
from zope.interface import Interface, alsoProvides, noLongerProvides
from zope.traversing.browser.absoluteurl import absoluteURL

# local imports
from plone.mls.core.navigation import ListingBatch
from plone.mls.listing.api import prepare_search_params, search
from plone.mls.listing.browser.interfaces import (IBaseListingItems,
    IListingDetails)
from plone.mls.listing.i18n import _


CONFIGURATION_KEY = 'plone.mls.listing.listingcollection'


class IPossibleListingCollection(Interface):
    """Marker interface for possible ListingCollection viewlet."""


class IListingCollection(IBaseListingItems):
    """Marker interface for ListingCollection viewlet."""


class ListingCollectionViewlet(ViewletBase):
    """Dynamic collection of MLS listings."""

    _listings = None
    _batching = None

    @property
    def available(self):
        return IListingCollection.providedBy(self.context) and \
               not IListingDetails.providedBy(self.view)

    @property
    def config(self):
        """Get view configuration data from annotations."""
        annotations = IAnnotations(self.context)
        return annotations.get(CONFIGURATION_KEY, {})

    def update(self):
        """Prepare view related data."""
        super(ListingCollectionViewlet, self).update()
        self.context_state = queryMultiAdapter((self.context, self.request),
                                               name='plone_context_state')

        self.limit = self.config.get('limit', 25)
        self._get_listings()

    def _get_listings(self):
        """Query the recent listings from the MLS."""
        params = {
            'limit': self.limit,
            'offset': self.request.get('b_start', 0),
            'lang': self.portal_state.language(),
        }
        params.update(self.config)
        params = prepare_search_params(params)
        results, batching = search(params)
        self._listings = results
        self._batching = batching

    @property
    @memoize
    def listings(self):
        """Return listing results."""
        return self._listings

    @memoize
    def view_url(self):
        """Generate view url."""
        if not self.context_state.is_view_template():
            return self.context_state.current_base_url()
        else:
            return absoluteURL(self.context, self.request) + '/'

    @property
    def batching(self):
        return ListingBatch(self.listings, self.limit,
                            self.request.get('b_start', 0), orphan=1,
                            batch_data=self._batching)


class IListingCollectionConfiguration(Interface):
    """Listing Collection Configuration Form."""

    listing_type = schema.Tuple(
        default=('cl', 'cs', 'll', 'rl', 'rs', ),
        required=False,
        title=_(u'Listing Type'),
        value_type=schema.Choice(
            source='plone.mls.listing.ListingTypes'
        ),
    )

    location_state = schema.Choice(
        required=False,
        title=_(u'State'),
        source='plone.mls.listing.LocationStates',
    )

    location_county = schema.Choice(
        required=False,
        title=_(u'County'),
        source='plone.mls.listing.LocationCounties',
    )

    location_district = schema.Choice(
        required=False,
        title=_(u'District'),
        source='plone.mls.listing.LocationDistricts',
    )

    price_min = schema.Int(
        required=False,
        title=_(u'Price (Min)'),
    )

    price_max = schema.Int(
        required=False,
        title=_(u'Price (Max)'),
    )

    location_type = schema.Tuple(
        required=False,
        title=_(u'Location Type'),
        value_type=schema.Choice(
            source='plone.mls.listing.LocationTypes'
        ),
    )

    geographic_type = schema.Tuple(
        required=False,
        title=_(u'Geographic Type'),
        value_type=schema.Choice(
            source='plone.mls.listing.GeographicTypes'
        ),
    )

    view_type = schema.Tuple(
        required=False,
        title=_(u'View Type'),
        value_type=schema.Choice(
            source='plone.mls.listing.ViewTypes'
        ),
    )

    object_type = schema.Tuple(
        required=False,
        title=_(u'Object Type'),
        value_type=schema.Choice(
            source='plone.mls.listing.ObjectTypes'
        ),
    )

    ownership_type = schema.Tuple(
        required=False,
        title=_(u'Ownership Type'),
        value_type=schema.Choice(
            source='plone.mls.listing.OwnershipTypes'
        ),
    )

    limit = schema.Int(
        default=25,
        required=False,
        title=_(u'Items per Page'),
    )


class ListingCollectionConfiguration(form.Form):
    """Listing Collection Configuration Form."""

    fields = field.Fields(IListingCollectionConfiguration)
    fields['geographic_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['listing_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['location_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['object_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['ownership_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['view_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    label = _(u"'Listing Collection' Configuration")
    description = _(
        u"Adjust the behaviour for this 'Listing Collection' viewlet."
    )

    def getContent(self):
        annotations = IAnnotations(self.context)
        return annotations.get(CONFIGURATION_KEY,
                               annotations.setdefault(CONFIGURATION_KEY, {}))

    @button.buttonAndHandler(_(u'Save'))
    def handle_save(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        annotations = IAnnotations(self.context)
        annotations[CONFIGURATION_KEY] = data
        self.request.response.redirect(absoluteURL(self.context, self.request))

    @button.buttonAndHandler(_(u'Cancel'))
    def handle_cancel(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request))


class ListingCollectionStatus(object):
    """Return activation/deactivation status of ListingCollection viewlet."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def can_activate(self):
        return IPossibleListingCollection.providedBy(self.context) and \
            not IListingCollection.providedBy(self.context)

    @property
    def active(self):
        return IListingCollection.providedBy(self.context)


class ListingCollectionToggle(object):
    """Toggle ListingCollection viewlet for the current context."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        msg_type = 'info'

        if IListingCollection.providedBy(self.context):
            # Deactivate ListingCollection viewlet.
            noLongerProvides(self.context, IListingCollection)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u"'Listing Collection' viewlet deactivated.")
        elif IPossibleListingCollection.providedBy(self.context):
            alsoProvides(self.context, IListingCollection)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u"'Listing Collection' viewlet activated.")
        else:
            msg = _(
                u"The 'Listing Collection' viewlet does't work with this "
                u"content type. Add 'IPossibleListingCollection' to the "
                u"provided interfaces to enable this feature."
            )
            msg_type = 'error'

        self.context.plone_utils.addPortalMessage(msg, msg_type)
        self.request.response.redirect(self.context.absolute_url())
