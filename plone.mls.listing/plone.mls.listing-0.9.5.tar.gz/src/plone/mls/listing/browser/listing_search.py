# -*- coding: utf-8 -*-
"""MLS Listing Search."""

# zope imports
from Acquisition import aq_inner
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.directives import form
from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager, IPortletRetriever
from plone.z3cform import z2
from z3c.form import field, button
from z3c.form.browser import checkbox, radio
from z3c.form.interfaces import IFormLayer
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, queryMultiAdapter
from zope.interface import Interface, alsoProvides, noLongerProvides
from zope.traversing.browser.absoluteurl import absoluteURL

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

# local imports
from plone.mls.core.navigation import ListingBatch
from plone.mls.listing.api import prepare_search_params, search
from plone.mls.listing.browser.interfaces import (IBaseListingItems,
    IListingDetails)
from plone.mls.listing.browser.valuerange.widget import ValueRangeFieldWidget
from plone.mls.listing.i18n import _

CONFIGURATION_KEY = 'plone.mls.listing.listingsearch'

FIELD_ORDER = {
    'row_listing_type': [
        'listing_type',
    ],
    'row_location': [
        'location_state',
        'location_county',
        'location_district',
    ],
    'row_price': [
        'location_city',
        'price_min',
        'price_max',
    ],
    'row_beds_baths': [
        'beds',
        'baths',
    ],
    'row_sizes': [
        'lot_size',
        'interior_area',
    ],
    'row_other': [
        'air_condition',
        'pool',
        'jacuzzi',
    ],
    'row_tabbed': [
        'location_type',
        'geographic_type',
        'view_type',
        'object_type',
        'ownership_type'
    ],
}


def encode_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict


class IPossibleListingSearch(Interface):
    """Marker interface for possible ListingSearch viewlet."""


class IListingSearch(IBaseListingItems):
    """Marker interface for ListingSearch viewlet."""


class IListingSearchForm(Interface):
    """Listing search form schema definition."""

    listing_type = schema.Tuple(
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

    location_city = schema.TextLine(
        required=False,
        title=_(u'City/Town'),
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

    beds = schema.Tuple(
        default=('--MINVALUE--', '--MAXVALUE--'),
        required=False,
        title=_(u'Bedrooms'),
        value_type=schema.Choice(
            source='plone.mls.listing.Rooms',
        ),
    )

    baths = schema.Tuple(
        default=('--MINVALUE--', '--MAXVALUE--'),
        required=False,
        title=_(u'Bathrooms'),
        value_type=schema.Choice(
            source='plone.mls.listing.Rooms',
        ),
    )

    air_condition = schema.Choice(
        default='--NOVALUE--',
        required=False,
        source='plone.mls.listing.YesNoAll',
        title=_(u'Air Condition'),
    )

    pool = schema.Choice(
        default='--NOVALUE--',
        required=False,
        source='plone.mls.listing.YesNoAll',
        title=_(u'Pool'),
    )

    jacuzzi = schema.Choice(
        default='--NOVALUE--',
        required=False,
        source='plone.mls.listing.YesNoAll',
        title=_(u'Jacuzzi'),
    )

    lot_size = schema.Tuple(
        default=('--MINVALUE--', '--MAXVALUE--'),
        required=False,
        title=_(u'Lot Size'),
        value_type=schema.Choice(
            source='plone.mls.listing.LotSizes',
        ),
    )

    interior_area = schema.Tuple(
        default=('--MINVALUE--', '--MAXVALUE--'),
        required=False,
        title=_(u'Interior Area'),
        value_type=schema.Choice(
            source='plone.mls.listing.InteriorAreaSizes',
        ),
    )


class ListingSearchForm(form.Form):
    """Listing Search Form."""
    fields = field.Fields(IListingSearchForm)
    template = ViewPageTemplateFile('templates/search_form.pt')
    ignoreContext = True
    method = 'get'

    fields['air_condition'].widgetFactory = radio.RadioFieldWidget
    fields['baths'].widgetFactory = ValueRangeFieldWidget
    fields['lot_size'].widgetFactory = ValueRangeFieldWidget
    fields['interior_area'].widgetFactory = ValueRangeFieldWidget
    fields['beds'].widgetFactory = ValueRangeFieldWidget
    fields['geographic_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['jacuzzi'].widgetFactory = radio.RadioFieldWidget
    fields['listing_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['location_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['object_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['ownership_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['pool'].widgetFactory = radio.RadioFieldWidget
    fields['view_type'].widgetFactory = checkbox.CheckBoxFieldWidget

    def update(self):
        return super(ListingSearchForm, self).update()

    @button.buttonAndHandler(PMF(u'label_search', default=u'Search'),
                             name='search')
    def handle_search(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

    def _widgets(self, row):
        """Return a list of widgets that should be shown for a given row."""
        widget_data = dict(self.widgets.items())
        available_fields = FIELD_ORDER.get(row, [])
        return [widget_data.get(field, None) for field in available_fields]

    def widgets_listing_type(self):
        """Return the widgets for the row ``row_listing_type``."""
        return self._widgets('row_listing_type')

    def widgets_location(self):
        """Return the widgets for the row ``row_location``."""
        return self._widgets('row_location')

    def widgets_price(self):
        """Return the widgets for the row ``row_price``."""
        return self._widgets('row_price')

    def widgets_beds_baths(self):
        """Return the widgets for the row ``row_beds_baths``."""
        return self._widgets('row_beds_baths')

    def widgets_sizes(self):
        """Return the widgets for the row ``row_sizes``."""
        return self._widgets('row_sizes')

    def widgets_other(self):
        """Return the widgets for the row ``row_other``."""
        return self._widgets('row_other')

    def widgets_outstanding(self):
        """Return all other widgets that have not been shown until now."""
        defined_fields = FIELD_ORDER.values()
        shown_fields = [shown_field for field_lists in defined_fields for \
                        shown_field in field_lists]
        return [widget for field_name, widget in self.widgets.items() if not \
                    field_name in shown_fields]

    def widgets_tabbed(self):
        """Return the widgets for the row ``row_tabbed``."""
        return self._widgets('row_tabbed')


class ListingSearchViewlet(ViewletBase):
    """Search for listings in the MLS."""

    _listings = None
    _batching = None

    @property
    def available(self):
        return IListingSearch.providedBy(self.context) and \
               not IListingDetails.providedBy(self.view)

    @property
    def config(self):
        """Get view configuration data from annotations."""
        annotations = IAnnotations(self.context)
        return annotations.get(CONFIGURATION_KEY, {})

    @property
    def hide_form(self):
        if self.config.get('hide_form', False) == False:
            return False

        from plone.mls.listing.portlets.quick_search import IQuickSearchPortlet
        portlets = []
        for column in ["plone.leftcolumn", "plone.rightcolumn"]:
            manager = manager = getUtility(IPortletManager, name=column)
            retriever = queryMultiAdapter((self.context, manager),
                                          IPortletRetriever)
            portlets.extend(retriever.getPortlets())
        return len([portlet for portlet in portlets if \
            IQuickSearchPortlet.providedBy(portlet['assignment'])]) > 0

    def update(self):
        """Prepare view related data."""
        super(ListingSearchViewlet, self).update()
        self.context_state = queryMultiAdapter((self.context, self.request),
                                               name='plone_context_state')

        self.limit = self.config.get('limit', 25)

        z2.switch_on(self, request_layer=IFormLayer)
        self.form = ListingSearchForm(aq_inner(self.context), self.request)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()

        if self.available and len(self.request.form) > 0:
            data, errors = self.form.extractData()
            if not errors:
                self._get_listings(prepare_search_params(data))

            self.request.form = encode_dict(self.request.form)

    def _get_listings(self, params):
        """Query the recent listings from the MLS."""
        search_params = {
            'limit': self.limit,
            'offset': self.request.get('b_start', 0),
            'lang': self.portal_state.language(),
        }
        search_params.update(params)
        results, batching = search(search_params)
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


class IListingSearchConfiguration(Interface):
    """Listing Search Configuration Form."""

    limit = schema.Int(
        default=25,
        required=False,
        title=_(u'Items per Page'),
    )

    hide_form = schema.Bool(
        default=True,
        required=False,
        title=_(
            u'Hide the search form when Quick Search Portlet is available?'
        ),
    )


class ListingSearchConfiguration(form.Form):
    """Listing Search Configuration Form."""

    fields = field.Fields(IListingSearchConfiguration)
    label = _(u"'Listing Search' Configuration")
    description = _(u"Adjust the behaviour for this 'Listing Search' viewlet.")

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
        return u''

    @button.buttonAndHandler(_(u'Cancel'))
    def handle_cancel(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request))
        return u''


class ListingSearchStatus(object):
    """Return activation/deactivation status of ListingSearch viewlet."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def can_activate(self):
        return IPossibleListingSearch.providedBy(self.context) and \
            not IListingSearch.providedBy(self.context)

    @property
    def active(self):
        return IListingSearch.providedBy(self.context)


class ListingSearchToggle(object):
    """Toggle ListingSearch viewlet for the current context."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        msg_type = 'info'

        if IListingSearch.providedBy(self.context):
            # Deactivate ListingSearch viewlet.
            noLongerProvides(self.context, IListingSearch)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u"'Listing Search' viewlet deactivated.")
        elif IPossibleListingSearch.providedBy(self.context):
            alsoProvides(self.context, IListingSearch)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u"'Listing Search' viewlet activated.")
        else:
            msg = _(
                u"The 'Listing Search' viewlet does't work with this content "
                u"type. Add 'IPossibleListingSearch' to the provided "
                u"interfaces to enable this feature."
            )
            msg_type = 'error'

        self.context.plone_utils.addPortalMessage(msg, msg_type)
        self.request.response.redirect(self.context.absolute_url())
